package com.indexalert.app

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import kotlin.math.max


data class WeeklyPoint(val ts: Long, val value: Double)

data class WeeklyHistory(
    val points: List<WeeklyPoint>,
    val min: Double,
    val max: Double,
    val changePercent: Double,
    val source: String
)

fun BackendMarket.weekHistory(indexId: String): WeeklyHistory {
    val base = BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/')
    val c = URL("$base/history/$indexId").openConnection() as HttpURLConnection
    c.requestMethod = "GET"
    c.connectTimeout = 10000
    c.readTimeout = 15000
    c.setRequestProperty("Accept", "application/json")
    if (c.responseCode !in 200..299) {
        val code = c.responseCode
        c.disconnect()
        throw IllegalStateException("1주 차트 서버 오류 $code")
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
            if (ts > 0 && value.isFinite() && value > 0) add(WeeklyPoint(ts, value))
        }
    }
    if (points.size < 2) throw IllegalStateException("차트 데이터 부족")
    return WeeklyHistory(
        points = points,
        min = root.optDouble("min", points.minOf { it.value }),
        max = root.optDouble("max", points.maxOf { it.value }),
        changePercent = root.optDouble("change_percent", 0.0),
        source = root.optString("source", "1주 시세")
    )
}

@Composable
fun WeeklyChartSection(indexId: String) {
    var expanded by remember(indexId) { mutableStateOf(false) }
    var loading by remember(indexId) { mutableStateOf(false) }
    var history by remember(indexId) { mutableStateOf<WeeklyHistory?>(null) }
    var error by remember(indexId) { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()

    Spacer(Modifier.height(8.dp))
    OutlinedButton(
        onClick = {
            expanded = !expanded
            if (expanded && history == null && !loading) {
                loading = true
                error = null
                scope.launch {
                    val result = withContext(Dispatchers.IO) {
                        runCatching { BackendMarket.weekHistory(indexId) }
                    }
                    result.onSuccess { history = it }
                        .onFailure { error = it.message ?: "1주 차트 조회 실패" }
                    loading = false
                }
            }
        },
        modifier = Modifier.fillMaxWidth()
    ) {
        Text(if (expanded) "1주 차트 ▲ 접기" else "1주 차트 ▼ 보기")
    }

    if (!expanded) return
    Spacer(Modifier.height(8.dp))

    when {
        loading -> LinearProgressIndicator(Modifier.fillMaxWidth())
        error != null -> Text("차트 확인 실패: $error", style = MaterialTheme.typography.bodySmall)
        history != null -> WeeklyLineChart(history!!)
    }
}

@Composable
private fun WeeklyLineChart(history: WeeklyHistory) {
    val lineColor = MaterialTheme.colorScheme.primary
    val gridColor = MaterialTheme.colorScheme.outlineVariant
    val values = history.points.map { it.value }
    val low = values.minOrNull() ?: 0.0
    val high = values.maxOrNull() ?: low
    val span = max(high - low, max(high * 0.002, 0.01))

    Canvas(
        Modifier
            .fillMaxWidth()
            .height(140.dp)
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

    val df = remember { SimpleDateFormat("MM/dd", Locale.KOREA) }
    val firstDate = df.format(Date(history.points.first().ts * 1000L))
    val lastDate = df.format(Date(history.points.last().ts * 1000L))
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(firstDate, style = MaterialTheme.typography.labelSmall)
        Text(lastDate, style = MaterialTheme.typography.labelSmall)
    }
    Text(
        "1주 최저 ${fmtWeekly(history.min)} · 최고 ${fmtWeekly(history.max)} · ${signedPctWeekly(history.changePercent)}",
        style = MaterialTheme.typography.bodySmall
    )
    Text("차트 기준: ${history.source}", style = MaterialTheme.typography.labelSmall)
}

private fun fmtWeekly(v: Double): String = String.format(Locale.US, "%,.2f", v)
private fun signedPctWeekly(v: Double): String = String.format(Locale.US, "%+.2f%%", v)
