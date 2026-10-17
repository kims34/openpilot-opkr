"""No-network adversarial tests. All source records are invented fixture bytes."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import research_v1_krx_private_2021_calendar_candidate_audit as m


def fixture(*, omit=None, add=None):
    dates = m._bounds(m.START, m.END)
    holidays = set(m.EXPECTED_HOLIDAYS)
    if omit is not None:
        holidays.remove(omit)
    if add is not None:
        holidays.add(add)
    rows = {
        day: {
            "day": day,
            "pair_sha256": hashlib.sha256(("synthetic:" + day).encode()).hexdigest(),
            "daily_rows": 0 if day in holidays else 500,
            "source_day_class": (
                "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP"
                if day in holidays else m.OPEN
            ),
        }
        for day in dates
    }
    fingerprint = hashlib.sha256(json.dumps(
        [{"day": day, "pair_sha256": rows[day]["pair_sha256"]} for day in dates],
        sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    return rows, fingerprint


class PrivateCalendar2021AuditTest(unittest.TestCase):
    def test_positive_private_dates_still_never_admit_official_market_pit(self):
        rows, fingerprint = fixture()
        z = m.compare_verified_2021(
            rows, prior_snapshot_sha256=fingerprint,
            expected_snapshot_sha256=fingerprint,
        )
        self.assertEqual(z["private_2021_complete_sha_verified_pairs"], 261)
        self.assertEqual(z["private_2021_empty_source_days"], 13)
        self.assertEqual(z["initial_2020_december_public_closure_candidates"], 10)
        self.assertEqual(z["later_2021_august_public_closure_candidates"], 3)
        self.assertTrue(z["2021_private_and_public_candidate_sets_exactly_equal"])
        self.assertTrue(z["second_pass_snapshot_identity_matches_first_pass"])
        for name in m.SAFETY:
            if name != "ordering":
                self.assertIs(z[name], False, name)
        self.assertEqual(z["ordering"], "DISABLED")

    def test_same_thirteen_total_but_one_wrong_date_is_detected(self):
        other = next(d for d in m._bounds(m.START, m.END) if d not in m.EXPECTED_HOLIDAYS)
        rows, fp = fixture(omit="20210816", add=other)
        out = m.compare_verified_2021(rows, prior_snapshot_sha256=fp,
                                      expected_snapshot_sha256=fp)
        self.assertEqual(out["private_2021_empty_source_days"], 13)
        self.assertFalse(out["2021_private_and_public_candidate_sets_exactly_equal"])
        self.assertEqual(out["private_2021_missing_expected_closure_count"], 1)
        self.assertEqual(out["private_2021_unexpected_empty_date_count"], 1)
        self.assertFalse(out["official_market_status_admitted"])

    def test_modified_second_pass_sha_detects_toctou(self):
        rows, fp = fixture()
        rows["20210816"]["pair_sha256"] = "f" * 64
        with self.assertRaisesRegex(m.PrivateCalendarEvidenceGap, "BETWEEN_AUDIT_PASSES"):
            m.compare_verified_2021(rows, prior_snapshot_sha256=fp,
                                    expected_snapshot_sha256=fp)

    def test_unpinned_first_pass_rejected(self):
        rows, fp = fixture()
        with self.assertRaisesRegex(m.PrivateCalendarEvidenceGap, "PINNED"):
            m.compare_verified_2021(rows, prior_snapshot_sha256="e" * 64,
                                    expected_snapshot_sha256=fp)

    def test_rejects_missing_day_even_if_empty_holiday_days_still_thirteen(self):
        rows, fp = fixture()
        rows.pop("20211011")
        with self.assertRaisesRegex(m.PrivateCalendarEvidenceGap, "COMPLETE_WEEKDAY"):
            m.compare_verified_2021(rows, prior_snapshot_sha256=fp,
                                    expected_snapshot_sha256=fp)

    def test_rejects_empty_source_with_nonempty_class(self):
        rows, fp = fixture()
        rows["20210816"]["source_day_class"] = m.OPEN
        with self.assertRaisesRegex(m.PrivateCalendarEvidenceGap, "EMPTY_DAY_CLASS"):
            m.compare_verified_2021(rows, prior_snapshot_sha256=fp,
                                    expected_snapshot_sha256=fp)

    def test_rejects_nonempty_source_labeled_empty(self):
        rows, fp = fixture()
        rows["20210817"]["source_day_class"] = (
            "PROVIDER_BOTH_EMPTY_UNVERIFIED_CALENDAR_OR_SOURCE_GAP"
        )
        with self.assertRaisesRegex(m.PrivateCalendarEvidenceGap, "NONEMPTY_DAY_CLASS"):
            m.compare_verified_2021(rows, prior_snapshot_sha256=fp,
                                    expected_snapshot_sha256=fp)

    def test_boolean_fake_price_row_count_and_invalid_sha_rejected(self):
        rows, fp = fixture()
        for key, value in (("daily_rows", True), ("pair_sha256", "not-a-digest")):
            changed = copy.deepcopy(rows)
            changed["20210816"][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(
                m.PrivateCalendarEvidenceGap, "RECEIPT_INVALID"
            ):
                m.compare_verified_2021(changed, prior_snapshot_sha256=fp,
                                        expected_snapshot_sha256=fp)

    def test_no_worker_or_mount_cannot_access_volume(self):
        cases = [
            {"RAILWAY_SERVICE_NAME": "some-other-worker", "KRX_PRIVATE_RAW_DIR": "/data"},
            {"RAILWAY_SERVICE_NAME": m.WORKER, "KRX_PRIVATE_RAW_DIR": "/tmp"},
            {"RAILWAY_SERVICE_NAME": m.WORKER, "KRX_PRIVATE_RAW_DIR": "/datax"},
            {"RAILWAY_SERVICE_NAME": m.WORKER},
        ]
        for env in cases:
            with self.subTest(env=env):
                z = m.audit_private_2021(execute=True, environment=env)
                self.assertTrue(z["status"].startswith("FAIL_CLOSED"))
                self.assertFalse(z["network_request_attempted"])
                self.assertFalse(z["2021_private_and_public_candidate_sets_exactly_equal"])

    def test_default_execution_dry_run_no_storage(self):
        z = m.audit_private_2021()
        self.assertEqual(z["status"], "DRY_RUN_NO_PRIVATE_STORAGE_READ")
        self.assertFalse(z["storage_mutated"])
        self.assertFalse(z["full_universe_source_admitted"])

    def test_private_reader_requires_complete_reverified_first_pass(self):
        rows, fp = fixture()
        fake = {
            "status": "ALL_REQUESTED_WEEKDAYS_VERIFIED_NOT_PIT_ADMITTED",
            "expected_weekdays": 261, "verified_date_pairs": 261,
            "empty_daily_unverified_calendar_or_source_gap_days": 13,
            "invalid_pair_count": 0, "missing_weekday_pair_count": 0,
            "network_request_attempted": False, "storage_mutated": False,
            "source_admitted": False, "snapshot_fingerprint_sha256": fp,
        }
        env = {"RAILWAY_SERVICE_NAME": m.WORKER, "KRX_PRIVATE_RAW_DIR": "/data"}
        with patch.object(m, "_trusted_private_root", return_value=Path("/data/test")):
            with patch.object(m, "PINNED_2021_PRIVATE_SNAPSHOT_SHA256", fp):
                z = m.audit_private_2021(
                    execute=True, environment=env,
                    integrity=lambda **_: fake,
                    check_one=lambda root, day: rows[day],
                )
                self.assertEqual(z["status"],
                                 "PRIVATE_EMPTY_DATE_SET_MATCHES_CANDIDATES_NOT_PIT")
                self.assertFalse(z["m20_performance_run_authorized"])
                bad = copy.deepcopy(fake)
                bad["source_admitted"] = True
                no = m.audit_private_2021(
                    execute=True, environment=env,
                    integrity=lambda **_: bad,
                    check_one=lambda root, day: rows[day],
                )
                self.assertEqual(no["status"],
                                 "FAIL_CLOSED_2021_PRIVATE_PROOF_UNVERIFIED")

    def test_reader_rejects_second_pass_mutation(self):
        rows, fp = fixture()
        fake = {
            "status": "ALL_REQUESTED_WEEKDAYS_VERIFIED_NOT_PIT_ADMITTED",
            "expected_weekdays": 261, "verified_date_pairs": 261,
            "empty_daily_unverified_calendar_or_source_gap_days": 13,
            "invalid_pair_count": 0, "missing_weekday_pair_count": 0,
            "network_request_attempted": False, "storage_mutated": False,
            "source_admitted": False, "snapshot_fingerprint_sha256": fp,
        }
        changed = copy.deepcopy(rows)
        changed["20211011"]["pair_sha256"] = "f" * 64
        with patch.object(m, "_trusted_private_root", return_value=Path("/data/test")):
            with patch.object(m, "PINNED_2021_PRIVATE_SNAPSHOT_SHA256", fp):
                z = m.audit_private_2021(
                    execute=True,
                    environment={"RAILWAY_SERVICE_NAME": m.WORKER,
                                 "KRX_PRIVATE_RAW_DIR": "/data"},
                    integrity=lambda **_: fake,
                    check_one=lambda root, day: changed[day],
                )
        self.assertEqual(z["status"], "FAIL_CLOSED_2021_PRIVATE_PROOF_UNVERIFIED")
        self.assertFalse(z["official_market_status_admitted"])


if __name__ == "__main__":
    unittest.main()
