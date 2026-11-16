package com.indexalert.viewer

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
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

@Composable
private fun ViewerScreen(data: ScreenData, refreshing: Boolean, refresh: () -> Unit) {
    Column(Modifier.fillMaxSize().background(Color(0xFFF4F7FB))
        .verticalScroll(rememberScrollState()).padding(20.dp)) {
        Text("IndexAlert", fontSize = 28.sp, fontWeight = FontWeight.Bold)
        Text("과거 데이터 확률", fontSize = 18.sp, color = Color(0xFF244BD0))
        Spacer(Modifier.height(10.dp))
        Text("시세·검증 결과 조회 전용입니다. 기존 앱의 알림과 설정은 유지됩니다.", style = MaterialTheme.typography.bodySmall)
        Button(onClick = refresh, enabled = !refreshing, modifier = Modifier.padding(vertical = 12.dp)) {
            Text(if (refreshing) "확인 중…" else "새로고침")
        }
        val names = linkedMapOf("sp500" to "SPY · S&P 500", "ndx" to "QQQ · NASDAQ 100", "djdiv" to "SCHD", "kospi100" to "KOSPI", "usdkrw" to "USD/KRW")
        names.forEach { (id, name) ->
            Card(Modifier.fillMaxWidth().padding(bottom = 12.dp),
                colors = CardDefaults.cardColors(containerColor = Color.White)) {
                Column(Modifier.padding(18.dp)) {
                    Text(name, fontWeight = FontWeight.Bold, fontSize = 19.sp)
                    val row = data.markets[id]
                    val price = row?.optDouble("last_value", Double.NaN) ?: Double.NaN
                    if (price.isFinite() && price > 0) {
                        Text(String.format(Locale.US, "%,.2f", price), fontSize = 30.sp, fontWeight = FontWeight.Bold)
                        val change = row?.optDouble("day_change_percent", Double.NaN) ?: Double.NaN
                        if (row?.optBoolean("basis_verified", false) == true && change.isFinite()) {
                            Text(String.format(Locale.US, "전일 대비 %+.2f%%", change),
                                color = if (change >= 0) Color(0xFFBA2338) else Color(0xFF2454BB))
                        }
                        Text(row?.optString("source").orEmpty(), style = MaterialTheme.typography.bodySmall)
                    } else Text(if (data.updated) "시세를 확인하지 못했습니다." else "시세 확인 중…")

                }
            }
        }
        Text("과거 데이터 기반 도달확률", fontWeight = FontWeight.Bold, fontSize = 22.sp)
        Text("기간 중 한 번이라도 목표에 도달할 확률입니다. 기간 말 종가 예측과 다릅니다.",
            style = MaterialTheme.typography.bodySmall)
        Text("비교 모델 대비 개선 여부와 관계없이 모든 항목을 표시합니다. 독립 실전 검증 완료 수치는 아닙니다.",
            style = MaterialTheme.typography.bodySmall)
        val forecasts=ViewerPolicy.historical(data.scores, System.currentTimeMillis()/1000)
        for (horizon in listOf(21,63)) {
            Text(if (horizon==21) "1개월 · 21거래일" else "3개월 · 63거래일",
                fontWeight = FontWeight.Bold, fontSize = 21.sp, modifier = Modifier.padding(top = 20.dp, bottom = 8.dp))
            for (symbol in listOf("SPY","QQQ","SCHD")) {
                val group=forecasts.filter { it.optString("symbol")==symbol && it.optInt("horizon_sessions")==horizon }
                Card(Modifier.fillMaxWidth().padding(bottom = 12.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White)) {
                    Column(Modifier.padding(16.dp)) {
                        Text(symbol, fontWeight = FontWeight.Bold, fontSize = 20.sp)
                        val first=group.firstOrNull()
                        if (first != null) {
                            Text("${first.optString("as_of")} 종가 기준 → ${first.optString("target_date")}까지",
                                style = MaterialTheme.typography.bodySmall)
                            val evidence=first.getJSONObject("evidence")
                            Text("과거 ${evidence.optInt("samples")}개 기준일 · ${evidence.optString("first")} ~ ${evidence.optString("last")}",
                                style = MaterialTheme.typography.bodySmall)
                        }
                        for (threshold in listOf(5,10)) for (direction in listOf("up","down")) {
                            val label="${if(direction=="up") "+" else "-"}${threshold}% 도달"
                            val f=group.firstOrNull { it.optInt("threshold_percent")==threshold && it.optString("direction")==direction }
                            HorizontalDivider(Modifier.padding(vertical = 9.dp))
                            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                Text(label, fontWeight = FontWeight.SemiBold)
                                Text(if(f==null) "확인 중" else String.format(Locale.US,"%.1f%%",f.optDouble("probability")),
                                    fontWeight = FontWeight.Bold, fontSize = 20.sp)
                            }
                            if (f != null) {
                                val evidence=f.getJSONObject("evidence")
                                Text(String.format(Locale.US,"과거 적중률 %.1f%% · 실제 도달 비율 %.1f%%",
                                    evidence.optDouble("accuracy_pct"),evidence.optDouble("actual_touch_rate_pct")),
                                    style = MaterialTheme.typography.bodySmall)
                                Text(String.format(Locale.US,"단순 다수 판단 적중률 %.1f%%",evidence.optDouble("majority_accuracy_pct")),
                                    style = MaterialTheme.typography.labelSmall)
                            }
                        }
                    }
                }
            }
        }
        Text("적중률: 예측 확률 50% 이상이면 도달, 미만이면 미도달로 판단한 과거 일치율입니다. 도달확률 자체와 다릅니다. 상승·하락은 동시에 도달할 수 있어 합이 100%가 아닙니다.",
            style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(top = 8.dp))
        Text("같은 과거 데이터를 개발에 재사용한 추정입니다. 새 종가가 확정되면 갱신되며, 유효기간이 지난 값은 숨깁니다.",
            style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(top = 8.dp, bottom = 18.dp))
    }
}
