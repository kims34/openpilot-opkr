package com.indexalert.app

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
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


data class MarketBriefing(
    val id: String,
    val category: String,
    val text: String,
    val confidence: String
)

object MarketBriefingRepository {
    private var cachedAt = 0L
    private var cache: Map<String, MarketBriefing> = emptyMap()
    private const val CACHE_MS = 5 * 60 * 1000L

    @Synchronized
    fun get(indexId: String): MarketBriefing? {
        val now = System.currentTimeMillis()
        if (cache.isNotEmpty() && now - cachedAt < CACHE_MS) return cache[indexId]

        return runCatching {
            val base = BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/')
            val connection = URL("$base/briefings").openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.connectTimeout = 10000
            connection.readTimeout = 15000
            connection.setRequestProperty("Accept", "application/json")
            val text = connection.inputStream.bufferedReader().use { it.readText() }
            connection.disconnect()

            val root = JSONObject(text)
            val arr = root.optJSONArray("items")
            val parsed = mutableMapOf<String, MarketBriefing>()
            if (arr != null) {
                for (i in 0 until arr.length()) {
                    val o = arr.getJSONObject(i)
                    val id = o.optString("id")
                    if (id.isBlank()) continue
                    parsed[id] = MarketBriefing(
                        id = id,
                        category = o.optString("category", "혼합"),
                        text = o.optString("text", "원인 브리핑을 준비 중입니다."),
                        confidence = o.optString("confidence", "뉴스·시세 기반 추정")
                    )
                }
            }
            cache = parsed
            cachedAt = now
            parsed[indexId]
        }.getOrNull()
    }
}

@Composable
fun MarketBriefingSection(indexId: String) {
    var briefing by remember(indexId) { mutableStateOf<MarketBriefing?>(null) }

    LaunchedEffect(indexId) {
        briefing = withContext(Dispatchers.IO) { MarketBriefingRepository.get(indexId) }
    }

    val item = briefing ?: return
    Spacer(Modifier.height(10.dp))
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.small,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        color = MaterialTheme.colorScheme.surfaceVariant
    ) {
        Column(Modifier.padding(10.dp)) {
            Text(
                "오늘 한줄 브리핑 · ${item.category}",
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.Bold
            )
            Text(
                item.text,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 3.dp)
            )
            Text(
                item.confidence,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(top = 3.dp)
            )
        }
    }
}
