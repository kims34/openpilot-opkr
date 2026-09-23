package com.indexalert.app

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.material3.MaterialTheme
import androidx.lifecycle.lifecycleScope
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.TimeUnit
import kotlin.math.abs

private data class DashboardPayload(
    val snapshots: List<IndexSnapshot>,
    val ready: Boolean,
    val laggards: List<LaggardItem>,
    val laggardStatus: String
)

data class LaggardFeed(val items: List<LaggardItem>, val statusText: String)

class DashboardActivity : ComponentActivity() {
    private val permission = registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) {
            PushBridge.scheduleSync(this)
            refreshNow()
        } else {
            status.value = "알림 권한 필요 · IndexAlert 알림을 허용해야 실제 알림을 받을 수 있습니다."
        }
    }
    private var snapshots = androidx.compose.runtime.mutableStateOf<List<IndexSnapshot>>(emptyList())
    private var laggards = androidx.compose.runtime.mutableStateOf<List<LaggardItem>>(emptyList())
    private var laggardStatus = androidx.compose.runtime.mutableStateOf("")
    private var loading = androidx.compose.runtime.mutableStateOf(false)
    private var status = androidx.compose.runtime.mutableStateOf("")
    private var serverPushReady = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        createChannel(this)
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            permission.launch(Manifest.permission.POST_NOTIFICATIONS)
        }

        val firebaseConfigured = PushBridge.tryInit(this)
        ensureLocalWatch()
        status.value = when {
            !PushBridge.notificationsEnabled(this) -> "알림 권한 확인 중 · 허용 후 서버 푸시 등록"
            firebaseConfigured -> "Firebase 앱 연결됨 · 서버 등록 확인 중 · 임시 로컬 감시 유지"
            else -> "Firebase 설정 전 · 15분 로컬 감시 모드"
        }

        setContent {
            MaterialTheme {
                Home(
                    ctx = this,
                    snapshots = snapshots.value,
                    loading = loading.value,
                    statusText = status.value,
                    onRefresh = { refreshNow() },
                    laggards = laggards.value,
                    laggardStatus = laggardStatus.value
                )
            }
        }
        refreshNow()
    }

    private fun ensureLocalWatch() {
        val req = PeriodicWorkRequestBuilder<IndexWorker>(15, TimeUnit.MINUTES).build()
        WorkManager.getInstance(this)
            .enqueueUniquePeriodicWork("index-watch", ExistingPeriodicWorkPolicy.UPDATE, req)
    }

    private fun stopLocalWatch() {
        WorkManager.getInstance(this).cancelUniqueWork("index-watch")
    }

    private fun refreshNow() {
        if (loading.value) return
        loading.value = true
        lifecycleScope.launch {
            val result = withContext(Dispatchers.IO) {
                val ready = PushBridge.sync(applicationContext)
                val data = if (PushBridge.configured()) {
                    runCatching { BackendMarket.snapshots(applicationContext) }.getOrElse {
                        rules.map { r ->
                            runCatching { MarketEngine.snapshot(applicationContext, r) }
                                .getOrElse { e -> IndexSnapshot.error(r, e.message ?: "데이터 확인 실패") }
                        }
                    }
                } else {
                    rules.map { r ->
                        runCatching { MarketEngine.snapshot(applicationContext, r) }
                            .getOrElse { e -> IndexSnapshot.error(r, e.message ?: "데이터 확인 실패") }
                    }
                }
                val feed = if (PushBridge.configured()) {
                    runCatching { BackendMarket.laggards() }
                        .getOrElse { LaggardFeed(emptyList(), "S&P500 TOP10 서버 계산 대기") }
                } else {
                    LaggardFeed(emptyList(), "서버 연결 시 S&P500 TOP10 제공")
                }
                DashboardPayload(data, ready, feed.items, feed.statusText)
            }

            snapshots.value = result.snapshots
            laggards.value = result.laggards
            laggardStatus.value = result.laggardStatus
            serverPushReady = result.ready
            if (serverPushReady) stopLocalWatch() else ensureLocalWatch()

            val mode = when {
                !PushBridge.notificationsEnabled(this@DashboardActivity) ->
                    "알림 권한 필요 · 휴대폰 설정에서 IndexAlert 알림을 허용하세요"
                serverPushReady -> "서버 푸시 감시 활성화 · 휴대폰 주기 조회 없음"
                PushBridge.configured() -> "서버 등록 재시도 중 · 15분 로컬 감시 유지"
                else -> "Firebase 설정 전 · 15분 로컬 감시 모드"
            }
            status.value = "$mode · ${SimpleDateFormat("MM/dd HH:mm", Locale.KOREA).format(Date())}"
            loading.value = false
        }
    }
}

object BackendMarket {
    fun snapshots(ctx: Context): List<IndexSnapshot> {
        val base = BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/')
        val c = URL("$base/status").openConnection() as HttpURLConnection
        c.requestMethod = "GET"
        c.connectTimeout = 10000
        c.readTimeout = 10000
        c.setRequestProperty("Accept", "application/json")
        val text = c.inputStream.bufferedReader().use { it.readText() }
        c.disconnect()
        val arr = JSONObject(text).getJSONArray("indices")
        val byId = mutableMapOf<String, JSONObject>()
        for (i in 0 until arr.length()) {
            val o = arr.getJSONObject(i)
            byId[o.getString("id")] = o
        }
        val prefs = ctx.getSharedPreferences("state", Context.MODE_PRIVATE)
        return rules.map { rule ->
            val o = byId[rule.id] ?: return@map IndexSnapshot.error(rule, "서버 상태 없음")
            val ath = nullableDouble(o, "ath")
            val value = nullableDouble(o, "last_value")
            val dd = nullableDouble(o, "drawdown")
                ?: if (ath != null && value != null && ath > 0) (value / ath - 1.0) * 100.0 else null
            val alertsEnabled = o.optBoolean("alerts_enabled", rule.levels.isNotEmpty())
            val enabled = if (alertsEnabled) {
                rule.levels.filter { prefs.getBoolean("enabled_${rule.id}_${it.first}", true) }
            } else emptyList()
            val reached = if (dd == null) emptyList() else enabled.filter { dd <= -it.first }
            val stage = reached.maxByOrNull { it.first }
            val next = if (dd == null) enabled.firstOrNull() else enabled.firstOrNull { it.first > abs(dd) }
            IndexSnapshot(
                rule = rule,
                current = value,
                ath = ath,
                drawdown = dd,
                stageText = if (!alertsEnabled) "" else stage?.let { "-${it.first}% 구간 · ${it.second}%" } ?: "대기",
                nextText = if (!alertsEnabled) "" else next?.let { "-${it.first}%" }
                    ?: if (enabled.isEmpty()) "알림 단계 꺼짐" else "최종 단계 도달",
                sourceText = o.optString("source", "서버 감시"),
                dayChange = nullableDouble(o, "day_change"),
                dayChangePercent = nullableDouble(o, "day_change_percent"),
                athDate = nullableString(o, "ath_date"),
                athDays = nullableInt(o, "ath_days"),
                alertsEnabled = alertsEnabled
            )
        }
    }

    fun laggards(): LaggardFeed {
        val base = BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/')
        val c = URL("$base/laggards").openConnection() as HttpURLConnection
        c.requestMethod = "GET"
        c.connectTimeout = 10000
        c.readTimeout = 10000
        c.setRequestProperty("Accept", "application/json")
        val text = c.inputStream.bufferedReader().use { it.readText() }
        c.disconnect()
        val root = JSONObject(text)
        val status = root.optString("status", "building")
        val coverage = root.optString("coverage", "0/0")
        val arr = root.optJSONArray("items")
        val items = mutableListOf<LaggardItem>()
        if (arr != null) {
            for (i in 0 until arr.length()) {
                val o = arr.getJSONObject(i)
                items.add(
                    LaggardItem(
                        rank = o.optInt("rank", i + 1),
                        symbol = o.optString("symbol"),
                        name = o.optString("name"),
                        current = o.optDouble("current", 0.0),
                        ath = o.optDouble("ath", 0.0),
                        drawdown = o.optDouble("drawdown", 0.0),
                        sp500 = o.optBoolean("sp500", true),
                        nasdaq100 = o.optBoolean("nasdaq100", false),
                        schd = o.optBoolean("schd", false)
                    )
                )
            }
        }
        val label = when (status) {
            "ready" -> "서버 일일 갱신 · 계산 범위 $coverage"
            "building" -> "최초 ATH 계산 중 · $coverage"
            else -> "순위 갱신 대기 · $coverage"
        }
        return LaggardFeed(items, label)
    }

    private fun nullableDouble(o: JSONObject, key: String): Double? {
        if (!o.has(key) || o.isNull(key)) return null
        val v = o.optDouble(key, Double.NaN)
        return if (v.isFinite()) v else null
    }

    private fun nullableString(o: JSONObject, key: String): String? {
        if (!o.has(key) || o.isNull(key)) return null
        return o.optString(key).takeIf { it.isNotBlank() && it != "null" }
    }

    private fun nullableInt(o: JSONObject, key: String): Int? {
        if (!o.has(key) || o.isNull(key)) return null
        return o.optInt(key)
    }
}
