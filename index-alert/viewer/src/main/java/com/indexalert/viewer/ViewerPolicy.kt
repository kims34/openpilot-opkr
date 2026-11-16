package com.indexalert.viewer

import org.json.JSONObject

data class VerifiedForecast(val label: String, val probability: Double)

object ViewerPolicy {
    fun backtested(node: JSONObject?, symbol: String, now: Long): JSONObject? {
        val f = node?.optJSONObject("backtested_forecast") ?: return null
        val event = mapOf("SPY" to "down5_touch", "QQQ" to "up5_touch")[symbol] ?: return null
        val p = f.optDouble("probability", Double.NaN)
        if (f.optString("display_policy_version") != "backtested-touch-v1" ||
            f.opt("display_allowed") != true || f.opt("independent_confirmed") != false ||
            f.optString("verification_status") != "historical_backtest_passed" ||
            f.optString("verification_evidence_id") != "five-percent-historical-v1-20261116:$symbol" ||
            f.optString("model_version") != "volatility-scaled-5pct-touch-shadow-v1" ||
            f.optString("model_sha256") != "2b0f049d9258a5e8d569b8d46a7d40ca1ce50ce09a9fcb559cbea7bd0547b581" ||
            f.optString("symbol") != symbol || f.optString("event") != event ||
            f.optInt("horizon_sessions") != 21 || f.optInt("threshold_percent") != 5 ||
            f.optLong("valid_until") <= now || f.optString("as_of").isBlank() ||
            f.optString("target_date").isBlank() || f.optJSONObject("evidence") == null ||
            !p.isFinite() || p !in 0.0..100.0) return null
        return f
    }
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
