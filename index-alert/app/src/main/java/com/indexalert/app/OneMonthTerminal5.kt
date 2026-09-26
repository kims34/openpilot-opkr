package com.indexalert.app

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

private data class Terminal5Estimate(
    val up: Double,
    val down: Double,
    val asOf: String,
    val selectionUp: String,
    val selectionDown: String,
    val effectiveSampleUp: Double,
    val effectiveSampleDown: Double,
    val skillUp: Double?,
    val skillDown: Double?
)

private object Terminal5Repository {
    private var fetchedAt = 0L
    private var cache: Map<String, Terminal5Estimate> = emptyMap()

    @Synchronized
    fun get(indexId: String): Terminal5Estimate? {
        val now = System.currentTimeMillis()
        if (now - fetchedAt < 30_000L && cache.isNotEmpty()) return cache[indexId]
        val base = BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/')
        val c = URL("$base/next-day-probabilities").openConnection() as HttpURLConnection
        c.connectTimeout = 6000
        c.readTimeout = 25000
        c.setRequestProperty("Accept", "application/json")
        try {
            if (c.responseCode !in 200..299) return cache[indexId]
            val root = JSONObject(c.inputStream.bufferedReader().use { it.readText() })
            val items = root.optJSONObject("items") ?: return cache[indexId]
            val parsed = mutableMapOf<String, Terminal5Estimate>()
            listOf("sp500", "ndx", "djdiv").forEach { id ->
                val one = items.optJSONObject(id)?.optJSONObject("one_month") ?: return@forEach
                val horizon = one.optInt("terminal_5_horizon_sessions", 0)
                val threshold = one.optInt("terminal_5_threshold_percent", 0)
                val up = one.optDouble("terminal_up_5_probability", Double.NaN)
                val down = one.optDouble("terminal_down_5_probability", Double.NaN)
                if (horizon != 21 || threshold != 5 || !up.isFinite() || !down.isFinite()) return@forEach
                if (up !in 0.0..100.0 || down !in 0.0..100.0) return@forEach
                val upValidation = one.optJSONObject("terminal_5_validation_up")
                val downValidation = one.optJSONObject("terminal_5_validation_down")
                parsed[id] = Terminal5Estimate(
                    up = up,
                    down = down,
                    asOf = one.optString("terminal_5_as_of", items.optJSONObject(id)?.optString("as_of", "") ?: ""),
                    selectionUp = one.optString("terminal_5_selection_up", "baseline"),
                    selectionDown = one.optString("terminal_5_selection_down", "baseline"),
                    effectiveSampleUp = one.optDouble("terminal_5_effective_sample_up", 0.0),
                    effectiveSampleDown = one.optDouble("terminal_5_effective_sample_down", 0.0),
                    skillUp = upValidation?.optDouble("skill", Double.NaN)?.takeIf { it.isFinite() },
                    skillDown = downValidation?.optDouble("skill", Double.NaN)?.takeIf { it.isFinite() }
                )
            }
            if (parsed.isNotEmpty()) {
                cache = parsed
                fetchedAt = now
            }
            return cache[indexId]
        } finally {
            c.disconnect()
        }
    }
}

@Composable
fun OneMonthTerminal5Section(indexId: String, refreshKey: String = "") {
    if (indexId !in setOf("sp500", "ndx", "djdiv")) return
    val ctx = LocalContext.current.applicationContext
    var estimate by remember(indexId) { mutableStateOf<Terminal5Estimate?>(null) }
    var checked by remember(indexId) { mutableStateOf(false) }

    LaunchedEffect(indexId, refreshKey) {
        while (true) {
            estimate = withContext(Dispatchers.IO) { Terminal5Repository.get(indexId) }
            checked = true
            delay(60_000L)
        }
    }

    Spacer(Modifier.height(8.dp))
    Card(
        modifier = Modifier.fillMaxWidth(),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(Modifier.padding(12.dp)) {
            Text("1개월 뒤 종가 기준 ±5% 확률", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleSmall)
            val e = estimate
            if (e == null) {
                Text(if (checked) "검증된 확률 계산 중" else "과거 유사 장세 분석 중…", style = MaterialTheme.typography.bodySmall)
                return@Column
            }
            Text("+5% 이상 상승  ${String.format(Locale.US, "%.1f%%", e.up)}", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
            Text("-5% 이하 하락  ${String.format(Locale.US, "%.1f%%", e.down)}", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
            Text("${e.asOf} 종가 기준 → 21거래일 뒤 종가 · 장중 터치 확률과 별도", style = MaterialTheme.typography.bodySmall)
            val upMethod = if (e.selectionUp == "analog") "유사장세" else "장기 기본확률"
            val downMethod = if (e.selectionDown == "analog") "유사장세" else "장기 기본확률"
            Text("상승 $upMethod · 하락 $downMethod · 유효표본 ${oneDecimalT5(e.effectiveSampleUp)} / ${oneDecimalT5(e.effectiveSampleDown)}", style = MaterialTheme.typography.bodySmall)
            if (e.skillUp != null || e.skillDown != null) {
                val upSkill = e.skillUp?.let { String.format(Locale.US, "%+.1f%%", it) } ?: "-"
                val downSkill = e.skillDown?.let { String.format(Locale.US, "%+.1f%%", it) } ?: "-"
                Text("후반부 검증 개선도: 상승 $upSkill · 하락 $downSkill", style = MaterialTheme.typography.labelSmall)
            }
            Text("과거 통계 기반 추정치이며 미래 수익률을 보장하지 않습니다.", style = MaterialTheme.typography.labelSmall)
        }
    }
}

private fun oneDecimalT5(v: Double): String = String.format(Locale.US, "%.1f", v)
