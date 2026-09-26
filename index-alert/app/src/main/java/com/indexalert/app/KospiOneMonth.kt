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
        if (o.has("error")) return@runCatching null

        val up = o.optDouble("up_10_probability", Double.NaN)
        val down = o.optDouble("down_10_probability", Double.NaN)
        val baseUp = o.optDouble("baseline_up_10_probability", Double.NaN)
        val baseDown = o.optDouble("baseline_down_10_probability", Double.NaN)
        val horizon = o.optInt("horizon_sessions", 0)
        val threshold = o.optInt("threshold_percent", 0)
        val basis = o.optString("price_basis")
        val sample = o.optInt("sample_size", 0)
        val baselineSample = o.optInt("baseline_sample_size", 0)
        val vol = o.optDouble("annualized_volatility", Double.NaN)
        if (horizon != 21 || threshold != 10 || basis !in setOf("daily_high_low", "daily_close")) return@runCatching null
        if (!up.isFinite() || !down.isFinite() || up !in 0.0..100.0 || down !in 0.0..100.0) return@runCatching null
        if (!baseUp.isFinite() || !baseDown.isFinite() || baselineSample < 252 || sample <= 0 || !vol.isFinite()) return@runCatching null

        val features = o.optJSONObject("features")?.let { f ->
            MonthFeatures(
                f.optDouble("return_5d", 0.0),
                f.optDouble("return_21d", 0.0),
                f.optDouble("return_63d", 0.0),
                f.optDouble("drawdown_252d", 0.0),
                f.optDouble("ma50_gap", 0.0),
                f.optDouble("ma200_gap", 0.0)
            )
        }
        val top3 = buildList {
            val arr = o.optJSONArray("terminal_return_top3") ?: return@buildList
            for (i in 0 until minOf(3, arr.length())) {
                val item = arr.optJSONObject(i) ?: continue
                val label = item.optString("label").trim()
                val probability = item.optDouble("probability", Double.NaN)
                if (label.isNotBlank() && probability.isFinite() && probability in 0.0..100.0) {
                    add(TerminalReturnRank(label, probability))
                }
            }
        }

        OneMonthEstimate(
            up10Probability = up,
            down10Probability = down,
            horizonSessions = horizon,
            sampleSize = sample,
            baselineSampleSize = baselineSample,
            baselineUp10Probability = baseUp,
            baselineDown10Probability = baseDown,
            trendRegime = o.optString("trend_regime"),
            volatilityRegime = o.optString("volatility_regime"),
            annualizedVolatility = vol,
            asOf = o.optString("as_of"),
            method = o.optString("method"),
            priceBasis = basis,
            selectionUp = o.optString("selection_up", "baseline"),
            selectionDown = o.optString("selection_down", "baseline"),
            validationUp = parseValidation(o.optJSONObject("validation_up")),
            validationDown = parseValidation(o.optJSONObject("validation_down")),
            effectiveSampleUp = o.optDouble("effective_sample_up", 0.0),
            effectiveSampleDown = o.optDouble("effective_sample_down", 0.0),
            features = features,
            terminalReturnTop3 = top3,
            terminalReturnModeLabel = o.optString("terminal_return_mode_label").takeIf { it.isNotBlank() },
            terminalReturnModeProbability = o.optDouble("terminal_return_mode_probability", Double.NaN).takeIf { it.isFinite() && it in 0.0..100.0 },
            terminalReturnSelection = o.optString("terminal_return_selection").takeIf { it == "analog" || it == "baseline" },
            terminalReturnValidation = parseValidation(o.optJSONObject("terminal_return_validation")),
            terminalReturnEffectiveSample = o.optDouble("terminal_return_effective_sample", 0.0),
            terminalReturnBinWidthPercent = o.optInt("terminal_return_bin_width_percent", 0)
        )
    }.getOrNull()

    private fun parseValidation(o: JSONObject?): MonthValidation? {
        if (o == null) return null
        val model = o.optDouble("model_brier", Double.NaN)
        val baseline = o.optDouble("baseline_brier", Double.NaN)
        val skill = o.optDouble("skill", Double.NaN)
        val count = o.optInt("count", 0)
        if (count <= 0 || !model.isFinite() || !baseline.isFinite() || !skill.isFinite()) return null
        return MonthValidation(count, model, baseline, skill)
    }
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

            Text("향후 1개월(21거래일) ±10% 도달 확률", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            Text("+10% 이상 상승 도달  ${kPct1(m.up10Probability)}", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            Text("-10% 이상 하락 도달  ${kPct1(m.down10Probability)}", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)

            if (m.terminalReturnTop3.isNotEmpty()) {
                Spacer(Modifier.height(8.dp))
                Text("1개월 뒤 가장 가능성 높은 종가 수익률 구간", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                m.terminalReturnTop3.take(3).forEachIndexed { index, rank ->
                    Text(
                        "${index + 1}위  ${rank.label}  ·  확률 ${kPct1(rank.probability)}",
                        style = if (index == 0) MaterialTheme.typography.titleMedium else MaterialTheme.typography.bodyLarge,
                        fontWeight = if (index == 0) FontWeight.Bold else FontWeight.SemiBold
                    )
                }
                val widthText = if (m.terminalReturnBinWidthPercent > 0) "${m.terminalReturnBinWidthPercent}%p 구간" else "수익률 구간"
                Text("21거래일 뒤 종가 기준 · $widthText 확률 순위", style = MaterialTheme.typography.bodySmall)
            }

            val basis = if (m.priceBasis == "daily_high_low") "장중 고가·저가 터치 기준" else "종가 터치 기준"
            Text("${m.asOf} 종가 기준 · $basis", style = MaterialTheme.typography.bodySmall)
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
                Text("장기 기본빈도: +10% ${kPct1(m.baselineUp10Probability)} / -10% ${kPct1(m.baselineDown10Probability)} · 완료표본 ${m.baselineSampleSize}회", style = MaterialTheme.typography.bodySmall)
                kospiValidationLine("+10%", m.selectionUp, m.validationUp)
                kospiValidationLine("-10%", m.selectionDown, m.validationDown)
                if (m.terminalReturnTop3.isNotEmpty()) {
                    Spacer(Modifier.height(6.dp))
                    Text("[1개월 종가 수익률 분포]", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.bodyMedium)
                    m.terminalReturnTop3.take(3).forEachIndexed { index, rank ->
                        Text("${index + 1}위 ${rank.label} · ${kPct1(rank.probability)}", style = MaterialTheme.typography.bodySmall)
                    }
                    kospiValidationLine("종가분포", m.terminalReturnSelection ?: "baseline", m.terminalReturnValidation)
                }
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
