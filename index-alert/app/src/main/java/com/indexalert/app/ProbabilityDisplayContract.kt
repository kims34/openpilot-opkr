package com.indexalert.app

/** Display permission is separate from a historical score or model version. */
object ProbabilityDisplayContract {
    const val VERSION = "verified-only-v1"

    fun <T> resolve(freshReceived: Boolean, parsed: T?, saved: T?): T? =
        if (freshReceived) parsed else saved

    fun allows(
        policyVersion: String,
        displayAllowed: Boolean,
        verificationStatus: String,
        evidenceId: String,
        expiresAt: Long,
        nowSeconds: Long
    ): Boolean = policyVersion == VERSION && displayAllowed &&
        verificationStatus == "independent_confirmed" &&
        evidenceId.isNotBlank() && expiresAt > nowSeconds
}
