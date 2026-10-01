import hashlib
import tempfile
import unittest
from unittest.mock import patch

from fastapi import HTTPException

import monitor
import push_receipts
import push_self_test


class PushSelfTestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        monitor.DB_PATH = self.tmp.name + "/test.db"
        monitor.ATH_REFRESH.clear()
        monitor.init_db()
        self.token = "t" * 40
        monitor.register(monitor.RegisterBody(token=self.token, protocol=2))
        self.body = push_self_test.PushSelfTestBody(
            token=self.token,
            platform="android",
            protocol=2,
            client_build="4.6-46",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def _ack(self, event_id: str):
        return push_receipts.record(push_receipts.PushAckBody(
            event_id=event_id,
            token_hash=hashlib.sha256(self.token.encode()).hexdigest(),
            notifications_enabled=True,
            protocol=2,
        ))

    @patch("push_self_test.monitor.init_firebase", return_value=True)
    @patch("push_self_test.messaging.send", return_value="projects/test/messages/1")
    def test_registered_device_gets_one_isolated_self_test_but_send_is_not_receipt(self, send, _firebase):
        out = push_self_test.request_self_test(self.body)
        self.assertTrue(out["ok"])
        self.assertTrue(out["queued"])
        self.assertFalse(out["already_sent"])
        self.assertFalse(out["receipt_confirmed"])
        self.assertTrue(out["event_id"])
        self.assertEqual(send.call_count, 1)

        with monitor.db() as con:
            row = con.execute(
                "SELECT index_id,threshold,event_id,sent FROM deliveries WHERE token=?",
                (self.token,),
            ).fetchone()
        self.assertEqual(row[0], push_self_test.INDEX_ID)
        self.assertEqual(row[1], 0)
        self.assertEqual(row[2], out["event_id"])
        self.assertEqual(row[3], 1)
        self.assertNotIn(push_self_test.INDEX_ID, monitor.RULES)

    @patch("push_self_test.monitor.init_firebase", return_value=True)
    @patch("push_self_test.messaging.send", return_value="projects/test/messages/1")
    def test_same_build_does_not_resend_while_receipt_is_pending(self, send, _firebase):
        first = push_self_test.request_self_test(self.body)
        second = push_self_test.request_self_test(self.body)
        self.assertTrue(first["queued"])
        self.assertFalse(first["receipt_confirmed"])
        self.assertFalse(second["queued"])
        self.assertTrue(second["already_sent"])
        self.assertFalse(second["receipt_confirmed"])
        self.assertEqual(second["event_id"], first["event_id"])
        self.assertEqual(send.call_count, 1)

    @patch("push_self_test.monitor.init_firebase", return_value=True)
    @patch("push_self_test.messaging.send", return_value="projects/test/messages/1")
    def test_same_build_reports_receipt_only_after_real_privacy_safe_ack(self, send, _firebase):
        first = push_self_test.request_self_test(self.body)
        self.assertFalse(first["receipt_confirmed"])

        ack = self._ack(first["event_id"])
        self.assertTrue(ack["acknowledged"])

        after = push_self_test.request_self_test(self.body)
        self.assertFalse(after["queued"])
        self.assertTrue(after["already_sent"])
        self.assertTrue(after["receipt_confirmed"])
        self.assertEqual(after["event_id"], first["event_id"])
        self.assertEqual(send.call_count, 1)

    @patch("push_self_test.monitor.init_firebase", return_value=True)
    @patch("push_self_test.messaging.send", return_value="projects/test/messages/2")
    def test_new_build_can_run_new_self_test(self, send, _firebase):
        push_self_test.request_self_test(self.body)
        newer = push_self_test.PushSelfTestBody(
            token=self.token,
            protocol=2,
            client_build="4.6-47",
        )
        out = push_self_test.request_self_test(newer)
        self.assertTrue(out["queued"])
        self.assertFalse(out["receipt_confirmed"])
        self.assertEqual(send.call_count, 2)

    @patch("push_self_test.monitor.init_firebase", return_value=True)
    def test_transient_send_failure_retries_same_event_without_duplicate_row(self, _firebase):
        with patch("push_self_test.messaging.send", side_effect=RuntimeError("temporary")):
            with self.assertRaises(HTTPException) as cm:
                push_self_test.request_self_test(self.body)
            self.assertEqual(cm.exception.status_code, 503)

        with monitor.db() as con:
            before = con.execute(
                "SELECT event_id,sent,COUNT(*) OVER() FROM deliveries WHERE token=? AND index_id=?",
                (self.token, push_self_test.INDEX_ID),
            ).fetchone()
        self.assertEqual(before[1], 0)
        self.assertEqual(before[2], 1)

        with patch("push_self_test.messaging.send", return_value="projects/test/messages/retry") as send:
            out = push_self_test.request_self_test(self.body)
        self.assertTrue(out["queued"])
        self.assertFalse(out["already_sent"])
        self.assertFalse(out["receipt_confirmed"])
        self.assertEqual(send.call_count, 1)

        with monitor.db() as con:
            after = con.execute(
                "SELECT event_id,sent,COUNT(*) OVER() FROM deliveries WHERE token=? AND index_id=?",
                (self.token, push_self_test.INDEX_ID),
            ).fetchone()
        self.assertEqual(after[0], before[0])
        self.assertEqual(after[1], 1)
        self.assertEqual(after[2], 1)

    @patch("push_self_test.monitor.init_firebase", return_value=True)
    @patch("push_self_test.messaging.send", return_value="projects/test/messages/1")
    def test_self_test_event_is_eligible_for_existing_privacy_safe_ack(self, _send, _firebase):
        first = push_self_test.request_self_test(self.body)
        ack = self._ack(first["event_id"])
        self.assertTrue(ack["acknowledged"])
        self.assertTrue(push_receipts.received_for(self.token, first["event_id"]))

    def test_unregistered_device_fails_closed(self):
        body = push_self_test.PushSelfTestBody(
            token="x" * 40,
            protocol=2,
            client_build="4.6-46",
        )
        with self.assertRaises(HTTPException):
            push_self_test.request_self_test(body)


if __name__ == "__main__":
    unittest.main()
