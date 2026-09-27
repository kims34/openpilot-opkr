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
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.Locale

private const val EXTENDED_MODEL = "4.1-extended-session"
private val EXTENDED_IDS = setOf("sp500", "ndx", "djdiv", "kospi100")

data class ExtendedSessionEstimate(
    val available: Boolean,
    val status: String,
    val probability: Double?,
    val baselineProbability: Double?,
    val adjustmentPp: Double?,
    val extendedMovePercent: Double?,
    val estimatedOpenPrice: Double?,
    val source: String?,
    val session: String?,
    val estimated: Boolean,
    val actualExtendedTrade: Boolean,
    val targetDate: String?,
    val modelVersion: String,
    val kospiBaseProbability: Double?,
    val kospiBaseModel: String?
)

object ExtendedSessionProbabilityRepository {
    private var lastFetch = 0L
    private var cache: Map<String, ExtendedSessionEstimate> = emptyMap()

    @Synchronized
    fun get(indexId: String): ExtendedSessionEstimate? {
        if (indexId !in EXTENDED_IDS) return null
        val now = System.currentTimeMillis()
        if (now - lastFetch < 20_000L && cache.isNotEmpty()) return cache[indexId]
        val fresh = runCatching { fetchAll() }.getOrNull()
        if (fresh != null) {
            cache = fresh
            lastFetch = now
        }
        return cache[indexId]
    }

    private fun fetchAll(): Map<String, ExtendedSessionEstimate> {
        val base = BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/')
        val c = URL("$base/next-day-probabilities").openConnection() as HttpURLConnection
        c.connectTimeout = 7000
        c.readTimeout = 30000
        c.setRequestProperty("Accept", "application/json")
        return try {
            check(c.responseCode in 200..299)
            val root = JSONObject(c.inputStream.bufferedReader().use { it.readText() })
            val items = root.optJSONObject("items") ?: JSONObject()
            buildMap {
                EXTENDED_IDS.forEach { id ->
                    val parent = items.optJSONObject(id) ?: return@forEach
                    val e = parent.optJSONObject("extended_session")
                    val model = e?.optString("model_version").orEmpty()
                    val probability = e?.numberOrNull("probability")?.takeIf { it in 0.0..100.0 }
                    val available = e?.optBoolean("available", false) == true && probability != null && model == EXTENDED_MODEL
                    val parentProbability = parent.numberOrNull("probability")?.takeIf { it in 0.0..100.0 }
                    put(
                        id,
                        ExtendedSessionEstimate(
                            available = available,
                            status = e?.optString("status").takeUnless { it.isNullOrBlank() }
                                ?: "시간외 체결/연동값 대기",
                            probability = probability,
                            baselineProbability = e?.numberOrNull("baseline_probability")?.takeIf { it in 0.0..100.0 },
                            adjustmentPp = e?.numberOrNull("adjustment_pp"),
                            extendedMovePercent = e?.numberOrNull("extended_move_percent"),
                            estimatedOpenPrice = e?.numberOrNull("estimated_open_price"),
                            source = e?.optString("source")?.takeIf { it.isNotBlank() },
                            session = e?.optString("session")?.takeIf { it.isNotBlank() },
                            estimated = e?.optBoolean("estimated", false) == true,
                            actualExtendedTrade = e?.optBoolean("actual_extended_trade", false) == true,
                            targetDate = e?.optString("target_date")?.takeIf { it.isNotBlank() }
                                ?: parent.optString("target_date").takeIf { it.isNotBlank() },
                            modelVersion = model.ifBlank { EXTENDED_MODEL },
                            kospiBaseProbability = if (id == "kospi100") parentProbability else null,
                            kospiBaseModel = if (id == "kospi100") parent.optString("model_version").takeIf { it.isNotBlank() } else null
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
fun ExtendedSessionProbabilitySection(indexId: String, refreshKey: String = "") {
    if (indexId !in EXTENDED_IDS) return
    var estimate by remember(indexId) { mutableStateOf<ExtendedSessionEstimate?>(null) }
    var checked by remember(indexId) { mutableStateOf(false) }

    LaunchedEffect(indexId, refreshKey) {
        while (true) {
            estimate = withContext(Dispatchers.IO) { ExtendedSessionProbabilityRepository.get(indexId) }
            checked = true
            delay(60_000L)
        }
    }

    Spacer(Modifier.height(8.dp))
    Card(
        Modifier.fillMaxWidth(),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(Modifier.padding(12.dp)) {
            val e = estimate
            Text("시간외 반영 확률", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleSmall)

            if (e == null) {
                Text(
                    if (checked) "시간외 시세 상태를 확인하지 못했습니다." else "시간외 시세 확인 중…",
                    style = MaterialTheme.typography.bodySmall
                )
                return@Column
            }

            if (indexId == "kospi100" && e.kospiBaseProbability != null) {
                Text(
                    "다음 거래일 기본 상승확률  ${String.format(Locale.US, "%.1f%%", e.kospiBaseProbability)}",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.SemiBold
                )
            }

            if (!e.available || e.probability == null) {
                Text(e.status, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.SemiBold)
                Text(
                    if (indexId == "kospi100")
                        "코스피 현물지수는 시간외에 직접 거래되지 않아 유효한 연동값이 있을 때만 추정치를 반영합니다."
                    else
                        "ETF 프리·애프터마켓 또는 연동 선물의 최신 유효값이 들어오면 자동 반영합니다.",
                    style = MaterialTheme.typography.bodySmall
                )
                return@Column
            }

            Text(
                "다음 거래일 종가 상승 추정  ${String.format(Locale.US, "%.1f%%", e.probability)}",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            if (e.baselineProbability != null && e.adjustmentPp != null) {
                Text(
                    "기본 ${String.format(Locale.US, "%.1f%%", e.baselineProbability)} → 시간외 ${String.format(Locale.US, "%.1f%%", e.probability)} " +
                        "(${String.format(Locale.US, "%+.1f%%p", e.adjustmentPp)})",
                    style = MaterialTheme.typography.bodySmall
                )
            }
            e.extendedMovePercent?.let {
                Text("시간외 연동 움직임 ${String.format(Locale.US, "%+.2f%%", it)}", style = MaterialTheme.typography.bodySmall)
            }
            e.estimatedOpenPrice?.let {
                val label = if (indexId == "kospi100") "다음 시가 연동 추정값" else "다음 시가 참고값"
                Text("$label ${String.format(Locale.US, "%,.2f", it)}", style = MaterialTheme.typography.bodySmall)
            }
            e.source?.let { Text("기준  $it", style = MaterialTheme.typography.bodySmall) }

            val quality = when {
                e.actualExtendedTrade -> "실제 ETF 시간외 체결가 반영"
                e.estimated -> "연동 추정치 · 실제 현물지수/ETF 체결가와 구분"
                else -> "시간외 시장 연동"
            }
            Text(quality, style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.SemiBold)
            e.targetDate?.let { Text("대상 거래일 $it", style = MaterialTheme.typography.labelSmall) }
        }
    }
}
