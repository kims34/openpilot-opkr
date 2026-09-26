package com.indexalert.app

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.Locale


data class NextDayEstimate(
    val probability: Double,
    val sampleSize: Int,
    val baseRate: Double,
    val method: String
)

object NextDayProbabilityRepository {
    private var cachedAt = 0L
    private var cache: Map<String, NextDayEstimate> = emptyMap()
    private const val CACHE_MS = 15 * 60 * 1000L

    @Synchronized
    fun get(indexId: String): NextDayEstimate? {
        val now = System.currentTimeMillis()
        if (cache.isNotEmpty() && now - cachedAt < CACHE_MS) return cache[indexId]

        return runCatching {
            val base = BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/')
            val c = URL("$base/next-day-probabilities").openConnection() as HttpURLConnection
            c.requestMethod = "GET"
            c.connectTimeout = 10000
            c.readTimeout = 20000
            c.setRequestProperty("Accept", "application/json")
            if (c.responseCode !in 200..299) {
                val code = c.responseCode
                c.disconnect()
                throw IllegalStateException("확률 서버 오류 $code")
            }
            val text = c.inputStream.bufferedReader().use { it.readText() }
            c.disconnect()

            val root = JSONObject(text).optJSONObject("items") ?: JSONObject()
            val parsed = mutableMapOf<String, NextDayEstimate>()
            listOf("sp500", "ndx", "djdiv").forEach { id ->
                val o = root.optJSONObject(id) ?: return@forEach
                if (o.has("error")) return@forEach
                val probability = o.optDouble("probability", Double.NaN)
                if (!probability.isFinite()) return@forEach
                parsed[id] = NextDayEstimate(
                    probability = probability,
                    sampleSize = o.optInt("sample_size", 0),
                    baseRate = o.optDouble("base_rate", Double.NaN),
                    method = o.optString("method", "최근 10년 유사 흐름 통계")
                )
            }
            cache = parsed
            cachedAt = now
            parsed[indexId]
        }.getOrNull()
    }
}

@Composable
fun NextDayProbabilitySection(indexId: String) {
    if (indexId !in setOf("sp500", "ndx", "djdiv")) return

    var estimate by remember(indexId) { mutableStateOf<NextDayEstimate?>(null) }
    LaunchedEffect(indexId) {
        estimate = withContext(Dispatchers.IO) { NextDayProbabilityRepository.get(indexId) }
    }

    val e = estimate ?: return
    Spacer(Modifier.height(10.dp))
    Card(
        modifier = Modifier.fillMaxWidth(),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(Modifier.padding(12.dp)) {
            Text(
                "다음 거래일 상승 추정  ${String.format(Locale.US, "%.0f%%", e.probability)}",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            Text(
                "최근 10년 유사 흐름 표본 ${e.sampleSize}회 · 통계적 추정",
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 3.dp)
            )
            Text(
                "다음 정규장 종가가 직전 정규장 종가보다 높을 확률을 과거 유사 흐름으로 계산한 값이며 보장된 예측이 아닙니다.",
                style = MaterialTheme.typography.labelSmall,
                modifier = Modifier.padding(top = 4.dp)
            )
        }
    }
}
