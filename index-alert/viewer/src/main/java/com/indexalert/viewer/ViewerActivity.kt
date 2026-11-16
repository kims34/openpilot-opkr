package com.indexalert.viewer

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.*
import org.json.JSONObject
import java.util.Locale

private data class ScreenData(
    val markets: Map<String, JSONObject> = emptyMap(),
    val probabilities: JSONObject? = null,
    val monthly: JSONObject? = null,
    val scores: JSONObject? = null,
    val updated: Boolean = false
)

class ViewerActivity : ComponentActivity() {
    private var screen by mutableStateOf(ScreenData())
    private var refreshing by mutableStateOf(false)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme(colorScheme = lightColorScheme(primary = Color(0xFF244BD0))) {
                ViewerScreen(screen, refreshing) { lifecycleScope.launch { refresh() } }
            }
        }
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                while (isActive) { refresh(); delay(60_000) }
            }
        }
    }

    private suspend fun refresh() {
        if (refreshing) return
        refreshing = true
        try {
            val results = withContext(Dispatchers.IO) {
                coroutineScope {
                    listOf("/status", "/next-day-probabilities", "/one-month-probabilities", "/monthly-prospective-scores")
                        .map { path -> async { runCatching { ViewerTransport.read(path) }.getOrNull() } }
                        .awaitAll()
                }
            }
            val markets = buildMap {
                val rows = results[0]?.optJSONArray("indices")
                if (rows != null) for (i in 0 until rows.length()) {
                    val row = rows.optJSONObject(i) ?: continue
                    put(row.optString("id"), row)
                }
            }
            // No saved forecast fallback. A failed request clears old results.
            screen = ScreenData(markets, results[1], results[2], results[3], true)
        } finally { refreshing = false }
    }
}

private val UpColor = Color(0xFFB92340)
private val DownColor = Color(0xFF2458C6)
private val Muted = Color(0xFF525E73)

@Composable
private fun ViewerScreen(data: ScreenData, refreshing: Boolean, refresh: () -> Unit) {
    var symbol by rememberSaveable { mutableStateOf("SPY") }
    var horizon by rememberSaveable { mutableIntStateOf(21) }
    var showHistory by rememberSaveable { mutableStateOf(false) }
    var showMarkets by rememberSaveable { mutableStateOf(false) }
    val now = System.currentTimeMillis()/1000
    val forecasts = ViewerPolicy.historical(data.scores, now) + ViewerPolicy.annual(data.scores, now) + ViewerPolicy.extended(data.scores, now)
    val selected = forecasts.filter { it.optString("symbol") == symbol && it.optInt("horizon_sessions") == horizon }
    val marketId = mapOf("SPY" to "sp500", "QQQ" to "ndx", "SCHD" to "djdiv")[symbol]
    val market = data.markets[marketId]

    Column(Modifier.fillMaxSize().background(Color(0xFFF3F6FB))
        .windowInsetsPadding(WindowInsets.safeDrawing)
        .verticalScroll(rememberScrollState()).padding(horizontal = 18.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Column(Modifier.weight(1f)) {
                Text("IndexAlert", fontSize = 25.sp, fontWeight = FontWeight.Bold)
                Text("상승·하락 도달확률", color = Muted, fontSize = 15.sp)
            }
            OutlinedButton(onClick = refresh, enabled = !refreshing) { Text(if (refreshing) "갱신 중" else "새로고침") }
        }
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            for (item in listOf("SPY", "QQQ", "SCHD")) {
                FilterChip(selected = symbol == item, onClick = { symbol = item; showHistory = false },
                    label = { Text(item, fontWeight = FontWeight.SemiBold) }, modifier = Modifier.weight(1f))
            }
        }
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            for (days in listOf(21, 63, 252)) {
                FilterChip(selected = horizon == days, onClick = { horizon = days; showHistory = false },
                    label = { Text(when (days) { 21 -> "1개월"; 63 -> "3개월"; else -> "1년" }) },
                    modifier = Modifier.weight(1f))
            }
        }
        Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(18.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White)) {
            Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
                Text("$symbol · ${when (horizon) { 21 -> "1개월"; 63 -> "3개월"; else -> "1년" }}", fontSize = 22.sp, fontWeight = FontWeight.Bold)
                val price = market?.optDouble("last_value", Double.NaN) ?: Double.NaN
                if (price.isFinite() && price > 0) {
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text(String.format(Locale.US, "%,.2f", price), fontSize = 24.sp, fontWeight = FontWeight.SemiBold)
                        val change = market?.optDouble("day_change_percent", Double.NaN) ?: Double.NaN
                        if (market?.optBoolean("basis_verified", false) == true && change.isFinite()) {
                            Text(String.format(Locale.US, "%+.2f%%", change), color = if (change >= 0) UpColor else DownColor)
                        }
                    }
                    Text(market?.optString("source").orEmpty(), color = Muted, style = MaterialTheme.typography.labelSmall)
                }
                val first = selected.firstOrNull()
                if (first != null) {
                    Text("기준 종가: ${first.optString("as_of")}", color = Muted, style = MaterialTheme.typography.bodySmall)
                    Text("목표 기간: 다음 $horizon 거래일 · ${first.optString("target_date")}까지",
                        color = Muted, style = MaterialTheme.typography.bodySmall)
                } else Text(if (data.updated) "최신 유효 확률을 확인하지 못했어요. 새로고침해 주세요." else "과거 데이터 확인 중…",
                    color = Muted, style = MaterialTheme.typography.bodySmall)
                Text("기준 종가에서 목표 가격에 한 번이라도 닿을 확률", fontWeight = FontWeight.Medium,
                    modifier = Modifier.padding(top = 5.dp), style = MaterialTheme.typography.bodyMedium)
            }
        }
        Text("막대 하나의 전체 길이 = 100%", color = Muted, style = MaterialTheme.typography.bodySmall)
        Text("진한 색 = 도달 · 연한 색 = 미도달", color = Muted, style = MaterialTheme.typography.labelSmall)
        DirectionChart(selected, "up", "▲ 상승확률", UpColor)
        DirectionChart(selected, "down", "▼ 하락확률", DownColor)
        Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color(0xFFE9EFFD))) {
            Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text("합이 100%가 아니어도 정상이에요", fontWeight = FontWeight.Bold)
                Text("각 막대 안에서는 ‘도달 + 미도달 = 100%’예요.", style = MaterialTheme.typography.bodySmall)
                Text("+10%에 도달하면 +5%에도 도달한 거예요. 같은 기간에 상승·하락 목표를 모두 찍을 수도 있어요.",
                    style = MaterialTheme.typography.bodySmall)
                Text("서로 겹치는 사건이라 각각 읽어 주세요. ±15%를 추가해도 합계가 100%로 나뉘지 않아요.",
                    style = MaterialTheme.typography.bodySmall)
            }
        }
        OutlinedButton(onClick = { showHistory = !showHistory }, modifier = Modifier.fillMaxWidth()) {
            Text(if (showHistory) "과거 기록 접기 ▲" else "과거 적중률·표본 보기 ▼")
        }
        if (showHistory) HistoryDetails(selected)
        Text("과거 데이터 기반 추정 · 독립 실전 검증 완료 아님", color = Muted, style = MaterialTheme.typography.bodySmall)
        Text("21·63·252거래일 × 3개 종목 × ±5%·±10%·±15%·±20%, 총 72개 항목을 선택해 볼 수 있어요. 새 종가가 확정되면 갱신되며 만료된 값은 표시하지 않아요.",
            color = Muted, style = MaterialTheme.typography.labelSmall)
        TextButton(onClick = { showMarkets = !showMarkets }, modifier = Modifier.fillMaxWidth()) {
            Text(if (showMarkets) "다른 시세 접기 ▲" else "다른 시세 보기 ▼")
        }
        if (showMarkets) {
            for ((id, label) in linkedMapOf("sp500" to "SPY", "ndx" to "QQQ", "djdiv" to "SCHD", "kospi100" to "KOSPI", "usdkrw" to "USD/KRW")) {
                val price = data.markets[id]?.optDouble("last_value", Double.NaN) ?: Double.NaN
                Row(Modifier.fillMaxWidth().padding(vertical = 5.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(label)
                    Text(if (price.isFinite() && price > 0) String.format(Locale.US, "%,.2f", price) else "확인 중")
                }
            }
        }
        Spacer(Modifier.height(8.dp))
    }
}

@Composable
private fun DirectionChart(forecasts: List<JSONObject>, direction: String, title: String, color: Color) {
    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White)) {
        Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(18.dp)) {
            Text(title, color = color, fontSize = 18.sp, fontWeight = FontWeight.Bold)
            for (threshold in listOf(5, 10, 15, 20)) {
                val label = "${if (direction == "up") "+" else "-"}$threshold% 도달"
                val forecast = forecasts.firstOrNull { it.optString("direction") == direction && it.optInt("threshold_percent") == threshold }
                val probability = forecast?.optDouble("probability", Double.NaN) ?: Double.NaN
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text(label, fontSize = 17.sp, fontWeight = FontWeight.Medium)
                        Text(if (probability.isFinite()) String.format(Locale.US, if (probability > 0 && probability < 1) "%.2f%%" else "%.1f%%", probability) else "확인 중",
                            color = color, fontSize = 25.sp, fontWeight = FontWeight.Bold)
                    }
                    if (probability.isFinite()) {
                        LinearProgressIndicator(progress = { (probability/100).toFloat().coerceIn(0f, 1f) },
                            modifier = Modifier.fillMaxWidth().height(14.dp).clip(RoundedCornerShape(8.dp)),
                            color = color, trackColor = color.copy(alpha = .10f), strokeCap = StrokeCap.Round)
                    } else Text("유효한 데이터가 들어오면 표시돼요.", color = Muted, style = MaterialTheme.typography.bodySmall)
                }
            }
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                for (label in listOf("0%", "50%", "100%")) Text(label, color = Muted, style = MaterialTheme.typography.labelSmall)
            }
        }
    }
}

@Composable
private fun HistoryDetails(forecasts: List<JSONObject>) {
    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White)) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("과거 기록", fontSize = 18.sp, fontWeight = FontWeight.Bold)
            val evidence = forecasts.firstOrNull()?.optJSONObject("evidence")
            if (evidence != null) {
                Text("${evidence.optInt("samples")}개 기준일 · ${evidence.optString("first")} ~ ${evidence.optString("last")}",
                    color = Muted, style = MaterialTheme.typography.bodySmall)
            }
            for (direction in listOf("up", "down")) for (threshold in listOf(5, 10, 15, 20)) {
                val f = forecasts.firstOrNull { it.optString("direction") == direction && it.optInt("threshold_percent") == threshold }
                val e = f?.optJSONObject("evidence") ?: continue
                HorizontalDivider()
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("${if (direction == "up") "+" else "-"}$threshold% 도달", fontWeight = FontWeight.SemiBold)
                    Text(String.format(Locale.US, "적중률 %.1f%%", e.optDouble("accuracy_pct")), fontWeight = FontWeight.SemiBold)
                }
                Text(String.format(Locale.US, "실제 도달 비율 %.1f%% · 단순 다수 판단 적중률 %.1f%%",
                    e.optDouble("actual_touch_rate_pct"), e.optDouble("majority_accuracy_pct")),
                    color = Muted, style = MaterialTheme.typography.labelSmall)
            }
            Text("적중률은 과거 예측 확률이 50% 이상이면 ‘도달’, 미만이면 ‘미도달’로 판단했을 때 실제 결과와 맞은 비율이에요.",
                color = Muted, style = MaterialTheme.typography.bodySmall)
            Text("큰 변동이 드문 항목은 미도달만 골라도 적중률이 높게 나올 수 있어요. 실제 도달 비율과 함께 읽어 주세요.", color = Muted, style = MaterialTheme.typography.bodySmall)
            Text("0%는 과거 관측·환산 표본에서 도달 사례가 없다는 뜻이며, 발생이 불가능하다는 뜻은 아니에요.", color = Muted, style = MaterialTheme.typography.bodySmall)
            Text("같은 과거 데이터를 개발에 재사용한 결과예요. 기간 말 종가의 수익률을 나눠 합계 100%로 만든 분포와는 다른 지표예요.",
                color = Muted, style = MaterialTheme.typography.bodySmall)
        }
    }
}
