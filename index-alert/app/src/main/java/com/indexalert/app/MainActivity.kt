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
import java.time.Instant
import java.time.ZoneId
import java.time.temporal.ChronoUnit
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
    val description: String,
    val timezone: String
)

val rules = listOf(
    Rule(
        "sp500", "SPY (S&P 500 ETF)", "SPY", "SPY",
        listOf(5 to 10, 10 to 15, 15 to 20, 20 to 25, 25 to 15, 30 to 10, 35 to 5),
        "S&P 500 추종 ETF · SPY 자체 가격 기준", "America/New_York"
    ),
    Rule(
        "ndx", "QQQ (NASDAQ 100 ETF)", "QQQ", "QQQ",
        listOf(10 to 10, 15 to 15, 20 to 20, 25 to 20, 30 to 20, 35 to 15),
        "NASDAQ-100 추종 ETF · QQQ 자체 가격 기준", "America/New_York"
    ),
    Rule(
        "djdiv", "SCHD", "SCHD", "SCHD",
        listOf(5 to 15, 10 to 20, 15 to 20, 20 to 20, 25 to 15, 30 to 10),
        "SCHD ETF 자체 가격 기준", "America/New_York"
    ),
    Rule(
        "kospi100", "KOSPI 100", "KOSPI100.KS", null,
        emptyList(),
        "KOSPI 100 지수 · 표시 전용 (알림 없음)", "Asia/Seoul"
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
    val dayChange: Double? = null,
    val dayChangePercent: Double? = null,
    val athDate: String? = null,
    val athDays: Int? = null,
    val alertsEnabled: Boolean = true,
    val error: String? = null
) {
    companion object {
        fun error(rule: Rule, msg: String) = IndexSnapshot(
            rule, null, null, null, "확인 불가", "-", "데이터 오류",
            alertsEnabled = rule.levels.isNotEmpty(), error = msg
        )
    }
}

data class LaggardItem(
    val rank: Int,
    val symbol: String,
    val name: String,
    val current: Double,
    val ath: Double,
    val drawdown: Double,
    val sp500: Boolean,
    val nasdaq100: Boolean,
    val schd: Boolean,
    val universe: String = "sp500",
    val previousClose: Double = 0.0,
    val dayChange: Double = 0.0,
    val dayChangePercent: Double = 0.0,
    val athDays: Int = 0
)

@Composable
fun Home(
    ctx: Context,
    snapshots: List<IndexSnapshot>,
    loading: Boolean,
    statusText: String,
    onRefresh: () -> Unit,
    laggards: List<LaggardItem> = emptyList(),
    laggardStatus: String = ""
) {
    val prefs = ctx.getSharedPreferences("state", Context.MODE_PRIVATE)
    var refreshHistory by remember { mutableIntStateOf(0) }
    Column(Modifier.fillMaxSize().padding(18.dp).verticalScroll(rememberScrollState())) {
        Text("시장 하락 알리미", style = MaterialTheme.typography.headlineMedium)
        Text("SPY · QQQ · SCHD · KOSPI100 / ATH 기준 현황", style = MaterialTheme.typography.bodyMedium)
        Spacer(Modifier.height(14.dp))

        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = onRefresh, enabled = !loading, modifier = Modifier.weight(1f)) {
                Text(if (loading) "새로고침 중" else "새로고침")
            }
            OutlinedButton(
                onClick = {
                    IndexWorker.notify(ctx, "테스트 알림", "시장 하락 알리미가 정상 작동합니다.")
                    HistoryStore.add(ctx, "테스트 알림 발송")
                    refreshHistory++
                },
                modifier = Modifier.weight(1f)
            ) { Text("테스트 알림") }
        }
        Text(statusText, Modifier.padding(top = 8.dp), style = MaterialTheme.typography.bodySmall)

        Spacer(Modifier.height(10.dp))
        if (snapshots.isEmpty() && loading) LinearProgressIndicator(Modifier.fillMaxWidth())
        snapshots.forEach { s -> IndexCard(s) }

        Spacer(Modifier.height(18.dp))
        Text("개별종목 ATH 하락 TOP 10", style = MaterialTheme.typography.titleLarge)
        Text("각 그룹별 ATH 대비 하락률이 큰 순 · 중복 편입은 그대로 표시", style = MaterialTheme.typography.bodySmall)
        val groups = listOf(
            "sp500" to "S&P500 하락 TOP 10",
            "nasdaq100" to "NASDAQ100 하락 TOP 10",
            "schd" to "SCHD 보유종목 하락 TOP 10"
        )
        var anyGroup = false
        groups.forEach { (key, title) ->
            val group = laggards.filter { it.universe == key }.sortedBy { it.rank }
            if (group.isNotEmpty()) {
                anyGroup = true
                Spacer(Modifier.height(12.dp))
                Text(title, style = MaterialTheme.typography.titleMedium)
                group.forEach { LaggardCard(it) }
            }
        }
        if (!anyGroup) {
            Text(laggardStatus.ifBlank { "TOP10 순위 계산 중" }, Modifier.padding(top = 8.dp))
        } else if (laggardStatus.isNotBlank()) {
            Text(laggardStatus, Modifier.padding(top = 6.dp), style = MaterialTheme.typography.bodySmall)
        }

        Spacer(Modifier.height(18.dp))
        Text("알림 단계 설정", style = MaterialTheme.typography.titleLarge)
        Text("SPY · QQQ · SCHD만 알림을 사용합니다. 각 단계는 같은 하락 사이클에서 한 번만 울립니다.", style = MaterialTheme.typography.bodySmall)
        rules.filter { it.levels.isNotEmpty() }.forEach { rule ->
            Card(Modifier.fillMaxWidth().padding(vertical = 6.dp)) {
                Column(Modifier.padding(14.dp)) {
                    Text(rule.name, style = MaterialTheme.typography.titleMedium)
                    rule.levels.forEach { lv ->
                        key("${rule.id}_${lv.first}") {
                            var enabled by remember { mutableStateOf(prefs.getBoolean("enabled_${rule.id}_${lv.first}", true)) }
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
        if (history.isEmpty()) Text("아직 기록된 알림이 없습니다.", style = MaterialTheme.typography.bodySmall)
        else history.take(8).forEach { Text("• $it", Modifier.padding(vertical = 2.dp)) }

        Spacer(Modifier.height(18.dp))
        Text(
            "SPY · QQQ · SCHD는 정규장과 프리마켓·애프터마켓의 ETF 자체 가격을 서버가 감시합니다. " +
                "KOSPI100은 지수 현황만 표시하며 알림을 보내지 않습니다. 개별종목 TOP10은 서버 캐시를 주기적으로 갱신합니다. " +
                "무료 프로토타입 시세는 공식 거래소 실시간 피드와 다를 수 있습니다.",
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
                val change = if (s.dayChange != null && s.dayChangePercent != null) "  ${signed(s.dayChange)} (${signedPct(s.dayChangePercent)})" else ""
                Text("현재값  ${fmt(s.current)}$change", style = MaterialTheme.typography.titleMedium)
                val age = s.athDays?.let { if (it == 0) " · 오늘 최고가" else " · 최고가 후 ${it}일" } ?: ""
                val date = s.athDate?.let { " ($it)" } ?: ""
                Text("ATH      ${fmt(s.ath)}$age$date")
                Text("ATH 대비 ${s.drawdown?.let { String.format(Locale.US, "%.2f%%", it) } ?: "-"}")
                if (s.alertsEnabled) {
                    Text("현재 단계 ${s.stageText}")
                    Text("다음 알림 ${s.nextText}")
                }
                Text("기준       ${s.sourceText}", style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

@Composable
fun LaggardCard(item: LaggardItem) {
    Card(Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
        Column(Modifier.padding(12.dp)) {
            Text("${item.rank}. ${item.symbol} · ${item.name}", style = MaterialTheme.typography.titleMedium)
            Text("현재 ${fmt(item.current)}  ${signed(item.dayChange)} (${signedPct(item.dayChangePercent)})")
            val age = if (item.athDays == 0) "오늘 최고가" else "최고가 후 ${item.athDays}일"
            Text("ATH ${fmt(item.ath)} · $age · ATH 대비 ${String.format(Locale.US, "%.2f%%", item.drawdown)}")
            val memberships = buildList {
                if (item.sp500) add("S&P500")
                if (item.nasdaq100) add("Nasdaq100")
                if (item.schd) add("SCHD")
            }.joinToString(" · ")
            Text("포함: ${memberships.ifBlank { "해당 없음" }}", style = MaterialTheme.typography.bodySmall)
        }
    }
}

private fun fmt(v: Double?): String = v?.let { String.format(Locale.US, "%,.2f", it) } ?: "-"
private fun signed(v: Double): String = String.format(Locale.US, "%+,.2f", v)
private fun signedPct(v: Double): String = String.format(Locale.US, "%+.2f%%", v)

data class ChartData(val current: Double, val previousClose: Double, val marketState: String, val high: Double, val highTs: Long)
data class AthData(val value: Double, val timestamp: Long)

object MarketEngine {
    fun snapshot(ctx: Context, rule: Rule): IndexSnapshot {
        val prefs = ctx.getSharedPreferences("state", Context.MODE_PRIVATE)
        val baseData = fetchCurrent(rule.cashSymbol)
        val key = "ath_cash_${rule.id}"
        var ath = prefs.getString(key, null)?.toDoubleOrNull() ?: 0.0
        var athTs = prefs.getLong("ath_ts_${rule.id}", 0L)
        val day = SimpleDateFormat("yyyy-MM-dd", Locale.US).format(Date())
        if (ath <= 0 || prefs.getString("ath_day_${rule.id}", null) != day) {
            val hist = fetchAth(rule.cashSymbol)
            if (hist.value >= ath) { ath = hist.value; athTs = hist.timestamp }
            prefs.edit().putString("ath_day_${rule.id}", day).apply()
        }
        if (baseData.high >= ath) { ath = baseData.high; athTs = baseData.highTs }
        prefs.edit().putString(key, ath.toString()).putLong("ath_ts_${rule.id}", athTs).apply()
        val current = baseData.current
        val source = if (rule.id == "kospi100") "KOSPI 100 지수 · 로컬 보조 조회" else "ETF 자체 가격 · 로컬 보조 조회"
        val dd = if (ath > 0) (current / ath - 1.0) * 100.0 else 0.0
        val dayChange = current - baseData.previousClose
        val dayChangePct = if (baseData.previousClose > 0) (current / baseData.previousClose - 1.0) * 100.0 else 0.0
        val enabledLevels = rule.levels.filter { prefs.getBoolean("enabled_${rule.id}_${it.first}", true) }
        val reached = enabledLevels.filter { dd <= -it.first }
        val stage = reached.maxByOrNull { it.first }
        val next = enabledLevels.firstOrNull { it.first > abs(dd) }
        val stageText = if (rule.levels.isEmpty()) "" else stage?.let { "-${it.first}% 구간 · ${it.second}%" } ?: "대기"
        val nextText = if (rule.levels.isEmpty()) "" else next?.let { "-${it.first}%" } ?: "최종 단계 도달"
        val zone = ZoneId.of(rule.timezone)
        val athDate = if (athTs > 0) Instant.ofEpochSecond(athTs).atZone(zone).toLocalDate() else null
        val athDays = athDate?.let { ChronoUnit.DAYS.between(it, java.time.LocalDate.now(zone)).toInt().coerceAtLeast(0) }
        return IndexSnapshot(rule, current, ath, dd, stageText, nextText, source, dayChange, dayChangePct, athDate?.toString(), athDays, rule.levels.isNotEmpty())
    }

    private fun fetchCurrent(symbol: String): ChartData {
        val result = fetchResult(symbol, "5d", "5m", true)
        val meta = result.getJSONObject("meta")
        val quote = result.getJSONObject("indicators").getJSONArray("quote").getJSONObject(0)
        val closes = quote.getJSONArray("close")
        val timestamps = result.optJSONArray("timestamp")
        var last = Double.NaN
        var lastIndex = -1
        for (i in closes.length() - 1 downTo 0) if (!closes.isNull(i)) { last = closes.getDouble(i); lastIndex = i; break }
        if (!last.isFinite()) last = meta.optDouble("regularMarketPrice", Double.NaN)
        val prev = when {
            meta.has("regularMarketPreviousClose") -> meta.optDouble("regularMarketPreviousClose", Double.NaN)
            meta.has("chartPreviousClose") -> meta.optDouble("chartPreviousClose", Double.NaN)
            meta.has("previousClose") -> meta.optDouble("previousClose", Double.NaN)
            else -> Double.NaN
        }
        val previousClose = if (prev.isFinite() && prev > 0) prev else last
        if (!last.isFinite() || last <= 0) error("현재값 없음")
        val highs = quote.optJSONArray("high")
        var recentHigh = last
        var recentHighTs = if (timestamps != null && lastIndex >= 0) timestamps.optLong(lastIndex, 0L) else 0L
        if (highs != null) for (i in 0 until highs.length()) {
            val high = highs.optDouble(i, Double.NaN)
            if (high.isFinite() && high >= recentHigh) { recentHigh = high; recentHighTs = timestamps?.optLong(i, recentHighTs) ?: recentHighTs }
        }
        return ChartData(last, previousClose, meta.optString("marketState", "CLOSED"), recentHigh, recentHighTs)
    }

    private fun fetchAth(symbol: String): AthData {
        val enc = URLEncoder.encode(symbol, "UTF-8")
        val url = URL("https://query1.finance.yahoo.com/v8/finance/chart/$enc?range=max&interval=1d&includePrePost=false&events=splits")
        val conn = url.openConnection() as HttpURLConnection
        conn.connectTimeout = 12000
        conn.readTimeout = 12000
        conn.setRequestProperty("User-Agent", "Mozilla/5.0")
        val text = conn.inputStream.bufferedReader().use { it.readText() }
        conn.disconnect()
        val chart = JSONObject(text).getJSONObject("chart")
        val arr = chart.optJSONArray("result") ?: error("result 없음")
        if (arr.length() == 0 || arr.isNull(0)) error("빈 응답")
        val result = arr.getJSONObject(0)
        val timestamps = result.getJSONArray("timestamp")
        val quote = result.getJSONObject("indicators").getJSONArray("quote").getJSONObject(0)
        val highs = quote.getJSONArray("high")
        val splits = mutableListOf<Pair<Long, Double>>()
        val splitObj = result.optJSONObject("events")?.optJSONObject("splits")
        if (splitObj != null) {
            val keys = splitObj.keys()
            while (keys.hasNext()) {
                val ev = splitObj.optJSONObject(keys.next()) ?: continue
                val ts = ev.optLong("date", 0L)
                var ratio = 0.0
                val num = ev.optDouble("numerator", 0.0)
                val den = ev.optDouble("denominator", 0.0)
                if (num > 0.0 && den > 0.0) ratio = num / den
                else {
                    val raw = ev.optString("splitRatio", "")
                    if (raw.contains(":")) {
                        val p = raw.split(":", limit = 2)
                        ratio = (p.getOrNull(0)?.toDoubleOrNull() ?: 0.0) / (p.getOrNull(1)?.toDoubleOrNull() ?: 1.0)
                    }
                }
                if (ts > 0L && ratio > 0.0) splits.add(ts to ratio)
            }
        }
        var ath = 0.0
        var athTs = 0L
        val count = minOf(timestamps.length(), highs.length())
        for (i in 0 until count) {
            if (highs.isNull(i)) continue
            val h = highs.optDouble(i, Double.NaN)
            if (!h.isFinite() || h <= 0.0) continue
            val ts = timestamps.optLong(i, 0L)
            var factor = 1.0
            splits.forEach { (splitTs, ratio) -> if (splitTs > ts) factor *= ratio }
            val adjusted = h / factor
            if (adjusted >= ath) { ath = adjusted; athTs = ts }
        }
        if (ath <= 0) error("ATH 계산 실패")
        return AthData(ath, athTs)
    }

    private fun fetchResult(symbol: String, range: String, interval: String, includePrePost: Boolean): JSONObject {
        val enc = URLEncoder.encode(symbol, "UTF-8")
        val url = URL("https://query1.finance.yahoo.com/v8/finance/chart/$enc?range=$range&interval=$interval&includePrePost=$includePrePost")
        val conn = url.openConnection() as HttpURLConnection
        conn.connectTimeout = 12000
        conn.readTimeout = 12000
        conn.setRequestProperty("User-Agent", "Mozilla/5.0")
        val text = conn.inputStream.bufferedReader().use { it.readText() }
        conn.disconnect()
        val chart = JSONObject(text).getJSONObject("chart")
        val arr = chart.optJSONArray("result") ?: error("result 없음")
        if (arr.length() == 0 || arr.isNull(0)) error("빈 응답")
        return arr.getJSONObject(0)
    }
}

class IndexWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork(): Result {
        if (PushBridge.sync(applicationContext)) {
            WorkManager.getInstance(applicationContext).cancelUniqueWork("index-watch")
            return Result.success()
        }
        rules.forEach { rule -> runCatching { check(rule) } }
        return Result.success()
    }

    private fun check(rule: Rule) {
        if (rule.levels.isEmpty()) return
        val s = MarketEngine.snapshot(applicationContext, rule)
        synchronized(HistoryStore) {
            val dd = s.drawdown ?: return
            val prefs = applicationContext.getSharedPreferences("state", Context.MODE_PRIVATE)
            val crossed = rule.levels.filter { lv ->
                prefs.getBoolean("enabled_${rule.id}_${lv.first}", true) && dd <= -lv.first && !prefs.getBoolean("delivered_${rule.id}_${s.ath}_${lv.first}", false)
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
    }

    companion object {
        fun notify(ctx: Context, title: String, body: String): Boolean {
            createChannel(ctx)
            val nm = ctx.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            if (!nm.areNotificationsEnabled()) return false
            val intent = android.content.Intent(ctx, DashboardActivity::class.java)
            val pending = android.app.PendingIntent.getActivity(ctx, 0, intent, android.app.PendingIntent.FLAG_UPDATE_CURRENT or android.app.PendingIntent.FLAG_IMMUTABLE)
            val n = NotificationCompat.Builder(ctx, "index_alerts")
                .setContentIntent(pending)
                .setSmallIcon(android.R.drawable.ic_dialog_info)
                .setContentTitle(title)
                .setContentText(body)
                .setStyle(NotificationCompat.BigTextStyle().bigText(body))
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setAutoCancel(true)
                .build()
            return runCatching { nm.notify((System.currentTimeMillis() % Int.MAX_VALUE).toInt(), n); true }.getOrDefault(false)
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
        val channel = NotificationChannel("index_alerts", "ETF 하락 알림", NotificationManager.IMPORTANCE_HIGH)
        channel.description = "SPY · QQQ · SCHD ATH 대비 단계별 하락 알림"
        nm.createNotificationChannel(channel)
    }
}
