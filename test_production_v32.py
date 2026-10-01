import hashlib
import tempfile
import unittest
from unittest.mock import patch

from fastapi import HTTPException

import monitor
import production_v32 as p
import push_receipts
import push_self_test


class ProductionV32RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        monitor.DB_PATH = self.tmp.name + "/test.db"
        monitor.ATH_REFRESH.clear()
        p._init_device_build_db()

    def tearDown(self):
        self.tmp.cleanup()

    def _register_device(self, token: str):
        return monitor.register(monitor.RegisterBody(token=token, protocol=2))

    def _insert_self_test(self, token: str, build: str, event_id: str, created: float):
        with monitor.db() as con:
            con.execute(
                """INSERT INTO deliveries(token,index_id,cycle,threshold,event_id,payload,created,sent)
                   VALUES(?,?,?,?,?,?,?,1)""",
                (
                    token,
                    push_self_test.INDEX_ID,
                    f"android-{build}",
                    0,
                    event_id,
                    "{}",
                    created,
                ),
            )

    def _ack(self, token: str, event_id: str):
        return push_receipts.record(
            push_receipts.PushAckBody(
                event_id=event_id,
                token_hash=hashlib.sha256(token.encode()).hexdigest(),
                notifications_enabled=True,
                protocol=2,
            )
        )

    def test_register_records_build_and_advertises_direct_client_self_test(self):
        token = "r" * 40
        with patch.object(
            p.production,
            "register",
            return_value={"ok": True, "registered": True, "firebase": True, "protocol": 2},
        ):
            out = p.register_v32(
                p.RegisterBodyV32(
                    token=token,
                    platform="android",
                    protocol=2,
                    client_build="4.7-47",
                )
            )

        self.assertTrue(out["registered"])
        self.assertEqual(out["client_build"], "4.7-47")
        self.assertTrue(out["client_build_observed"])
        self.assertEqual(out["registration_build_contract"], p.REGISTRATION_BUILD_CONTRACT)
        self.assertEqual(out["self_test_trigger_contract"], p.SELF_TEST_TRIGGER_CONTRACT)
        with monitor.db() as con:
            row = con.execute(
                "SELECT client_build FROM device_builds WHERE token=?", (token,)
            ).fetchone()
        self.assertEqual(row, ("4.7-47",))

    def test_legacy_registration_clears_old_build_observation(self):
        token = "l" * 40
        p._record_device_build(token, "4.7-47")
        with patch.object(
            p.production,
            "register",
            return_value={"ok": True, "registered": True, "firebase": True, "protocol": 2},
        ):
            out = p.register_v32(
                p.RegisterBodyV32(token=token, platform="android", protocol=2)
            )
        self.assertFalse(out["client_build_observed"])
        self.assertIsNone(out["self_test_trigger_contract"])
        with monitor.db() as con:
            row = con.execute(
                "SELECT client_build FROM device_builds WHERE token=?", (token,)
            ).fetchone()
        self.assertIsNone(row)

    def test_health_requires_receipt_for_exact_registered_build(self):
        token = "h" * 40
        self._register_device(token)
        p._record_device_build(token, "4.7-47")

        self._insert_self_test(token, "4.6-46", "evt-old", 1.0)
        self._ack(token, "evt-old")
        old = p.push_health_v32()
        self.assertEqual(old["latest_registered_client_build"], "4.7-47")
        self.assertEqual(old["latest_self_test_build"], "4.6-46")
        self.assertFalse(old["current_build_physical_e2e_confirmed"])

        self._insert_self_test(token, "4.7-47", "evt-current", 2.0)
        sent = p.push_health_v32()
        self.assertEqual(sent["latest_self_test_build"], "4.7-47")
        self.assertFalse(sent["current_build_physical_e2e_confirmed"])

        self._ack(token, "evt-current")
        confirmed = p.push_health_v32()
        self.assertTrue(confirmed["current_build_physical_e2e_confirmed"])
        self.assertTrue(confirmed["registration_build_observed"])
        self.assertEqual(
            confirmed["registration_build_contract"], p.REGISTRATION_BUILD_CONTRACT
        )
        self.assertEqual(
            confirmed["self_test_trigger_contract"], p.SELF_TEST_TRIGGER_CONTRACT
        )

    def test_invalid_build_is_rejected_before_registration(self):
        with self.assertRaises(HTTPException):
            p.register_v32(
                p.RegisterBodyV32(
                    token="x" * 40,
                    protocol=2,
                    client_build="bad build!",
                )
            )


if __name__ == "__main__":
    unittest.main()
