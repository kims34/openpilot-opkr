package com.indexalert.app

import android.Manifest
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
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.TimeUnit

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
            status.value = "서버 설정 전 · 15분 로컬 감시 모드"
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
                rules.map { r ->
                    runCatching { MarketEngine.snapshot(applicationContext, r) }
                        .getOrElse { IndexSnapshot.error(r, it.message ?: "데이터 확인 실패") }
                }
            }
            snapshots.value = data
            val mode = if (PushBridge.configured()) "서버 푸시" else "로컬 감시"
            status.value = "$mode · 마지막 새로고침 ${SimpleDateFormat("MM/dd HH:mm", Locale.KOREA).format(Date())}"
            loading.value = false
        }
    }
}
