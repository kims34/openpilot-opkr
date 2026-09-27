package com.indexalert.app

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
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
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.Locale

private const val FIRST_HOUR_MODEL = "4.0-first-hour"

data class FirstHourEstimate(
    val available: Boolean,
    val status: String,
    val probability: Double?,
    val previousProbability: Double?,
    val adjustmentPp: Double?,
    val firstHourReturnPercent: Double?,
    val fromPreviousClosePercent: Double?,
    val targetDate: String?,
    val modelVersion: String,
    val trainingCount: Int,
    val prospectiveCount: Int,
    val prospectiveBrier: Double?,
    val prospectivePreviousBrier: Double?
)

object FirstHourProbabilityRepository {
    private var lastFetch = 0L
    private var cache: Map<String, FirstHourEstimate> = emptyMap()
    private val ids = setOf("sp500", "ndx", "djdiv")

    @Synchronized
    fun get(indexId: String): FirstHourEstimate? {
        if (indexId !in ids) return null
        val now = System.currentTimeMillis()
        if (now - lastFetch < 20_000L && cache.isNotEmpty()) return cache[indexId]
        val fresh = runCatching { fetchAll() }.getOrNull()
        if (fresh != null) {
            cache = fresh
            lastFetch = now
        }
        return cache[indexId]
    }

    private fun fetchAll(): Map<String, FirstHourEstimate> {
        val base = BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/')
        val c = URL("$base/next-day-probabilities").openConnection() as HttpURLConnection
        c.connectTimeout = 6000
        c.readTimeout = 30000
        c.setRequestProperty("Accept", "application/json")
        return try {
            check(c.responseCode in 200..299)
            val root = JSONObject(c.inputStream.bufferedReader().use { it.readText() })
            val items = root.optJSONObject("items") ?: JSONObject()
            buildMap {
                ids.forEach { id ->
                    val value = items.optJSONObject(id)?.optJSONObject("first_hour") ?: return@forEach
                    val model = value.optString("model_version")
                    if (model != FIRST_HOUR_MODEL) return@forEach
                    val available = value.optBoolean("available", false)
                    val probability = value.numberOrNull("probability")?.takeIf { it in 0.0..100.0 }
                    put(
                        id,
                        FirstHourEstimate(
                            available = available && probability != null,
                            status = value.optString("status", if (available) "첫 1시간 계산 완료" else "첫 1시간 마감 대기"),
                            probability = probability,
                            previousProbability = value.numberOrNull("previous_probability")?.takeIf { it in 0.0..100.0 },
                            adjustmentPp = value.numberOrNull("adjustment_pp"),
                            firstHourReturnPercent = value.numberOrNull("first_hour_return_percent"),
                            fromPreviousClosePercent = value.numberOrNull("from_previous_close_percent"),
                            targetDate = value.optString("target_date").takeIf { it.isNotBlank() },
                            modelVersion = model,
                            trainingCount = value.optInt("training_count", 0),
                            prospectiveCount = value.optInt("prospective_count", 0),
                            prospectiveBrier = value.numberOrNull("prospective_brier"),
                            prospectivePreviousBrier = value.numberOrNull("prospective_previous_brier")
                        )
                    )
                }
            }
        } finally {
            c.disconnect()
        }
    }

    private fun JSONObject.numberOrNull(key: String): Double? =
        optDouble(key, Double.NaN).takeIf { it.isFinite() }
}

@Composable
fun FirstHourProbabilitySection(indexId: String, refreshKey: String = "") {
    if (indexId !in setOf("sp500", "ndx", "djdiv")) return
    var estimate by remember(indexId) { mutableStateOf<FirstHourEstimate?>(null) }
    var checked by remember(indexId) { mutableStateOf(false) }
    var details by remember(indexId) { mutableStateOf(false) }

    LaunchedEffect(indexId, refreshKey) {
        while (true) {
            estimate = withContext(Dispatchers.IO) { FirstHourProbabilityRepository.get(indexId) }
            checked = true
            delay(60_000L)
        }
    }

    Spacer(Modifier.height(8.dp))
    Card(
        Modifier.fillMaxWidth(),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
    ) {
        Column(Modifier.padding(12.dp)) {
            val e = estimate
            Text("첫 1시간 반영 종가 상승확률", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleSmall)
            if (e == null) {
                Text(
                    if (checked) "첫 1시간 확률 상태를 확인하지 못했습니다." else "미국장 상태 확인 중…",
                    style = MaterialTheme.typography.bodySmall
                )
                return@Column
            }

            if (!e.available || e.probability == null) {
                Text(e.status, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.SemiBold)
                Text("첫 정규장 1시간이 완전히 끝난 뒤, 통상 10:35 ET부터 계산합니다.", style = MaterialTheme.typography.bodySmall)
                return@Column
            }

            Text(
                "오늘 종가 > 전일 종가  ${String.format(Locale.US, "%.1f%%", e.probability)}",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            if (e.previousProbability != null && e.adjustmentPp != null) {
                Text(
                    "개장후 ${String.format(Locale.US, "%.1f%%", e.previousProbability)} → 첫 1시간 ${String.format(Locale.US, "%.1f%%", e.probability)} " +
                        "(${String.format(Locale.US, "%+.1f%%p", e.adjustmentPp)})",
                    style = MaterialTheme.typography.bodySmall
                )
            }
            e.firstHourReturnPercent?.let {
                Text("첫 1시간 수익률 ${String.format(Locale.US, "%+.2f%%", it)}", style = MaterialTheme.typography.bodySmall)
            }
            e.fromPreviousClosePercent?.let {
                Text("전일 종가 대비 첫 1시간 종가 ${String.format(Locale.US, "%+.2f%%", it)}", style = MaterialTheme.typography.bodySmall)
            }
            Text("첫 1시간 완성봉 · SPY/QQQ 동조 · VIX · 거래량 반영 · ${e.targetDate ?: "오늘"} 종가 기준", style = MaterialTheme.typography.bodySmall)

            TextButton(onClick = { details = !details }, contentPadding = PaddingValues(0.dp)) {
                Text(if (details) "첫 1시간 모델 정보 접기 ▲" else "첫 1시간 모델 정보 보기 ▼")
            }
            if (details) {
                Text("모델 ${e.modelVersion} · 학습표본 ${e.trainingCount}회", style = MaterialTheme.typography.bodySmall)
                Text("최종 126거래일 홀드아웃 · 21일×6블록 · 이동블록 부트스트랩 검증 통과", style = MaterialTheme.typography.bodySmall)
                if (e.prospectiveCount > 0 && e.prospectiveBrier != null && e.prospectivePreviousBrier != null) {
                    val gain = e.prospectivePreviousBrier - e.prospectiveBrier
                    Text(
                        "실전 누적 ${e.prospectiveCount}회 · Brier ${String.format(Locale.US, "%.4f", e.prospectiveBrier)} " +
                            "/ 기존 ${String.format(Locale.US, "%.4f", e.prospectivePreviousBrier)} · 개선 ${String.format(Locale.US, "%+.4f", gain)}",
                        style = MaterialTheme.typography.bodySmall
                    )
                } else {
                    Text("실전 성과는 적용 이후 매 거래일 종료 후 별도로 누적 검증합니다.", style = MaterialTheme.typography.bodySmall)
                }
                Text("확률은 통계적 추정치이며 투자수익을 보장하지 않습니다.", style = MaterialTheme.typography.labelSmall)
            }
        }
    }
}
