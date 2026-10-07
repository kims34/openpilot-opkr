import unittest

import probability_live_gate as gate


class ProspectiveBrierGateTests(unittest.TestCase):
    def test_before_minimum_keeps_historically_validated_candidate(self):
        rows = [(0.90, 0.50, 1.0)] * 10
        result = gate.evaluate(rows)
        self.assertEqual(result["status"], "historical_only")
        self.assertFalse(result["fallback"])
        self.assertEqual(result["n"], 10)

    def test_zero_scored_rows_is_valid_historical_only_state(self):
        verdict = gate.evaluate([])
        self.assertEqual(verdict["status"], "historical_only")
        self.assertFalse(verdict["fallback"])
        self.assertTrue(verdict["score_rows_structurally_valid"])
        raw = {"probability": 57.0, "base_rate": 52.0}
        out = gate.apply(raw, verdict, "base_rate")
        self.assertEqual(out["probability"], 57.0)
        self.assertEqual(out["served_from"], "candidate")

    def test_confirmed_live_advantage_keeps_candidate(self):
        rows = [(0.90, 0.50, 1.0)] * 30
        result = gate.evaluate(rows)
        self.assertEqual(result["status"], "live_confirmed")
        self.assertFalse(result["fallback"])
        self.assertGreater(result["ci_low"], 0.0)

    def test_inconclusive_live_evidence_falls_back(self):
        rows = [(0.60, 0.60, float(i % 2)) for i in range(30)]
        result = gate.evaluate(rows)
        self.assertEqual(result["status"], "fallback_inconclusive")
        self.assertTrue(result["fallback"])

    def test_live_underperformance_falls_back(self):
        rows = [(0.10, 0.90, 1.0)] * 30
        result = gate.evaluate(rows)
        self.assertEqual(result["status"], "fallback_underperforming")
        self.assertTrue(result["fallback"])
        self.assertLess(result["ci_high"], 0.0)

    def test_malformed_score_rows_fail_closed_instead_of_being_dropped(self):
        bad_rows = [
            [(0.9, 0.5)],
            [("0.9", 0.5, 1.0)],
            [(True, 0.5, 1.0)],
            [(float("nan"), 0.5, 1.0)],
            [(0.9, 0.5, 0.5)],
            [(0.9, 0.5, 1.0, 99)],
        ]
        for rows in bad_rows:
            with self.subTest(rows=rows):
                with self.assertRaises(gate.ProbabilityLiveGateError):
                    gate.evaluate(rows)

    def test_minimum_sample_requires_exact_positive_integer(self):
        for value in (True, 0, -1, 30.0, "30", None):
            with self.subTest(value=value):
                with self.assertRaises(gate.ProbabilityLiveGateError):
                    gate.evaluate([], min_n=value)

    def test_gate_output_cannot_be_forged_to_disable_required_fallback(self):
        verdict = gate.evaluate([(0.60, 0.60, float(i % 2)) for i in range(30)])
        self.assertTrue(verdict["fallback"])
        forged = dict(verdict, fallback=False)
        raw = {"probability": 57.0, "base_rate": 52.0}
        with self.assertRaises(gate.ProbabilityLiveGateError):
            gate.apply(raw, forged, "base_rate")

    def test_gate_never_self_verifies_live_provenance(self):
        verdict = gate.evaluate([(0.90, 0.50, 1.0)] * 30)
        self.assertTrue(verdict["score_rows_structurally_valid"])
        self.assertFalse(verdict["independent_live_provenance_verified"])
        self.assertEqual(verdict["status_scope"], "PROSPECTIVE_SCORE_ONLY")

    def test_fail_safe_helper_serves_previous_probability(self):
        raw = {
            "probability": 61.0,
            "preopen_probability": 54.0,
            "status": "개장후 시가 반영",
        }
        out = gate.fail_safe_to_previous(
            raw, "preopen_probability", error_code="PROSPECTIVE_GATE_UNAVAILABLE"
        )
        self.assertEqual(out["probability"], 54.0)
        self.assertEqual(out["served_probability"], 54.0)
        self.assertEqual(out["served_from"], "previous_stage")
        self.assertEqual(out["live_gate_status"], "fallback_gate_unavailable")
        self.assertFalse(out["live_gate_independent_provenance_verified"])

    def test_required_fallback_without_reference_fails_closed(self):
        verdict = gate.evaluate([(0.60, 0.60, float(i % 2)) for i in range(30)])
        with self.assertRaises(gate.ProbabilityLiveGateError):
            gate.apply({"probability": 57.0}, verdict, "base_rate")

    def test_apply_preserves_model_internal_candidate_and_uses_reference(self):
        raw = {
            "probability": 57.0,
            "base_rate": 52.0,
            "candidate_probability": 61.0,
            "status": "validated",
        }
        verdict = gate.evaluate([(0.57, 0.52, float(i % 2)) for i in range(30)])
        out = gate.apply(raw, verdict, "base_rate")
        self.assertEqual(out["candidate_probability"], 61.0)
        self.assertEqual(out["live_candidate_probability"], 57.0)
        self.assertEqual(out["probability"], 52.0)
        self.assertEqual(out["served_probability"], 52.0)
        self.assertEqual(out["served_from"], "previous_stage")
        self.assertEqual(out["live_gate_policy_version"], gate.SERVING_POLICY_VERSION)


if __name__ == "__main__":
    unittest.main()
