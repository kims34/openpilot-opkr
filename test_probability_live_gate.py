import unittest

import probability_live_gate as gate


class ProspectiveBrierGateTests(unittest.TestCase):
    def test_before_minimum_keeps_historically_validated_candidate(self):
        rows = [(0.90, 0.50, 1.0)] * 10
        result = gate.evaluate(rows)
        self.assertEqual(result["status"], "historical_only")
        self.assertFalse(result["fallback"])
        self.assertEqual(result["n"], 10)

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
