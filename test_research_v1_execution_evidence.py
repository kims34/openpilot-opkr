import unittest

import numpy as np
import pandas as pd

from research_v1_execution_evidence import (
    EMPIRICAL_EXECUTION_SOURCE,
    ExecutionEvidenceError,
    audit_execution_evidence,
    validate_execution_observations,
)


class TestExecutionEvidence(unittest.TestCase):
    def _rows(self):
        return pd.DataFrame([
            {
                "decision_date": "2026-09-28",
                "symbol": "5930",
                "side": "BUY",
                "recommendation_at": "2026-09-29T00:00:00Z",
                "order_submitted_at": "2026-09-29T00:00:01Z",
                "requested_qty": 10,
                "filled_qty": 10,
                "first_fill_at": "2026-09-29T00:00:02Z",
                "final_fill_at": "2026-09-29T00:00:03Z",
                "avg_fill_price": 70000,
                "reference_open": 69900,
                "markout_5m_price": 70100,
                "markout_30m_price": 70300,
                "markout_close_price": 70500,
                "source": EMPIRICAL_EXECUTION_SOURCE,
                "ingested_at": "2026-09-29T06:40:00Z",
            },
            {
                "decision_date": "2026-09-28",
                "symbol": "660",
                "side": "BUY",
                "recommendation_at": "2026-09-29T00:00:00Z",
                "order_submitted_at": "2026-09-29T00:00:01Z",
                "requested_qty": 20,
                "filled_qty": 5,
                "first_fill_at": "2026-09-29T00:00:04Z",
                "final_fill_at": "2026-09-29T00:00:08Z",
                "avg_fill_price": 120000,
                "reference_open": 119900,
                "markout_5m_price": 119800,
                "markout_30m_price": 120100,
                "markout_close_price": 119500,
                "source": EMPIRICAL_EXECUTION_SOURCE,
                "ingested_at": "2026-09-29T06:40:00Z",
            },
            {
                "decision_date": "2026-09-28",
                "symbol": "3550",
                "side": "BUY",
                "recommendation_at": "2026-09-29T00:00:00Z",
                "order_submitted_at": "2026-09-29T00:00:01Z",
                "requested_qty": 5,
                "filled_qty": 0,
                "first_fill_at": None,
                "final_fill_at": None,
                "avg_fill_price": np.nan,
                "reference_open": 300000,
                "markout_5m_price": np.nan,
                "markout_30m_price": np.nan,
                "markout_close_price": np.nan,
                "source": EMPIRICAL_EXECUTION_SOURCE,
                "ingested_at": "2026-09-29T06:40:00Z",
            },
        ])

    def test_full_partial_and_no_fill_are_preserved(self):
        x = validate_execution_observations(self._rows())
        self.assertEqual(x["full_fill"].tolist(), [True, False, False])
        self.assertEqual(x["partial_fill"].tolist(), [False, True, False])
        self.assertEqual(x["no_fill"].tolist(), [False, False, True])
        self.assertAlmostEqual(float(x.loc[1, "fill_ratio"]), 0.25)

    def test_audit_is_structural_not_promotion(self):
        a = audit_execution_evidence(self._rows())
        self.assertEqual(a["observations"], 3)
        self.assertEqual(a["no_fill_observations"], 1)
        self.assertEqual(a["partial_fill_observations"], 1)
        self.assertTrue(a["structural_execution_evidence_ready"])
        self.assertFalse(a["promotion_ready"])

    def test_simulated_source_rejected(self):
        rows = self._rows()
        rows.loc[0, "source"] = "BACKTEST_SIMULATED_FILL"
        with self.assertRaises(ExecutionEvidenceError):
            validate_execution_observations(rows)

    def test_overfill_rejected(self):
        rows = self._rows()
        rows.loc[0, "filled_qty"] = 11
        with self.assertRaises(ExecutionEvidenceError):
            validate_execution_observations(rows)

    def test_fill_before_submission_rejected(self):
        rows = self._rows()
        rows.loc[0, "first_fill_at"] = "2026-09-29T00:00:00Z"
        with self.assertRaises(ExecutionEvidenceError):
            validate_execution_observations(rows)

    def test_zero_fill_cannot_have_fake_fill_price(self):
        rows = self._rows()
        rows.loc[2, "avg_fill_price"] = 300100
        with self.assertRaises(ExecutionEvidenceError):
            validate_execution_observations(rows)

    def test_filled_rows_require_markouts(self):
        rows = self._rows()
        rows.loc[0, "markout_5m_price"] = np.nan
        with self.assertRaises(ExecutionEvidenceError):
            validate_execution_observations(rows)


if __name__ == "__main__":
    unittest.main()
