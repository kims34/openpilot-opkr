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
import androidx.work.*
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.TimeUnit
import kotlin.math.max

class MainActivity : ComponentActivity() {
    private val permission = registerForActivityResult(ActivityResultContracts.RequestPermission()) {}
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        createChannel(this)
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) permission.launch(Manifest.permission.POST_NOTIFICATIONS)
        val req = PeriodicWorkRequestBuilder<IndexWorker>(15, TimeUnit.MINUTES).build()
        WorkManager.getInstance(this).enqueueUniquePeriodicWork("index-watch", ExistingPeriodicWorkPolicy.UPDATE, req)
        setContent { MaterialTheme { Home(this) } }
    }
}

data class Rule(val name:String, val symbol:String, val levels:List<Pair<Int,Int>>)
val rules = listOf(
    Rule("S&P 500", "^GSPC", listOf(5 to 10,10 to 15,15 to 20,20 to 25,25 to 15,30 to 10,35 to 5)),
    Rule("NASDAQ 100", "^NDX", listOf(10 to 10,15 to 15,20 to 20,25 to 20,30 to 20,35 to 15)),
    Rule("SCHD 기준지수 (DJUSDIV)", "DJUSDIV", listOf(5 to 15,10 to 20,15 to 20,20 to 20,25 to 15,30 to 10))
)

@Composable fun Home(ctx: Context) {
    var status by remember { mutableStateOf("저전력 백그라운드 감시 활성화") }
    Column(Modifier.fillMaxSize().padding(18.dp).verticalScroll(rememberScrollState())) {
        Text("지수 하락 알리미", style=MaterialTheme.typography.headlineMedium)
        Text("Galaxy S25 · ATH 기준 단계별 알림", style=MaterialTheme.typography.bodyMedium)
        Spacer(Modifier.height(14.dp))
        rules.forEach { r ->
            Card(Modifier.fillMaxWidth().padding(vertical=6.dp)) { Column(Modifier.padding(16.dp)) {
                Text(r.name, style=MaterialTheme.typography.titleMedium)
                Text("감시: " + r.levels.joinToString(" · ") { "-${it.first}%(${it.second}%)" })
                Text("같은 하락 단계는 1회만 알림")
            }}
        }
        Spacer(Modifier.height(12.dp))
        Button(onClick={ IndexWorker.notify(ctx,"테스트 알림","지수 하락 알리미가 정상 작동합니다."); status="테스트 알림을 보냈습니다." }, Modifier.fillMaxWidth()) { Text("테스트 알림") }
        Text(status, Modifier.padding(top=10.dp))
        Text("※ 무료 프로토타입 데이터는 지수가 실제 갱신될 때 신호를 계산합니다.", Modifier.padding(top=18.dp))
    }
}

class IndexWorker(ctx: Context, params: WorkerParameters): CoroutineWorker(ctx, params) {
    override suspend fun doWork(): Result {
        rules.forEach { runCatching { check(it) } }
        return Result.success()
    }
    private fun check(rule: Rule) {
        val data = fetch(rule.symbol) ?: return
        val prefs = applicationContext.getSharedPreferences("state", Context.MODE_PRIVATE)
        val storedAth = prefs.getFloat("ath_${rule.symbol}", 0f).toDouble()
        val ath = max(storedAth, data.second)
        if (ath > storedAth) {
            val edit = prefs.edit().putFloat("ath_${rule.symbol}", ath.toFloat())
            if (storedAth > 0) rule.levels.forEach { edit.putBoolean("fired_${rule.symbol}_${it.first}", false) }
            edit.apply()
        }
        if (ath <= 0) return
        val dd = (data.first / ath - 1.0) * 100.0
        val crossed = rule.levels.filter { dd <= -it.first && !prefs.getBoolean("fired_${rule.symbol}_${it.first}", false) }
        if (crossed.isNotEmpty()) {
            val edit = prefs.edit()
            crossed.forEach { edit.putBoolean("fired_${rule.symbol}_${it.first}", true) }
            edit.apply()
            val deepest = crossed.maxBy { it.first }
            notify(applicationContext, "${rule.name} -${deepest.first}% 구간 진입", "ATH 대비 %.2f%% · 추가매수 자금 %d%% 단계".format(dd, deepest.second))
        }
    }
    private fun fetch(symbol:String): Pair<Double,Double>? {
        val enc = java.net.URLEncoder.encode(symbol, "UTF-8")
        val u = URL("https://query1.finance.yahoo.com/v8/finance/chart/$enc?range=max&interval=1d")
        val c = u.openConnection() as HttpURLConnection
        c.connectTimeout=12000; c.readTimeout=12000; c.setRequestProperty("User-Agent","Mozilla/5.0")
        val txt = c.inputStream.bufferedReader().use { it.readText() }
        val result = JSONObject(txt).getJSONObject("chart").getJSONArray("result").getJSONObject(0)
        val quote = result.getJSONObject("indicators").getJSONArray("quote").getJSONObject(0)
        val highs = quote.getJSONArray("high"); val closes=quote.getJSONArray("close")
        var ath=0.0; var last=0.0
        for(i in 0 until highs.length()) if(!highs.isNull(i)) ath=max(ath, highs.getDouble(i))
        for(i in closes.length()-1 downTo 0) if(!closes.isNull(i)){ last=closes.getDouble(i); break }
        if(last<=0 || ath<=0) return null
        return last to ath
    }
    companion object {
        fun notify(ctx:Context,title:String,body:String){
            val nm=ctx.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            val n=NotificationCompat.Builder(ctx,"index_alerts").setSmallIcon(android.R.drawable.ic_dialog_info).setContentTitle(title).setContentText(body).setStyle(NotificationCompat.BigTextStyle().bigText(body)).setPriority(NotificationCompat.PRIORITY_HIGH).setAutoCancel(true).build()
            nm.notify((System.currentTimeMillis()%Int.MAX_VALUE).toInt(),n)
        }
    }
}
fun createChannel(ctx:Context){ if(Build.VERSION.SDK_INT>=26){ val nm=ctx.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager; nm.createNotificationChannel(NotificationChannel("index_alerts","지수 하락 알림",NotificationManager.IMPORTANCE_HIGH)) } }
