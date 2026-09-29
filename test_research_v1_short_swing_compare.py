import unittest

import pandas as pd

from research_v1_short_swing_compare import (
    BLOCK_LENGTH,
    compare_common_oos_paths,
    paired_moving_block_bootstrap_lcb,
)


class ShortSwingComparisonTest(unittest.TestCase):
    def test_cash_days_are_zero_and_paths_are_paired(self):
        idx = pd.date_range("2026-01-01", periods=25, freq="B")
        h5 = pd.Series(0.01, index=idx[:20])
        h10 = pd.Series(0.02, index=idx[5:])
        out = compare_common_oos_paths(h5, h10)
        self.assertEqual(out["n_days"], 25)
        self.assertEqual(out["block_length"], BLOCK_LENGTH)
        self.assertGreater(out["mean_difference"], 0.0)

    def test_empty_path_is_safe(self):
        out = paired_moving_block_bootstrap_lcb([])
        self.assertEqual(out["n_days"], 0)
        self.assertEqual(out["lcb95"], 0.0)


if __name__ == "__main__":
    unittest.main()

