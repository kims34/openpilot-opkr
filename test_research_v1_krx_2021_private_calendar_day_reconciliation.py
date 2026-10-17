"""No-provider tests of the historical KRX 2021 per-day private calendar gate."""
from __future__ import annotations

from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import research_v1_krx_2021_private_calendar_day_reconciliation as p


def fixture():
    dates = p._bounds("2021-01-01", "2021-12-31")
    rows = [{
        "day": day,
        "pair_sha256": hashlib.sha256(day.encode()).hexdigest(),
        "daily_rows": 0 if day in p.EXPECTED_CLOSED else 100,
        "source_day_class": (
            "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP"
            if day in p.EXPECTED_CLOSED else p.NONEMPTY
        ),
    } for day in dates]
    sha = hashlib.sha256(json.dumps(
        [{"day": x["day"], "pair_sha256": x["pair_sha256"]} for x in rows],
        sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    return rows, sha


def assess(rows, pinned_digest):
    with patch.object(p, "SOURCE_SNAPSHOT_SHA256", pinned_digest):
        return p._source_rows_match_expected_calendar(rows)


class KRX2021PrivateCalendarTest(unittest.TestCase):
    def test_2021_fixed_vintage_schedule_is_10_plus_3_exact_weekdays(self):
        self.assertEqual(len(p.KRX_INITIAL_2021_CLOSED), 10)
        self.assertEqual(len(p.KRX_REVISED_2021_CLOSED), 3)
        self.assertEqual(len(p.EXPECTED_CLOSED), 13)
        self.assertTrue(p.KRX_INITIAL_2021_CLOSED.isdisjoint(p.KRX_REVISED_2021_CLOSED))
        self.assertEqual(p.KRX_REVISED_2021_CLOSED,
                         frozenset(("20210816", "20211004", "20211011")))
        self.assertEqual(len(p._bounds("2021-01-01", "2021-12-31")), 261)

    def test_all_261_synthetic_days_match_exact_holidays_but_not_pit(self):
        rows, sha = fixture()
        out = assess(rows, sha)
        self.assertEqual(out["status"],
            "2021_RETROSPECTIVE_EXCHANGE_CALENDAR_DATES_MATCH_SOURCE_EMPTY_NOT_PIT")
        self.assertTrue(out["original_pair_fingerprint_matched"])
        self.assertTrue(out["source_date_by_date_retrospective_calendar_match"])
        self.assertEqual(out["private_original_2021_weekday_pairs_verified"], 261)
        self.assertEqual(out["original_source_empty_days_count"], 13)
        self.assertEqual(out["expected_closures_missing_from_source_empty_days_count"], 0)
        self.assertEqual(out["unexpected_source_empty_days_count"], 0)
        for key in ("source_original_publication_pit_verified",
                    "2021_exchange_calendar_pit_admitted",
                    "individual_security_tradability_verified",
                    "halt_delist_corporate_actions_verified",
                    "full_universe_source_admitted",
                    "m20_performance_run_authorized", "independent_holdout_authorized",
                    "champion_change_authorized", "real_orders_authorized",
                    "funds_movement_authorized", "permissions_change_authorized",
                    "network_request_attempted", "storage_mutated",
                    "raw_security_rows_or_private_dates_emitted"):
            self.assertIs(out[key], False, key)
        self.assertEqual(out["ordering"], "DISABLED")
        for row in rows:
            self.assertNotIn(row["day"], str(out))
            self.assertNotIn(row["pair_sha256"], str(out))

    def test_13_equal_annual_count_but_one_wrong_date_cannot_pass(self):
        rows, sha = fixture()
        expected = next(x for x in rows if x["day"] == "20210816")
        other = next(x for x in rows if x["day"] == "20210817")
        expected.update(daily_rows=5, source_day_class=p.NONEMPTY)
        other.update(daily_rows=0, source_day_class=
            "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP")
        out = assess(rows, sha)
        self.assertEqual(out["original_source_empty_days_count"], 13)
        self.assertEqual(out["expected_closures_missing_from_source_empty_days_count"], 1)
        self.assertEqual(out["unexpected_source_empty_days_count"], 1)
        self.assertEqual(out["status"], "FAIL_CLOSED_2021_DAY_BY_DAY_CALENDAR_MISMATCH")
        self.assertFalse(out["source_date_by_date_retrospective_calendar_match"])

    def test_drift_from_actual_2021_production_snapshot_blocks_any_calendar_verdict(self):
        rows, sha = fixture()
        with patch.object(p, "SOURCE_SNAPSHOT_SHA256", "f" * 64):
            out = p._source_rows_match_expected_calendar(rows)
        self.assertEqual(out["status"], "FAIL_CLOSED_2021_IMMUTABLE_SOURCE_FINGERPRINT_DRIFT")
        self.assertFalse(out["original_pair_fingerprint_matched"])

    def test_12_or_14_empty_dates_cannot_pass(self):
        for use_extra in (False, True):
            rows, sha = fixture()
            target = "20210817" if use_extra else "20210816"
            row = next(x for x in rows if x["day"] == target)
            row.update(daily_rows=0 if use_extra else 100,
                       source_day_class=(
                           "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP"
                           if use_extra else p.NONEMPTY))
            with self.subTest(extra=use_extra):
                out = assess(rows, sha)
                self.assertEqual(out["status"], "FAIL_CLOSED_2021_DAY_BY_DAY_CALENDAR_MISMATCH")
                self.assertFalse(out["source_date_by_date_retrospective_calendar_match"])

    def test_missing_or_extra_weekday_rejected(self):
        rows, sha = fixture()
        for bad in (rows[:-1], rows + [rows[0]]):
            with self.subTest(size=len(bad)):
                self.assertEqual(assess(bad, sha)["status"], "FAIL_CLOSED_2021_EXPECTED_SCOPE")

    def test_reordered_source_receipts_rejected(self):
        rows, sha = fixture()
        rows[5], rows[6] = rows[6], rows[5]
        out = assess(rows, sha)
        self.assertEqual(out["status"], "FAIL_CLOSED_2021_SOURCE_ROW_BINDING")

    def test_source_digest_and_calendar_row_count_shape_rejected(self):
        for key, value in (("pair_sha256", "invalid"), ("pair_sha256", None),
                           ("daily_rows", True), ("daily_rows", -1),
                           ("daily_rows", "0")):
            rows, sha = fixture()
            rows[3][key] = value
            with self.subTest(key=key, value=value):
                self.assertEqual(assess(rows, sha)["status"],
                                 "FAIL_CLOSED_2021_SOURCE_ROW_BINDING")

    def test_forged_calendar_source_class_and_rows_mismatch_rejected(self):
        rows, sha = fixture()
        self.assertEqual(rows[1]["day"], "20210104")
        rows[1]["daily_rows"] = 0
        self.assertEqual(assess(rows, sha)["status"],
                         "FAIL_CLOSED_2021_EMPTY_ROW_CONTRADICTION")

    def test_unsupported_day_class_rejected(self):
        rows, sha = fixture()
        rows[0]["source_day_class"] = "OFFICIAL_HOLIDAY_VERIFIED"
        self.assertEqual(assess(rows, sha)["status"],
                         "FAIL_CLOSED_2021_SOURCE_DAY_CLASS")

    def test_source_data_must_never_include_symbol_price_secret_or_external_fields(self):
        rows, sha = fixture()
        rows[3]["ticker"] = "SYNTHETIC"
        self.assertEqual(assess(rows, sha)["status"],
                         "FAIL_CLOSED_2021_SOURCE_ROW_SHAPE")

    def test_2021_initial_release_date_is_not_a_trading_day_proof(self):
        rows, sha = fixture()
        result = assess(rows, sha)
        self.assertEqual(result["2021_later_announcement_publication_date"], "2021-08-04")
        self.assertIs(result["2021_exchange_calendar_pit_admitted"], False)

    def test_default_dry_run_does_not_touch_private_volume_or_network(self):
        def forbidden(*args, **kwargs):
            raise AssertionError("must never run")
        out = p.run(audit=False, check_day=forbidden, verify_root=forbidden)
        self.assertEqual(out["status"], "DRY_RUN_PRIVATE_STORAGE_UNTOUCHED")
        self.assertFalse(out["network_request_attempted"])
        self.assertFalse(out["storage_mutated"])

    def test_wrong_worker_or_fake_mount_cannot_begin_private_reads(self):
        def forbidden(*args, **kwargs):
            raise AssertionError("must never read")
        for env, code in [
            ({"RAILWAY_SERVICE_NAME":"not-worker","KRX_PRIVATE_RAW_DIR":"/data"},
             "FAIL_CLOSED_NOT_DEDICATED_KRX_PRIVATE_WORKER"),
            ({"RAILWAY_SERVICE_NAME":p.WORKER,"KRX_PRIVATE_RAW_DIR":"/datafake"},
             "FAIL_CLOSED_NOT_ON_PRIVATE_DATA_VOLUME"),
            ({"RAILWAY_SERVICE_NAME":p.WORKER,"KRX_PRIVATE_RAW_DIR":"/tmp"},
             "FAIL_CLOSED_NOT_ON_PRIVATE_DATA_VOLUME"),
        ]:
            with self.subTest(code=code):
                self.assertEqual(p.run(audit=True,environment=env,check_day=forbidden,
                    verify_root=forbidden)["status"],code)

    def test_private_root_validation_failure_stops_cleanly(self):
        def bad(root):
            raise p.OfflinePrivateAuditError("PRIVATE_STORE_ROOT_INVALID")
        out=p.run(audit=True,environment={"RAILWAY_SERVICE_NAME":p.WORKER,
                                          "KRX_PRIVATE_RAW_DIR":"/data"},
                  verify_root=bad)
        self.assertEqual(out["status"],"FAIL_CLOSED_PRIVATE_ROOT_NOT_VERIFIED")

    def test_private_day_read_failure_does_not_leak_date_or_partial_digest(self):
        def bad(root, day):
            raise RuntimeError("SECRET_SIMULATION" + day)
        out=p.run(audit=True,environment={"RAILWAY_SERVICE_NAME":p.WORKER,
                                          "KRX_PRIVATE_RAW_DIR":"/data"},
                  verify_root=lambda x:x,check_day=bad)
        self.assertEqual(out["status"],"FAIL_CLOSED_PRIVATE_SOURCE_DAY_INVALID")
        self.assertNotIn("SECRET_SIMULATION",str(out))
        self.assertNotIn("20210101",str(out))

    def test_worker_mocked_261_rows_respects_snapshot_binding(self):
        rows, sha=fixture()
        by_day={v["day"]:v for v in rows}
        seen=[]
        def read_day(root,day):
            seen.append(day)
            return by_day[day]
        with patch.object(p,"SOURCE_SNAPSHOT_SHA256",sha):
            out=p.run(audit=True,environment={"RAILWAY_SERVICE_NAME":p.WORKER,
                        "KRX_PRIVATE_RAW_DIR":"/data"},verify_root=lambda x:x,
                      check_day=read_day)
        self.assertEqual(len(seen),261)
        self.assertTrue(out["source_date_by_date_retrospective_calendar_match"])
        self.assertFalse(out["source_original_publication_pit_verified"])
        self.assertEqual(out["ordering"],"DISABLED")


if __name__ == "__main__":
    unittest.main()
