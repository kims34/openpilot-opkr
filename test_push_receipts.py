import hashlib
import json
import tempfile
import unittest

from fastapi import HTTPException

import monitor
import push_receipts


class PushReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        monitor.DB_PATH = self.tmp.name + "/test.db"
        monitor.ATH_REFRESH.clear()
        monitor.init_db()
        self.token = "t" * 40
        monitor.register(monitor.RegisterBody(token=self.token, protocol=2))
        self.event_id = "evt-test-1"
        with monitor.db() as con:
            con.execute(
                "INSERT INTO deliveries(token,index_id,cycle,threshold,event_id,payload,created,sent) VALUES(?,?,?,?,?,?,?,1)",
                (self.token, "sp500", "cycle", 5, self.event_id, "{}", 1.0),
            )

    def tearDown(self):
        self.tmp.cleanup()

    def _hash(self):
        return hashlib.sha256(self.token.encode("utf-8")).hexdigest()

    def test_valid_sent_event_is_acknowledged_without_token_echo(self):
        out = push_receipts.record(push_receipts.PushAckBody(
            event_id=self.event_id,
            token_hash=self._hash(),
            notifications_enabled=True,
            protocol=2,
        ))
        self.assertTrue(out["ok"])
        self.assertTrue(out["acknowledged"])
        self.assertFalse(out["duplicate"])
        self.assertNotIn(self.token, json.dumps(out, sort_keys=True))
        stats = push_receipts.stats()
        self.assertEqual(stats["received_deliveries"], 1)
        self.assertTrue(stats["latest_receipt_notifications_enabled"])

    def test_duplicate_ack_is_idempotent(self):
        body = push_receipts.PushAckBody(
            event_id=self.event_id,
            token_hash=self._hash(),
            notifications_enabled=True,
            protocol=2,
        )
        push_receipts.record(body)
        out = push_receipts.record(body)
        self.assertTrue(out["duplicate"])
        self.assertEqual(push_receipts.stats()["received_deliveries"], 1)

    def test_unknown_device_and_unsent_event_fail_closed(self):
        with self.assertRaises(HTTPException):
            push_receipts.record(push_receipts.PushAckBody(
                event_id=self.event_id,
                token_hash="0" * 64,
                notifications_enabled=True,
                protocol=2,
            ))
        with self.assertRaises(HTTPException):
            push_receipts.record(push_receipts.PushAckBody(
                event_id="not-sent",
                token_hash=self._hash(),
                notifications_enabled=True,
                protocol=2,
            ))


if __name__ == "__main__":
    unittest.main()
