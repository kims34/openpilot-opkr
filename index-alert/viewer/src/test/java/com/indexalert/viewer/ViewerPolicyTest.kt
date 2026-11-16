package com.indexalert.viewer

import org.json.JSONObject
import org.json.JSONArray
import org.junit.Assert.*
import org.junit.Test

class ViewerPolicyTest {
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
