package com.indexalert.viewer

import org.json.JSONObject

data class VerifiedForecast(val label: String, val probability: Double)

object ViewerPolicy {
    fun historical(node: JSONObject?, now: Long): List<JSONObject> {
        val array=node?.optJSONArray("historical_forecasts") ?: return emptyList()
        val seen=mutableSetOf<String>()
        return buildList {
            for (i in 0 until array.length()) {
                val f=array.optJSONObject(i) ?: continue
                val symbol=f.optString("symbol");val h=f.optInt("horizon_sessions")
                val threshold=f.optInt("threshold_percent");val direction=f.optString("direction")
                val event="$h:$direction${threshold}_touch";val p=f.optDouble("probability",Double.NaN)
                val evidence=f.optJSONObject("evidence") ?: continue
                val accuracy=evidence.optDouble("accuracy_pct",Double.NaN)
                if (symbol !in listOf("SPY","QQQ","SCHD") || h !in listOf(21,63) ||
                    threshold !in listOf(5,10) || direction !in listOf("up","down") ||
                    f.optString("event") != event ||
                    f.optString("display_policy_version") != "historical-estimates-v1" ||
                    f.opt("display_allowed") != true || f.opt("independent_confirmed") != false ||
                    f.optString("verification_status") != "historical_estimate" ||
                    f.optString("verification_evidence_id") != "all-touch-history-v1-20261116:$symbol:$event" ||
                    f.optString("model_version") != "historical-volatility-touch-all-v1" ||
                    f.optString("model_sha256") != "35d5657d55d54360a1e82cf90dab051070f3b50ee91437e0133773b4a741cda1" ||
                    f.optLong("valid_until") <= now || f.optString("as_of").isBlank() ||
                    f.optString("target_date").isBlank() || !p.isFinite() || p !in 0.0..100.0 ||
                    !accuracy.isFinite() || accuracy !in 0.0..100.0 || evidence.optInt("samples") < 1 ||
                    evidence.optString("symbol") != symbol || evidence.optString("event") != event) continue
                if (seen.add("$symbol:$event")) add(f)
            }
        }
    }
    fun quarterly(f: JSONObject?, now: Long): JSONObject? {
        f ?: return null
        val p=f.optDouble("probability", Double.NaN)
        if (f.optString("display_policy_version") != "backtested-quarterly-v1" ||
            f.opt("display_allowed") != true || f.opt("independent_confirmed") != false ||
            f.optString("verification_status") != "historical_backtest_passed" ||
            f.optString("verification_evidence_id") != "quarterly-touch-history-v1-20261116:SPY:up5_touch" ||
            f.optString("model_version") != "quarterly-volatility-scaled-touch-v1" ||
            f.optString("model_sha256") != "94de4a9c927f03b600c5155782902f71c3ce9120c6cf42839eac229c63886276" ||
            f.optString("symbol") != "SPY" || f.optString("event") != "up5_touch" ||
            f.optInt("horizon_sessions") != 63 || f.optInt("threshold_percent") != 5 ||
            f.optLong("valid_until") <= now || f.optString("as_of").isBlank() ||
            f.optString("target_date").isBlank() || f.optJSONObject("evidence") == null ||
            !p.isFinite() || p !in 0.0..100.0) return null
        return f
    }
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
