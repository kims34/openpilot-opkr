package com.indexalert.app

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.core.app.NotificationCompat
import androidx.lifecycle.lifecycleScope
import androidx.work.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.TimeUnit
import kotlin.math.abs
import kotlin.math.max

class MainActivity : ComponentActivity() {
    private val permission = registerForActivityResult(ActivityResultContracts.RequestPermission()) {}
    private val snapshots = mutableStateOf<List<IndexSnapshot>>(emptyList())
    private val loading = mutableStateOf(false)
    private val statusText = mutableStateOf("저전력 15분 간격 감시가 활성화됩니다.")

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        createChannel(this)
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            permission.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
        val req = PeriodicWorkRequestBuilder<IndexWorker>(15, TimeUnit.MINUTES).build()
        WorkManager.getInstance(this).enqueueUniquePeriodicWork("index-watch", ExistingPeriodicWorkPolicy.UPDATE, req)
        setContent {
            MaterialTheme {
                Home(
                    ctx = this,
                    snapshots = snapshots.value,
                    loading = loading.value,
                    statusText = statusText.value,
                    onRefresh = { refreshNow() }
                )
            }
        }
        refreshNow()
    }

    private fun refreshNow() {
        if (loading.value) return
        loading.value = true
        lifecycleScope.launch {
            val list = withContext(Dispatchers.IO) {
                rules.map { rule ->
                    runCatching { MarketEngine.snapshot(applicationContext, rule) }
                        .getOrElse { IndexSnapshot.error(rule, it.message ?: "데이터 확인 실패") }
                }
            }
            snapshots.value = list
            statusText.value = "마지막 새로고침: ${SimpleDateFormat("MM/dd HH:mm", Locale.KOREA).format(Date())}"
            loading.value = false
        }
    }
}

data class Rule(
    val id: String,
    val name: String,
    val cashSymbol: String,
    val proxySymbol: String?,
    val levels: List<Pair<Int, Int>>,
    val description: String
)

val rules = listOf(
    Rule(
        "sp500", "S&P 500", "^GSPC", "ES=F",
        listOf(5 to 10, 10 to 15, 15 to 20, 20 to 25, 25 to 15, 30 to 10, 35 to 5),
        "현물 S&P 500 · 장외는 S&P 선물 연동 추정"
    ),
    Rule(
        "ndx", "NASDAQ 100", "^NDX", "NQ=F",
        listOf(10 to 10, 15 to 15, 20 to 20, 25 to 20, 30 to 20, 35 to 15),
        "현물 NDX · 장외는 Nasdaq 선물 연동 추정"
    ),
    Rule(
        "djdiv", "SCHD 기준지수", "^DJUSDIV", "SCHD",
        listOf(5 to 15, 10 to 20, 15 to 20, 20 to 20, 25 to 15, 30 to 10),
        "Dow Jones U.S. Dividend 100"
    )
)

data class IndexSnapshot(
    val rule: Rule,
    val current: Double?,
    val ath: Double?,
    val drawdown: Double?,
    val stageText: String,
    val nextText: String,
    val sourceText: String,
    val error: String? = null
) {
    companion object {
        fun error(rule: Rule, msg: String) = IndexSnapshot(rule, null, null, null, "확인 불가", "-", "데이터 오류", msg)
    }
}

@Composable
fun Home(
    ctx: Context,
    snapshots: List<IndexSnapshot>,
    loading: Boolean,
    statusText: String,
    onRefresh: () -> Unit
) {
    val prefs = ctx.getSharedPreferences("state", Context.MODE_PRIVATE)
    var refreshHistory by remember { mutableIntStateOf(0) }
    Column(
        Modifier.fillMaxSize().padding(18.dp).verticalScroll(rememberScrollState())
    ) {
        Text("지수 하락 알리미", style = MaterialTheme.typography.headlineMedium)
        Text("Galaxy S25 · ATH 대비 단계별 매수구간 알림", style = MaterialTheme.typography.bodyMedium)
        Spacer(Modifier.height(14.dp))

        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = onRefresh, enabled = !loading, modifier = Modifier.weight(1f)) {
                Text(if (loading) "새로고침 중" else "지수 새로고침")
            }
            OutlinedButton(
                onClick = {
                    IndexWorker.notify(ctx, "테스트 알림", "지수 하락 알리미가 정상 작동합니다.")
                    HistoryStore.add(ctx, "테스트 알림 발송")
                    refreshHistory++
                },
                modifier = Modifier.weight(1f)
            ) { Text("테스트 알림") }
        }
        Text(statusText, Modifier.padding(top = 8.dp), style = MaterialTheme.typography.bodySmall)

        Spacer(Modifier.height(10.dp))
        if (snapshots.isEmpty() && loading) {
            LinearProgressIndicator(Modifier.fillMaxWidth())
        }
        snapshots.forEach { s -> IndexCard(s) }

        Spacer(Modifier.height(18.dp))
        Text("알림 단계 설정", style = MaterialTheme.typography.titleLarge)
        Text("각 단계는 같은 하락 사이클에서 한 번만 울립니다.", style = MaterialTheme.typography.bodySmall)
        rules.forEach { rule ->
            Card(Modifier.fillMaxWidth().padding(vertical = 6.dp)) {
                Column(Modifier.padding(14.dp)) {
                    Text(rule.name, style = MaterialTheme.typography.titleMedium)
                    rule.levels.forEach { lv ->
                        key("${rule.id}_${lv.first}") {
                            var enabled by remember {
                                mutableStateOf(prefs.getBoolean("enabled_${rule.id}_${lv.first}", true))
                            }
                            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                Text("-${lv.first}%  ·  추가매수 자금 ${lv.second}%")
                                Switch(
                                    checked = enabled,
                                    onCheckedChange = {
                                        enabled = it
                                        prefs.edit().putBoolean("enabled_${rule.id}_${lv.first}", it).apply()
                                        PushBridge.scheduleSync(ctx)
                                    }
                                )
                            }
                        }
                    }
                }
            }
        }

        Spacer(Modifier.height(18.dp))
        Text("최근 알림", style = MaterialTheme.typography.titleLarge)
        val history = remember(refreshHistory, statusText) { HistoryStore.list(ctx) }
        if (history.isEmpty()) {
            Text("아직 기록된 알림이 없습니다.", style = MaterialTheme.typography.bodySmall)
        } else {
            history.take(8).forEach { Text("• $it", Modifier.padding(vertical = 2.dp)) }
        }

        Spacer(Modifier.height(18.dp))
        Text(
            "장외 시간에는 현물지수 자체가 아니라 연동 시장의 움직임으로 환산한 추정치가 표시됩니다. " +
                "무료 프로토타입 데이터가 공식 거래소 실시간 피드와 다를 수 있습니다.",
            style = MaterialTheme.typography.bodySmall
        )
        Spacer(Modifier.height(24.dp))
    }
}

@Composable
fun IndexCard(s: IndexSnapshot) {
    Card(Modifier.fillMaxWidth().padding(vertical = 6.dp)) {
        Column(Modifier.padding(16.dp)) {
            Text(s.rule.name, style = MaterialTheme.typography.titleLarge)
            Text(s.rule.description, style = MaterialTheme.typography.bodySmall)
            if (s.error != null) {
                Spacer(Modifier.height(6.dp))
                Text("데이터 확인 실패: ${s.error}")
            } else {
                Spacer(Modifier.height(8.dp))
                Text("현재값  ${fmt(s.current)}", style = MaterialTheme.typography.titleMedium)
                Text("ATH      ${fmt(s.ath)}")
                Text("ATH 대비 ${s.drawdown?.let { String.format(Locale.US, "%.2f%%", it) } ?: "-"}")
                Text("현재 단계 ${s.stageText}")
                Text("다음 알림 ${s.nextText}")
                Text("기준       ${s.sourceText}", style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

private fun fmt(v: Double?): String = v?.let { String.format(Locale.US, "%,.2f", it) } ?: "-"

data class ChartData(val current: Double, val previousClose: Double, val marketState: String, val high: Double)

object MarketEngine {
    fun snapshot(ctx: Context, rule: Rule): IndexSnapshot {
        val prefs = ctx.getSharedPreferences("state", Context.MODE_PRIVATE)
        // Local fallback uses official cash data only: an ETF price cannot share
        // an index ATH, and an unanchored futures ratio can create false alerts.
        val baseData = fetchCurrent(rule.cashSymbol)
        val key = "ath_cash_${rule.id}"
        var ath = prefs.getString(key, null)?.toDoubleOrNull() ?: 0.0
        val day = SimpleDateFormat("yyyy-MM-dd", Locale.US).format(Date())
        if (ath <= 0 || prefs.getString("ath_day_${rule.id}", null) != day) {
            ath = max(ath, fetchAth(rule.cashSymbol))
            prefs.edit().putString("ath_day_${rule.id}", day).apply()
        }
        ath = max(ath, baseData.high)
        prefs.edit().putString(key, ath.toString()).apply()
        val current = baseData.current
        val source = "현물 마지막 값 · 로컬 보조 조회"

        val dd = if (ath > 0) (current / ath - 1.0) * 100.0 else 0.0
        val enabledLevels = rule.levels.filter { prefs.getBoolean("enabled_${rule.id}_${it.first}", true) }
        val reached = enabledLevels.filter { dd <= -it.first }
        val stage = reached.maxByOrNull { it.first }
        val next = enabledLevels.firstOrNull { it.first > abs(dd) }
        val stageText = stage?.let { "-${it.first}% 구간 · ${it.second}%" } ?: "대기"
        val nextText = next?.let { "-${it.first}%" } ?: "최종 단계 도달"

        return IndexSnapshot(rule, current, ath, dd, stageText, nextText, source)
    }

    private fun fetchCurrent(symbol: String): ChartData {
        val result = fetchResult(symbol, "5d", "5m", false)
        val meta = result.getJSONObject("meta")
        val quote = result.getJSONObject("indicators").getJSONArray("quote").getJSONObject(0)
        val closes = quote.getJSONArray("close")
        var last = Double.NaN
        for (i in closes.length() - 1 downTo 0) {
            if (!closes.isNull(i)) {
                last = closes.getDouble(i)
                break
            }
        }
        if (!last.isFinite()) {
            last = meta.optDouble("regularMarketPrice", Double.NaN)
        }
        val prev = when {
            meta.has("chartPreviousClose") -> meta.optDouble("chartPreviousClose", Double.NaN)
            meta.has("previousClose") -> meta.optDouble("previousClose", Double.NaN)
            else -> Double.NaN
        }
        val previousClose = if (prev.isFinite() && prev > 0) prev else last
        if (!last.isFinite() || last <= 0) error("현재값 없음")
        val highs = quote.optJSONArray("high")
        var recentHigh = last
        if (highs != null) for (i in 0 until highs.length()) {
            val high = highs.optDouble(i, Double.NaN)
            if (high.isFinite()) recentHigh = max(recentHigh, high)
        }
        return ChartData(last, previousClose, meta.optString("marketState", "CLOSED"), recentHigh)
    }

    private fun fetchAth(symbol: String): Double {
        val result = fetchResult(symbol, "max", "1d", false)
        val quote = result.getJSONObject("indicators").getJSONArray("quote").getJSONObject(0)
        val highs = quote.getJSONArray("high")
        var ath = 0.0
        for (i in 0 until highs.length()) {
            if (!highs.isNull(i)) ath = max(ath, highs.getDouble(i))
        }
        if (ath <= 0) error("ATH 계산 실패")
        return ath
    }

    private fun fetchResult(symbol: String, range: String, interval: String, includePrePost: Boolean): JSONObject {
        val enc = URLEncoder.encode(symbol, "UTF-8")
        val url = URL("https://query1.finance.yahoo.com/v8/finance/chart/$enc?range=$range&interval=$interval&includePrePost=$includePrePost")
        val conn = url.openConnection() as HttpURLConnection
        conn.connectTimeout = 12000
        conn.readTimeout = 12000
        conn.setRequestProperty("User-Agent", "Mozilla/5.0")
        val text = conn.inputStream.bufferedReader().use { it.readText() }
        val chart = JSONObject(text).getJSONObject("chart")
        val arr = chart.optJSONArray("result") ?: error("result 없음")
        if (arr.length() == 0 || arr.isNull(0)) error("빈 응답")
        return arr.getJSONObject(0)
    }
}

class IndexWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork(): Result {
        if (PushBridge.sync(applicationContext)) return Result.success()
        rules.forEach { rule -> runCatching { check(rule) } }
        return Result.success()
    }

    private fun check(rule: Rule) {
        val s = MarketEngine.snapshot(applicationContext, rule)
        val dd = s.drawdown ?: return
        val prefs = applicationContext.getSharedPreferences("state", Context.MODE_PRIVATE)
        val crossed = rule.levels.filter { lv ->
            prefs.getBoolean("enabled_${rule.id}_${lv.first}", true) &&
                dd <= -lv.first &&
                !prefs.getBoolean("delivered_${rule.id}_${s.ath}_${lv.first}", false)
        }
        if (crossed.isEmpty()) return
        val edit = prefs.edit()
        val deepest = crossed.maxBy { it.first }
        val next = rule.levels.firstOrNull { it.first > deepest.first }
        val title = "${rule.name} -${deepest.first}% 매수구간 진입"
        val body = buildString {
            append("ATH 대비 ${String.format(Locale.US, "%.2f%%", dd)} · 이번 단계 ${deepest.second}%")
            append(" · ${s.sourceText}")
            if (next != null) append(" · 다음 -${next.first}%")
        }
        if (!notify(applicationContext, title, body)) return
        crossed.forEach { edit.putBoolean("delivered_${rule.id}_${s.ath}_${it.first}", true) }
        edit.apply()
        HistoryStore.add(applicationContext, "$title / $body")
    }

    companion object {
        fun notify(ctx: Context, title: String, body: String): Boolean {
            createChannel(ctx)
            val nm = ctx.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            if (!nm.areNotificationsEnabled()) return false
            val intent = android.content.Intent(ctx, DashboardActivity::class.java)
            val pending = android.app.PendingIntent.getActivity(ctx, 0, intent,
                android.app.PendingIntent.FLAG_UPDATE_CURRENT or android.app.PendingIntent.FLAG_IMMUTABLE)
            val n = NotificationCompat.Builder(ctx, "index_alerts")
                .setContentIntent(pending)
                .setSmallIcon(android.R.drawable.ic_dialog_info)
                .setContentTitle(title)
                .setContentText(body)
                .setStyle(NotificationCompat.BigTextStyle().bigText(body))
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setAutoCancel(true)
                .build()
            return runCatching {
                nm.notify((System.currentTimeMillis() % Int.MAX_VALUE).toInt(), n)
                true
            }.getOrDefault(false)
        }
    }
}

object HistoryStore {
    @Synchronized
    fun add(ctx: Context, text: String) {
        val prefs = ctx.getSharedPreferences("state", Context.MODE_PRIVATE)
        val stamp = SimpleDateFormat("MM/dd HH:mm", Locale.KOREA).format(Date())
        val old = prefs.getString("history", "") ?: ""
        val merged = ("$stamp  $text\n" + old).lineSequence().take(30).joinToString("\n")
        prefs.edit().putString("history", merged).apply()
    }

    fun list(ctx: Context): List<String> {
        val raw = ctx.getSharedPreferences("state", Context.MODE_PRIVATE).getString("history", "") ?: ""
        return raw.lineSequence().filter { it.isNotBlank() }.toList()
    }
}

fun createChannel(ctx: Context) {
    if (Build.VERSION.SDK_INT >= 26) {
        val nm = ctx.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val channel = NotificationChannel("index_alerts", "지수 하락 알림", NotificationManager.IMPORTANCE_HIGH)
        channel.description = "ATH 대비 단계별 지수 하락 알림"
        nm.createNotificationChannel(channel)
    }
}

