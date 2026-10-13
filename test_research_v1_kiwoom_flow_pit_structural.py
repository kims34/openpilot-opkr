"""Synthetic-only broker PIT boundary tests; none contain market observations."""
import copy
import unittest

from research_v1_kiwoom_flow_pit_structural import (
    KiwoomFlowPITError, audit_candidate_pit,
)


def rec(**replacements):
    candidate = {
        "source": "KIWOOM_REST_KA10059",
        "isin": "KR7005930003",  # Format sample only; NOT identity authority
        "symbol": "005930",
        "venue": "KRX",
        "event_date": "2026-10-08",
        "published_at": "2026-10-08T17:55:00+09:00",
        "available_at": "2026-10-08T18:00:00+09:00",
        "ingested_at": "2026-10-13T20:00:00+09:00",
        "decision_at": "2026-10-09T09:00:00+09:00",
        "response_sha256": "a" * 64,
    }
    candidate.update(replacements)
    return candidate


class CandidateKiwoomFlowPITTest(unittest.TestCase):
    def test_valid_structure_never_proves_historical_vintage(self):
        out = audit_candidate_pit([rec()])
        self.assertTrue(out["structural_asof_timeline_valid"])
        for field in (
            "published_original_vintage_independently_verified",
            "full_universe_historical_coverage_verified",
            "broker_publication_time_contract_verified", "source_admitted",
            "performance_testing_authorized", "sealed_holdout_authorized",
            "live_trading_authorized",
        ):
            self.assertFalse(out[field])

    def test_kiwoom_timestamp_does_not_inherit_krx_20h_rule(self):
        # This is deliberately earlier than the frozen KRX 20:00 final floor.
        # It might or might not have been a real broker publication. Even when
        # structurally consistent, the result cannot be admitted as PIT.
        out = audit_candidate_pit([rec()])
        self.assertFalse(out["broker_publication_time_contract_verified"])

    def test_same_record_unavailable_until_after_decision_fails(self):
        with self.assertRaisesRegex(KiwoomFlowPITError, "lookahead"):
            audit_candidate_pit([rec(decision_at="2026-10-08T17:59:00+09:00")])

    def test_naive_published_at_fails(self):
        with self.assertRaisesRegex(KiwoomFlowPITError, "UTC offset"):
            audit_candidate_pit([rec(published_at="2026-10-08T17:55:00")])

    def test_published_before_event_day_fails(self):
        with self.assertRaisesRegex(KiwoomFlowPITError, "chronology"):
            audit_candidate_pit([rec(published_at="2026-10-07T23:59:59+09:00")])

    def test_available_before_published_fails(self):
        with self.assertRaisesRegex(KiwoomFlowPITError, "chronology"):
            audit_candidate_pit([rec(available_at="2026-10-08T17:00:00+09:00")])

    def test_ingestion_before_availability_fails(self):
        with self.assertRaisesRegex(KiwoomFlowPITError, "chronology"):
            audit_candidate_pit([rec(ingested_at="2026-10-08T17:00:00+09:00")])

    def test_duplicate_issue_venue_date_fails(self):
        with self.assertRaisesRegex(KiwoomFlowPITError, "duplicated"):
            audit_candidate_pit([rec(), rec()])

    def test_venue_ambiguity_fails(self):
        with self.assertRaisesRegex(KiwoomFlowPITError, "venue unknown"):
            audit_candidate_pit([rec(venue="AUTO")])

    def test_unhashable_malformed_venue_is_rejected_cleanly(self):
        with self.assertRaisesRegex(KiwoomFlowPITError, "venue unknown"):
            audit_candidate_pit([rec(venue=["KRX"])])

    def test_no_automatic_venue_aggregation(self):
        out = audit_candidate_pit([rec(), rec(venue="NXT")])
        self.assertEqual(out["candidate_rows"], 2)
        self.assertFalse(out["full_universe_historical_coverage_verified"])

    def test_missing_security_identity_fails(self):
        candidate = rec()
        del candidate["isin"]
        with self.assertRaisesRegex(KiwoomFlowPITError, "missing required"):
            audit_candidate_pit([candidate])

    def test_current_snapshot_digest_cannot_prove_vintage(self):
        candidate = rec(
            original_historical_release_verified=True,
            independent_snapshot_signature="self-declared",
            original_availability_verified=True,
        )
        out = audit_candidate_pit([candidate])
        self.assertFalse(out["published_original_vintage_independently_verified"])
        self.assertFalse(out["source_admitted"])

    def test_empty_observations_fail(self):
        with self.assertRaises(KiwoomFlowPITError):
            audit_candidate_pit([])

    def test_fake_hash_is_not_trusted(self):
        with self.assertRaisesRegex(KiwoomFlowPITError, "digest"):
            audit_candidate_pit([rec(response_sha256="NOT_REAL")])

    def test_invalid_event_date_fails(self):
        with self.assertRaisesRegex(KiwoomFlowPITError, "invalid event_date"):
            audit_candidate_pit([rec(event_date="2026-02-30")])


if __name__ == "__main__":
    unittest.main()
