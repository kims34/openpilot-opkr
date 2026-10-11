"""Synthetic only. No OpenAPI access, no secrets, no portfolio outcomes."""
import copy
import dataclasses
import json
import unittest

from research_v1_krx_sep28_entry_quarantine_shadow import (
    EntryQuarantineError,
    evaluate_new_entry_quarantine_shadow,
)

SOURCE = "2026-09-28"
OBSERVED = "2026-10-10T10:30:00+09:00"
DECISION = "2026-10-12T18:31:00+09:00"


def rows():
    data = []
    for i in range(1, 804):
        common = {
            "source_session": SOURCE,
            "symbol": f"{i:06d}",
            "open": "10,000", "high": "10,200",
            "low": "9,900", "close": "10,100",
            "volume": "1,000", "value": "10,100,000",
        }
        if i <= 27:
            common.update(open="0", high="0", low="0",
                          close="10,100", volume="0", value="0")
        data.append(common)
    return data


def top(symbols=("000003", "000040", "000041")):
    return [
        {"symbol": symbol, "score": float(3-i),
         "normal_market_eligible": True}
        for i, symbol in enumerate(symbols)
    ]


def evaluate(**overrides):
    params = {
        "source_session": SOURCE,
        "source_observed_at": OBSERVED,
        "decision_at": DECISION,
        "source_raw_sha256_claim": "a" * 64,
        "common_stock_observations": rows(),
        "original_top3": top(),
        "held_positions": [
            {"position_id": "held-1", "symbol": "000003", "unresolved_qty": 17},
            {"position_id": "held-2", "symbol": "000040", "unresolved_qty": 2},
        ],
    }
    params.update(overrides)
    return evaluate_new_entry_quarantine_shadow(**params)


class Sep28QuarantineShadowTests(unittest.TestCase):
    def test_exact_27_is_entry_veto_only_with_no_backfill(self):
        output = evaluate()
        self.assertEqual([x[0] for x in output.private_slot_decisions], [1,2,3])
        self.assertEqual(
            [x[2] for x in output.private_slot_decisions],
            ["NEW_ENTRY_QUARANTINE_VETO",
             "STRUCTURALLY_RETAINED_NOT_AUTHORIZED",
             "STRUCTURALLY_RETAINED_NOT_AUTHORIZED"],
        )
        summary = output.summary
        self.assertEqual(summary["observed_common_stock_count"], 803)
        self.assertEqual(summary["observed_nonpositive_count"], 27)
        self.assertEqual(summary["observed_remaining_source_rows"], 776)
        self.assertEqual(summary["shadow_structurally_retained_slots"], 2)
        self.assertEqual(summary["shadow_anomalous_new_entry_veto_slots"], 1)
        self.assertIs(summary["rank4plus_backfill"], False)
        self.assertIs(summary["canonical_krx_source_fail_closed_preserved"], True)

    def test_held_positions_never_removed_or_marked_economically_resolved(self):
        held = [
            {"position_id": "old", "symbol": "000001", "unresolved_qty": 42},
            {"position_id": "other", "symbol": "000040", "unresolved_qty": 3},
        ]
        original = copy.deepcopy(held)
        result = evaluate(held_positions=held)
        self.assertEqual(held, original)
        self.assertEqual(result.summary["held_positions_observed_count"], 2)
        self.assertEqual(result.summary["held_positions_overlapping_quarantine_count"], 1)
        self.assertTrue(result.summary["held_positions_untouched"])
        self.assertFalse(result.summary["held_positions_exact_economics_verified"])

    def test_before_actual_observation_is_future_leakage(self):
        with self.assertRaisesRegex(EntryQuarantineError, "FUTURE_OBSERVATION_LEAKAGE"):
            evaluate(decision_at="2026-10-07T18:31:00+09:00")
        with self.assertRaisesRegex(EntryQuarantineError, "FUTURE_OBSERVATION_LEAKAGE"):
            evaluate(decision_at="2026-09-28T18:31:00+09:00")

    def test_original_market_veto_is_not_overridden(self):
        a = top()
        a[1]["normal_market_eligible"] = False
        s = evaluate(original_top3=a).summary
        self.assertEqual(s["pre_existing_market_veto_slots"], 1)
        self.assertEqual(s["shadow_structurally_retained_slots"], 1)

    def test_unknown_source_symbol_is_vetoed_not_assumed_safe(self):
        s = evaluate(original_top3=top(["999999", "000040", "000041"])).summary
        self.assertEqual(s["unknown_source_veto_slots"], 1)
        self.assertEqual(s["shadow_structurally_retained_slots"], 2)

    def test_vetoed_all_top3_records_no_trade_not_rank4(self):
        s = evaluate(original_top3=top(["000001", "000002", "000003"])).summary
        self.assertTrue(s["no_trade_observation"])
        self.assertEqual(s["shadow_structurally_retained_slots"], 0)
        self.assertFalse(s["rank4plus_backfill"])

    def test_cannot_reduce_or_expand_original_top3(self):
        with self.assertRaisesRegex(EntryQuarantineError, "TOP3_SCOPE"):
            evaluate(original_top3=top(["000001", "000002", "000003", "000040"]))
        with self.assertRaisesRegex(EntryQuarantineError, "TOP3_ORDER"):
            evaluate(original_top3=list(reversed(top())))
        with self.assertRaisesRegex(EntryQuarantineError, "TOP3_SCOPE"):
            evaluate(original_top3=top(["000040", "000040"]))
        a = top()
        a[0]["score"] = True
        with self.assertRaises(EntryQuarantineError):
            evaluate(original_top3=a)

    def test_anomaly_count_or_price_shape_change_fails_closed(self):
        fewer = rows()
        fewer[0].update(open="10,000", high="10,200", low="9,900", volume="1,000", value="10,100,000")
        with self.assertRaisesRegex(EntryQuarantineError, "SOURCE_ANOMALY_COUNT_CHANGED"):
            evaluate(common_stock_observations=fewer)
        changed = rows()
        changed[0]["volume"] = "1"
        with self.assertRaisesRegex(EntryQuarantineError, "SOURCE_ANOMALY_SHAPE_CHANGED"):
            evaluate(common_stock_observations=changed)
        invalid = rows()
        invalid[40]["low"] = "11,000"
        with self.assertRaisesRegex(EntryQuarantineError, "SOURCE_POSITIVE_PRICE_INVALID"):
            evaluate(common_stock_observations=invalid)

    def test_incomplete_duplicate_or_mixed_source_scope_fails_closed(self):
        fewer = rows()[:-1]
        with self.assertRaisesRegex(EntryQuarantineError, "UNVERIFIED_COMMON_STOCK_SCOPE"):
            evaluate(common_stock_observations=fewer)
        duplicated = rows()
        duplicated[-1]["symbol"] = duplicated[0]["symbol"]
        with self.assertRaisesRegex(EntryQuarantineError, "DUPLICATE_SOURCE_SYMBOL"):
            evaluate(common_stock_observations=duplicated)
        mixed = rows()
        mixed[-1]["source_session"] = "2026-09-29"
        with self.assertRaisesRegex(EntryQuarantineError, "SOURCE_ROW_SESSION_MISMATCH"):
            evaluate(common_stock_observations=mixed)

    def test_rejects_malformed_numbers_and_dates(self):
        bad = rows()
        bad[60]["value"] = -1
        with self.assertRaises(EntryQuarantineError):
            evaluate(common_stock_observations=bad)
        bad = rows()
        bad[60]["volume"] = "3e9"
        with self.assertRaises(EntryQuarantineError):
            evaluate(common_stock_observations=bad)
        with self.assertRaisesRegex(EntryQuarantineError, "AWARE_TIMESTAMP_REQUIRED"):
            evaluate(decision_at="2026-10-12T18:31:00")
        with self.assertRaisesRegex(EntryQuarantineError, "SESSION_OUTSIDE_PINNED"):
            evaluate(source_session="2026-09-29")

    def test_missing_held_scope_fails_closed(self):
        with self.assertRaisesRegex(EntryQuarantineError, "HELD_POSITION_SCOPE_MISSING"):
            evaluate(held_positions=None)
        with self.assertRaisesRegex(EntryQuarantineError, "HELD_POSITION_SCOPE_INVALID"):
            evaluate(held_positions=[{"position_id": "x", "symbol": "000001"},
                                     {"position_id": "x", "symbol": "000040"}])

    def test_all_authority_and_metrics_remain_false(self):
        summary = evaluate().summary
        for key in (
            "source_original_bytes_independently_verified_here",
            "full_source_admission_verified", "official_halt_status_verified",
            "historical_pit_backtest_authorized",
            "prospective_alpha_admission_authorized",
            "independent_holdout_authorized", "champion_change_authorized",
            "net_ev_certified", "held_positions_exact_economics_verified",
            "real_orders_authorized", "funds_movement_authorized",
            "permission_change_authorized",
        ):
            self.assertIs(summary[key], False, key)
        self.assertEqual(summary["ordering"], "DISABLED")
        self.assertFalse("000003" in json.dumps(summary))
        self.assertFalse("held-1" in json.dumps(summary))
        self.assertFalse("a" * 64 in json.dumps(summary))
        self.assertNotIn("000003", repr(evaluate()))

    def test_synthetic_input_never_modified(self):
        raw = rows()
        prior = copy.deepcopy(raw)
        ranked = top()
        ranked_before = copy.deepcopy(ranked)
        held = [{"position_id": "one", "symbol": "000003"}]
        output = evaluate(common_stock_observations=raw,original_top3=ranked,held_positions=held)
        self.assertEqual(raw, prior)
        self.assertEqual(ranked, ranked_before)
        self.assertEqual(held, [{"position_id": "one", "symbol": "000003"}])
        self.assertEqual(len(output.private_slot_decisions), 3)


if __name__ == "__main__":
    unittest.main()
