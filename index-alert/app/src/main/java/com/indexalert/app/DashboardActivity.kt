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

class DashboardActivity : ComponentActivity() {
    private val permission = registerForActivityResult(ActivityResultContracts.RequestPermission()) {}
    private var snapshots = androidx.compose.runtime.mutableStateOf<List<IndexSnapshot>>(emptyList())
    private var loading = androidx.compose.runtime.mutableStateOf(false)
    private var status = androidx.compose.runtime.mutableStateOf("")

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        createChannel(this)
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            permission.launch(Manifest.permission.POST_NOTIFICATIONS)
        }

        val pushReady = PushBridge.tryInit(this)
        if (pushReady) {
            WorkManager.getInstance(this).cancelUniqueWork("index-watch")
            status.value = "서버 푸시 감시 활성화 · 휴대폰 주기 조회 없음"
        } else {
            val req = PeriodicWorkRequestBuilder<IndexWorker>(15, TimeUnit.MINUTES).build()
            WorkManager.getInstance(this).enqueueUniquePeriodicWork("index-watch", ExistingPeriodicWorkPolicy.UPDATE, req)
            status.value = "Firebase 설정 전 · 15분 로컬 감시 모드"
        }

        setContent {
            MaterialTheme {
                Home(
                    ctx = this,
                    snapshots = snapshots.value,
                    loading = loading.value,
                    statusText = status.value,
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
            val data = withContext(Dispatchers.IO) {
                if (PushBridge.configured()) {
                    runCatching { BackendMarket.snapshots(applicationContext) }.getOrElse {
                        rules.map { r ->
                            runCatching { MarketEngine.snapshot(applicationContext, r) }
                                .getOrElse { e -> IndexSnapshot.error(r, e.message ?: "데이터 확인 실패") }
                        }
                    }
                } else {
                    rules.map { r ->
                        runCatching { MarketEngine.snapshot(applicationContext, r) }
                            .getOrElse { IndexSnapshot.error(r, it.message ?: "데이터 확인 실패") }
                    }
                }
            }
            snapshots.value = data
            val mode = if (PushBridge.configured()) "서버 푸시" else "로컬 감시"
            status.value = "$mode · 마지막 새로고침 ${SimpleDateFormat("MM/dd HH:mm", Locale.KOREA).format(Date())}"
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
            val dd = if (ath != null && value != null && ath > 0) (value / ath - 1.0) * 100.0 else null
            val enabled = rule.levels.filter { prefs.getBoolean("enabled_${rule.id}_${it.first}", true) }
            val reached = if (dd == null) emptyList() else enabled.filter { dd <= -it.first }
            val stage = reached.maxByOrNull { it.first }
            val next = if (dd == null) enabled.firstOrNull() else enabled.firstOrNull { it.first > abs(dd) }
            IndexSnapshot(
                rule = rule,
                current = value,
                ath = ath,
                drawdown = dd,
                stageText = stage?.let { "-${it.first}% 구간 · ${it.second}%" } ?: "대기",
                nextText = next?.let { "-${it.first}%" } ?: "최종 단계 도달",
                sourceText = o.optString("source", "서버 감시")
            )
        }
    }

    private fun nullableDouble(o: JSONObject, key: String): Double? {
        if (!o.has(key) || o.isNull(key)) return null
        val v = o.optDouble(key, Double.NaN)
        return if (v.isFinite()) v else null
    }
}
