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
        Text("검증 화면", fontSize = 18.sp, color = Color(0xFF244BD0))
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
                    if (id != "usdkrw") {
                        HorizontalDivider(Modifier.padding(vertical = 12.dp))
                        val node = if (id == "kospi100") data.monthly?.optJSONObject("items")?.optJSONObject(id)
                            else data.probabilities?.optJSONObject("items")?.optJSONObject(id)
                        val forecasts = ViewerPolicy.forecasts(node, ViewerPolicy.symbols[id].orEmpty(), System.currentTimeMillis()/1000)
                        Text("독립 검증 예측", fontWeight = FontWeight.SemiBold)
                        if (forecasts.isEmpty()) {
                            Text(if (data.updated) "검증 완료된 확률이 없습니다." else "검증 결과 확인 중…")
                        } else forecasts.forEach { f ->
                            Text("${f.label}  ${String.format(Locale.US, "%.1f%%", f.probability)}")
                        }
                    }
                }
            }
        }
        Text("21거래일 실전 검증 기록", fontWeight = FontWeight.Bold)
        for (symbol in listOf("SPY", "QQQ")) {
            val score = data.scores?.optJSONObject("symbols")?.optJSONObject(symbol)
            Text(if (score == null) "$symbol · 기록 확인 중" else
                "$symbol · 저장 ${score.optInt("stored_count")}건 / 채점 완료 ${score.optInt("scored_count")}건",
                style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(top = 5.dp))
        }
        Spacer(Modifier.height(16.dp))
        Text("21거래일 ±5% 도달확률", fontWeight = FontWeight.Bold)
        for (symbol in listOf("SPY", "QQQ")) {
            val candidate = data.scores?.optJSONObject("candidates")?.optJSONObject(symbol)
            if (candidate != null) {
                Text(candidate.optString("target_label"), fontWeight = FontWeight.SemiBold,
                    modifier = Modifier.padding(top = 10.dp))
                Text("과거 백테스트 통과 · 실전 검증 진행 중", style = MaterialTheme.typography.bodySmall)
                val forecast = ViewerPolicy.backtested(candidate, symbol, System.currentTimeMillis()/1000)
                if (forecast != null) {
                    Text(String.format(Locale.US, "%.1f%%", forecast.optDouble("probability")),
                        fontSize = 30.sp, fontWeight = FontWeight.Bold)
                    Text("${forecast.optString("as_of")} 종가 기준 → ${forecast.optString("target_date")}까지",
                        style = MaterialTheme.typography.bodySmall)
                    Text("기간 중 고가·저가 기준 · 21일 뒤 종가 예측과 다릅니다.", style = MaterialTheme.typography.bodySmall)
                    val evidence = forecast.getJSONObject("evidence")
                    Text("과거 ${evidence.optInt("samples")}개 기준일 · ${evidence.optString("first")} ~ ${evidence.optString("last")}",
                        style = MaterialTheme.typography.bodySmall)
                    Text(String.format(Locale.US, "비교 모델 대비 확률 오차 %.2f%% 감소 (적중률 아님)", evidence.optDouble("gain")),
                        style = MaterialTheme.typography.bodySmall)
                    Text("같은 과거 데이터를 개발에 재사용한 결과입니다.", style = MaterialTheme.typography.labelSmall)
                } else Text("최신 유효 확률을 확인하지 못했습니다. 새로고침해 주세요.", style = MaterialTheme.typography.bodySmall)
                Text("발행 ${candidate.optInt("stored_count")}건 / 결과 대기 ${candidate.optInt("pending_count")}건 / 채점 ${candidate.optInt("scored_count")}건",
                    style = MaterialTheme.typography.bodySmall)
                val maturity = candidate.optString("next_maturity_session").takeIf { it.isNotBlank() && it != "null" }
                if (maturity != null) Text("첫 결과 확인 대상 거래일: $maturity", style = MaterialTheme.typography.bodySmall)
                Text("첫 결과가 나오는 것과 검증 완료는 다릅니다.", style = MaterialTheme.typography.labelSmall)
            } else Text("$symbol · 후보 기록 확인 중", style = MaterialTheme.typography.bodySmall)
        }
        Text("과거 백테스트 통과 항목만 별도로 표시합니다. 탈락한 방향과 기본 발생률은 표시하지 않습니다.",
            style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(top = 14.dp, bottom = 18.dp))
    }
}
