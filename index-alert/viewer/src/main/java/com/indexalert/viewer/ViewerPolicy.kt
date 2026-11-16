package com.indexalert.viewer

import org.json.JSONObject

data class VerifiedForecast(val label: String, val probability: Double)

object ViewerPolicy {
    const val VERSION = "verified-only-v1"
    val symbols = mapOf("sp500" to "SPY", "ndx" to "QQQ", "djdiv" to "SCHD", "kospi100" to "^KS11")

    fun forecasts(node: JSONObject?, expectedSymbol: String, now: Long): List<VerifiedForecast> {
        val array = node?.optJSONArray("verified_forecasts") ?: return emptyList()
        return buildList {
            for (i in 0 until array.length()) {
                val f = array.optJSONObject(i) ?: continue
                val p = f.optDouble("probability", Double.NaN)
                if (f.optString("display_policy_version") != VERSION || f.opt("display_allowed") != true ||
                    f.optString("verification_status") != "independent_confirmed" ||
                    f.optString("verification_evidence_id").isBlank() ||
                    f.optLong("verification_expires_at", 0) <= now ||
                    f.optString("symbol") != expectedSymbol || f.optString("model_version").isBlank() ||
                    f.optString("target_date").isBlank() || f.optString("event").isBlank() ||
                    f.optInt("horizon_sessions", 0) < 1 || !p.isFinite() || p !in 0.0..100.0) continue
                add(VerifiedForecast(f.optString("label", f.optString("event")), p))
            }
        }
    }
}
