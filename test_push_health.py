import hashlib
import json
import os
import tempfile
import unittest
from unittest.mock import patch

import monitor
import push_health
import push_receipts
import push_self_test


class PushHealthTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        monitor.DB_PATH = self.tmp.name + "/test.db"
        monitor.ATH_REFRESH.clear()
        monitor.init_db()

    def tearDown(self):
        self.tmp.cleanup()

    def _ack(self, token: str, event_id: str):
        return push_receipts.record(push_receipts.PushAckBody(
            event_id=event_id,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            notifications_enabled=True,
            protocol=2,
        ))

    def _insert_self_test(self, *, token: str, build: str, event_id: str, created: float, sent: int = 1):
        with monitor.db() as con:
            con.execute(
                "INSERT INTO deliveries(token,index_id,cycle,threshold,event_id,payload,created,sent) VALUES(?,?,?,?,?,?,?,?)",
                (token, push_self_test.INDEX_ID, f"android-{build}", 0, event_id, "{}", created, sent),
            )

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
        self.assertIsNone(out["latest_self_test_build"])
        self.assertFalse(out["current_build_physical_e2e_confirmed"])

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
        self._insert_self_test(
            token=token,
            build="4.6-46",
            event_id=event_id,
            created=1.0,
        )

        before = push_health.snapshot()
        self.assertEqual(before["sent_deliveries"], 1)
        self.assertEqual(before["received_deliveries"], 0)
        self.assertEqual(before["unconfirmed_sent_deliveries"], 1)
        self.assertIsNone(before["last_client_receipt_at"])
        self.assertEqual(before["latest_self_test_build"], "4.6-46")
        self.assertTrue(before["latest_self_test_sent"])
        self.assertFalse(before["latest_self_test_receipt_confirmed"])
        self.assertFalse(before["current_build_physical_e2e_confirmed"])

        ack = self._ack(token, event_id)
        self.assertTrue(ack["acknowledged"])

        after = push_health.snapshot()
        self.assertEqual(after["sent_deliveries"], 1)
        self.assertEqual(after["received_deliveries"], 1)
        self.assertEqual(after["unconfirmed_sent_deliveries"], 0)
        self.assertIsNotNone(after["last_client_receipt_at"])
        self.assertTrue(after["latest_receipt_notifications_enabled"])
        self.assertTrue(after["latest_self_test_receipt_confirmed"])
        self.assertTrue(after["current_build_physical_e2e_confirmed"])

    def test_old_build_receipt_cannot_confirm_newest_build(self):
        token = "n" * 40
        monitor.register(monitor.RegisterBody(token=token, protocol=2))
        self._insert_self_test(
            token=token,
            build="4.5-45",
            event_id="evt-old-build",
            created=1.0,
        )
        self._ack(token, "evt-old-build")
        self._insert_self_test(
            token=token,
            build="4.6-46",
            event_id="evt-new-build",
            created=2.0,
        )

        out = push_health.snapshot()
        self.assertEqual(out["received_deliveries"], 1)
        self.assertIsNotNone(out["last_client_receipt_at"])
        self.assertEqual(out["latest_self_test_build"], "4.6-46")
        self.assertTrue(out["latest_self_test_sent"])
        self.assertFalse(out["latest_self_test_receipt_confirmed"])
        self.assertFalse(out["current_build_physical_e2e_confirmed"])

        self._ack(token, "evt-new-build")
        confirmed = push_health.snapshot()
        self.assertEqual(confirmed["received_deliveries"], 2)
        self.assertTrue(confirmed["latest_self_test_receipt_confirmed"])
        self.assertTrue(confirmed["current_build_physical_e2e_confirmed"])

    def test_latest_unsent_self_test_never_counts_as_physical_e2e(self):
        token = "u" * 40
        monitor.register(monitor.RegisterBody(token=token, protocol=2))
        self._insert_self_test(
            token=token,
            build="4.6-46",
            event_id="evt-unsent",
            created=3.0,
            sent=0,
        )
        out = push_health.snapshot()
        self.assertEqual(out["latest_self_test_build"], "4.6-46")
        self.assertFalse(out["latest_self_test_sent"])
        self.assertFalse(out["latest_self_test_receipt_confirmed"])
        self.assertFalse(out["current_build_physical_e2e_confirmed"])


if __name__ == "__main__":
    unittest.main()
