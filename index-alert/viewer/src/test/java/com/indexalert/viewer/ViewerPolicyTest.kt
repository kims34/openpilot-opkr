package com.indexalert.viewer

import org.json.JSONObject
import org.json.JSONArray
import org.junit.Assert.*
import org.junit.Test

class ViewerPolicyTest {
    private fun quarterProof() = historical()
        .put("display_policy_version", "backtested-quarterly-v1")
        .put("verification_evidence_id", "quarterly-touch-history-v1-20261116:SPY:up5_touch")
        .put("model_version", "quarterly-volatility-scaled-touch-v1")
        .put("model_sha256", "94de4a9c927f03b600c5155782902f71c3ce9120c6cf42839eac229c63886276")
        .put("event", "up5_touch").put("horizon_sessions", 63)
    @Test fun quarterlyRequiresItsOwnHorizonEventAndEvidence() {
        val f=quarterProof()
        assertNotNull(ViewerPolicy.quarterly(f, 100))
        assertNull(ViewerPolicy.backtested(JSONObject().put("backtested_forecast",f), "SPY",100))
        assertNull(ViewerPolicy.quarterly(f.put("horizon_sessions",21),100))
        assertNull(ViewerPolicy.quarterly(quarterProof().put("event","up10_touch"),100))
        assertNull(ViewerPolicy.quarterly(quarterProof().put("symbol","QQQ"),100))
        assertNull(ViewerPolicy.quarterly(quarterProof(),200))
    }
    private fun historical() = JSONObject().put("display_policy_version", "backtested-touch-v1")
        .put("display_allowed", true).put("independent_confirmed", false)
        .put("verification_status", "historical_backtest_passed")
        .put("verification_evidence_id", "five-percent-historical-v1-20261116:SPY")
        .put("model_version", "volatility-scaled-5pct-touch-shadow-v1")
        .put("model_sha256", "2b0f049d9258a5e8d569b8d46a7d40ca1ce50ce09a9fcb559cbea7bd0547b581")
        .put("symbol", "SPY").put("event", "down5_touch").put("horizon_sessions", 21)
        .put("threshold_percent", 5).put("valid_until", 200).put("as_of", "2026-11-13")
        .put("target_date", "2026-12-15").put("evidence", JSONObject()).put("probability", 23)
    @Test fun historicalAdmissionStaysSeparateFromIndependentEvidence() {
        val f=historical()
        assertNotNull(ViewerPolicy.backtested(JSONObject().put("backtested_forecast", f), "SPY", 100))
        assertTrue(ViewerPolicy.forecasts(node(f), "SPY", 100).isEmpty())
    }
    @Test fun historicalAdmissionRejectsWrongEventExpiredAndUnknownSymbol() {
        val n=JSONObject().put("backtested_forecast", historical())
        assertNull(ViewerPolicy.backtested(n, "SPY", 200))
        assertNull(ViewerPolicy.backtested(n, "QQQ", 100))
        assertNull(ViewerPolicy.backtested(n, "SCHD", 100))
        n.getJSONObject("backtested_forecast").put("event", "up5_touch")
        assertNull(ViewerPolicy.backtested(n, "SPY", 100))
    }
    private fun proof() = JSONObject().put("display_policy_version", "verified-only-v1")
        .put("display_allowed", true).put("verification_status", "independent_confirmed")
        .put("verification_evidence_id", "evidence").put("verification_expires_at", 200)
        .put("symbol", "SPY").put("model_version", "model").put("event", "up")
        .put("target_date", "2026-11-17").put("horizon_sessions", 1).put("probability", 60)
    private fun node(f: JSONObject) = JSONObject().put("verified_forecasts", JSONArray().put(f))
    @Test fun legacyCachedNumbersAreNeverDisplayed() {
        assertTrue(ViewerPolicy.forecasts(JSONObject().put("probability", 55).put("base_rate", 50), "SPY", 100).isEmpty())
    }
    @Test fun approvalCannotBeInheritedOrReusedForAnotherSymbol() {
        assertTrue(ViewerPolicy.forecasts(node(proof()), "QQQ", 100).isEmpty())
        assertTrue(ViewerPolicy.forecasts(node(proof().put("display_allowed", "true")), "SPY", 100).isEmpty())
    }
    @Test fun expiredOrMissingEvidenceIsNotDisplayed() {
        assertTrue(ViewerPolicy.forecasts(node(proof()), "SPY", 200).isEmpty())
        assertTrue(ViewerPolicy.forecasts(node(proof().put("verification_evidence_id", "")), "SPY", 100).isEmpty())
    }
    @Test fun onlyBoundValidEvidenceDisplaysAPercentage() {
        assertEquals(60.0, ViewerPolicy.forecasts(node(proof()), "SPY", 100).single().probability, 0.0)
        assertTrue(ViewerPolicy.forecasts(node(proof().put("probability", 101)), "SPY", 100).isEmpty())
    }
}
