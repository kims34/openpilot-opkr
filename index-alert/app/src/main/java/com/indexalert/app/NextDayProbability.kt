package com.indexalert.app

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.util.Locale
import kotlin.math.exp
import kotlin.math.max
import kotlin.math.min
import kotlin.math.pow
import kotlin.math.sqrt


data class NextDayEstimate(
    val probability: Double,
    val sampleSize: Int,
    val baseRate: Double,
    val method: String,
    val rangeLow: Double? = null,
    val rangeHigh: Double? = null,
    val reliability: String = "낮음",
    val backtestSkill: Double? = null,
    val validationCount: Int = 0,
    val modelVersion: String = "2.1"
)

object NextDayProbabilityRepository {
    private var cachedAt = 0L
    private var cache: Map<String, NextDayEstimate> = emptyMap()
    private const val CACHE_MS = 15 * 60 * 1000L
    private val symbols = mapOf("sp500" to "SPY", "ndx" to "QQQ", "djdiv" to "SCHD")
    private val ny = ZoneId.of("America/New_York")

    @Synchronized
    fun get(indexId: String): NextDayEstimate? {
        val now = System.currentTimeMillis()
        if (cache.isNotEmpty() && now - cachedAt < CACHE_MS) return cache[indexId]

        val server = runCatching { fetchFromServer() }.getOrNull().orEmpty()
        val merged = server.toMutableMap()
        if (merged.size < symbols.size) {
            symbols.forEach { (id, symbol) ->
                if (id !in merged) {
                    runCatching { calculateLocally(symbol) }.getOrNull()?.let { merged[id] = it }
                }
            }
        }
        cache = merged
        cachedAt = now
        return cache[indexId]
    }

    private fun fetchFromServer(): Map<String, NextDayEstimate> {
        val base = BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/')
        val c = URL("$base/next-day-probabilities").openConnection() as HttpURLConnection
        c.requestMethod = "GET"
        c.connectTimeout = 6000
        c.readTimeout = 20000
        c.setRequestProperty("Accept", "application/json")
        try {
            if (c.responseCode !in 200..299) throw IllegalStateException("확률 서버 오류 ${c.responseCode}")
            val root = JSONObject(c.inputStream.bufferedReader().use { it.readText() })
            val items = root.optJSONObject("items") ?: JSONObject()
            return buildMap {
                symbols.keys.forEach { id ->
                    val o = items.optJSONObject(id) ?: return@forEach
                    if (o.has("error")) return@forEach
                    val probability = o.optDouble("probability", Double.NaN)
                    if (!probability.isFinite()) return@forEach
                    put(
                        id,
                        NextDayEstimate(
                            probability = probability,
                            sampleSize = o.optInt("sample_size", 0),
                            baseRate = o.optDouble("base_rate", Double.NaN),
                            method = o.optString("method", "10년 다변수 유사도 + 워크포워드 검증"),
                            rangeLow = o.optDouble("range_low", Double.NaN).takeIf { it.isFinite() },
                            rangeHigh = o.optDouble("range_high", Double.NaN).takeIf { it.isFinite() },
                            reliability = o.optString("reliability", "낮음"),
                            backtestSkill = o.optDouble("backtest_skill", Double.NaN).takeIf { it.isFinite() },
                            validationCount = o.optInt("validation_count", 0),
                            modelVersion = o.optString("model_version", root.optString("model_version", "2.1"))
                        )
                    )
                }
            }
        } finally {
            c.disconnect()
        }
    }

    private data class PricePoint(val ts: Long, val price: Double)
    private data class ModelData(val prices: List<Double>, val features: Array<DoubleArray?>)
    private data class CoreResult(val posterior: Double, val baseRate: Double, val effectiveN: Double)
    private data class ValidationResult(val skill: Double, val trust: Double, val count: Int)
    private data class Neighbor(val distance2: Double, val index: Int, val outcome: Double)

    private fun fetchSeries(symbol: String): List<PricePoint> {
        val encoded = URLEncoder.encode(symbol, "UTF-8")
        val url = "https://query1.finance.yahoo.com/v8/finance/chart/$encoded?range=10y&interval=1d&includePrePost=false&events=div%2Csplits"
        val c = URL(url).openConnection() as HttpURLConnection
        c.requestMethod = "GET"
        c.connectTimeout = 8000
        c.readTimeout = 18000
        c.setRequestProperty("Accept", "application/json")
        c.setRequestProperty("User-Agent", "Mozilla/5.0 IndexAlert/2.1")
        try {
            if (c.responseCode !in 200..299) throw IllegalStateException("Yahoo 확률 계산 오류 ${c.responseCode}")
            val root = JSONObject(c.inputStream.bufferedReader().use { it.readText() })
            val result = root.getJSONObject("chart").getJSONArray("result").getJSONObject(0)
            val timestamps = result.optJSONArray("timestamp") ?: JSONArray()
            val indicators = result.getJSONObject("indicators")
            val quote = indicators.getJSONArray("quote").getJSONObject(0)
            val quoteCloses = quote.optJSONArray("close") ?: JSONArray()
            val adjBlocks = indicators.optJSONArray("adjclose")
            val adjCloses = if (adjBlocks != null && adjBlocks.length() > 0) adjBlocks.getJSONObject(0).optJSONArray("adjclose") else null
            val source = if (adjCloses != null && adjCloses.length() == timestamps.length()) adjCloses else quoteCloses

            val rows = mutableListOf<PricePoint>()
            val n = minOf(timestamps.length(), source.length())
            for (i in 0 until n) {
                if (source.isNull(i)) continue
                val px = source.optDouble(i, Double.NaN)
                val ts = timestamps.optLong(i, 0L)
                if (ts > 0 && px.isFinite() && px > 0.0) rows += PricePoint(ts, px)
            }

            val meta = result.optJSONObject("meta")
            val regularEnd = meta?.optJSONObject("currentTradingPeriod")?.optJSONObject("regular")?.optLong("end", 0L) ?: 0L
            val nowSec = System.currentTimeMillis() / 1000L
            if (rows.isNotEmpty() && regularEnd > 0 && nowSec < regularEnd) {
                val lastDay = Instant.ofEpochSecond(rows.last().ts).atZone(ny).toLocalDate()
                if (lastDay == LocalDate.now(ny)) rows.removeAt(rows.lastIndex)
            }
            if (rows.size < 520) throw IllegalStateException("확률 계산 이력 부족")
            return rows
        } finally {
            c.disconnect()
        }
    }

    private fun feature(prices: List<Double>, i: Int): DoubleArray {
        val r1 = prices[i] / prices[i - 1] - 1.0
        val r5 = prices[i] / prices[i - 5] - 1.0
        val r20 = prices[i] / prices[i - 20] - 1.0
        var mean = 0.0
        val returns = DoubleArray(20)
        for (j in 0 until 20) {
            val idx = i - 19 + j
            val r = prices[idx] / prices[idx - 1] - 1.0
            returns[j] = r
            mean += r
        }
        mean /= 20.0
        var variance = 0.0
        for (r in returns) variance += (r - mean) * (r - mean)
        val vol20 = sqrt(variance / 20.0)
        var high60 = 0.0
        for (j in i - 59..i) high60 = max(high60, prices[j])
        val dd60 = prices[i] / high60 - 1.0
        return doubleArrayOf(r1, r5, r20, vol20, dd60)
    }

    private fun prepare(prices: List<Double>): ModelData {
        val features = arrayOfNulls<DoubleArray>(prices.size)
        for (i in 60 until prices.size) features[i] = feature(prices, i)
        return ModelData(prices, features)
    }

    private fun corePredict(data: ModelData, t: Int): CoreResult {
        if (t < 320) throw IllegalStateException("확률 학습 이력 부족")
        val current = data.features[t] ?: throw IllegalStateException("현재 특징 계산 실패")
        val count = t - 60
        val means = DoubleArray(5)
        for (i in 60 until t) {
            val f = data.features[i] ?: continue
            for (k in 0..4) means[k] += f[k]
        }
        for (k in 0..4) means[k] /= count.toDouble()

        val floors = doubleArrayOf(0.003, 0.010, 0.020, 0.003, 0.020)
        val scales = DoubleArray(5)
        for (i in 60 until t) {
            val f = data.features[i] ?: continue
            for (k in 0..4) {
                val d = f[k] - means[k]
                scales[k] += d * d
            }
        }
        for (k in 0..4) scales[k] = max(sqrt(scales[k] / max(1, count - 1).toDouble()), floors[k])

        val ranked = ArrayList<Neighbor>(count)
        var baseWeight = 0.0
        var baseWins = 0.0
        for (i in 60 until t) {
            val f = data.features[i] ?: continue
            val outcome = if (data.prices[i + 1] > data.prices[i]) 1.0 else 0.0
            var d2 = 0.0
            for (k in 0..4) {
                val z = (f[k] - current[k]) / scales[k]
                d2 += z * z
            }
            d2 /= 5.0
            ranked += Neighbor(d2, i, outcome)

            val ageYears = (t - i).toDouble() / 252.0
            val w = 0.5.pow(ageYears / 5.0)
            baseWeight += w
            baseWins += w * outcome
        }
        ranked.sortBy { it.distance2 }

        val neighborCount = min(180, max(80, (sqrt(ranked.size.toDouble()) * 2.5).toInt()))
        var sumWeight = 0.0
        var weightedWins = 0.0
        var sumWeightSq = 0.0
        for (n in ranked.take(neighborCount)) {
            val similarity = exp(-0.5 * n.distance2)
            val ageYears = (t - n.index).toDouble() / 252.0
            val recency = 0.5.pow(ageYears / 4.0)
            val w = max(similarity, 1e-8) * recency
            sumWeight += w
            weightedWins += w * n.outcome
            sumWeightSq += w * w
        }
        val raw = if (sumWeight > 0) weightedWins / sumWeight else 0.5
        val effectiveN = if (sumWeightSq > 0) sumWeight * sumWeight / sumWeightSq else 0.0
        val baseRate = if (baseWeight > 0) baseWins / baseWeight else 0.5
        val priorStrength = 80.0
        val posterior = (raw * effectiveN + baseRate * priorStrength) / (effectiveN + priorStrength)
        return CoreResult(posterior, baseRate, effectiveN)
    }

    private fun validate(data: ModelData): ValidationResult {
        val n = data.prices.size
        val start = max(400, n - 1 - 504)
        var modelSq = 0.0
        var baseSq = 0.0
        var count = 0
        var t = start
        while (t < n - 1) {
            val estimate = runCatching { corePredict(data, t) }.getOrNull()
            if (estimate != null) {
                val outcome = if (data.prices[t + 1] > data.prices[t]) 1.0 else 0.0
                modelSq += (estimate.posterior - outcome) * (estimate.posterior - outcome)
                baseSq += (estimate.baseRate - outcome) * (estimate.baseRate - outcome)
                count++
            }
            t += 5
        }
        if (count < 40 || baseSq <= 0.0) return ValidationResult(0.0, 0.0, count)
        val modelBrier = modelSq / count
        val baseBrier = baseSq / count
        val skill = 1.0 - modelBrier / baseBrier
        val trust = min(1.0, max(0.0, skill / 0.05))
        return ValidationResult(skill, trust, count)
    }

    private fun calculateLocally(symbol: String): NextDayEstimate {
        val series = fetchSeries(symbol)
        val data = prepare(series.map { it.price })
        val core = corePredict(data, data.prices.lastIndex)
        val validation = validate(data)
        val probability = core.baseRate + validation.trust * (core.posterior - core.baseRate)

        val informationN = max(30.0, core.effectiveN + 80.0)
        val se = sqrt(max(probability * (1.0 - probability), 1e-9) / informationN)
        val halfWidth = 1.2816 * se + (1.0 - validation.trust) * 0.01
        val low = max(0.0, probability - halfWidth)
        val high = min(1.0, probability + halfWidth)
        val reliability = when {
            validation.count >= 80 && validation.skill >= 0.03 && core.effectiveN >= 70 -> "높음"
            validation.count >= 60 && validation.skill > 0.0 && core.effectiveN >= 45 -> "보통"
            else -> "낮음"
        }
        return NextDayEstimate(
            probability = probability * 100.0,
            sampleSize = core.effectiveN.toInt(),
            baseRate = core.baseRate * 100.0,
            method = "10년·5요인 유사도 + 최근가중 + 베이지안 수축 + 2년 워크포워드 검증",
            rangeLow = low * 100.0,
            rangeHigh = high * 100.0,
            reliability = reliability,
            backtestSkill = validation.skill * 100.0,
            validationCount = validation.count,
            modelVersion = "2.1-local"
        )
    }
}

@Composable
fun NextDayProbabilitySection(indexId: String) {
    if (indexId !in setOf("sp500", "ndx", "djdiv")) return

    var estimate by remember(indexId) { mutableStateOf<NextDayEstimate?>(null) }
    LaunchedEffect(indexId) {
        estimate = withContext(Dispatchers.IO) { NextDayProbabilityRepository.get(indexId) }
    }

    val e = estimate ?: return
    Spacer(Modifier.height(10.dp))
    Card(
        modifier = Modifier.fillMaxWidth(),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(Modifier.padding(12.dp)) {
            Text(
                "다음 거래일 상승 추정  ${String.format(Locale.US, "%.0f%%", e.probability)}",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            if (e.rangeLow != null && e.rangeHigh != null) {
                Text(
                    "80% 추정범위 ${String.format(Locale.US, "%.0f", e.rangeLow)}–${String.format(Locale.US, "%.0f", e.rangeHigh)}% · 검증 신뢰도 ${e.reliability}",
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(top = 3.dp)
                )
            }
            val skillText = e.backtestSkill?.let {
                " · 워크포워드 개선 ${String.format(Locale.US, "%+.1f%%", it)}"
            } ?: ""
            Text(
                "유효 유사표본 ${e.sampleSize}회 · 검증 ${e.validationCount}회$skillText",
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 3.dp)
            )
            Text(
                "장기 상승률 ${String.format(Locale.US, "%.1f%%", e.baseRate)} 쪽으로 수축하며, 과거 검증에서 개선이 없으면 장기확률에서 거의 벗어나지 않도록 제한합니다.",
                style = MaterialTheme.typography.labelSmall,
                modifier = Modifier.padding(top = 4.dp)
            )
            Text(
                "1일·5일·20일 추세, 20일 변동성, 60일 고점 대비 위치를 사용한 통계적 추정이며 보장된 예측이 아닙니다.",
                style = MaterialTheme.typography.labelSmall,
                modifier = Modifier.padding(top = 3.dp)
            )
        }
    }
}
