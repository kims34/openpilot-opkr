"""Offline security and evidence-boundary tests; synthetic metadata is NOT market evidence."""
import copy
import hashlib
import unittest

from research_v1_kiwoom_flow_source_gate import REQUEST, audit_kiwoom_probe


def example():
    return {
        "purpose": "SOURCE_FEASIBILITY_NOT_PROFITABILITY",
        "ordering": False,
        "performance_admitted": False,
        "raw_rows_persisted": False,
        "status": "SOURCE_REACHABLE_METADATA_ONLY",
        "requested_body": dict(REQUEST),
        "pages": [
            {
                "rows": 2,
                "min_date": "20261007",
                "max_date": "20261008",
                "invalid_dates": 0,
                "missing_required_rows": 0,
                "invalid_numeric_rows": 0,
                "negative_activity_rows": 0,
                "nonmonotonic_date_pairs": 0,
                "raw_sha256": hashlib.sha256(b"synthetic-metadata-only").hexdigest(),
                "more": False,
            },
        ],
        "duplicate_dates": 0,
        "pagination_exhausted": True,
        "history_exhausted": False,
        "historical_retention_verified": False,
    }


class KiwoomInvestorFlowGateTest(unittest.TestCase):
    def test_missing_report_is_blocked(self):
        report = audit_kiwoom_probe(None)
        self.assertFalse(report["metadata_validation_pass"])
        self.assertFalse(report["performance_testing_authorized"])

    def test_good_metadata_only_reachable_not_admitted(self):
        result = audit_kiwoom_probe(example())
        self.assertTrue(result["metadata_validation_pass"])
        self.assertFalse(result["bounded_route_reachability"])
        self.assertTrue(result["reported_bounded_response_shape_compatible"])
        for key in (
            "source_admitted", "new_strategy_preregistered",
            "full_universe_coverage_verified", "broker_historical_vintage_pit_verified",
            "performance_testing_authorized", "sealed_holdout_authorized",
            "live_trading_authorized", "champion_change_authorized",
        ):
            self.assertFalse(result[key], key)

    def test_reject_ordering_switch(self):
        report = example()
        report["ordering"] = True
        self.assertIn("unsafe_ordering", audit_kiwoom_probe(report)["metadata_failures"])

    def test_reject_result_marked_admitted(self):
        report = example()
        report["performance_admitted"] = True
        self.assertFalse(audit_kiwoom_probe(report)["metadata_validation_pass"])

    def test_reject_missing_required_scope(self):
        report = example()
        report["requested_body"]["trde_tp"] = "1"
        self.assertIn("request_scope_drift", audit_kiwoom_probe(report)["metadata_failures"])

    def test_reject_invalid_numeric_rows(self):
        report = example()
        report["pages"][0]["invalid_numeric_rows"] = 1
        self.assertFalse(audit_kiwoom_probe(report)["metadata_validation_pass"])

    def test_reject_negative_cumulative_activity(self):
        report = example()
        report["pages"][0]["negative_activity_rows"] = 1
        self.assertIn("negative_activity_rows_present", audit_kiwoom_probe(report)["metadata_failures"])

    def test_reject_nonmonotonic_dates(self):
        report = example()
        report["pages"][0]["nonmonotonic_date_pairs"] = 1
        self.assertIn("nonmonotonic_date_pairs_present", audit_kiwoom_probe(report)["metadata_failures"])

    def test_reject_duplicate_dates(self):
        report = example()
        report["duplicate_dates"] = 1
        self.assertFalse(audit_kiwoom_probe(report)["metadata_validation_pass"])

    def test_reject_truncated_continuation(self):
        report = example()
        report["pages"][0]["more"] = True
        report["pagination_exhausted"] = False
        self.assertIn("pagination_not_exhausted", audit_kiwoom_probe(report)["metadata_failures"])

    def test_reject_page_overlap(self):
        report = example()
        report["pages"][0]["more"] = True
        report["pages"].append({
            "rows": 1,
            "min_date": "20261007",
            "max_date": "20261007",
            "invalid_dates": 0,
            "missing_required_rows": 0,
            "invalid_numeric_rows": 0,
            "raw_sha256": hashlib.sha256(b"next-synthetic-page").hexdigest(),
            "more": False,
        })
        self.assertIn("overlapping_or_unsorted_pages", audit_kiwoom_probe(report)["metadata_failures"])

    def test_reject_false_exhaustion_with_live_next_key(self):
        report = example()
        report["pages"][0]["more"] = True
        report["pagination_exhausted"] = True
        self.assertIn("pagination_exhaustion_conflict", audit_kiwoom_probe(report)["metadata_failures"])

    def test_structural_pass_not_authenticated_proof(self):
        self.assertFalse(audit_kiwoom_probe(example())["authenticated_route_evidence_verified"])

    def test_reject_invalid_response_hash(self):
        report = example()
        report["pages"][0]["raw_sha256"] = "invalid"
        self.assertFalse(audit_kiwoom_probe(report)["metadata_validation_pass"])

    def test_reject_empty_conflicting_status(self):
        report = example()
        report["status"] = "SOURCE_REACHABLE_EMPTY"
        self.assertIn("empty_status_conflict", audit_kiwoom_probe(report)["metadata_failures"])

    def test_unverified_complete_history_claim_is_rejected(self):
        report = example()
        report["history_exhausted"] = True
        self.assertIn("unverified_history_misrepresented", audit_kiwoom_probe(report)["metadata_failures"])

    def test_unverified_retention_claim_is_rejected(self):
        report = example()
        report["historical_retention_verified"] = True
        self.assertIn("unverified_history_misrepresented", audit_kiwoom_probe(report)["metadata_failures"])

    def test_nested_credential_key_in_page_is_rejected(self):
        report = example()
        report["pages"][0]["authorization"] = "synthetic-secret"
        self.assertIn("sensitive_key_in_nested_metadata", audit_kiwoom_probe(report)["metadata_failures"])

    def test_reject_sensitive_metadata_fields(self):
        report = example()
        report["access_token"] = "NEVER-STORE-THIS"
        self.assertIn("sensitive_key_in_metadata", audit_kiwoom_probe(report)["metadata_failures"])

    def test_unsupported_fields_cannot_grant_pit(self):
        report = example()
        report.update({
            "publication_time_verified": True,
            "history_is_complete": True,
            "feature_performance_testing_authorized": True,
        })
        result = audit_kiwoom_probe(report)
        self.assertFalse(result["broker_historical_vintage_pit_verified"])
        self.assertFalse(result["performance_testing_authorized"])


if __name__ == "__main__":
    unittest.main()
