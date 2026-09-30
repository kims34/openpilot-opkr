import json
import os
import tempfile
import unittest
from unittest.mock import patch

import monitor
import push_health


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


if __name__ == "__main__":
    unittest.main()
