import hashlib
import importlib
import tempfile
import unittest
from unittest.mock import patch

from fastapi import HTTPException

import monitor
import push_receipts
import push_self_test


class ProductionV32RegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # unittest discovery imports every test module before test_monitor runs.
        # Loading the full production stack at module import time mutates the
        # shared monitor globals and makes the isolated monitor tests order-
        # dependent. Import v32 only when this suite actually starts.
        cls.p = importlib.import_module("production_v32")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        monitor.DB_PATH = self.tmp.name + "/test.db"
        monitor.ATH_REFRESH.clear()
        self.p._init_device_build_db()

    def tearDown(self):
        self.tmp.cleanup()

    def _register_device(self, token: str):
        return monitor.register(monitor.RegisterBody(token=token, protocol=2))

    def _insert_self_test(self, token: str, build: str, event_id: str, created: float, sent: int = 1):
        with monitor.db() as con:
            con.execute(
                """INSERT INTO deliveries(token,index_id,cycle,threshold,event_id,payload,created,sent)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (
                    token,
                    push_self_test.INDEX_ID,
                    f"android-{build}",
                    0,
                    event_id,
                    "{}",
                    created,
                    sent,
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
        p = self.p
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
        self.assertEqual(
            out["physical_e2e_binding_contract"], p.PHYSICAL_E2E_BINDING_CONTRACT
        )
        with monitor.db() as con:
            row = con.execute(
                "SELECT client_build FROM device_builds WHERE token=?", (token,)
            ).fetchone()
        self.assertEqual(row, ("4.7-47",))

    def test_legacy_registration_clears_old_build_observation(self):
        p = self.p
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
        self.assertIsNone(out["physical_e2e_binding_contract"])
        with monitor.db() as con:
            row = con.execute(
                "SELECT client_build FROM device_builds WHERE token=?", (token,)
            ).fetchone()
        self.assertIsNone(row)

    def test_blocker_codes_are_fail_closed_and_ordered(self):
        p = self.p
        empty = p.push_health_v32()
        self.assertEqual(empty["physical_e2e_blocker"], "NO_REGISTERED_BUILD")
        self.assertFalse(empty["current_build_physical_e2e_confirmed"])

        token = "n" * 40
        self._register_device(token)
        p._record_device_build(token, "4.7-47")
        no_test = p.push_health_v32()
        self.assertEqual(no_test["physical_e2e_blocker"], "NO_SELF_TEST")

        self._insert_self_test(token, "4.7-47", "evt-unsent", 1.0, sent=0)
        unsent = p.push_health_v32()
        self.assertEqual(unsent["physical_e2e_blocker"], "SELF_TEST_NOT_SENT")

    def test_health_requires_receipt_for_exact_registered_device_and_build(self):
        p = self.p
        token = "h" * 40
        self._register_device(token)
        p._record_device_build(token, "4.7-47")

        self._insert_self_test(token, "4.6-46", "evt-old", 1.0)
        self._ack(token, "evt-old")
        old = p.push_health_v32()
        self.assertEqual(old["latest_registered_client_build"], "4.7-47")
        self.assertEqual(old["latest_self_test_build"], "4.6-46")
        self.assertTrue(old["registration_device_matches_self_test"])
        self.assertFalse(old["registration_build_matches_self_test"])
        self.assertEqual(old["physical_e2e_blocker"], "BUILD_MISMATCH")
        self.assertFalse(old["current_build_physical_e2e_confirmed"])

        self._insert_self_test(token, "4.7-47", "evt-current", 2.0)
        sent = p.push_health_v32()
        self.assertEqual(sent["latest_self_test_build"], "4.7-47")
        self.assertTrue(sent["registration_device_matches_self_test"])
        self.assertTrue(sent["registration_build_matches_self_test"])
        self.assertEqual(sent["physical_e2e_blocker"], "RECEIPT_PENDING")
        self.assertFalse(sent["current_build_physical_e2e_confirmed"])

        self._ack(token, "evt-current")
        confirmed = p.push_health_v32()
        self.assertEqual(confirmed["physical_e2e_blocker"], "CONFIRMED")
        self.assertTrue(confirmed["current_build_physical_e2e_confirmed"])
        self.assertTrue(confirmed["registration_build_observed"])
        self.assertTrue(confirmed["registration_device_matches_self_test"])
        self.assertTrue(confirmed["registration_build_matches_self_test"])
        self.assertEqual(
            confirmed["registration_build_contract"], p.REGISTRATION_BUILD_CONTRACT
        )
        self.assertEqual(
            confirmed["self_test_trigger_contract"], p.SELF_TEST_TRIGGER_CONTRACT
        )
        self.assertEqual(
            confirmed["physical_e2e_binding_contract"], p.PHYSICAL_E2E_BINDING_CONTRACT
        )

    def test_same_build_receipt_from_different_device_never_confirms_latest_registration(self):
        p = self.p
        older_token = "a" * 40
        latest_token = "b" * 40
        for token in (older_token, latest_token):
            self._register_device(token)

        p._record_device_build(older_token, "4.7-47")
        p._record_device_build(latest_token, "4.7-47")

        self._insert_self_test(older_token, "4.7-47", "evt-device-a", 10.0)
        self._ack(older_token, "evt-device-a")
        wrong_device = p.push_health_v32()
        self.assertEqual(wrong_device["latest_registered_client_build"], "4.7-47")
        self.assertEqual(wrong_device["latest_self_test_build"], "4.7-47")
        self.assertFalse(wrong_device["registration_device_matches_self_test"])
        self.assertTrue(wrong_device["registration_build_matches_self_test"])
        self.assertEqual(wrong_device["physical_e2e_blocker"], "DEVICE_MISMATCH")
        self.assertFalse(wrong_device["current_build_physical_e2e_confirmed"])

        self._insert_self_test(latest_token, "4.7-47", "evt-device-b", 11.0)
        self._ack(latest_token, "evt-device-b")
        right_device = p.push_health_v32()
        self.assertTrue(right_device["registration_device_matches_self_test"])
        self.assertTrue(right_device["registration_build_matches_self_test"])
        self.assertEqual(right_device["physical_e2e_blocker"], "CONFIRMED")
        self.assertTrue(right_device["current_build_physical_e2e_confirmed"])

    def test_public_health_never_exposes_private_token_or_event_id(self):
        p = self.p
        token = "p" * 40
        event_id = "evt-private-should-never-leak"
        self._register_device(token)
        p._record_device_build(token, "4.7-47")
        self._insert_self_test(token, "4.7-47", event_id, 1.0)
        self._ack(token, event_id)
        rendered = repr(p.push_health_v32())
        self.assertNotIn(token, rendered)
        self.assertNotIn(event_id, rendered)

    def test_invalid_build_is_rejected_before_registration(self):
        p = self.p
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
