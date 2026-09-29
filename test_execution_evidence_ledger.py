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
            source=e.SOURCE,
            ingested_at="2026-09-30T06:40:00Z",
        )
        data.update(updates)
        return e.ExecutionObservation(**data)

    def test_full_fill_record_is_immutable_and_idempotent(self):
        first = e.record(self.full_fill())
        second = e.record(self.full_fill())
        self.assertTrue(first["created"])
        self.assertFalse(second["created"])
        self.assertEqual(first["observation_key"], second["observation_key"])
        self.assertEqual(e.summary()["full_fill"], 1)

    def test_same_key_different_payload_is_rejected(self):
        e.record(self.full_fill())
        with self.assertRaises(HTTPException) as cm:
            e.record(self.full_fill(avg_fill_price=70010))
        self.assertEqual(cm.exception.status_code, 409)

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
        self.assertFalse(s["promotion_ready"])

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

    def test_source_must_be_empirical(self):
        with self.assertRaises(HTTPException):
            e.record(self.full_fill(source="BACKTEST_SIMULATED_FILL"))

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
