package com.indexalert.app

import android.content.Context
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.Locale

private const val VALIDATED_MODEL = "3.2-live-guardrails"

data class MonthValidation(
    val count: Int,
    val modelBrier: Double,
    val baselineBrier: Double,
    val skill: Double
)

data class MonthFeatures(
    val r5: Double,
    val r21: Double,
    val r63: Double,
    val drawdown252: Double,
    val ma50Gap: Double,
    val ma200Gap: Double
)

data class TerminalReturnRank(
    val label: String,
    val probability: Double
)

data class OneMonthEstimate(
    val up10Probability: Double,
    val down10Probability: Double,
    val horizonSessions: Int,
    val sampleSize: Int,
    val baselineSampleSize: Int,
    val baselineUp10Probability: Double,
    val baselineDown10Probability: Double,
    val trendRegime: String,
    val volatilityRegime: String,
    val annualizedVolatility: Double,
    val asOf: String,
    val method: String,
    val priceBasis: String,
    val selectionUp: String,
    val selectionDown: String,
    val validationUp: MonthValidation?,
    val validationDown: MonthValidation?,
    val effectiveSampleUp: Double,
    val effectiveSampleDown: Double,
    val features: MonthFeatures?,
    val terminalReturnTop3: List<TerminalReturnRank>,
    val terminalReturnModeLabel: String?,
    val terminalReturnModeProbability: Double?,
    val terminalReturnSelection: String?,
    val terminalReturnValidation: MonthValidation?,
    val terminalReturnEffectiveSample: Double,
    val terminalReturnBinWidthPercent: Int
)

data class NextDayEstimate(
    val probability: Double,
    val baseRate: Double,
    val asOf: String,
    val targetDate: String,
    val validUntil: Long,
    val validationCount: Int,
    val brier: Double,
    val baselineBrier: Double,
    val skill: Double,
    val evidence: String,
    val useBase: Boolean,
    val calibrationLow: Int,
    val calibrationHigh: Int,
    val calibrationCount: Int,
    val observedRise: Double?,
    val observedLow: Double?,
    val observedHigh: Double?,
    val prospectiveCount: Int,
    val auditStart: String,
    val auditEnd: String,
    val oneMonth: OneMonthEstimate? = null,
    val cached: Boolean = false
)

object NextDayProbabilityRepository {
    private var lastFetch = 0L
    private var cache: Map<String, NextDayEstimate> = emptyMap()
    private val ids = setOf("sp500", "ndx", "djdiv")

    @Synchronized
    fun get(ctx: Context, indexId: String): NextDayEstimate? {
        val now = System.currentTimeMillis()
        if (now - lastFetch < 30_000L) return cache[indexId]?.takeIf { it.validUntil * 1000 > now }
        val prefs = ctx.getSharedPreferences("validated_probability", Context.MODE_PRIVATE)
        val fresh = runCatching { fetch() }.getOrNull()
        val parsed = fresh?.let { parse(it, now, false) }.orEmpty()
        if (parsed.isNotEmpty()) prefs.edit().putString("payload", fresh).apply()
        val saved = prefs.getString("payload", null)?.let { parse(it, now, true) }.orEmpty()
        cache = saved + parsed
        lastFetch = now
        return cache[indexId]
    }

    private fun fetch(): String {
        val base = BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/')
        val c = URL("$base/next-day-probabilities").openConnection() as HttpURLConnection
        c.connectTimeout = 6000
        c.readTimeout = 20000
        c.setRequestProperty("Accept", "application/json")
        return try {
            check(c.responseCode in 200..299)
            c.inputStream.bufferedReader().use { it.readText() }
        } finally { c.disconnect() }
    }

    private fun parse(raw: String, now: Long, saved: Boolean): Map<String, NextDayEstimate> = runCatching {
        val root = JSONObject(raw)
        val items = root.optJSONObject("items") ?: JSONObject()
        buildMap {
            ids.forEach { id ->
                val o = items.optJSONObject(id) ?: return@forEach
                if (o.has("error") || o.optString("model_version") != VALIDATED_MODEL) return@forEach
                val p = o.optDouble("probability", Double.NaN)
                val base = o.optDouble("base_rate", Double.NaN)
                val expires = o.optLong("valid_until", 0)
                if (!p.isFinite() || p !in 0.0..100.0 || !base.isFinite() || base !in 0.0..100.0 || expires * 1000 <= now) return@forEach
                val count = o.optInt("validation_count", 0)
                val brier = o.optDouble("backtest_brier", Double.NaN)
                val baseline = o.optDouble("baseline_brier", Double.NaN)
                val skill = o.optDouble("backtest_skill", Double.NaN)
                if (count < 252 || !brier.isFinite() || !baseline.isFinite() || !skill.isFinite()) return@forEach
                val calibration = o.optJSONObject("calibration") ?: JSONObject()
                put(id, NextDayEstimate(
                    p, base, o.optString("as_of"), o.optString("target_date"), expires,
                    count, brier, baseline, skill, o.optString("evidence", "예측 우위 미확인"),
                    o.optString("validation_choice") == "base",
                    calibration.optInt("low"), calibration.optInt("high"), calibration.optInt("count"),
                    calibration.numberOrNull("observed_rise_rate"),
                    calibration.numberOrNull("range_low"), calibration.numberOrNull("range_high"),
                    o.optInt("prospective_count"), o.optString("audit_start"), o.optString("audit_end"),
                    parseOneMonth(o.optJSONObject("one_month")),
                    saved || o.optBoolean("cached")
                ))
            }
        }
    }.getOrDefault(emptyMap())

    private fun parseOneMonth(o: JSONObject?): OneMonthEstimate? {
        if (o == null || o.has("error")) return null
        val up = o.optDouble("up_10_probability", Double.NaN)
        val down = o.optDouble("down_10_probability", Double.NaN)
        val baseUp = o.optDouble("baseline_up_10_probability", Double.NaN)
        val baseDown = o.optDouble("baseline_down_10_probability", Double.NaN)
        val horizon = o.optInt("horizon_sessions", 0)
        val threshold = o.optInt("threshold_percent", 0)
        val basis = o.optString("price_basis")
        val sample = o.optInt("sample_size", 0)
        val baselineSample = o.optInt("baseline_sample_size", 0)
        val vol = o.optDouble("annualized_volatility", Double.NaN)
        if (horizon != 21 || threshold != 10 || basis !in setOf("daily_high_low", "daily_close")) return null
        if (!up.isFinite() || !down.isFinite() || up !in 0.0..100.0 || down !in 0.0..100.0) return null
        if (!baseUp.isFinite() || !baseDown.isFinite() || baselineSample < 252 || sample <= 0 || !vol.isFinite()) return null
        val features = o.optJSONObject("features")?.let { f ->
            MonthFeatures(
                f.optDouble("return_5d", 0.0), f.optDouble("return_21d", 0.0),
                f.optDouble("return_63d", 0.0), f.optDouble("drawdown_252d", 0.0),
                f.optDouble("ma50_gap", 0.0), f.optDouble("ma200_gap", 0.0)
            )
        }
        val top3 = buildList {
            val arr = o.optJSONArray("terminal_return_top3") ?: return@buildList
            for (i in 0 until minOf(3, arr.length())) {
                val item = arr.optJSONObject(i) ?: continue
                val label = item.optString("label").trim()
                val probability = item.optDouble("probability", Double.NaN)
                if (label.isNotBlank() && probability.isFinite() && probability in 0.0..100.0) {
                    add(TerminalReturnRank(label, probability))
                }
            }
        }
        val modeLabel = o.optString("terminal_return_mode_label").takeIf { it.isNotBlank() }
        val modeProbability = o.numberOrNull("terminal_return_mode_probability")?.takeIf { it in 0.0..100.0 }
        return OneMonthEstimate(
            up, down, horizon, sample, baselineSample, baseUp, baseDown,
            o.optString("trend_regime"), o.optString("volatility_regime"), vol,
            o.optString("as_of"), o.optString("method"), basis,
            o.optString("selection_up", "baseline"), o.optString("selection_down", "baseline"),
            parseMonthValidation(o.optJSONObject("validation_up")),
            parseMonthValidation(o.optJSONObject("validation_down")),
            o.optDouble("effective_sample_up", 0.0), o.optDouble("effective_sample_down", 0.0),
            features,
            top3,
            modeLabel,
            modeProbability,
            o.optString("terminal_return_selection").takeIf { it == "analog" || it == "baseline" },
            parseMonthValidation(o.optJSONObject("terminal_return_validation")),
            o.optDouble("terminal_return_effective_sample", 0.0),
            o.optInt("terminal_return_bin_width_percent", 0)
        )
    }

    private fun parseMonthValidation(o: JSONObject?): MonthValidation? {
        if (o == null) return null
        val model = o.optDouble("model_brier", Double.NaN)
        val baseline = o.optDouble("baseline_brier", Double.NaN)
        val skill = o.optDouble("skill", Double.NaN)
        val count = o.optInt("count", 0)
        if (count <= 0 || !model.isFinite() || !baseline.isFinite() || !skill.isFinite()) return null
        return MonthValidation(count, model, baseline, skill)
    }

    private fun JSONObject.numberOrNull(key: String): Double? = optDouble(key, Double.NaN).takeIf { it.isFinite() }
}

@Composable
fun NextDayProbabilitySection(indexId: String, refreshKey: String = "") {
    if (indexId !in setOf("sp500", "ndx", "djdiv")) return
    val ctx = LocalContext.current.applicationContext
    var estimate by remember(indexId) { mutableStateOf<NextDayEstimate?>(null) }
    var checked by remember(indexId) { mutableStateOf(false) }
    var details by remember(indexId) { mutableStateOf(false) }
    LaunchedEffect(indexId, refreshKey) {
        while (true) {
            estimate = withContext(Dispatchers.IO) { NextDayProbabilityRepository.get(ctx, indexId) }
            checked = true
            delay(60_000L)
        }
    }
    Spacer(Modifier.height(10.dp))
    Card(
        Modifier.fillMaxWidth(),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(Modifier.padding(12.dp)) {
            val e = estimate
            if (e == null) {
                Text("확률 분석", fontWeight = FontWeight.Bold)
                Text(if (checked) "검증된 최신 값을 확인하지 못했습니다. 잠시 후 새로고침해 주세요." else "최신 종가와 검증 결과 확인 중…",
                    style = MaterialTheme.typography.bodySmall)
                return@Column
            }

            Text("다음 거래일 종가 상승 추정  ${pct(e.probability)}",
                style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            Text("${e.asOf} 종가 기준 → ${e.targetDate} 종가 · 배당 미포함", style = MaterialTheme.typography.bodySmall)
            Text(if (e.useBase) "기본 상승률 사용 · 조건별 예측 근거 부족" else "조건별 추정 사용 · ${e.evidence}",
                style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(top = 4.dp))
            if (e.cached) Text("저장된 검증값 · 서버 연결 재확인 중", style = MaterialTheme.typography.labelSmall)

            e.oneMonth?.let { m ->
                HorizontalDivider(Modifier.padding(vertical = 9.dp))
                Text("향후 1개월(21거래일) ±10% 도달 확률", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Text("+10% 이상 상승 도달  ${pct1(m.up10Probability)}", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Text("-10% 이상 하락 도달  ${pct1(m.down10Probability)}", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)

                if (m.terminalReturnTop3.isNotEmpty()) {
                    Spacer(Modifier.height(8.dp))
                    Text("1개월 뒤 가장 가능성 높은 종가 수익률 구간", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                    m.terminalReturnTop3.take(3).forEachIndexed { index, rank ->
                        Text(
                            "${index + 1}위  ${rank.label}  ·  확률 ${pct1(rank.probability)}",
                            style = if (index == 0) MaterialTheme.typography.titleMedium else MaterialTheme.typography.bodyLarge,
                            fontWeight = if (index == 0) FontWeight.Bold else FontWeight.SemiBold
                        )
                    }
                    val widthText = if (m.terminalReturnBinWidthPercent > 0) "${m.terminalReturnBinWidthPercent}%p 구간" else "수익률 구간"
                    Text("21거래일 뒤 종가 기준 · $widthText 확률 순위", style = MaterialTheme.typography.bodySmall)
                }

                val basis = if (m.priceBasis == "daily_high_low") "장중 고가·저가 터치 기준" else "종가 터치 기준(장중 데이터 임시 미사용)"
                Text("${m.asOf} 종가 기준 · $basis", style = MaterialTheme.typography.bodySmall)
                Text("현재와 유사한 과거 장세 + 장기 기본확률을 결합 · 유효표본 상승 ${oneDecimal(m.effectiveSampleUp)} / 하락 ${oneDecimal(m.effectiveSampleDown)}",
                    style = MaterialTheme.typography.bodySmall)
            }

            TextButton(onClick = { details = !details }, contentPadding = PaddingValues(0.dp)) {
                Text(if (details) "검증 근거 접기 ▲" else "검증 근거 보기 ▼")
            }
            if (details) {
                Text("[다음 거래일] ${e.auditStart}–${e.auditEnd} · 일별 순차 검증 ${e.validationCount}회", style = MaterialTheme.typography.bodySmall)
                Text("Brier ${decimal(e.brier)} / 기본값 ${decimal(e.baselineBrier)} · 개선 ${String.format(Locale.US, "%+.2f%%", e.skill)}",
                    style = MaterialTheme.typography.bodySmall)
                if (e.observedLow != null && e.observedHigh != null) {
                    Text("과거 상승비율 95% 참고범위 ${pct(e.observedLow)}–${pct(e.observedHigh)}", style = MaterialTheme.typography.bodySmall)
                }
                Text("실제 사전 예측 누적 검증 ${e.prospectiveCount}회", style = MaterialTheme.typography.bodySmall)

                e.oneMonth?.let { m ->
                    Spacer(Modifier.height(8.dp))
                    Text("[1개월 ±10% 모델]", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.bodyMedium)
                    val trend = if (m.trendRegime == "up") "21일 상승추세" else "21일 하락추세"
                    val vol = if (m.volatilityRegime == "high") "고변동" else "저변동"
                    Text("현재 국면: $trend · $vol · 연환산 변동성 ${pct1(m.annualizedVolatility)}", style = MaterialTheme.typography.bodySmall)
                    m.features?.let { f ->
                        Text("수익률: 5일 ${signedPct1(f.r5)} · 21일 ${signedPct1(f.r21)} · 63일 ${signedPct1(f.r63)}", style = MaterialTheme.typography.bodySmall)
                        Text("1년 고점 대비 ${signedPct1(f.drawdown252)} · 50일선 ${signedPct1(f.ma50Gap)} · 200일선 ${signedPct1(f.ma200Gap)}", style = MaterialTheme.typography.bodySmall)
                    }
                    Text("장기 기본빈도: +10% ${pct1(m.baselineUp10Probability)} / -10% ${pct1(m.baselineDown10Probability)} · 완료표본 ${m.baselineSampleSize}회",
                        style = MaterialTheme.typography.bodySmall)
                    monthValidationLine("+10%", m.selectionUp, m.validationUp)
                    monthValidationLine("-10%", m.selectionDown, m.validationDown)
                    if (m.terminalReturnTop3.isNotEmpty()) {
                        Spacer(Modifier.height(6.dp))
                        Text("[1개월 종가 수익률 분포]", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.bodyMedium)
                        m.terminalReturnTop3.take(3).forEachIndexed { index, rank ->
                            Text("${index + 1}위 ${rank.label} · ${pct1(rank.probability)}", style = MaterialTheme.typography.bodySmall)
                        }
                        Text("분포 유효표본 ${oneDecimal(m.terminalReturnEffectiveSample)}", style = MaterialTheme.typography.bodySmall)
                        monthValidationLine("종가분포", m.terminalReturnSelection ?: "baseline", m.terminalReturnValidation)
                    }
                    Text("검증에서 유사장세 모델이 기본확률보다 낫지 않으면 해당 방향·분포는 자동으로 장기 기본확률을 사용합니다.",
                        style = MaterialTheme.typography.labelSmall)
                }
            }
            Text("과거 통계에 따른 추정이며 향후 상승·하락이나 수익을 보장하지 않습니다.", style = MaterialTheme.typography.labelSmall, modifier = Modifier.padding(top = 4.dp))
        }
    }
}

@Composable
private fun monthValidationLine(label: String, selection: String, v: MonthValidation?) {
    if (v == null) {
        Text("$label 검증: 계산 중", style = MaterialTheme.typography.bodySmall)
        return
    }
    val chosen = if (selection == "analog") "유사장세 모델 채택" else "장기 기본확률 채택"
    Text("$label: $chosen · 후반부 ${v.count}회 검증 · Brier ${decimal(v.modelBrier)} / 기본 ${decimal(v.baselineBrier)} · 개선 ${String.format(Locale.US, "%+.1f%%", v.skill)}",
        style = MaterialTheme.typography.bodySmall)
}

private fun pct(value: Double): String = String.format(Locale.US, "%.0f%%", value)
private fun pct1(value: Double): String = String.format(Locale.US, "%.1f%%", value)
private fun signedPct1(value: Double): String = String.format(Locale.US, "%+.1f%%", value)
private fun oneDecimal(value: Double): String = String.format(Locale.US, "%.1f", value)
private fun decimal(value: Double): String = String.format(Locale.US, "%.4f", value)
