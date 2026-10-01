import os
import tempfile
import unittest
from unittest.mock import patch

from fastapi import HTTPException

import execution_evidence_ledger as e
import monitor


class ExecutionEvidenceLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        monitor.DB_PATH = self.tmp.name + "/test.db"
        monitor.ATH_REFRESH.clear()
        monitor.init_db()

    def tearDown(self):
        self.tmp.cleanup()

    def full_fill(self, **updates):
        data = dict(
            decision_date="2026-09-29",
            symbol="5930",
            side="BUY",
            recommendation_at="2026-09-29T23:30:00Z",
            order_submitted_at="2026-09-29T23:30:01Z",
            requested_qty=10,
            filled_qty=10,
            first_fill_at="2026-09-29T23:30:02Z",
            final_fill_at="2026-09-29T23:30:03Z",
            avg_fill_price=70000,
            reference_open=69900,
            markout_5m_price=70100,
            markout_30m_price=70300,
            markout_close_price=70500,
            source=e.LIVE_EXECUTION_SOURCE,
            ingested_at="2026-09-30T06:40:00Z",
        )
        data.update(updates)
        return e.ExecutionObservation(**data)

    def assert_project_state_fail_closed(self, payload):
        self.assertFalse(payload["genuine_live_provenance_verified"])
        self.assertFalse(payload["promotion_ready"])
        self.assertFalse(payload["sealed_holdout_authorized"])
        self.assertFalse(payload["live_trading_authorized"])

    def test_full_fill_record_is_immutable_and_idempotent(self):
        first = e.record(self.full_fill())
        second = e.record(self.full_fill())
        self.assertTrue(first["created"])
        self.assertFalse(second["created"])
        self.assertEqual(first["observation_key"], second["observation_key"])
        self.assertTrue(first["source_label_only"])
        self.assertFalse(first["project_live_evidence_admitted"])
        self.assert_project_state_fail_closed(first)

        s = e.summary()
        self.assertEqual(s["full_fill"], 1)
        self.assertEqual(s["live_observations"], 1)
        self.assertEqual(s["live_labelled_observations"], 1)
        self.assertTrue(s["live_structural_execution_rows_present"])
        self.assertFalse(s["contains_live_execution_evidence"])
        self.assertEqual(
            s["contains_live_execution_evidence_semantics"],
            "DEPRECATED_FAIL_CLOSED_USE_LIVE_LABELLED_OBSERVATIONS",
        )
        self.assertFalse(s["project_live_evidence_admitted"])
        self.assertFalse(s["live_empirical_execution_evidence_ready"])
        self.assertFalse(s["empirical_execution_sufficiency_assessed"])
        self.assertFalse(s["empirical_execution_blocker_closed"])
        self.assert_project_state_fail_closed(s)

    def test_same_key_different_payload_is_rejected(self):
        e.record(self.full_fill())
        with self.assertRaises(HTTPException) as cm:
            e.record(self.full_fill(avg_fill_price=70010))
        self.assertEqual(cm.exception.status_code, 409)

    def test_paper_and_live_same_decision_can_coexist(self):
        live = e.record(self.full_fill(source=e.LIVE_EXECUTION_SOURCE))
        paper = e.record(self.full_fill(source=e.PAPER_EXECUTION_SOURCE))
        self.assertNotEqual(live["observation_key"], paper["observation_key"])
        s = e.summary()
        self.assertEqual(s["observations"], 2)
        self.assertEqual(s["live_labelled_observations"], 1)
        self.assertEqual(s["paper_observations"], 1)
        self.assertFalse(s["contains_live_execution_evidence"])
        self.assertFalse(s["genuine_live_provenance_verified"])

    def test_paper_only_is_not_live_execution_evidence(self):
        e.record(self.full_fill(source=e.PAPER_EXECUTION_SOURCE))
        s = e.summary()
        self.assertEqual(s["paper_observations"], 1)
        self.assertEqual(s["live_observations"], 0)
        self.assertEqual(s["live_labelled_observations"], 0)
        self.assertFalse(s["live_structural_execution_rows_present"])
        self.assertFalse(s["contains_live_execution_evidence"])
        self.assert_project_state_fail_closed(s)

    def test_partial_and_zero_fill_are_preserved(self):
        e.record(self.full_fill(symbol="660", requested_qty=20, filled_qty=5))
        e.record(self.full_fill(
            symbol="3550", requested_qty=5, filled_qty=0,
            first_fill_at=None, final_fill_at=None, avg_fill_price=None,
            markout_5m_price=None, markout_30m_price=None, markout_close_price=None,
        ))
        s = e.summary()
        self.assertEqual(s["observations"], 2)
        self.assertEqual(s["partial_fill"], 1)
        self.assertEqual(s["no_fill"], 1)
        self.assertFalse(s["contains_live_execution_evidence"])
        self.assert_project_state_fail_closed(s)

    def test_zero_fill_cannot_fabricate_fill_price(self):
        with self.assertRaises(HTTPException):
            e.record(self.full_fill(
                filled_qty=0, first_fill_at=None, final_fill_at=None,
                avg_fill_price=70000,
                markout_5m_price=None, markout_30m_price=None, markout_close_price=None,
            ))

    def test_filled_row_requires_markouts(self):
        with self.assertRaises(HTTPException):
            e.record(self.full_fill(markout_5m_price=None))

    def test_shadow_and_simulated_sources_are_rejected(self):
        for source in (
            e.SHADOW_DECISION_SOURCE,
            e.LEGACY_SHADOW_FILL_SOURCE,
            "BACKTEST_SIMULATED_FILL",
        ):
            with self.subTest(source=source):
                with self.assertRaises(HTTPException):
                    e.record(self.full_fill(source=source))

    def test_legacy_shadow_rows_are_preserved_but_quarantined_in_summary(self):
        e.init_db()
        with monitor.db() as con:
            con.execute("""
                INSERT INTO execution_evidence(
                    observation_key,decision_date,symbol,side,recommendation_at,order_submitted_at,
                    requested_qty,filled_qty,first_fill_at,final_fill_at,avg_fill_price,reference_open,
                    markout_5m_price,markout_30m_price,markout_close_price,source,ingested_at,payload_hash,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                "legacy-key", "2026-09-29", "005930", "BUY",
                "2026-09-29T23:30:00+00:00", "2026-09-29T23:30:01+00:00",
                10.0, 10.0, "2026-09-29T23:30:02+00:00", "2026-09-29T23:30:03+00:00",
                70000.0, 69900.0, 70100.0, 70300.0, 70500.0,
                e.LEGACY_SHADOW_FILL_SOURCE, "2026-09-30T06:40:00+00:00", "legacy-hash",
                "2026-09-30T06:40:00+00:00",
            ))
        s = e.summary()
        self.assertEqual(s["legacy_shadow_fill_observations"], 1)
        self.assertEqual(s["live_observations"], 0)
        self.assertFalse(s["contains_live_execution_evidence"])
        self.assertFalse(s["genuine_live_provenance_verified"])

    def test_logging_auth_fails_closed(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(HTTPException) as cm:
                e._auth("anything")
            self.assertEqual(cm.exception.status_code, 503)
        with patch.dict(os.environ, {"INDEXALERT_EXECUTION_LOG_TOKEN": "secret"}, clear=True):
            with self.assertRaises(HTTPException) as cm:
                e._auth("wrong")
            self.assertEqual(cm.exception.status_code, 401)
            e._auth("secret")


if __name__ == "__main__":
    unittest.main()
