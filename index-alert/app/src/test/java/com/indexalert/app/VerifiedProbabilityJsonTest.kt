package com.indexalert.app

import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test

class VerifiedProbabilityJsonTest {
    @Test fun modelNameAndHistoricalSkillAreNotDisplayEvidence() {
        val legacy = JSONObject().put("model_version", "3.3-calibration-gated")
            .put("probability", 75).put("backtest_skill", 20)
        assertFalse(legacy.independentDisplayAllowed(100))
    }
    @Test fun stringBooleanAndMissingEvidenceAreRejected() {
        val value = JSONObject().put("display_policy_version", "verified-only-v1")
            .put("display_allowed", "true").put("verification_status", "independent_confirmed")
            .put("verification_evidence_id", "proof").put("verification_expires_at", 200)
        assertFalse(value.independentDisplayAllowed(100))
        value.put("display_allowed", true).put("verification_evidence_id", "")
        assertFalse(value.independentDisplayAllowed(100))
    }
    @Test fun expiredServerAdmissionCannotResurfaceFromSavedJson() {
        val value = JSONObject().put("display_policy_version", "verified-only-v1")
            .put("display_allowed", true).put("verification_status", "independent_confirmed")
            .put("verification_evidence_id", "proof").put("verification_expires_at", 200)
        assertTrue(value.independentDisplayAllowed(100))
        assertFalse(value.independentDisplayAllowed(200))
    }
}
