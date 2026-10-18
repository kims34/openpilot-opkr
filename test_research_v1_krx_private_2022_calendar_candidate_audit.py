"""No-provider synthetic controls. All dates in fixtures are invented SOURCE SHAPES."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import research_v1_krx_private_2022_calendar_candidate_audit as m


def corpus(*, omit=None, add=None):
    days = m._bounds(m.START, m.END)
    empty = set(m.PUBLIC_CANDIDATES)
    if omit is not None:
        empty.remove(omit)
    if add is not None:
        empty.add(add)
    rows = {
        d: {
            "day": d,
            "pair_sha256": hashlib.sha256(("invented-shape-" + d).encode()).hexdigest(),
            "daily_rows": 0 if d in empty else 504,
            "source_day_class": (
                "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP"
                if d in empty else m.NONEMPTY_CLASS
            ),
        }
        for d in days
    }
    sha = hashlib.sha256(json.dumps(
        [{"day": d, "pair_sha256": rows[d]["pair_sha256"]} for d in days],
        sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    return rows, sha


class PrivateKRX2022CandidateTests(unittest.TestCase):
    def test_expected_candidate_dates_are_14_unique_weekdays(self):
        import datetime
        self.assertEqual(len(m.PUBLIC_CANDIDATES), 14)
        self.assertEqual(len(m.REGULAR_2022_CANDIDATES), 11)
        self.assertEqual(len(m.ELECTION_2022_CANDIDATES), 2)
        self.assertEqual(len(m.YEAR_END_2022_CANDIDATES), 1)
        self.assertEqual(len(m._bounds(m.START, m.END)), 260)
        for d in m.PUBLIC_CANDIDATES:
            date = datetime.datetime.strptime(d, "%Y%m%d").date()
            self.assertEqual(date.year, 2022)
            self.assertLess(date.weekday(), 5)

    def test_full_synthetic_match_never_authorizes_market(self):
        rows, sha = corpus()
        out = m.compare_verified_2022(
            rows, first_pass_snapshot_sha256=sha,
            expected_snapshot_sha256=sha
        )
        self.assertTrue(out["2022_private_candidate_date_sets_equal"])
        self.assertEqual(out["checked_original_sha_receipt_pairs"], 260)
        self.assertEqual(out["source_empty_weekdays"], 14)
        self.assertEqual(out["matched_candidate_empty_dates"], 14)
        self.assertEqual(out["expected_closure_dates_missing_in_private_empty_count"], 0)
        for key, value in m.DENIAL.items():
            self.assertEqual(out[key], value, key)

    def test_same_14_empty_but_one_wrong_actual_date_fails(self):
        other = next(d for d in m._bounds(m.START, m.END)
                     if d not in m.PUBLIC_CANDIDATES)
        rows, sha = corpus(omit="20220309", add=other)
        out = m.compare_verified_2022(
            rows, first_pass_snapshot_sha256=sha,
            expected_snapshot_sha256=sha)
        self.assertFalse(out["2022_private_candidate_date_sets_equal"])
        self.assertEqual(out["source_empty_weekdays"], 14)
        self.assertEqual(out["expected_closure_dates_missing_in_private_empty_count"], 1)
        self.assertEqual(out["unexpected_private_empty_dates_count"], 1)
        self.assertFalse(out["m20_performance_run_authorized"])

    def test_false_positive_fails_when_an_empty_day_is_missing(self):
        rows, sha = corpus(omit="20221230")
        out = m.compare_verified_2022(
            rows, first_pass_snapshot_sha256=sha,
            expected_snapshot_sha256=sha)
        self.assertFalse(out["2022_private_candidate_date_sets_equal"])
        self.assertEqual(out["source_empty_weekdays"], 13)

    def test_second_pass_mutation_rejects_even_unchanged_day_class(self):
        rows, sha = corpus()
        rows["20220909"]["pair_sha256"] = "e" * 64
        with self.assertRaisesRegex(m.Private2022CalendarGap, "BETWEEN_PASSES"):
            m.compare_verified_2022(
                rows, first_pass_snapshot_sha256=sha,
                expected_snapshot_sha256=sha)

    def test_wrong_pinned_prior_sha_rejected(self):
        rows, sha = corpus()
        with self.assertRaisesRegex(m.Private2022CalendarGap, "PINNED"):
            m.compare_verified_2022(
                rows, first_pass_snapshot_sha256="f" * 64,
                expected_snapshot_sha256=sha)

    def test_source_receipt_class_and_day_shape_rejected(self):
        rows, sha = corpus()
        mutations = [
            ("20220309", "daily_rows", True, "RECEIPT"),
            ("20220309", "pair_sha256", "not-hash", "RECEIPT"),
            ("20220309", "source_day_class", m.NONEMPTY_CLASS, "EMPTY_SOURCE_CLASS"),
            ("20220310", "source_day_class",
             "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP",
             "NONEMPTY_SOURCE_CLASS"),
            ("20220309", "day", "20220308", "RECEIPT"),
        ]
        for d, k, v, code in mutations:
            copied = copy.deepcopy(rows)
            copied[d][k] = v
            with self.subTest(d=d, k=k), self.assertRaisesRegex(
                m.Private2022CalendarGap, code
            ):
                m.compare_verified_2022(
                    copied, first_pass_snapshot_sha256=sha,
                    expected_snapshot_sha256=sha)

    def test_missing_pair_cannot_mask_holidays(self):
        rows, sha = corpus()
        rows.pop("20220309")
        with self.assertRaisesRegex(m.Private2022CalendarGap, "COMPLETE_WEEKDAY"):
            m.compare_verified_2022(
                rows, first_pass_snapshot_sha256=sha,
                expected_snapshot_sha256=sha)

    def test_default_no_original_read_and_no_authority(self):
        out = m.audit_private_2022()
        self.assertEqual(out["status"], "DRY_RUN_NO_PRIVATE_STORAGE_READ")
        self.assertFalse(out["2022_private_candidate_date_sets_equal"])
        for key, v in m.DENIAL.items():
            self.assertEqual(out[key], v, key)

    def test_worker_and_mount_scope_are_required(self):
        envs = [
            {"RAILWAY_SERVICE_NAME": "other", "KRX_PRIVATE_RAW_DIR": "/data"},
            {"RAILWAY_SERVICE_NAME": m.WORKER, "KRX_PRIVATE_RAW_DIR": "/tmp"},
            {"RAILWAY_SERVICE_NAME": m.WORKER, "KRX_PRIVATE_RAW_DIR": "/datax"},
            {"RAILWAY_SERVICE_NAME": m.WORKER},
        ]
        for e in envs:
            with self.subTest(env=e):
                out = m.audit_private_2022(execute=True, environment=e)
                self.assertTrue(out["status"].startswith("FAIL_CLOSED"))
                self.assertFalse(out["network_request_attempted"])

    def test_only_full_authority_denied_integrity_can_compare(self):
        rows, sha = corpus()
        env = {"RAILWAY_SERVICE_NAME": m.WORKER, "KRX_PRIVATE_RAW_DIR": "/data"}
        baseline = {
            "status": "ALL_REQUESTED_WEEKDAYS_VERIFIED_NOT_PIT_ADMITTED",
            "expected_weekdays": 260, "verified_date_pairs": 260,
            "empty_daily_unverified_calendar_or_source_gap_days": 14,
            "invalid_pair_count": 0, "missing_weekday_pair_count": 0,
            "network_request_attempted": False, "storage_mutated": False,
            "source_admitted": False, "snapshot_fingerprint_sha256": sha,
        }
        with patch.object(m, "_trusted_private_root", return_value=Path("/data/fake")):
            with patch.object(m, "PINNED_2022_PRIVATE_SNAPSHOT_SHA256", sha):
                out = m.audit_private_2022(
                    execute=True, environment=env,
                    integrity=lambda **_: baseline,
                    check_one=lambda root, day: rows[day])
                self.assertTrue(out["2022_private_candidate_date_sets_equal"])
                self.assertTrue(
                    out["original_raw_byte_integrity_audit_completed_this_invocation"])
                for name, value in [("source_admitted", True),
                                    ("network_request_attempted", True),
                                    ("storage_mutated", True),
                                    ("verified_date_pairs", 259)]:
                    forbidden = dict(baseline)
                    forbidden[name] = value
                    denied = m.audit_private_2022(
                        execute=True, environment=env,
                        integrity=lambda **_: forbidden,
                        check_one=lambda root, day: rows[day])
                    self.assertEqual(
                        denied["status"],
                        "FAIL_CLOSED_2022_ORIGINAL_PRIVATE_PROOF_UNVERIFIED")
                    self.assertFalse(denied["official_market_status_admitted"])

    def test_private_second_pass_source_drift_refused(self):
        rows, sha = corpus()
        changed = copy.deepcopy(rows)
        changed["20221230"]["pair_sha256"] = "a" * 64
        first = {
            "status": "ALL_REQUESTED_WEEKDAYS_VERIFIED_NOT_PIT_ADMITTED",
            "expected_weekdays": 260, "verified_date_pairs": 260,
            "empty_daily_unverified_calendar_or_source_gap_days": 14,
            "invalid_pair_count": 0, "missing_weekday_pair_count": 0,
            "network_request_attempted": False, "storage_mutated": False,
            "source_admitted": False, "snapshot_fingerprint_sha256": sha,
        }
        with patch.object(m, "_trusted_private_root", return_value=Path("/data/fake")):
            with patch.object(m, "PINNED_2022_PRIVATE_SNAPSHOT_SHA256", sha):
                out = m.audit_private_2022(
                    execute=True, environment={
                        "RAILWAY_SERVICE_NAME": m.WORKER,
                        "KRX_PRIVATE_RAW_DIR": "/data",
                    },
                    integrity=lambda **_: first,
                    check_one=lambda root, day: changed[day])
        self.assertEqual(out["status"], "FAIL_CLOSED_2022_ORIGINAL_PRIVATE_PROOF_UNVERIFIED")
        self.assertFalse(out["2022_private_candidate_date_sets_equal"])


if __name__ == "__main__":
    unittest.main()
