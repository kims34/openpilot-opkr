import json
import tempfile
import unittest

from fastapi import HTTPException

import client_registration
import monitor


class ClientRegistrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        monitor.DB_PATH = self.tmp.name + "/test.db"
        monitor.ATH_REFRESH.clear()
        monitor.init_db()

    def tearDown(self):
        self.tmp.cleanup()

    def test_records_latest_build_without_exposing_token(self):
        token = "x" * 40
        out = client_registration.register(client_registration.RegisterBody(
            token=token,
            platform="android",
            protocol=2,
            client_build="4.7-47",
        ))
        self.assertTrue(out["ok"])
        self.assertTrue(out["registered"])
        self.assertEqual(out["client_build"], "4.7-47")

        status = client_registration.latest_registered_build_status()
        self.assertEqual(status["latest_registered_client_build"], "4.7-47")
        self.assertIsNotNone(status["latest_registered_client_build_at"])
        self.assertTrue(status["client_build_registration_supported"])
        self.assertNotIn(token, json.dumps(status, sort_keys=True))

    def test_legacy_registration_remains_supported(self):
        token = "y" * 40
        out = client_registration.register(client_registration.RegisterBody(
            token=token,
            platform="android",
            protocol=2,
        ))
        self.assertTrue(out["registered"])
        status = client_registration.latest_registered_build_status()
        self.assertIsNone(status["latest_registered_client_build"])

    def test_invalid_build_is_rejected_before_registration(self):
        with self.assertRaises(HTTPException) as cm:
            client_registration.register(client_registration.RegisterBody(
                token="z" * 40,
                platform="android",
                protocol=2,
                client_build="bad build with spaces",
            ))
        self.assertEqual(cm.exception.status_code, 400)
        with monitor.db() as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM devices").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
