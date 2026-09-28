import inspect
import unittest

import pandas as pd

from research_v1_distributional_netev import (
    CONTEXT_FEATURES,
    _pipe,
    distributional_walk_forward,
    freeze_original_topk,
)


class DistributionalNetEVRegressionTest(unittest.TestCase):
    def test_distributional_walk_forward_accepts_feature_override(self):
        params = inspect.signature(distributional_walk_forward).parameters
        self.assertIn("features", params)

    def test_pipe_uses_requested_feature_subset(self):
        features = [CONTEXT_FEATURES[0], CONTEXT_FEATURES[1]]
        model = _pipe(features)
        X = pd.DataFrame({features[0]: [0.0, 1.0, 2.0], features[1]: [1.0, 0.0, 1.0]})
        y = pd.Series([0.0, 0.01, -0.01])
        model.fit(X, y)
        pred = model.predict(X)
        self.assertEqual(len(pred), len(X))

    def test_freeze_original_topk_never_backfills_lower_rank(self):
        frame = pd.DataFrame(
            {
                "decision_date": ["2026-01-02"] * 5 + ["2026-01-05"] * 2,
                "symbol": ["A", "B", "C", "D", "E", "F", "G"],
                "score": [0.9, 0.8, 0.7, 0.6, 0.5, 0.9, 0.8],
            }
        )
        frozen = freeze_original_topk(frame, 3)
        day1 = frozen[frozen["decision_date"] == "2026-01-02"]["symbol"].tolist()
        day2 = frozen[frozen["decision_date"] == "2026-01-05"]["symbol"].tolist()
        self.assertEqual(day1, ["A", "B", "C"])
        self.assertEqual(day2, ["F", "G"])
        self.assertNotIn("D", day1)
        self.assertNotIn("E", day1)


if __name__ == "__main__":
    unittest.main()
