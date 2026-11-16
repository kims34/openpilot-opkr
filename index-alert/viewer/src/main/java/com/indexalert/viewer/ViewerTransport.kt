package com.indexalert.viewer

import java.net.HttpURLConnection
import java.net.URL
import org.json.JSONObject

object ViewerTransport {
    val allowedPaths = setOf("/status", "/next-day-probabilities", "/one-month-probabilities", "/monthly-prospective-scores")

    fun read(path: String): JSONObject {
        require(path in allowedPaths)
        val c = URL(BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/') + path).openConnection() as HttpURLConnection
        c.requestMethod = "GET"
        c.instanceFollowRedirects = false
        c.connectTimeout = 8000
        c.readTimeout = 15000
        c.setRequestProperty("Accept", "application/json")
        return try {
            check(c.responseCode == 200)
            val text = c.inputStream.bufferedReader().use { reader ->
                val out = StringBuilder()
                val buffer = CharArray(4096)
                while (true) {
                    val count = reader.read(buffer)
                    if (count < 0) break
                    check(out.length + count <= 1_000_000)
                    out.append(buffer, 0, count)
                }
                out.toString()
            }
            JSONObject(text)
        } finally { c.disconnect() }
    }
}
