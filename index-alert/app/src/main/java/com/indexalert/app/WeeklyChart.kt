package com.indexalert.app

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import kotlin.math.max

private val MonthlyMetricBlue = Color(0xFF1565C0)

data class MonthlyPoint(val ts: Long, val value: Double)

data class MonthlyHistory(
    val points: List<MonthlyPoint>,
    val min: Double,
    val minTs: Long,
    val max: Double,
    val maxTs: Long,
    val current: Double,
    val fromHighPercent: Double,
    val source: String
)

fun BackendMarket.monthHistory(indexId: String): MonthlyHistory {
    val base = BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/')
    val c = URL("$base/history/$indexId").openConnection() as HttpURLConnection
    c.requestMethod = "GET"
    c.connectTimeout = 10000
    c.readTimeout = 15000
    c.setRequestProperty("Accept", "application/json")
    if (c.responseCode !in 200..299) {
        val code = c.responseCode
        c.disconnect()
        throw IllegalStateException("1개월 차트 서버 오류 $code")
    }
    val text = c.inputStream.bufferedReader().use { it.readText() }
    c.disconnect()

    val root = JSONObject(text)
    val arr = root.getJSONArray("points")
    val points = buildList {
        for (i in 0 until arr.length()) {
            val o = arr.getJSONObject(i)
            val ts = o.optLong("ts", 0L)
            val value = o.optDouble("value", Double.NaN)
            if (ts > 0 && value.isFinite() && value > 0) add(MonthlyPoint(ts, value))
        }
    }
    if (points.size < 2) throw IllegalStateException("차트 데이터 부족")

    val maxValue = root.optDouble("max", points.maxOf { it.value })
    val minValue = root.optDouble("min", points.minOf { it.value })
    val current = root.optDouble("current", points.last().value)
    val fromHigh = root.optDouble(
        "from_high_percent",
        if (maxValue > 0) (current / maxValue - 1.0) * 100.0 else 0.0
    )

    return MonthlyHistory(
        points = points,
        min = minValue,
        minTs = root.optLong("min_ts", points.minByOrNull { it.value }?.ts ?: 0L),
        max = maxValue,
        maxTs = root.optLong("max_ts", points.maxByOrNull { it.value }?.ts ?: 0L),
        current = current,
        fromHighPercent = fromHigh,
        source = root.optString("source", "최근 1개월 일봉")
    )
}

@Composable
fun MonthlyChartSection(indexId: String) {
    var loading by remember(indexId) { mutableStateOf(true) }
    var history by remember(indexId) { mutableStateOf<MonthlyHistory?>(null) }
    var error by remember(indexId) { mutableStateOf<String?>(null) }

    LaunchedEffect(indexId) {
        loading = true
        error = null
        val result = withContext(Dispatchers.IO) {
            runCatching { BackendMarket.monthHistory(indexId) }
        }
        result.onSuccess { history = it }
            .onFailure { error = it.message ?: "1개월 차트 조회 실패" }
        loading = false
    }

    Spacer(Modifier.height(10.dp))
    Text("최근 1개월 · 일봉", style = MaterialTheme.typography.titleSmall)
    Spacer(Modifier.height(6.dp))

    when {
        loading -> LinearProgressIndicator(Modifier.fillMaxWidth())
        error != null -> Text("차트 확인 실패: $error", style = MaterialTheme.typography.bodySmall)
        history != null -> MonthlyLineChart(history!!)
    }
}

@Composable
private fun MonthlyLineChart(history: MonthlyHistory) {
    val lineColor = MaterialTheme.colorScheme.primary
    val gridColor = MaterialTheme.colorScheme.outlineVariant
    val values = history.points.map { it.value }
    val low = values.minOrNull() ?: 0.0
    val high = values.maxOrNull() ?: low
    val span = max(high - low, max(high * 0.002, 0.01))
    val df = remember { SimpleDateFormat("MM/dd", Locale.KOREA) }

    val highDate = if (history.maxTs > 0) df.format(Date(history.maxTs * 1000L)) else "-"
    val lowDate = if (history.minTs > 0) df.format(Date(history.minTs * 1000L)) else "-"

    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text("최고 ${fmtMonthly(history.max)} · $highDate", style = MaterialTheme.typography.bodySmall)
        Text("최저 ${fmtMonthly(history.min)} · $lowDate", style = MaterialTheme.typography.bodySmall)
    }

    Canvas(
        Modifier
            .fillMaxWidth()
            .height(160.dp)
            .padding(vertical = 8.dp)
    ) {
        drawLine(gridColor, Offset(0f, size.height * 0.25f), Offset(size.width, size.height * 0.25f), 1f)
        drawLine(gridColor, Offset(0f, size.height * 0.5f), Offset(size.width, size.height * 0.5f), 1f)
        drawLine(gridColor, Offset(0f, size.height * 0.75f), Offset(size.width, size.height * 0.75f), 1f)

        val count = history.points.size
        history.points.zipWithNext().forEachIndexed { i, pair ->
            val a = pair.first
            val b = pair.second
            val x1 = if (count <= 1) 0f else size.width * i / (count - 1).toFloat()
            val x2 = if (count <= 1) size.width else size.width * (i + 1) / (count - 1).toFloat()
            val y1 = size.height - ((a.value - low) / span).toFloat() * size.height
            val y2 = size.height - ((b.value - low) / span).toFloat() * size.height
            drawLine(lineColor, Offset(x1, y1), Offset(x2, y2), strokeWidth = 4f)
        }
    }

    val firstDate = df.format(Date(history.points.first().ts * 1000L))
    val lastDate = df.format(Date(history.points.last().ts * 1000L))
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(firstDate, style = MaterialTheme.typography.labelSmall)
        Text(lastDate, style = MaterialTheme.typography.labelSmall)
    }

    Text("현재 ${fmtMonthly(history.current)}", style = MaterialTheme.typography.bodyMedium)
    Text(
        "1개월 최고가 대비 등락률 ${signedPctMonthly(history.fromHighPercent)}",
        color = MonthlyMetricBlue,
        fontWeight = FontWeight.Bold,
        style = MaterialTheme.typography.titleSmall
    )
    Text("차트 기준: ${history.source}", style = MaterialTheme.typography.labelSmall)
}

private fun fmtMonthly(v: Double): String = String.format(Locale.US, "%,.2f", v)
private fun signedPctMonthly(v: Double): String = String.format(Locale.US, "%+.2f%%", v)
