import unittest
import numpy as np

import probability_model_v34_runtime as v34


class ProbabilityV34Tests(unittest.TestCase):
    def synthetic(self, n=1800):
        rng = np.random.default_rng(20260927)
        r = rng.normal(0.00035, 0.011, n - 1)
        p = np.empty(n)
        p[0] = 100.0
        for i, x in enumerate(r, 1):
            p[i] = p[i - 1] * np.exp(x)
        dates = np.busday_offset('2019-01-01', np.arange(n), roll='forward').astype(str).tolist()
        return p, dates

    def test_probability_is_bounded(self):
        p, dates = self.synthetic()
        out = v34.estimate_prices(p, dates=dates, target_date=dates[-1])
        self.assertGreaterEqual(out['probability'], 0.0)
        self.assertLessEqual(out['probability'], 100.0)

    def test_future_prices_do_not_change_past_forecast(self):
        p, dates = self.synthetic()
        cut = 1500
        a = v34.estimate_prices(p[:cut], dates=dates[:cut], target_date=dates[cut])
        changed = p.copy()
        changed[cut:] *= np.linspace(0.7, 1.4, len(changed) - cut)
        b = v34.estimate_prices(changed[:cut], dates=dates[:cut], target_date=dates[cut])
        self.assertAlmostEqual(a['probability'], b['probability'], places=12)
        self.assertEqual(a['feature_strategy'], b['feature_strategy'])

    def test_failed_gate_falls_back(self):
        p, dates = self.synthetic()
        out = v34.estimate_prices(p, dates=dates, target_date=dates[-1])
        if not out['feature_gate_passed']:
            self.assertTrue(out['fallback_to_previous'])
            self.assertEqual(out['validation_choice'], '3.3_safe_fallback')


if __name__ == '__main__':
    unittest.main()
