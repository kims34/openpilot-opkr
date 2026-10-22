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


    def test_2021_market_vintage_initial_preopen_never_uses_future_august_notice(self):
        for day in ("2021-01-01", "2021-08-03", "2021-08-04"):
            with self.subTest(day=day):
                x = p.strict_krx_2021_calendar_preopen_reference(day)
                self.assertEqual(x["reference_market_closure_count"], 10)
                self.assertEqual(
                    x["extra_2021_exchange_closures_from_later_notice_usable_preopen"], 0)
                self.assertEqual(x["reference_vintage"],
                                 "KRX_2021_INITIAL_MARKET_CALENDAR")
                self.assertFalse(x["official_asof_market_calendar_source_admitted"])

    def test_2021_market_vintage_added_days_safe_no_earlier_than_next_preopen(self):
        for day in ("2021-08-05", "2021-08-16", "2021-10-11", "2021-12-31"):
            with self.subTest(day=day):
                x = p.strict_krx_2021_calendar_preopen_reference(day)
                self.assertEqual(x["reference_market_closure_count"], 13)
                self.assertEqual(
                    x["extra_2021_exchange_closures_from_later_notice_usable_preopen"], 3)
                self.assertEqual(x["first_conservative_preopen_for_revised_reference"],
                                 "2021-08-05")
                self.assertEqual(x["reference_vintage"],
                                 "KRX_2021_REVISED_NOTICE_CONSERVATIVE_NEXT_DAY")
                self.assertFalse(x["official_exchange_publication_instant_verified"])

    def test_2021_market_vintage_date_shape_invalid_fails_closed(self):
        for bad in ("2021-02-29", "2021-08-00", "2021-13-01",
                    "2021-8-5", "2021/08/05", "2022-08-05",
                    "2020-12-31", "", 20210805, True, None):
            with self.subTest(bad=bad), self.assertRaises(p.OfflinePrivateAuditError):
                p.strict_krx_2021_calendar_preopen_reference(bad)

    def test_2021_market_vintage_never_authorizes_any_economic_or_order_right(self):
        for day in ("2021-02-01", "2021-08-04", "2021-08-05"):
            v = p.strict_krx_2021_calendar_preopen_reference(day)
            for flag in (
                "official_exchange_publication_instant_verified",
                "official_asof_market_calendar_source_admitted",
                "individual_security_tradability_verified",
                "historical_source_publication_pit_verified",
                "m20_performance_run_authorized",
                "independent_holdout_authorized",
                "live_orders_authorized",
                "network_request_attempted",
            ):
                self.assertIs(v[flag], False, flag)
            self.assertEqual(v["ordering"], "DISABLED")

    def test_2021_retrospective_13_day_match_is_not_retroactive_preopen_proof(self):
        rows, source_sha = fixture()
        x = assess(rows, source_sha)
        self.assertTrue(x["source_date_by_date_retrospective_calendar_match"])
        pre = p.strict_krx_2021_calendar_preopen_reference("2021-08-04")
        self.assertEqual(pre["reference_market_closure_count"], 10)
        self.assertFalse(pre["official_asof_market_calendar_source_admitted"])
        self.assertFalse(x["2021_exchange_calendar_pit_admitted"])


    def test_private_root_unexpected_exceptions_redacted(self):
        # The stored source root can fail with unexpected exceptions before
        # any actual per-day object is read. Never expose private paths.
        for problem in (
            RuntimeError("PRIVATE_SOURCE_ROOT_PATH_20210816"),
            KeyError("PRIVATE_SECURITY_TOKEN_20211004"),
            AttributeError("PRIVATE_RAW_OBJECT_HASH_20210101"),
        ):
            with self.subTest(error=type(problem).__name__):
                read_called = []
                def forbidden_read(root, day):
                    read_called.append(day)
                    raise AssertionError("never read source after invalid root")
                def root_error(root):
                    raise problem
                out = p.run(
                    audit=True,
                    environment={
                        "RAILWAY_SERVICE_NAME": p.WORKER,
                        "KRX_PRIVATE_RAW_DIR": "/data",
                    },
                    verify_root=root_error,
                    check_day=forbidden_read,
                )
                self.assertEqual(read_called, [])
                self.assertEqual(
                    out["status"], "FAIL_CLOSED_PRIVATE_ROOT_NOT_VERIFIED")
                self.assertEqual(out["private_original_2021_weekday_pairs_verified"], 0)
                self.assertFalse(out["original_pair_fingerprint_matched"])
                self.assertFalse(out["source_date_by_date_retrospective_calendar_match"])
                self.assertFalse(out["raw_security_rows_or_private_dates_emitted"])
                self.assertFalse(out["official_exchange_calendar_pit_admitted"]
                                 if "official_exchange_calendar_pit_admitted" in out
                                 else out["2021_exchange_calendar_pit_admitted"])
                self.assertFalse(out["real_orders_authorized"])
                self.assertEqual(out["ordering"], "DISABLED")
                for forbidden in (
                    "PRIVATE_SOURCE_ROOT_PATH", "PRIVATE_SECURITY_TOKEN",
                    "PRIVATE_RAW_OBJECT_HASH", "20210816", "20211004", "20210101",
                ):
                    self.assertNotIn(forbidden, str(out))

    def test_root_failure_keeps_no_network_no_storage_writes(self):
        def unexpected(root):
            raise RuntimeError("PRIVATE_VOLUME_ACL_FAILURE")
        out = p.run(
            audit=True,
            environment={"RAILWAY_SERVICE_NAME": p.WORKER,
                         "KRX_PRIVATE_RAW_DIR": "/data"},
            verify_root=unexpected,
        )
        self.assertEqual(out["status"], "FAIL_CLOSED_PRIVATE_ROOT_NOT_VERIFIED")
        self.assertFalse(out["official_network_requests_made"]
                         if "official_network_requests_made" in out
                         else out.get("network_request_attempted", True))
        self.assertFalse(out["storage_mutated"])
        self.assertFalse(out["m20_performance_run_authorized"])


    def test_post_read_private_calendar_comparison_unexpected_failure_redacts_all(self):
        rows, _ = fixture()
        by_day = {row["day"]: row for row in rows}
        for problem in (
            RuntimeError("PRIVATE_2021_COMPARISON_20210816_SHA"),
            KeyError("PRIVATE_2021_ACCOUNT_PATH"),
            AttributeError("PRIVATE_2021_SECURITY_TOKEN"),
        ):
            with self.subTest(error=type(problem).__name__):
                seen = []
                def synthetic_read(root, day):
                    seen.append(day)
                    return by_day[day]
                with patch.object(p, "_source_rows_match_expected_calendar",
                                  side_effect=problem):
                    out = p.run(
                        audit=True,
                        environment={
                            "RAILWAY_SERVICE_NAME": p.WORKER,
                            "KRX_PRIVATE_RAW_DIR": "/data",
                        },
                        verify_root=lambda x: Path("/data/mock"),
                        check_day=synthetic_read,
                    )
                self.assertEqual(len(seen), 261)
                self.assertEqual(
                    out["status"],
                    "FAIL_CLOSED_PRIVATE_CALENDAR_COMPARISON_UNVERIFIED",
                )
                self.assertFalse(out["source_date_by_date_retrospective_calendar_match"])
                self.assertEqual(out["private_original_2021_weekday_pairs_verified"], 0)
                self.assertFalse(out["original_pair_fingerprint_matched"])
                self.assertFalse(out["2021_exchange_calendar_pit_admitted"])
                self.assertFalse(out["m20_performance_run_authorized"])
                self.assertFalse(out["real_orders_authorized"])
                self.assertFalse(out["raw_security_rows_or_private_dates_emitted"])
                self.assertFalse(out["network_request_attempted"])
                self.assertFalse(out["storage_mutated"])
                self.assertEqual(out["ordering"], "DISABLED")
                for forbidden in (
                    "PRIVATE_2021_COMPARISON", "PRIVATE_2021_ACCOUNT",
                    "PRIVATE_2021_SECURITY", "20210816",
                ):
                    self.assertNotIn(forbidden, str(out))



if __name__ == "__main__":
    unittest.main()
