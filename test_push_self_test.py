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
            client_build="4.4-44",
        )

    def tearDown(self):
        self.tmp.cleanup()

    @patch("push_self_test.monitor.init_firebase", return_value=True)
    @patch("push_self_test.messaging.send", return_value="projects/test/messages/1")
    def test_registered_device_gets_one_isolated_self_test(self, send, _firebase):
        out = push_self_test.request_self_test(self.body)
        self.assertTrue(out["ok"])
        self.assertTrue(out["queued"])
        self.assertFalse(out["already_sent"])
        self.assertEqual(send.call_count, 1)

        with monitor.db() as con:
            row = con.execute(
                "SELECT index_id,threshold,event_id,sent FROM deliveries WHERE token=?",
                (self.token,),
            ).fetchone()
        self.assertEqual(row[0], push_self_test.INDEX_ID)
        self.assertEqual(row[1], 0)
        self.assertEqual(row[3], 1)
        self.assertNotIn(push_self_test.INDEX_ID, monitor.RULES)

    @patch("push_self_test.monitor.init_firebase", return_value=True)
    @patch("push_self_test.messaging.send", return_value="projects/test/messages/1")
    def test_same_build_is_idempotent(self, send, _firebase):
        first = push_self_test.request_self_test(self.body)
        second = push_self_test.request_self_test(self.body)
        self.assertTrue(first["queued"])
        self.assertFalse(second["queued"])
        self.assertTrue(second["already_sent"])
        self.assertEqual(send.call_count, 1)

    @patch("push_self_test.monitor.init_firebase", return_value=True)
    @patch("push_self_test.messaging.send", return_value="projects/test/messages/2")
    def test_new_build_can_run_new_self_test(self, send, _firebase):
        push_self_test.request_self_test(self.body)
        newer = push_self_test.PushSelfTestBody(
            token=self.token,
            protocol=2,
            client_build="4.4-45",
        )
        out = push_self_test.request_self_test(newer)
        self.assertTrue(out["queued"])
        self.assertEqual(send.call_count, 2)

    @patch("push_self_test.monitor.init_firebase", return_value=True)
    @patch("push_self_test.messaging.send", return_value="projects/test/messages/1")
    def test_self_test_event_is_eligible_for_existing_privacy_safe_ack(self, _send, _firebase):
        push_self_test.request_self_test(self.body)
        with monitor.db() as con:
            event_id = con.execute(
                "SELECT event_id FROM deliveries WHERE token=? AND index_id=?",
                (self.token, push_self_test.INDEX_ID),
            ).fetchone()[0]
        import hashlib
        token_hash = hashlib.sha256(self.token.encode()).hexdigest()
        ack = push_receipts.record(push_receipts.PushAckBody(
            event_id=event_id,
            token_hash=token_hash,
            notifications_enabled=True,
            protocol=2,
        ))
        self.assertTrue(ack["acknowledged"])

    def test_unregistered_device_fails_closed(self):
        body = push_self_test.PushSelfTestBody(
            token="x" * 40,
            protocol=2,
            client_build="4.4-44",
        )
        with self.assertRaises(HTTPException):
            push_self_test.request_self_test(body)


if __name__ == "__main__":
    unittest.main()
