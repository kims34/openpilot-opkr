package com.indexalert.app

import org.json.JSONObject

internal fun JSONObject.independentDisplayAllowed(
    nowSeconds: Long = System.currentTimeMillis() / 1000
): Boolean = ProbabilityDisplayContract.allows(
    optString("display_policy_version"),
    opt("display_allowed") == true,
    optString("verification_status"),
    optString("verification_evidence_id"),
    optLong("verification_expires_at", 0),
    nowSeconds
)
