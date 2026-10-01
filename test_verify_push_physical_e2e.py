import unittest

from verify_push_physical_e2e import (
    PhysicalE2EVerificationError,
    verify_push_health,
)


class PhysicalE2EVerifierTests(unittest.TestCase):
    def _payload(self, **overrides):
        base = {
            "ok": True,
            "firebase": True,
            "tokens_exposed": False,
            "client_receipts_supported": True,
            "latest_self_test_build": "4.6-46",
            "latest_self_test_sent": True,
            "latest_self_test_receipt_confirmed": True,
            "current_build_physical_e2e_confirmed": True,
            "received_deliveries": 2,
            "last_client_receipt_at": 1760000000.0,
        }
        base.update(overrides)
        return base

    def test_exact_current_build_receipt_passes(self):
        out = verify_push_health(self._payload(), expected_build="4.6-46")
        self.assertTrue(out["physical_e2e_confirmed"])
        self.assertTrue(all(out["checks"].values()))

    def test_old_build_receipt_never_passes_current_build(self):
        out = verify_push_health(
            self._payload(latest_self_test_build="4.5-45"),
            expected_build="4.6-46",
        )
        self.assertFalse(out["physical_e2e_confirmed"])
        self.assertFalse(out["checks"]["latest_self_test_build_matches"])

    def test_provider_send_without_receipt_fails(self):
        out = verify_push_health(
            self._payload(
                latest_self_test_receipt_confirmed=False,
                current_build_physical_e2e_confirmed=False,
                received_deliveries=1,
                last_client_receipt_at=1760000000.0,
            ),
            expected_build="4.6-46",
        )
        self.assertFalse(out["physical_e2e_confirmed"])
        self.assertTrue(out["checks"]["latest_self_test_sent"])
        self.assertFalse(out["checks"]["latest_self_test_receipt_confirmed"])

    def test_aggregate_old_receipt_is_not_enough(self):
        out = verify_push_health(
            self._payload(
                latest_self_test_receipt_confirmed=False,
                current_build_physical_e2e_confirmed=False,
                received_deliveries=9,
            ),
            expected_build="4.6-46",
        )
        self.assertFalse(out["physical_e2e_confirmed"])
        self.assertTrue(out["checks"]["received_delivery_count_positive"])

    def test_receipt_timestamp_is_required(self):
        out = verify_push_health(
            self._payload(last_client_receipt_at=None),
            expected_build="4.6-46",
        )
        self.assertFalse(out["physical_e2e_confirmed"])
        self.assertFalse(out["checks"]["real_receipt_timestamp_present"])

    def test_health_and_privacy_contracts_are_required(self):
        for field, value in [
            ("ok", False),
            ("firebase", False),
            ("tokens_exposed", True),
            ("client_receipts_supported", False),
        ]:
            out = verify_push_health(
                self._payload(**{field: value}),
                expected_build="4.6-46",
            )
            self.assertFalse(out["physical_e2e_confirmed"])

    def test_invalid_expected_build_fails_closed(self):
        with self.assertRaises(PhysicalE2EVerificationError):
            verify_push_health(self._payload(), expected_build="")
        with self.assertRaises(PhysicalE2EVerificationError):
            verify_push_health(self._payload(), expected_build="4.6/46")


if __name__ == "__main__":
    unittest.main()
