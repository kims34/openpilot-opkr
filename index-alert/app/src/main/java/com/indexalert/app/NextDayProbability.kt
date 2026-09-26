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
import java.util.Locale
import kotlin.math.abs


data class NextDayEstimate(
    val probability: Double,
    val sampleSize: Int,
    val baseRate: Double,
    val method: String
)

object NextDayProbabilityRepository {
    private var cachedAt = 0L
    private var cache: Map<String, NextDayEstimate> = emptyMap()
    private const val CACHE_MS = 15 * 60 * 1000L
    private val symbols = mapOf("sp500" to "SPY", "ndx" to "QQQ", "djdiv" to "SCHD")

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
        c.readTimeout = 12000
        c.setRequestProperty("Accept", "application/json")
        try {
            if (c.responseCode !in 200..299) throw IllegalStateException("확률 서버 오류 ${c.responseCode}")
            val root = JSONObject(c.inputStream.bufferedReader().use { it.readText() }).optJSONObject("items") ?: JSONObject()
            return buildMap {
                symbols.keys.forEach { id ->
                    val o = root.optJSONObject(id) ?: return@forEach
                    if (o.has("error")) return@forEach
                    val probability = o.optDouble("probability", Double.NaN)
                    if (!probability.isFinite()) return@forEach
                    put(
                        id,
                        NextDayEstimate(
                            probability = probability,
                            sampleSize = o.optInt("sample_size", 0),
                            baseRate = o.optDouble("base_rate", Double.NaN),
                            method = o.optString("method", "최근 10년 유사 흐름 통계")
                        )
                    )
                }
            }
        } finally {
            c.disconnect()
        }
    }

    private fun calculateLocally(symbol: String): NextDayEstimate {
        val encoded = URLEncoder.encode(symbol, "UTF-8")
        val url = "https://query1.finance.yahoo.com/v8/finance/chart/$encoded?range=10y&interval=1d&includePrePost=false"
        val c = URL(url).openConnection() as HttpURLConnection
        c.requestMethod = "GET"
        c.connectTimeout = 8000
        c.readTimeout = 15000
        c.setRequestProperty("Accept", "application/json")
        c.setRequestProperty("User-Agent", "Mozilla/5.0 IndexAlert/2.0")
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
            val closesArray = if (adjCloses != null && adjCloses.length() == timestamps.length()) adjCloses else quoteCloses

            val prices = buildList {
                val n = minOf(timestamps.length(), closesArray.length())
                for (i in 0 until n) {
                    if (closesArray.isNull(i)) continue
                    val px = closesArray.optDouble(i, Double.NaN)
                    if (px.isFinite() && px > 0.0) add(px)
                }
            }
            if (prices.size < 260) throw IllegalStateException("확률 계산 이력 부족")

            val latestR1 = prices.last() / prices[prices.lastIndex - 1] - 1.0
            val latestR5 = prices.last() / prices[prices.lastIndex - 5] - 1.0
            var matches = emptyList<Int>()
            val bands = listOf(0.004 to 0.012, 0.0075 to 0.020, 0.012 to 0.035, 0.020 to 0.060)
            for ((r1Band, r5Band) in bands) {
                val found = mutableListOf<Int>()
                for (i in 5 until prices.lastIndex) {
                    val r1 = prices[i] / prices[i - 1] - 1.0
                    val r5 = prices[i] / prices[i - 5] - 1.0
                    if (abs(r1 - latestR1) <= r1Band && abs(r5 - latestR5) <= r5Band) {
                        found += if (prices[i + 1] > prices[i]) 1 else 0
                    }
                }
                matches = found
                if (matches.size >= 60) break
            }

            val allNext = buildList {
                for (i in 5 until prices.lastIndex) add(if (prices[i + 1] > prices[i]) 1 else 0)
            }
            val baseRate = allNext.average()
            val n = matches.size
            val raw = if (n > 0) matches.average() else baseRate
            val priorWeight = 40.0
            val probability = ((raw * n) + (baseRate * priorWeight)) / (n + priorWeight)
            return NextDayEstimate(
                probability = probability * 100.0,
                sampleSize = n,
                baseRate = baseRate * 100.0,
                method = "최근 10년 유사 당일·5일 모멘텀 통계"
            )
        } finally {
            c.disconnect()
        }
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
            Text(
                "최근 10년 유사 흐름 표본 ${e.sampleSize}회 · 통계적 추정",
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 3.dp)
            )
            Text(
                "다음 정규장 종가가 직전 정규장 종가보다 높을 확률을 과거 유사 흐름으로 계산한 값이며 보장된 예측이 아닙니다.",
                style = MaterialTheme.typography.labelSmall,
                modifier = Modifier.padding(top = 4.dp)
            )
        }
    }
}
