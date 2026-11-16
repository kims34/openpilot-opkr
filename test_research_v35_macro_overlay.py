"""Deterministic synthetic guardrails, never claims real financial accuracy."""
import copy
import random
import unittest
from datetime import date, datetime, time, timedelta, timezone

import research_v35_macro_overlay as research


def specimen(n=105):
    rng = random.Random(352026)
    start = date(2025, 1, 1)
    rows = []
    for i in range(n):
        day = start + timedelta(days=i)
        target = day + timedelta(days=1)
        high = (i % 8 < 4)
        vix = 30.0 if high else 12.0
        chance = 0.81 if high else 0.17
        outcome = int(rng.random() < chance)
        prediction = datetime.combine(day, time(16, 30, tzinfo=timezone.utc)).isoformat()
        published = datetime.combine(day, time(16, 15, tzinfo=timezone.utc)).isoformat()
        close = datetime.combine(target, time(16, 0, tzinfo=timezone.utc)).isoformat()
        known = datetime.combine(target, time(16, 20, tzinfo=timezone.utc)).isoformat()
        signals = {
            "vix": vix,
            "us10y": 3.2 + (0.15 if high else -0.15),
            "breadth": 0.40 if high else 0.68,
        }
        features = {
            key: {
                "value": val, "session": day.isoformat(),
                "published_at": published, "source_quality": "public_backfill",
            }
            for key, val in signals.items()
        }
        rows.append({
            "as_of": day.isoformat(),
            "target_date": target.isoformat(),
            "prediction_at": prediction,
            "baseline_issued_at": published,
            "target_close_at": close,
            "outcome_known_at": known,
            "outcome": outcome,
            "baseline_probability": 0.5,
            "features": features,
        })
    return rows


class MacroOverlayTests(unittest.TestCase):
    def test_synthetic_research_runs_but_never_admits_to_production(self):
        result = research.evaluate(specimen(), min_train=20, test_sessions=24, min_dev_half=12)
        self.assertEqual(result["rows"], 105)
        self.assertEqual(result["production_admission"], "BLOCKED")
        self.assertFalse(result["order_authorization"])
        self.assertEqual(result["source_evidence"]["source_quality"], "PUBLIC_BACKFILL_NO_PIT_PROOF")
        self.assertEqual(len(result["candidates"]), 3)

    def test_future_outcomes_do_not_modify_earlier_prediction(self):
        rows = specimen()
        early = research.predict_at(rows, 75, ("vix",), min_train=20)
        mutated = copy.deepcopy(rows)
        for x in mutated[76:]:
            x["outcome"] ^= 1
        late = research.predict_at(mutated, 75, ("vix",), min_train=20)
        self.assertAlmostEqual(early, late, places=13)

    def test_unpublished_historical_outcome_is_not_trained_on(self):
        rows = specimen()
        t = 70
        delayed = copy.deepcopy(rows)
        delayed[t - 1]["outcome_known_at"] = (
            datetime.fromisoformat(delayed[t]["prediction_at"]) + timedelta(hours=10)
        ).isoformat()
        p1 = research.predict_at(delayed, t, ("vix",), min_train=20)
        delayed[t - 1]["outcome"] ^= 1
        p2 = research.predict_at(delayed, t, ("vix",), min_train=20)
        self.assertAlmostEqual(p1, p2, places=13)

    def test_future_published_vix_is_rejected(self):
        rows = specimen()
        rows[25]["features"]["vix"]["published_at"] = (
            datetime.fromisoformat(rows[25]["prediction_at"]) + timedelta(seconds=1)
        ).isoformat()
        with self.assertRaises(research.EvidenceError):
            research.validate(rows)

    def test_future_feature_session_is_rejected(self):
        rows = specimen()
        rows[25]["features"]["breadth"]["session"] = rows[25]["target_date"]
        with self.assertRaises(research.EvidenceError):
            research.validate(rows)

    def test_future_baseline_is_rejected(self):
        rows = specimen()
        rows[25]["baseline_issued_at"] = rows[25]["outcome_known_at"]
        with self.assertRaises(research.EvidenceError):
            research.validate(rows)

    def test_naive_timestamp_is_rejected(self):
        rows = specimen()
        rows[0]["prediction_at"] = "2025-01-01T16:30:00"
        with self.assertRaises(research.EvidenceError):
            research.validate(rows)

    def test_invalid_and_out_of_order_rows_fail_closed(self):
        rows = specimen()
        rows[5], rows[6] = rows[6], rows[5]
        with self.assertRaises(research.EvidenceError):
            research.evaluate(rows, min_train=20, test_sessions=24, min_dev_half=12)
        rows = specimen()
        rows[5]["outcome"] = 0.6
        with self.assertRaises(research.EvidenceError):
            research.validate(rows)

    def test_only_vix_candidate_when_other_sources_missing(self):
        rows = specimen()
        for r in rows:
            del r["features"]["us10y"]
            del r["features"]["breadth"]
        result = research.evaluate(rows, min_train=20, test_sessions=24, min_dev_half=12)
        self.assertEqual([x["features"] for x in result["candidates"]], ["vix"])

    def test_unknown_or_unproven_source_type_is_rejected(self):
        rows = specimen()
        rows[3]["features"]["vix"]["source_quality"] = "original_verified_trust_me"
        with self.assertRaises(research.EvidenceError):
            research.validate(rows)

    def test_no_training_from_current_outcome(self):
        rows = specimen()
        before = research.predict_at(rows, 75, ("vix", "us10y"), min_train=20)
        rows[75]["outcome"] ^= 1
        after = research.predict_at(rows, 75, ("vix", "us10y"), min_train=20)
        self.assertAlmostEqual(before, after, places=13)

    def test_insufficient_chronological_evidence_does_not_pass(self):
        with self.assertRaises(research.EvidenceError):
            research.evaluate(specimen(34), min_train=20, test_sessions=20, min_dev_half=8)


if __name__ == "__main__":
    unittest.main()
