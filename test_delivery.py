"""Regression tests for threshold loss when FCM cannot deliver.

Run: python -m unittest discover -p 'test_*.py' -v
No live market requests or push messages are sent.
"""
import os
import tempfile
import unittest
from unittest.mock import patch

import monitor


class DeliveryRetryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        database = patch.object(monitor, "DB_PATH", os.path.join(self.directory.name, "state.db"))
        database.start()
        self.addCleanup(database.stop)
        monitor.init_db()
        monitor.save_state("ndx", 100, 100, 100, "현물지수")
        prices = patch.object(monitor, "current", return_value=(79, 100, "REGULAR", 1))
        prices.start()
        self.addCleanup(prices.stop)

    def test_failed_delivery_retries_and_success_prevents_duplicates(self):
        with patch.object(monitor, "send_push", side_effect=[0, 1]) as send:
            monitor.evaluate("ndx")
            self.assertEqual(monitor.fired_set("ndx"), set())
            self.assertEqual(monitor.get_state("ndx")[2], 79)
            monitor.evaluate("ndx")
            self.assertEqual(monitor.fired_set("ndx"), {10, 15, 20})
            monitor.evaluate("ndx")
            self.assertEqual(send.call_count, 2)

    def test_missing_firebase_does_not_consume_threshold(self):
        with patch.object(monitor, "init_firebase", return_value=False):
            monitor.evaluate("ndx")
        self.assertEqual(monitor.fired_set("ndx"), set())

    def test_no_devices_does_not_consume_threshold(self):
        with patch.object(monitor, "init_firebase", return_value=True):
            monitor.evaluate("ndx")
        self.assertEqual(monitor.fired_set("ndx"), set())

    def test_fcm_failure_then_recovery(self):
        with monitor.db() as con:
            con.execute("INSERT INTO devices VALUES(?,?,?)", ("test-token-not-a-real-device", "android", "now"))
        with patch.object(monitor, "init_firebase", return_value=True), patch.object(
            monitor.messaging, "send", side_effect=[RuntimeError("temporary outage"), "message-id"]
        ) as send:
            monitor.evaluate("ndx")
            self.assertEqual(monitor.fired_set("ndx"), set())
            monitor.evaluate("ndx")
            self.assertEqual(monitor.fired_set("ndx"), {10, 15, 20})
            self.assertEqual(send.call_count, 2)

    def test_new_ath_allows_another_notification_cycle(self):
        with patch.object(monitor, "send_push", return_value=1) as send:
            monitor.evaluate("ndx")
            with patch.object(monitor, "current", return_value=(110, 100, "REGULAR", 2)):
                monitor.evaluate("ndx")
            self.assertEqual(monitor.fired_set("ndx"), set())
            monitor.evaluate("ndx")
            self.assertEqual(send.call_count, 2)


if __name__ == "__main__":
    unittest.main()
