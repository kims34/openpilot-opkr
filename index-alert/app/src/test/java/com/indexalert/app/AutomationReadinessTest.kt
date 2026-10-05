package com.indexalert.app

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AutomationReadinessTest {
    private fun report(): MutableMap<String, Any?> = mutableMapOf(
        "status" to "BROKER_AUTOMATION_UNAVAILABLE",
        "mode" to "MASTER_OFF",
        "live_ordering_authorized" to false,
        "broker_order_submission_implemented" to false,
        "automation_control_persistence_implemented" to false,
        "independent_gate_admission_evaluated" to false,
        "account_or_capital_snapshot_observed" to false,
        "orders_requested" to false,
        "funds_movement_attempted" to false,
        "database_or_file_mutation_attempted" to false,
        "frozen_criteria_changed" to false,
        "required_user_control_fields" to listOf("automation_enabled", "max_automation_capital_krw")
    )

    @Test fun exactUnavailableReportIsRecognized() {
        assertTrue(AutomationReadiness.isUnavailableReport(report()))
    }

    @Test fun everyAuthorityOrMutationFlagRequiresExactBooleanFalse() {
        report().filterValues { it == false }.keys.forEach { key ->
            listOf(true, "false", "true", 0, 1, null).forEach { value ->
                val fields = report()
                fields[key] = value
                assertFalse("$key=$value", AutomationReadiness.isUnavailableReport(fields))
            }
            val fields = report()
            fields.remove(key)
            assertFalse("missing $key", AutomationReadiness.isUnavailableReport(fields))
        }
    }

    @Test fun unexpectedReadyOrLiveModesNeverEnableAutomation() {
        listOf("READY", "BROKER_AUTOMATION_AVAILABLE", null).forEach { value ->
            val fields = report()
            fields["status"] = value
            assertFalse(AutomationReadiness.isUnavailableReport(fields))
        }
        listOf("LIVE", "MASTER_ON", null).forEach { value ->
            val fields = report()
            fields["mode"] = value
            assertFalse(AutomationReadiness.isUnavailableReport(fields))
        }
    }

    @Test fun controlContractMustMatchAndCannotBeReplacedWithScalarOrExtraFields() {
        listOf(null, "automation_enabled", emptyList<String>(),
            listOf("automation_enabled"),
            listOf("automation_enabled", "max_automation_capital_krw", "threshold")).forEach { value ->
            val fields = report()
            fields["required_user_control_fields"] = value
            assertFalse(AutomationReadiness.isUnavailableReport(fields))
        }
    }
}
