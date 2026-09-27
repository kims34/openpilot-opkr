package com.indexalert.app

import android.content.Context
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

private const val AFTER_OPEN_MODEL = "3.9-open-nowcast"

data class AfterOpenEstimate(
    val available: Boolean,
    val status: String,
    val probability: Double?,
    val preopenProbability: Double?,
    val adjustmentPp: Double?,
    val openingGapPercent: Double?,
    val targetDate: String?,
    val modelVersion: String,
    val trainingCount: Int,
    val prospectiveCount: Int,
    val prospectiveBrier: Double?,
    val prospectivePreopenBrier: Double?
)

object AfterOpenProbabilityRepository {
    private var lastFetch = 0L
    private var cache: Map<String, AfterOpenEstimate> = emptyMap()
    private val ids = setOf("sp500", "ndx", "djdiv")

    @Synchronized
    fun get(indexId: String): AfterOpenEstimate? {
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

    private fun fetchAll(): Map<String, AfterOpenEstimate> {
        val base = BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/')
        val c = URL("$base/next-day-probabilities").openConnection() as HttpURLConnection
        c.connectTimeout = 6000
        c.readTimeout = 25000
        c.setRequestProperty("Accept", "application/json")
        return try {
            check(c.responseCode in 200..299)
            val root = JSONObject(c.inputStream.bufferedReader().use { it.readText() })
            val items = root.optJSONObject("items") ?: JSONObject()
            buildMap {
                ids.forEach { id ->
                    val a = items.optJSONObject(id)?.optJSONObject("after_open") ?: return@forEach
                    val model = a.optString("model_version")
                    if (model != AFTER_OPEN_MODEL) return@forEach
                    val available = a.optBoolean("available", false)
                    val p = a.numberOrNull("probability")?.takeIf { it in 0.0..100.0 }
                    val pre = a.numberOrNull("preopen_probability")?.takeIf { it in 0.0..100.0 }
                    put(
                        id,
                        AfterOpenEstimate(
                            available = available && p != null,
                            status = a.optString("status", if (available) "개장후 계산 완료" else "개장 후 5분부터 제공"),
                            probability = p,
                            preopenProbability = pre,
                            adjustmentPp = a.numberOrNull("adjustment_pp"),
                            openingGapPercent = a.numberOrNull("opening_gap_percent"),
                            targetDate = a.optString("target_date").takeIf { it.isNotBlank() },
                            modelVersion = model,
                            trainingCount = a.optInt("training_count", 0),
                            prospectiveCount = a.optInt("prospective_count", 0),
                            prospectiveBrier = a.numberOrNull("prospective_brier"),
                            prospectivePreopenBrier = a.numberOrNull("prospective_preopen_brier")
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
fun AfterOpenProbabilitySection(indexId: String, refreshKey: String = "") {
    if (indexId !in setOf("sp500", "ndx", "djdiv")) return
    var estimate by remember(indexId) { mutableStateOf<AfterOpenEstimate?>(null) }
    var checked by remember(indexId) { mutableStateOf(false) }
    var details by remember(indexId) { mutableStateOf(false) }

    LaunchedEffect(indexId, refreshKey) {
        while (true) {
            estimate = withContext(Dispatchers.IO) { AfterOpenProbabilityRepository.get(indexId) }
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
            Text("오늘 마감 상승확률", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleSmall)
            if (e == null) {
                Text(
                    if (checked) "장중 확률 상태를 확인하지 못했습니다." else "미국장 상태 확인 중…",
                    style = MaterialTheme.typography.bodySmall
                )
                return@Column
            }

            if (!e.available || e.probability == null) {
                Text(e.status, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.SemiBold)
                Text("미국 정규장 개장 5분 후에만 계산합니다.", style = MaterialTheme.typography.bodySmall)
                return@Column
            }

            Text(
                "오늘 종가 > 전일 종가  ${String.format(Locale.US, "%.1f%%", e.probability)}",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            if (e.preopenProbability != null && e.adjustmentPp != null) {
                Text(
                    "개장 전 ${String.format(Locale.US, "%.1f%%", e.preopenProbability)} → 개장후 ${String.format(Locale.US, "%.1f%%", e.probability)} " +
                        "(${String.format(Locale.US, "%+.1f%%p", e.adjustmentPp)})",
                    style = MaterialTheme.typography.bodySmall
                )
            }
            e.openingGapPercent?.let {
                Text("시가 갭 ${String.format(Locale.US, "%+.2f%%", it)} 반영", style = MaterialTheme.typography.bodySmall)
            }
            Text("개장 5분 이후 시가정보 반영 · ${e.targetDate ?: "오늘"} 정규장 종가 기준", style = MaterialTheme.typography.bodySmall)

            TextButton(onClick = { details = !details }, contentPadding = PaddingValues(0.dp)) {
                Text(if (details) "장중 모델 정보 접기 ▲" else "장중 모델 정보 보기 ▼")
            }
            if (details) {
                Text("모델 ${e.modelVersion} · 학습표본 ${e.trainingCount}회", style = MaterialTheme.typography.bodySmall)
                if (e.prospectiveCount > 0 && e.prospectiveBrier != null && e.prospectivePreopenBrier != null) {
                    val gain = e.prospectivePreopenBrier - e.prospectiveBrier
                    Text(
                        "실전 누적 ${e.prospectiveCount}회 · Brier ${String.format(Locale.US, "%.4f", e.prospectiveBrier)} " +
                            "/ 개장전 ${String.format(Locale.US, "%.4f", e.prospectivePreopenBrier)} · 개선 ${String.format(Locale.US, "%+.4f", gain)}",
                        style = MaterialTheme.typography.bodySmall
                    )
                } else {
                    Text("실전 성과는 매 거래일 종료 후 누적 검증합니다.", style = MaterialTheme.typography.bodySmall)
                }
                Text("확률은 통계적 추정치이며 투자수익을 보장하지 않습니다.", style = MaterialTheme.typography.labelSmall)
            }
        }
    }
}
