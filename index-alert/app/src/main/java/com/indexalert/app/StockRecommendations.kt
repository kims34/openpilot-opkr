package com.indexalert.app

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.Locale

private data class StockSixBin(
    val key: String,
    val label: String,
    val probability: Double
)

private data class StockPick(
    val rank: Int,
    val symbol: String,
    val name: String,
    val probability: Double,
    val baseRate: Double,
    val asOf: String,
    val targetDate: String,
    val current: Double?,
    val dayChange: Double?,
    val dayChangePercent: Double?,
    val sp500: Boolean,
    val nasdaq100: Boolean,
    val schd: Boolean,
    val reliability: String,
    val strategy: String,
    val sixBins: List<StockSixBin>
)

private data class StockPickFeed(
    val status: String,
    val coverage: String,
    val items: List<StockPick>,
    val note: String
)

private object StockRecommendationRepository {
    private var lastFetch = 0L
    private var cache: StockPickFeed? = null

    @Synchronized
    fun get(): StockPickFeed? {
        val now = System.currentTimeMillis()
        if (now - lastFetch < 60_000L && cache != null) return cache
        val base = BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/')
        val c = URL("$base/stock-recommendations").openConnection() as HttpURLConnection
        c.connectTimeout = 6000
        c.readTimeout = 12000
        c.setRequestProperty("Accept", "application/json")
        val raw = try {
            check(c.responseCode in 200..299)
            c.inputStream.bufferedReader().use { it.readText() }
        } finally {
            c.disconnect()
        }
        val root = JSONObject(raw)
        val arr = root.optJSONArray("items")
        val out = mutableListOf<StockPick>()
        if (arr != null) {
            for (i in 0 until minOf(3, arr.length())) {
                val o = arr.optJSONObject(i) ?: continue
                val probability = o.optDouble("probability", Double.NaN)
                val baseRate = o.optDouble("base_rate", Double.NaN)
                if (!probability.isFinite() || probability !in 0.0..100.0 || !baseRate.isFinite()) continue
                val month = o.optJSONObject("one_month")
                val binsArray = month?.optJSONArray("terminal_return_six_bins")
                val bins = mutableListOf<StockSixBin>()
                if (binsArray != null) {
                    for (j in 0 until binsArray.length()) {
                        val b = binsArray.optJSONObject(j) ?: continue
                        val p = b.optDouble("probability", Double.NaN)
                        if (p.isFinite() && p in 0.0..100.0) {
                            bins.add(StockSixBin(b.optString("key"), b.optString("label"), p))
                        }
                    }
                }
                val expected = listOf("up10_plus", "up5_10", "up0_5", "down0_5", "down5_10", "down10_minus")
                if (bins.size != 6 || bins.map { it.key } != expected || kotlin.math.abs(bins.sumOf { it.probability } - 100.0) > 0.2) continue
                out.add(
                    StockPick(
                        rank = o.optInt("rank", i + 1),
                        symbol = o.optString("symbol"),
                        name = o.optString("name"),
                        probability = probability,
                        baseRate = baseRate,
                        asOf = o.optString("as_of"),
                        targetDate = o.optString("target_date"),
                        current = o.numberOrNull("current"),
                        dayChange = o.numberOrNull("day_change"),
                        dayChangePercent = o.numberOrNull("day_change_percent"),
                        sp500 = o.optBoolean("sp500", false),
                        nasdaq100 = o.optBoolean("nasdaq100", false),
                        schd = o.optBoolean("schd", false),
                        reliability = o.optString("reliability"),
                        strategy = o.optString("current_strategy"),
                        sixBins = bins
                    )
                )
            }
        }
        return StockPickFeed(
            status = root.optString("status", "building"),
            coverage = root.optString("coverage", "0/0"),
            items = out.sortedBy { it.rank },
            note = root.optString("note", "통계 모델 순위이며 매수·수익을 보장하지 않습니다.")
        ).also {
            cache = it
            lastFetch = now
        }
    }

    private fun JSONObject.numberOrNull(key: String): Double? {
        if (!has(key) || isNull(key)) return null
        return optDouble(key, Double.NaN).takeIf { it.isFinite() }
    }
}

@Composable
fun StockRecommendationSection(refreshKey: String = "") {
    var feed by remember { mutableStateOf<StockPickFeed?>(null) }
    var checked by remember { mutableStateOf(false) }

    LaunchedEffect(refreshKey) {
        while (true) {
            feed = withContext(Dispatchers.IO) { runCatching { StockRecommendationRepository.get() }.getOrNull() }
            checked = true
            delay(60_000L)
        }
    }

    Spacer(Modifier.height(18.dp))
    Text("개별종목 다음 거래일 상승확률 TOP3", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
    Text("S&P500 · NASDAQ100 · SCHD 구성종목 통합 · 중복 종목은 1개로 계산", style = MaterialTheme.typography.bodySmall)
    Spacer(Modifier.height(6.dp))

    val f = feed
    if (f == null || f.items.isEmpty()) {
        Card(
            Modifier.fillMaxWidth(),
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
        ) {
            Column(Modifier.padding(12.dp)) {
                Text(if (checked) "TOP3 계산 중" else "종목 확률 계산 확인 중…", fontWeight = FontWeight.Bold)
                Text("서버가 전체 구성종목의 완료 종가를 검증한 뒤 순위를 만듭니다.", style = MaterialTheme.typography.bodySmall)
                f?.let { Text("상태 ${it.status} · 분석 커버리지 ${it.coverage}", style = MaterialTheme.typography.labelSmall) }
            }
        }
        return
    }

    f.items.forEach { item ->
        StockRecommendationCard(item)
    }
    Text("분석 커버리지 ${f.coverage} · ${f.note}", style = MaterialTheme.typography.labelSmall, modifier = Modifier.padding(top = 4.dp))
}

@Composable
private fun StockRecommendationCard(item: StockPick) {
    Card(
        Modifier.fillMaxWidth().padding(vertical = 5.dp),
        border = BorderStroke(1.5.dp, MaterialTheme.colorScheme.outline),
        shape = RoundedCornerShape(8.dp)
    ) {
        Column(Modifier.padding(14.dp)) {
            Text("${item.rank}. ${item.symbol} · ${item.name}", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            Text(
                "다음 거래일 종가 상승 추정  ${stockPct(item.probability)}",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            Text("${item.asOf} 종가 기준 → ${item.targetDate} 종가", style = MaterialTheme.typography.bodySmall)

            if (item.current != null) {
                val change = if (item.dayChange != null && item.dayChangePercent != null) {
                    "  ${stockSigned(item.dayChange)} (${stockSignedPct(item.dayChangePercent)})"
                } else ""
                Text("현재 ${stockFmt(item.current)}$change", style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.SemiBold)
            }

            val memberships = buildList {
                if (item.sp500) add("S&P500")
                if (item.nasdaq100) add("NASDAQ100")
                if (item.schd) add("SCHD")
            }.joinToString(" · ")
            Text("포함: ${memberships.ifBlank { "-" }}", style = MaterialTheme.typography.bodySmall)
            Text(
                if (item.strategy == "fixed") "검증 우위 미확인 · 기본 상승률 ${stockPct(item.baseRate)} 사용"
                else "검증된 조건모델 사용 · 기본 상승률 ${stockPct(item.baseRate)}",
                style = MaterialTheme.typography.bodySmall
            )

            HorizontalDivider(Modifier.padding(vertical = 8.dp))
            Text("향후 1개월(21거래일) 6구간", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            item.sixBins.forEach { bin ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(bin.label, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.SemiBold)
                    Text(stockPct1(bin.probability), style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold)
                }
            }
            Text("서로 겹치지 않는 6구간 · 합계 ${stockPct1(item.sixBins.sumOf { it.probability })}", style = MaterialTheme.typography.labelSmall, modifier = Modifier.padding(top = 3.dp))
        }
    }
}

private fun stockFmt(v: Double): String = String.format(Locale.US, "%,.2f", v)
private fun stockPct(v: Double): String = String.format(Locale.US, "%.1f%%", v)
private fun stockPct1(v: Double): String = String.format(Locale.US, "%.1f%%", v)
private fun stockSigned(v: Double): String = String.format(Locale.US, "%+,.2f", v)
private fun stockSignedPct(v: Double): String = String.format(Locale.US, "%+.2f%%", v)
