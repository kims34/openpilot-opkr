package com.indexalert.app

import org.junit.Assert.*
import org.junit.Test

class ProbabilityDisplayContractTest {
    @Test fun freshVerificationRefusalRevokesPreviouslySavedForecast() {
        assertNull(ProbabilityDisplayContract.resolve<String>(true, null, "old-probability"))
        assertEquals(emptyMap<String, Int>(), ProbabilityDisplayContract.resolve(true, emptyMap<String, Int>(), mapOf("SPY" to 60)))
        assertEquals("verified-saved", ProbabilityDisplayContract.resolve<String>(false, null, "verified-saved"))
    }

    @Test fun legacyHistoricalModelHasNoDisplayPermission() {
        assertFalse(ProbabilityDisplayContract.allows("", true, "historical_only", "", 200, 100))
    }
    @Test fun defaultOrHistoricalFallbackIsNotIndependentConfirmation() {
        assertFalse(ProbabilityDisplayContract.allows("verified-only-v1", true, "fallback_inconclusive", "proof", 200, 100))
        assertFalse(ProbabilityDisplayContract.allows("verified-only-v1", true, "historical_only", "proof", 200, 100))
    }
    @Test fun admissionRequiresEvidenceAndUnexpiredPermission() {
        assertFalse(ProbabilityDisplayContract.allows("verified-only-v1", true, "independent_confirmed", "", 200, 100))
        assertFalse(ProbabilityDisplayContract.allows("verified-only-v1", true, "independent_confirmed", "proof", 100, 100))
        assertFalse(ProbabilityDisplayContract.allows("verified-only-v1", false, "independent_confirmed", "proof", 200, 100))
        assertTrue(ProbabilityDisplayContract.allows("verified-only-v1", true, "independent_confirmed", "proof", 200, 100))
    }
}
