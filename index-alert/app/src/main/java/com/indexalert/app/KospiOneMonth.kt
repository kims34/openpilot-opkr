package com.indexalert.app

import android.content.Context
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

private object KospiOneMonthRepository {
    private var lastFetch = 0L
    private var cache: OneMonthEstimate? = null

    @Synchronized
    fun get(ctx: Context): OneMonthEstimate? {
        val now = System.currentTimeMillis()
        if (now - lastFetch < 60_000L && cache != null) return cache
        val prefs = ctx.getSharedPreferences("kospi_one_month", Context.MODE_PRIVATE)
        val fresh = runCatching { fetch() }.getOrNull()
        val parsed = fresh?.let { parse(it) }
        if (parsed != null && fresh != null) prefs.edit().putString("payload", fresh).apply()
        val saved = prefs.getString("payload", null)?.let { parse(it) }
        cache = parsed ?: saved
        lastFetch = now
        return cache
    }

    private fun fetch(): String {
        val base = BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/')
        val c = URL("$base/one-month-probabilities").openConnection() as HttpURLConnection
        c.requestMethod = "GET"
        c.connectTimeout = 6000
        c.readTimeout = 30000
        c.setRequestProperty("Accept", "application/json")
        return try {
            check(c.responseCode in 200..299)
            c.inputStream.bufferedReader().use { it.readText() }
        } finally {
            c.disconnect()
        }
    }

    private fun parse(raw: String): OneMonthEstimate? = runCatching {
        val root = JSONObject(raw)
        val o = root.optJSONObject("items")?.optJSONObject("kospi100") ?: return@runCatching null
        NextDayProbabilityRepository.parseOneMonth(o)
    }.getOrNull()
}

@Composable
fun KospiOneMonthProbabilitySection(refreshKey: String = "") {
    val ctx = LocalContext.current.applicationContext
    var estimate by remember { mutableStateOf<OneMonthEstimate?>(null) }
    var checked by remember { mutableStateOf(false) }
    var details by remember { mutableStateOf(false) }

    LaunchedEffect(refreshKey) {
        while (true) {
            estimate = withContext(Dispatchers.IO) { KospiOneMonthRepository.get(ctx) }
            checked = true
            delay(60_000L)
        }
    }

    Spacer(Modifier.height(10.dp))
    Card(
        Modifier.fillMaxWidth(),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(Modifier.padding(12.dp)) {
            val m = estimate
            if (m == null) {
                Text("KOSPI 1개월 확률 분석", fontWeight = FontWeight.Bold)
                Text(
                    if (checked) "최신 1개월 분석값을 확인하지 못했습니다. 잠시 후 새로고침해 주세요." else "최근 10년 KOSPI 일봉으로 1개월 분석 중…",
                    style = MaterialTheme.typography.bodySmall
                )
                return@Column
            }

            OneMonthSixBucketTable(m)
            Text("${m.asOf} 종가 기준 · 21거래일 뒤 종가 수익률 기준", style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(top = 5.dp))
            Text("현재 KOSPI 값은 네이버 증권 우선 · 확률 분석은 최근 10년 완료 일봉 사용", style = MaterialTheme.typography.bodySmall)

            TextButton(onClick = { details = !details }, contentPadding = PaddingValues(0.dp)) {
                Text(if (details) "검증 근거 접기 ▲" else "검증 근거 보기 ▼")
            }
            if (details) {
                val trend = if (m.trendRegime == "up") "21일 상승추세" else "21일 하락추세"
                val vol = if (m.volatilityRegime == "high") "고변동" else "저변동"
                Text("현재 국면: $trend · $vol · 연환산 변동성 ${kPct1(m.annualizedVolatility)}", style = MaterialTheme.typography.bodySmall)
                m.features?.let { f ->
                    Text("수익률: 5일 ${kSignedPct1(f.r5)} · 21일 ${kSignedPct1(f.r21)} · 63일 ${kSignedPct1(f.r63)}", style = MaterialTheme.typography.bodySmall)
                    Text("1년 고점 대비 ${kSignedPct1(f.drawdown252)} · 50일선 ${kSignedPct1(f.ma50Gap)} · 200일선 ${kSignedPct1(f.ma200Gap)}", style = MaterialTheme.typography.bodySmall)
                }
                if (m.terminalReturnSixBins.isNotEmpty()) {
                    Text("6구간 확률 합계 ${kPct1(m.terminalReturnSixBins.sumOf { it.probability })} · 구간 중복 없음", style = MaterialTheme.typography.bodySmall)
                    Text("분포 유효표본 ${String.format(Locale.US, "%.1f", m.terminalReturnSixEffectiveSample)}", style = MaterialTheme.typography.bodySmall)
                    kospiValidationLine("6구간 종가분포", m.terminalReturnSixSelection ?: "baseline", m.terminalReturnSixValidation)
                }
                Text("검증에서 유사장세 모델이 장기 기본분포보다 낫지 않으면 자동으로 장기 기본확률을 사용합니다.", style = MaterialTheme.typography.labelSmall)
            }
            Text("과거 통계에 따른 추정이며 향후 수익률을 보장하지 않습니다.", style = MaterialTheme.typography.labelSmall)
        }
    }
}

@Composable
private fun kospiValidationLine(label: String, selection: String, v: MonthValidation?) {
    if (v == null) {
        Text("$label 검증: 계산 중", style = MaterialTheme.typography.bodySmall)
        return
    }
    val chosen = if (selection == "analog") "유사장세 모델 채택" else "장기 기본확률 채택"
    Text(
        "$label: $chosen · 후반부 ${v.count}회 검증 · 개선 ${String.format(Locale.US, "%+.1f%%", v.skill)}",
        style = MaterialTheme.typography.bodySmall
    )
}

private fun kPct1(value: Double): String = String.format(Locale.US, "%.1f%%", value)
private fun kSignedPct1(value: Double): String = String.format(Locale.US, "%+.1f%%", value)
