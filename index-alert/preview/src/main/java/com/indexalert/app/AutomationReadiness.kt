package com.indexalert.app

import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

enum class AutomationAvailability(val description: String) {
    CHECKING("자동매매 사용 가능 여부를 확인하고 있습니다."),
    UNAVAILABLE("현재 자동매매를 사용할 수 없습니다."),
    UNKNOWN("자동매매 상태를 확인할 수 없습니다. 새로고침해 주세요.")
}

/** Read-only capability display. No controls, account access or order submission. */
object AutomationReadiness {
    private val falseFlags = listOf(
        "live_ordering_authorized",
        "broker_order_submission_implemented",
        "automation_control_persistence_implemented",
        "independent_gate_admission_evaluated",
        "account_or_capital_snapshot_observed",
        "orders_requested",
        "funds_movement_attempted",
        "database_or_file_mutation_attempted",
        "frozen_criteria_changed"
    )

    fun isUnavailableReport(fields: Map<String, Any?>): Boolean {
        return fields["status"] == "BROKER_AUTOMATION_UNAVAILABLE" &&
            fields["mode"] == "MASTER_OFF" &&
            falseFlags.all { fields[it] is Boolean && fields[it] == false } &&
            fields["required_user_control_fields"] ==
                listOf("automation_enabled", "max_automation_capital_krw")
    }

    fun fetchAvailability(): AutomationAvailability {
        val base = BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/')
        val connection = URL("$base/automation/readiness").openConnection() as HttpURLConnection
        try {
            connection.requestMethod = "GET"
            connection.connectTimeout = 5000
            connection.readTimeout = 5000
            connection.setRequestProperty("Accept", "application/json")
            if (connection.responseCode != HttpURLConnection.HTTP_OK) {
                return AutomationAvailability.UNKNOWN
            }
            val text = connection.inputStream.bufferedReader().use { reader ->
                val buffer = CharArray(8193)
                var count = 0
                while (count < buffer.size) {
                    val n = reader.read(buffer, count, buffer.size - count)
                    if (n < 0) break
                    count += n
                }
                if (count > 8192) return AutomationAvailability.UNKNOWN
                String(buffer, 0, count)
            }
            val report = JSONObject(text)
            val fields = mutableMapOf<String, Any?>(
                "status" to report.opt("status"),
                "mode" to report.opt("mode")
            )
            falseFlags.forEach { fields[it] = report.opt(it) }
            val controls = report.opt("required_user_control_fields")
            fields["required_user_control_fields"] = if (controls is JSONArray) {
                (0 until controls.length()).map { controls.opt(it) }
            } else null
            return if (isUnavailableReport(fields)) AutomationAvailability.UNAVAILABLE
                else AutomationAvailability.UNKNOWN
        } finally {
            connection.disconnect()
        }
    }
}
