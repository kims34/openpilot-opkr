import unittest

import numpy as np
import pandas as pd

from research_v1_execution_evidence import (
    LIVE_EXECUTION_SOURCE,
    PAPER_EXECUTION_SOURCE,
    SHADOW_DECISION_SOURCE,
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
                "source": LIVE_EXECUTION_SOURCE,
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
                "source": PAPER_EXECUTION_SOURCE,
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
                "source": PAPER_EXECUTION_SOURCE,
                "ingested_at": "2026-09-29T06:40:00Z",
            },
        ])

    def test_full_partial_and_no_fill_are_preserved(self):
        x = validate_execution_observations(self._rows())
        self.assertEqual(x["full_fill"].tolist(), [True, False, False])
        self.assertEqual(x["partial_fill"].tolist(), [False, True, False])
        self.assertEqual(x["no_fill"].tolist(), [False, False, True])
        self.assertEqual(x["execution_tier"].tolist(), ["LIVE", "PAPER", "PAPER"])
        self.assertAlmostEqual(float(x.loc[1, "fill_ratio"]), 0.25)

    def test_audit_separates_live_structure_from_empirical_sufficiency(self):
        a = audit_execution_evidence(self._rows())
        self.assertEqual(a["observations"], 3)
        self.assertEqual(a["paper_observations"], 2)
        self.assertEqual(a["live_observations"], 1)
        self.assertEqual(a["live_filled_observations"], 1)
        self.assertEqual(a["live_no_fill_observations"], 0)
        self.assertEqual(a["live_partial_fill_observations"], 0)
        self.assertEqual(a["live_full_fill_observations"], 1)
        self.assertEqual(a["no_fill_observations"], 1)
        self.assertEqual(a["partial_fill_observations"], 1)
        self.assertTrue(a["contains_paper_execution_evidence"])
        self.assertTrue(a["contains_live_execution_evidence"])
        self.assertFalse(a["live_execution_source_only"])
        self.assertTrue(a["structural_execution_evidence_ready"])
        self.assertTrue(a["live_structural_execution_evidence_present"])
        self.assertFalse(a["live_empirical_execution_evidence_ready"])
        self.assertFalse(a["empirical_execution_sufficiency_assessed"])
        self.assertFalse(a["empirical_execution_blocker_closed"])
        self.assertFalse(a["promotion_ready"])

    def test_one_or_more_live_rows_never_auto_close_empirical_blocker(self):
        rows = self._rows().iloc[[0]].copy()
        a = audit_execution_evidence(rows)
        self.assertTrue(a["live_structural_execution_evidence_present"])
        self.assertFalse(a["live_empirical_execution_evidence_ready"])
        self.assertFalse(a["empirical_execution_blocker_closed"])
        self.assertFalse(a["promotion_ready"])

    def test_paper_only_is_not_live_empirical_evidence(self):
        rows = self._rows()
        rows["source"] = PAPER_EXECUTION_SOURCE
        a = audit_execution_evidence(rows)
        self.assertTrue(a["structural_execution_evidence_ready"])
        self.assertFalse(a["contains_live_execution_evidence"])
        self.assertFalse(a["live_structural_execution_evidence_present"])
        self.assertFalse(a["live_empirical_execution_evidence_ready"])
        self.assertFalse(a["empirical_execution_blocker_closed"])
        self.assertFalse(a["promotion_ready"])

    def test_live_zero_fill_is_preserved_as_live_empirical_observation_without_closure(self):
        rows = self._rows().iloc[[2]].copy()
        rows["source"] = LIVE_EXECUTION_SOURCE
        a = audit_execution_evidence(rows)
        self.assertEqual(a["live_observations"], 1)
        self.assertEqual(a["live_no_fill_observations"], 1)
        self.assertFalse(a["live_structural_execution_evidence_present"])
        self.assertFalse(a["live_empirical_execution_evidence_ready"])
        self.assertFalse(a["empirical_execution_blocker_closed"])

    def test_shadow_decision_source_rejected_from_fill_schema(self):
        rows = self._rows()
        rows.loc[0, "source"] = SHADOW_DECISION_SOURCE
        with self.assertRaises(ExecutionEvidenceError):
            validate_execution_observations(rows)

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

    def test_zero_fill_cannot_have_fake_fill_price_or_markout(self):
        rows = self._rows()
        rows.loc[2, "avg_fill_price"] = 300100
        with self.assertRaises(ExecutionEvidenceError):
            validate_execution_observations(rows)

        rows = self._rows()
        rows.loc[2, "markout_5m_price"] = 300100
        with self.assertRaises(ExecutionEvidenceError):
            validate_execution_observations(rows)

    def test_filled_rows_require_markouts(self):
        rows = self._rows()
        rows.loc[0, "markout_5m_price"] = np.nan
        with self.assertRaises(ExecutionEvidenceError):
            validate_execution_observations(rows)

    def test_nonfinite_quantities_and_prices_are_rejected(self):
        fields = (
            "requested_qty", "filled_qty", "reference_open", "avg_fill_price",
            "markout_5m_price", "markout_30m_price", "markout_close_price",
        )
        for field in fields:
            for value in (np.inf, -np.inf):
                with self.subTest(field=field, value=value):
                    rows = self._rows()
                    rows[field] = rows[field].astype(float)
                    rows.loc[0, field] = value
                    with self.assertRaises(ExecutionEvidenceError):
                        validate_execution_observations(rows)

    def test_infinite_full_fill_cannot_claim_live_structural_presence(self):
        rows = self._rows()
        for field in ("requested_qty", "filled_qty"):
            rows[field] = rows[field].astype(float)
            rows.loc[0, field] = np.inf
        with self.assertRaises(ExecutionEvidenceError):
            audit_execution_evidence(rows)

    def test_no_fill_original_values_cannot_be_erased_by_coercion(self):
        for field in (
            "first_fill_at", "final_fill_at", "avg_fill_price",
            "markout_5m_price", "markout_30m_price", "markout_close_price",
        ):
            with self.subTest(field=field):
                rows = self._rows()
                rows[field] = rows[field].astype(object)
                rows.loc[2, field] = "malformed"
                with self.assertRaises(ExecutionEvidenceError):
                    validate_execution_observations(rows)

    def test_missing_symbol_cannot_become_text_identity(self):
        for value in (None, np.nan, pd.NA):
            with self.subTest(value=value):
                rows = self._rows()
                rows.loc[0, "symbol"] = value
                with self.assertRaises(ExecutionEvidenceError):
                    validate_execution_observations(rows)

    def test_fractional_share_quantities_are_rejected(self):
        for field, value in (("requested_qty", 10.5), ("filled_qty", 9.5)):
            with self.subTest(field=field):
                rows = self._rows()
                rows[field] = rows[field].astype(float)
                rows.loc[0, field] = value
                with self.assertRaises(ExecutionEvidenceError):
                    validate_execution_observations(rows)

    def test_boolean_numeric_execution_values_are_rejected(self):
        for field in ("requested_qty", "filled_qty", "reference_open", "avg_fill_price"):
            with self.subTest(field=field):
                rows = self._rows()
                rows[field] = rows[field].astype(object)
                rows.loc[0, field] = True
                with self.assertRaises(ExecutionEvidenceError):
                    validate_execution_observations(rows)

    def test_boolean_identity_and_timestamp_values_are_rejected(self):
        for field in ("symbol", "decision_date", "recommendation_at", "order_submitted_at", "ingested_at"):
            with self.subTest(field=field):
                rows = self._rows()
                rows[field] = rows[field].astype(object)
                rows.loc[0, field] = True
                with self.assertRaises(ExecutionEvidenceError):
                    validate_execution_observations(rows)

    def test_naive_or_numeric_execution_timestamps_are_rejected(self):
        for field in ("recommendation_at", "order_submitted_at", "ingested_at"):
            for value in ("2026-09-29T00:00:00", 1234567890):
                with self.subTest(field=field, value=value):
                    rows = self._rows()
                    rows[field] = rows[field].astype(object)
                    rows.loc[0, field] = value
                    with self.assertRaises(ExecutionEvidenceError):
                        validate_execution_observations(rows)

    def test_nonscalar_execution_timestamp_is_rejected(self):
        rows = self._rows()
        rows["recommendation_at"] = rows["recommendation_at"].astype(object)
        rows.at[0, "recommendation_at"] = ["2026-09-29T00:00:00Z"]
        with self.assertRaises(ExecutionEvidenceError):
            validate_execution_observations(rows)

    def test_ingestion_cannot_precede_submission_or_final_fill(self):
        rows = self._rows()
        rows.loc[0, "ingested_at"] = "2026-09-29T00:00:00.500Z"
        with self.assertRaises(ExecutionEvidenceError):
            validate_execution_observations(rows)
        rows = self._rows()
        rows.loc[0, "ingested_at"] = "2026-09-29T00:00:02.500Z"
        with self.assertRaises(ExecutionEvidenceError):
            validate_execution_observations(rows)

    def test_decision_date_rejects_datetime_and_numeric_coercion(self):
        for value in ("2026-09-28T23:59:59Z", 20260928, 0):
            with self.subTest(value=value):
                rows = self._rows()
                rows["decision_date"] = rows["decision_date"].astype(object)
                rows.at[0, "decision_date"] = value
                with self.assertRaises(ExecutionEvidenceError):
                    validate_execution_observations(rows)


if __name__ == "__main__":
    unittest.main()
