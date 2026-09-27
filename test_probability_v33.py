import unittest
import numpy as np

import probability_model_v33_runtime as v33


def synthetic_prices(n=1800, seed=733):
    rng = np.random.default_rng(seed)
    return (100 * np.exp(np.cumsum(rng.normal(0.00025, 0.011, n)))).tolist()


class ProbabilityV33Tests(unittest.TestCase):
    def test_version_and_probability_range(self):
        r = v33.estimate_prices(synthetic_prices())
        self.assertEqual(r["model_version"], "3.3-calibration-gated")
        self.assertGreaterEqual(r["probability"], 0.0)
        self.assertLessEqual(r["probability"], 100.0)
        self.assertIn(r["calibration_alpha"], v33.CALIBRATION_ALPHAS)

    def test_calibration_gate_never_claims_worse_audit(self):
        r = v33.estimate_prices(synthetic_prices(1900, 811))
        if r["calibration_gate_passed"]:
            self.assertLess(r["calibration_audit_brier"], r["previous_audit_brier"])
            self.assertLessEqual(r["calibration_first_half_brier"], r["previous_first_half_brier"] + 1e-12)
            self.assertLessEqual(r["calibration_second_half_brier"], r["previous_second_half_brier"] + 1e-12)
        else:
            self.assertAlmostEqual(r["probability"], r["previous_model_probability"], places=10)

    def test_audit_forecast_does_not_use_its_own_outcome(self):
        p = synthetic_prices(1600, 921)
        before = v33.estimate_prices(p, include_trace=True)
        row = before["audit_trace"][20]
        t = row["t"]
        altered = p.copy()
        altered[t + 1] *= 1.25
        after = v33.estimate_prices(altered, include_trace=True)
        self.assertAlmostEqual(
            before["audit_trace"][20]["probability"],
            after["audit_trace"][20]["probability"],
            places=12,
        )
        self.assertEqual(
            before["audit_trace"][20]["alpha"],
            after["audit_trace"][20]["alpha"],
        )

    def test_invalid_prices_fail(self):
        p = synthetic_prices(1600)
        p[700] = 0.0
        with self.assertRaises(ValueError):
            v33.estimate_prices(p)


if __name__ == "__main__":
    unittest.main()
