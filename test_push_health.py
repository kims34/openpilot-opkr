import hashlib
import json
import os
import tempfile
import unittest
from unittest.mock import patch

import monitor
import push_health
import push_receipts


class PushHealthTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        monitor.DB_PATH = self.tmp.name + "/test.db"
        monitor.ATH_REFRESH.clear()
        monitor.init_db()

    def tearDown(self):
        self.tmp.cleanup()

    def test_snapshot_never_exposes_token_and_reports_registration(self):
        token = "x" * 30
        monitor.register(monitor.RegisterBody(token=token, protocol=2))
        with patch.dict(os.environ, {}, clear=True):
            out = push_health.snapshot()
        self.assertTrue(out["ok"])
        self.assertEqual(out["registered_devices"], 1)
        self.assertIsNotNone(out["last_device_registration_at"])
        self.assertFalse(out["execution_logging_configured"])
        self.assertFalse(out["tokens_exposed"])
        self.assertNotIn(token, json.dumps(out, sort_keys=True))

    def test_execution_logging_configuration_is_boolean_only(self):
        marker = "configured-value"
        with patch.dict(os.environ, {"INDEXALERT_EXECUTION_LOG_TOKEN": marker}, clear=True):
            out = push_health.snapshot()
        self.assertTrue(out["execution_logging_configured"])
        self.assertNotIn(marker, json.dumps(out, sort_keys=True))

    def test_sent_delivery_is_unconfirmed_until_real_client_ack(self):
        token = "t" * 40
        event_id = "evt-health-1"
        monitor.register(monitor.RegisterBody(token=token, protocol=2))
        with monitor.db() as con:
            con.execute(
                "INSERT INTO deliveries(token,index_id,cycle,threshold,event_id,payload,created,sent) VALUES(?,?,?,?,?,?,?,1)",
                (token, "push_self_test", "android-4.6-46", 0, event_id, "{}", 1.0),
            )

        before = push_health.snapshot()
        self.assertEqual(before["sent_deliveries"], 1)
        self.assertEqual(before["received_deliveries"], 0)
        self.assertEqual(before["unconfirmed_sent_deliveries"], 1)
        self.assertIsNone(before["last_client_receipt_at"])

        ack = push_receipts.record(push_receipts.PushAckBody(
            event_id=event_id,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            notifications_enabled=True,
            protocol=2,
        ))
        self.assertTrue(ack["acknowledged"])

        after = push_health.snapshot()
        self.assertEqual(after["sent_deliveries"], 1)
        self.assertEqual(after["received_deliveries"], 1)
        self.assertEqual(after["unconfirmed_sent_deliveries"], 0)
        self.assertIsNotNone(after["last_client_receipt_at"])
        self.assertTrue(after["latest_receipt_notifications_enabled"])


if __name__ == "__main__":
    unittest.main()
