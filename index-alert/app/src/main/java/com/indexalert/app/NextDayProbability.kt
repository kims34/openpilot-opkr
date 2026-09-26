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

private const val VALIDATED_MODEL = "3.1-causal-adaptive-close"

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
        if (parsed.isNotEmpty()) {
            // Save only a response from the supported, audited model.
            prefs.edit().putString("payload", fresh).apply()
        }
        val saved = prefs.getString("payload", null)?.let { parse(it, now, true) }.orEmpty()
        cache = saved + parsed
        lastFetch = now
        return cache[indexId]
    }

    private fun fetch(): String {
        val base = BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/')
        val c = URL("$base/next-day-probabilities").openConnection() as HttpURLConnection
        c.connectTimeout = 6000
        c.readTimeout = 12000
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
                    saved || o.optBoolean("cached")
                ))
            }
        }
    }.getOrDefault(emptyMap())

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
                Text("다음 거래일 상승 확률", fontWeight = FontWeight.Bold)
                Text(if (checked) "검증된 최신 값을 확인하지 못했습니다. 잠시 후 새로고침해 주세요." else "최신 종가와 검증 결과 확인 중…",
                    style = MaterialTheme.typography.bodySmall)
            } else {
                Text("다음 거래일 종가 상승 추정  ${pct(e.probability)}",
                    style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Text("${e.asOf} 종가 기준 → ${e.targetDate} 종가 · 배당 미포함",
                    style = MaterialTheme.typography.bodySmall)
                Text(if (e.useBase) "기본 상승률 사용 · 조건별 예측 근거 부족" else "조건별 추정 사용 · ${e.evidence}",
                    style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.SemiBold,
                    modifier = Modifier.padding(top = 4.dp))
                if (e.cached) Text("저장된 검증값 · 서버 연결 재확인 중", style = MaterialTheme.typography.labelSmall)
                if (e.calibrationCount >= 100 && e.observedRise != null) {
                    Text("과거 ${e.calibrationLow}–${e.calibrationHigh}% 예측 ${e.calibrationCount}회 중 실제 ${pct(e.observedRise)} 상승",
                        style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(top = 4.dp))
                } else {
                    Text("이 확률 구간의 과거 검증 표본이 부족합니다.", style = MaterialTheme.typography.bodySmall)
                }
                TextButton(onClick = { details = !details }, contentPadding = PaddingValues(0.dp)) {
                    Text(if (details) "검증 근거 접기 ▲" else "검증 근거 보기 ▼")
                }
                if (details) {
                    Text("${e.auditStart}–${e.auditEnd} · 일별 순차 검증 ${e.validationCount}회", style = MaterialTheme.typography.bodySmall)
                    Text("확률 오차(Brier, 낮을수록 좋음) ${decimal(e.brier)} / 기본값 ${decimal(e.baselineBrier)}",
                        style = MaterialTheme.typography.bodySmall)
                    Text("기본값 대비 과거 오차 개선 ${String.format(Locale.US, "%+.2f%%", e.skill)} · ${e.evidence}",
                        style = MaterialTheme.typography.bodySmall)
                    if (e.observedLow != null && e.observedHigh != null) {
                        Text("과거 상승비율의 95% 참고범위 ${pct(e.observedLow)}–${pct(e.observedHigh)}. 내일 확률의 신뢰구간이 아닙니다.",
                            style = MaterialTheme.typography.bodySmall)
                    }
                    Text("실제 사전 예측 누적 검증 ${e.prospectiveCount}회 · 새 모델부터 별도 기록",
                        style = MaterialTheme.typography.bodySmall)
                }
                Text("과거 통계에 따른 추정이며 다음 거래일의 상승이나 수익을 보장하지 않습니다.",
                    style = MaterialTheme.typography.labelSmall, modifier = Modifier.padding(top = 4.dp))
            }
        }
    }
}

private fun pct(value: Double): String = String.format(Locale.US, "%.0f%%", value)
private fun decimal(value: Double): String = String.format(Locale.US, "%.4f", value)
