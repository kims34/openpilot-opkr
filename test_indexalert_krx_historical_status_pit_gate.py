"""Synthetic-only PIT historical status boundary tests."""
import unittest

from research_v1_krx_historical_status_pit_gate import assess_historical_status_candidate as check

D = "2020-06-15T15:30:00+09:00"
P = "2020-06-15T09:00:00+09:00"
A = "2020-06-15T09:01:00+09:00"
R = "2020-06-15T13:00:00+09:00"


def row(status="TRADABLE", record="b", start="2020-06-01T09:00:00+09:00",
        end=None, source="KRX_ORIGINAL_HISTORICAL_STATUS_ARCHIVE",
        published=P, available=A, retrieved=R):
    return {
        "episode_sha256": "a" * 64,
        "record_sha256": record * 64,
        "source_document_sha256": "c" * 64,
        "source_kind": source,
        "status": status,
        "effective_start_kst": start,
        "effective_end_kst": end,
        "originally_published_at_kst": published,
        "observed_available_at_kst": available,
        "retrieved_at_kst": retrieved,
    }


class TestHistoricalStatusPITBoundary(unittest.TestCase):
    def test_positive_event_cannot_unquarantine_27(self):
        x = check([row()], D)
        self.assertEqual(x["active_positive_candidate_count"], 1)
        self.assertFalse(x["pit_admitted"])
        self.assertEqual(x["27_quarantined_securities_released"], 0)
        self.assertFalse(x["complete_historical_episodes_verified"])
        self.assertFalse(x["real_orders_authorized"])

    def test_halt_blocks_effective_interval(self):
        x = check([row("HALTED")], D)
        self.assertEqual(x["active_danger_state_count"], 1)
        self.assertFalse(x["profitability_run_authorized"])

    def test_cleanup_and_delisted_are_danger_not_price_signal(self):
        for status in ("CLEANUP", "DELISTED"):
            with self.subTest(status=status):
                x = check([row(status)], D)
                self.assertEqual(x["active_danger_state_count"], 1)
                self.assertFalse(x["pit_admitted"])

    def test_outside_interval_does_not_prove_tradeable(self):
        x = check([row("HALTED", end="2020-06-14T15:30:00+09:00")], D)
        self.assertEqual(x["active_danger_state_count"], 0)
        self.assertFalse(x["complete_historical_episodes_verified"])

    def test_current_snapshot_not_historic(self):
        x = check([row(source="KRX_CURRENT_SCREEN",
                       retrieved="2026-10-13T09:00:00+09:00")], D)
        self.assertEqual(x["current_or_unknown_source_rejected"], 1)
        self.assertEqual(x["retrospective_retrieval_not_attested"], 1)
        self.assertFalse(x["independent_source_archive_verified"])

    def test_late_first_availability(self):
        x = check([row(available="2020-06-15T17:00:00+09:00",
                       retrieved="2020-06-15T17:30:00+09:00")], D)
        self.assertEqual(x["future_publication_or_availability"], 1)

    def test_retrieval_future_does_not_prove_historical_pit(self):
        x = check([row(retrieved="2026-10-13T09:00:00+09:00")], D)
        self.assertEqual(x["retrospective_retrieval_not_attested"], 1)
        self.assertFalse(x["pit_admitted"])

    def test_out_of_order_publication_and_availability(self):
        x = check([row(published="2020-06-15T12:00:00+09:00",
                       available="2020-06-15T09:00:00+09:00")], D)
        self.assertEqual(x["time_order_invalid"], 1)
        self.assertEqual(x["status"], "INCONSISTENT_OR_UNTIMELY_STATUS_EVIDENCE_BLOCKED")

    def test_conflicting_statuses_deny(self):
        x = check([row(), row("HALTED", record="d")], D)
        self.assertEqual(x["overlapping_conflict_count"], 1)
        self.assertFalse(x["pit_admitted"])

    def test_boundary_interval_exclusive_end(self):
        x = check([row("HALTED", end=D)], D)
        self.assertEqual(x["active_danger_state_count"], 0)

    def test_duplicate_record_and_cross_episode_fails(self):
        self.assertEqual(check([row(), row()], D)["status"], "FAIL_CLOSED_INVALID_EVIDENCE")
        other = row(record="e")
        other["episode_sha256"] = "f" * 64
        self.assertEqual(check([row(), other], D)["status"], "FAIL_CLOSED_INVALID_EVIDENCE")

    def test_naive_utc_invalid_and_wrong_expiry(self):
        self.assertEqual(check([row()], "2020-06-15T15:30:00")["status"], "FAIL_CLOSED_INVALID_EVIDENCE")
        self.assertEqual(check([row()], "2020-06-15T06:30:00+00:00")["status"], "FAIL_CLOSED_INVALID_EVIDENCE")
        self.assertEqual(check([row(end="2020-06-01T09:00:00+09:00")], D)["status"],
                         "FAIL_CLOSED_INVALID_EVIDENCE")

    def test_no_document_assurance_from_self_declared_metadata(self):
        x = check([row()], D)
        self.assertFalse(x["independent_source_archive_verified"])
        self.assertEqual(x["ordering"], "DISABLED")
        self.assertFalse(x["network_requests_made"])
        self.assertFalse(x["funds_movement_authorized"])


if __name__ == "__main__":
    unittest.main()
