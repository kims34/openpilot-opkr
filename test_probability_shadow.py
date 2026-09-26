import os
import sqlite3
import tempfile
import unittest

import probability_shadow as shadow


class ShadowProbabilityTests(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(prefix="indexalert-shadow-", suffix=".db")
        os.close(fd)

    def tearDown(self):
        try:
            os.remove(self.path)
        except FileNotFoundError:
            pass

    def _result(self, as_of, target, target_open, probability=60.0, base=55.0):
        return {
            "as_of": as_of,
            "target_date": target,
            "target_open": target_open,
            "probability": probability,
            "base_rate": base,
        }

    def test_preopen_forecasts_are_immutable_and_scored_once(self):
        first = self._result("2026-09-24", "2026-09-25", 1000.0, 60.0, 55.0)
        scores = shadow.record_shadow_forecasts(
            "SPY", first, [("2026-09-24", 100.0)], 500.0, self.path
        )
        self.assertEqual(scores, {})

        # Same as_of with different probability must not overwrite the forecast.
        changed = self._result("2026-09-24", "2026-09-25", 1000.0, 90.0, 55.0)
        shadow.record_shadow_forecasts(
            "SPY", changed, [("2026-09-24", 100.0)], 600.0, self.path
        )
        with sqlite3.connect(self.path) as con:
            rows = con.execute(
                "SELECT model,p FROM probability_shadow_forecasts ORDER BY model"
            ).fetchall()
        self.assertEqual(len(rows), len(shadow.SHADOW_MODELS))
        expected = shadow._probabilities(first)
        for model, p in rows:
            self.assertAlmostEqual(p, expected[model])

        # Once target close exists, each old forecast is scored exactly once.
        second = self._result("2026-09-25", "2026-09-28", 2000.0, 40.0, 50.0)
        scores = shadow.record_shadow_forecasts(
            "SPY",
            second,
            [("2026-09-24", 100.0), ("2026-09-25", 101.0)],
            1500.0,
            self.path,
        )
        self.assertEqual(set(scores), set(shadow.SHADOW_MODELS))
        self.assertTrue(all(item["count"] == 1 for item in scores.values()))

        # Re-scoring cannot alter the realised outcome or increment the count.
        scores2 = shadow.record_shadow_forecasts(
            "SPY",
            second,
            [("2026-09-24", 100.0), ("2026-09-25", 101.0)],
            1600.0,
            self.path,
        )
        self.assertEqual(scores, scores2)

    def test_late_forecast_is_not_recorded(self):
        result = self._result("2026-09-24", "2026-09-25", 1000.0)
        shadow.record_shadow_forecasts(
            "QQQ", result, [("2026-09-24", 100.0)], 1001.0, self.path
        )
        with sqlite3.connect(self.path) as con:
            count = con.execute(
                "SELECT COUNT(*) FROM probability_shadow_forecasts"
            ).fetchone()[0]
        self.assertEqual(count, 0)

    def test_shadow_formulas_stay_in_probability_range(self):
        for p in (0.0, 25.0, 50.0, 75.0, 100.0):
            for base in (0.0, 50.0, 100.0):
                values = shadow._probabilities(
                    self._result("a", "b", 1.0, probability=p, base=base)
                )
                self.assertTrue(all(0.0 <= value <= 1.0 for value in values.values()))


if __name__ == "__main__":
    unittest.main()
