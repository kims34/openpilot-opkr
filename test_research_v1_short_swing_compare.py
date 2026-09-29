import unittest

import pandas as pd

from research_v1_short_swing_compare import (
    BLOCK_LENGTH,
    compare_common_oos_paths,
    paired_moving_block_bootstrap_lcb,
)


class ShortSwingComparisonTest(unittest.TestCase):
    def test_only_shared_oos_span_is_compared(self):
        idx = pd.date_range("2026-01-01", periods=25, freq="B")
        h5 = pd.Series(0.01, index=idx[:20])
        h10 = pd.Series(0.02, index=idx[5:])
        out = compare_common_oos_paths(h5, h10)
        self.assertEqual(out["n_days"], 15)
        self.assertEqual(out["common_start"], str(idx[5]))
        self.assertEqual(out["common_end"], str(idx[19]))
        self.assertEqual(out["block_length"], BLOCK_LENGTH)
        self.assertAlmostEqual(out["mean_difference"], 0.01)

    def test_internal_missing_session_is_cash_zero(self):
        idx = pd.date_range("2026-01-01", periods=15, freq="B")
        h5 = pd.Series(0.01, index=idx)
        h10 = pd.Series(0.02, index=idx.delete(7))
        out = compare_common_oos_paths(h5, h10)
        expected = ((14 * 0.01) + (-0.01)) / 15
        self.assertEqual(out["n_days"], 15)
        self.assertAlmostEqual(out["mean_difference"], expected)

    def test_short_series_uses_full_length_blocks_without_short_resamples(self):
        out = paired_moving_block_bootstrap_lcb([0.01, -0.02, 0.03], block_length=10, samples=50)
        self.assertEqual(out["n_days"], 3)
        self.assertEqual(out["block_length"], 3)
        self.assertAlmostEqual(out["mean_difference"], (0.01 - 0.02 + 0.03) / 3)

    def test_empty_path_is_safe(self):
        out = paired_moving_block_bootstrap_lcb([])
        self.assertEqual(out["n_days"], 0)
        self.assertEqual(out["lcb95"], 0.0)


if __name__ == "__main__":
    unittest.main()
