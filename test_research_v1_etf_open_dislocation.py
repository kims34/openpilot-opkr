"""Synthetic fail-closed tests for IndexAlert's isolated ETF Open research."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
import unittest

from research_v1_etf_open_dislocation import (
    OfflineETFInputError, inspect_snapshot, replay_offline,
    _prohibited_state,
)
KST = timezone(timedelta(hours=9))


def ts(day="2026-10-26", clock="09:00:01"):
    return int(datetime.fromisoformat(
        day + "T" + clock + "+09:00").timestamp() * 1000)


def fixture():
    now = ts()
    return {
        "symbol": "123456", "venue": "KRX",
        "observed_at_ms": now, "quote_at_ms": now - 80,
        "bid_krw": 9990, "ask_krw": 10000,
        "bid_visible_qty": 200, "ask_visible_qty": 120,
        "nav_krw": 10110, "nav_at_ms": now - 800,
        "fx_at_ms": now - 450, "us_futures_at_ms": now - 300,
        "valuation_at_ms": now - 200,
        "fair_lower_krw": 10200, "fair_upper_krw": 10250,
    }


class ETFOpenOfflineResearchTest(unittest.TestCase):
    def test_illustrative_anomaly_only_observation_no_order(self):
        x = inspect_snapshot(fixture())
        self.assertEqual(x["status"], "OFFLINE_WATCH_ONLY_NO_ORDER")
        self.assertTrue(x["candidate"])
        self.assertGreaterEqual(x["gross_lower_bound_discount_bps"], 140)
        self.assertEqual(x["model_policy"], "ILLUSTRATIVE_UNCALIBRATED")
        for name, denied in _prohibited_state().items():
            self.assertEqual(x[name], denied, name)

    def test_no_fill_no_profit_is_claimed(self):
        x = replay_offline([fixture()])
        self.assertEqual(x["synthetic_discount_candidates"], 1)
        self.assertEqual(x["orders_submitted"], 0)
        self.assertEqual(x["positions_opened"], 0)
        self.assertEqual(x["fills_verified"], 0)
        self.assertFalse(x["net_profit_calculated"])
        self.assertFalse(x["net_after_tax_profit_verified"])
        self.assertEqual(x["ordering"], "DISABLED")

    def test_inav_alone_cannot_replace_fx_and_futures_asof_sources(self):
        x = fixture()
        del x["fx_at_ms"]
        with self.assertRaises(OfflineETFInputError):
            inspect_snapshot(x)
        x = fixture()
        del x["us_futures_at_ms"]
        with self.assertRaises(OfflineETFInputError):
            inspect_snapshot(x)

    def test_missing_fields_extra_fields_and_unknown_market_denied(self):
        with self.assertRaises(OfflineETFInputError):
            inspect_snapshot({})
        x = fixture()
        x["secret_broker_account"] = "private"
        with self.assertRaises(OfflineETFInputError):
            inspect_snapshot(x)
        x = fixture()
        x["venue"] = "KRX_DERIVATIVES"
        with self.assertRaises(OfflineETFInputError):
            inspect_snapshot(x)

    def test_invalid_book_crossed_locked_and_zero_size(self):
        for bid, ask, qty in ((10000, 10000, 100), (10001, 10000, 100),
                              (9990, 10000, 0)):
            x = fixture()
            x.update(bid_krw=bid, ask_krw=ask, ask_visible_qty=qty)
            with self.subTest(bid=bid, ask=ask, qty=qty):
                with self.assertRaises(OfflineETFInputError):
                    inspect_snapshot(x)

    def test_non_numeric_and_bool_values_denied(self):
        for value in (True, 10.5, "10000", -1):
            x = fixture()
            x["ask_krw"] = value
            with self.subTest(value=value), self.assertRaises(
                    OfflineETFInputError):
                inspect_snapshot(x)

    def test_not_9am_eligibility_preopen(self):
        x = fixture()
        x["observed_at_ms"] = ts(clock="08:59:59")
        x["quote_at_ms"] = x["observed_at_ms"]
        x["nav_at_ms"] = x["observed_at_ms"]
        x["fx_at_ms"] = x["observed_at_ms"]
        x["us_futures_at_ms"] = x["observed_at_ms"]
        x["valuation_at_ms"] = x["observed_at_ms"]
        self.assertEqual(inspect_snapshot(x)["reason"], "NOT_0900_TO_0905_KRX_WEEKDAY")

    def test_9_05_is_outside_this_initial_hypothesis(self):
        x = fixture()
        x["observed_at_ms"] = ts(clock="09:05:00")
        for k in ("quote_at_ms", "nav_at_ms", "fx_at_ms",
                  "us_futures_at_ms", "valuation_at_ms"):
            x[k] = x["observed_at_ms"]
        self.assertEqual(inspect_snapshot(x)["reason"], "NOT_0900_TO_0905_KRX_WEEKDAY")

    def test_weekend_rejected_without_calendar_claim(self):
        x = fixture()
        x["observed_at_ms"] = ts(day="2026-10-25")
        for k in ("quote_at_ms", "nav_at_ms", "fx_at_ms",
                  "us_futures_at_ms", "valuation_at_ms"):
            x[k] = x["observed_at_ms"]
        y = inspect_snapshot(x)
        self.assertFalse(y["candidate"])
        self.assertFalse(y["official_krx_session_verified"])

    def test_any_future_timestamp_is_lookahead_not_edge(self):
        for key in ("quote_at_ms", "nav_at_ms", "fx_at_ms",
                    "us_futures_at_ms", "valuation_at_ms"):
            x = fixture()
            x[key] = x["observed_at_ms"] + 1
            with self.subTest(field=key):
                y = inspect_snapshot(x)
                self.assertEqual(y["reason"], "FUTURE_DATED_REFERENCE_LOOKAHEAD")
                self.assertFalse(y["candidate"])

    def test_stale_quote_nav_fx_futures_and_valuation_each_block(self):
        for key in ("quote_at_ms", "nav_at_ms", "fx_at_ms",
                    "us_futures_at_ms", "valuation_at_ms"):
            x = fixture()
            x[key] = x["observed_at_ms"] - 4000
            with self.subTest(field=key):
                y = inspect_snapshot(x)
                self.assertEqual(y["reason"], "REFERENCE_OR_BOOK_STALE")
                self.assertFalse(y["candidate"])

    def test_fair_interval_uncertainty_and_inversion(self):
        x = fixture()
        x["fair_upper_krw"] = 10400
        self.assertEqual(inspect_snapshot(x)["reason"],
                         "FAIR_VALUE_UNCERTAINTY_TOO_WIDE")
        x["fair_upper_krw"] = 10199
        with self.assertRaises(OfflineETFInputError):
            inspect_snapshot(x)

    def test_valuation_cannot_use_a_later_reference(self):
        for key in ("nav_at_ms", "fx_at_ms", "us_futures_at_ms"):
            x = fixture()
            x[key] = x["valuation_at_ms"] + 1
            with self.subTest(field=key):
                y = inspect_snapshot(x)
                self.assertFalse(y["candidate"])
                self.assertEqual(y["reason"],
                                 "VALUATION_PRECEDES_REQUIRED_REFERENCE")
                for name, denied in _prohibited_state().items():
                    self.assertEqual(y[name], denied)

    def test_valuation_reference_exact_boundary(self):
        x = fixture()
        for key in ("nav_at_ms", "fx_at_ms", "us_futures_at_ms"):
            x[key] = x["valuation_at_ms"]
        self.assertTrue(inspect_snapshot(x)["candidate"])

    def test_uncertainty_fractional_bps_above_limit_rejected(self):
        x = fixture()
        x.update(fair_lower_krw=10000, fair_upper_krw=10081)
        self.assertEqual(inspect_snapshot(x)["reason"],
                         "FAIR_VALUE_UNCERTAINTY_TOO_WIDE")

    def test_uncertainty_exact_limit_allowed(self):
        x = fixture()
        x.update(fair_lower_krw=10250, fair_upper_krw=10332)
        self.assertTrue(inspect_snapshot(x)["candidate"])

    def test_high_ask_not_discount_even_if_nav_appears_low(self):
        x = fixture()
        x["ask_krw"] = 10210
        x["bid_krw"] = 10200
        y = inspect_snapshot(x)
        self.assertEqual(y["reason"], "NO_CONSERVATIVE_CANDIDATE")
        self.assertFalse(y["candidate"])

    def test_exact_source_receipt_time_not_wallclock_future_allowed(self):
        x = fixture()
        for k in ("quote_at_ms", "nav_at_ms", "fx_at_ms",
                  "us_futures_at_ms", "valuation_at_ms"):
            x[k] = x["observed_at_ms"]
        self.assertTrue(inspect_snapshot(x)["candidate"])

    def test_unsorted_duplicate_and_unbounded_replay_fail_closed(self):
        x = fixture()
        with self.assertRaises(OfflineETFInputError):
            replay_offline([x, x])
        with self.assertRaises(OfflineETFInputError):
            replay_offline([dict(x, observed_at_ms=x["observed_at_ms"] + 20), x])
        with self.assertRaises(OfflineETFInputError):
            replay_offline([])
        with self.assertRaises(OfflineETFInputError):
            replay_offline([x] * 10001)

    def test_mixed_replay_count_has_no_strategy_return(self):
        a = fixture()
        b = dict(a)
        b["observed_at_ms"] += 100
        b["quote_at_ms"] += 100
        b["nav_at_ms"] += 100
        b["fx_at_ms"] += 100
        b["us_futures_at_ms"] += 100
        b["valuation_at_ms"] += 100
        b["ask_krw"] = 10180
        b["bid_krw"] = 10170
        y = replay_offline([a, b])
        self.assertEqual(y["synthetic_discount_candidates"], 1)
        self.assertEqual(y["rejected_or_non_signal_snapshots"], 1)
        self.assertEqual(y["snapshots_observed"], 2)
        self.assertNotIn("annual_return", y)
        self.assertNotIn("profit_factor", y)

    def test_cannot_override_any_hard_safety_flag_through_user_event(self):
        x = fixture()
        x["live_orders_authorized"] = True
        with self.assertRaises(OfflineETFInputError):
            inspect_snapshot(x)


if __name__ == "__main__":
    unittest.main()

