import unittest

from verify_push_physical_e2e import (
    PHYSICAL_E2E_BINDING_CONTRACT,
    PhysicalE2EVerificationError,
    REGISTRATION_BUILD_CONTRACT,
    SELF_TEST_TRIGGER_CONTRACT,
    verify_push_health,
)


class PhysicalE2EVerifierTests(unittest.TestCase):
    def _payload(self, **overrides):
        base = {
            "ok": True,
            "firebase": True,
            "tokens_exposed": False,
            "client_receipts_supported": True,
            "registration_build_observed": True,
            "latest_registered_client_build": "4.7-47",
            "latest_registered_client_build_at": "2026-10-01T12:00:00+00:00",
            "registration_build_contract": REGISTRATION_BUILD_CONTRACT,
            "self_test_trigger_contract": SELF_TEST_TRIGGER_CONTRACT,
            "physical_e2e_binding_contract": PHYSICAL_E2E_BINDING_CONTRACT,
            "registration_device_matches_self_test": True,
            "registration_build_matches_self_test": True,
            "latest_self_test_build": "4.7-47",
            "latest_self_test_sent": True,
            "latest_self_test_receipt_confirmed": True,
            "current_build_physical_e2e_confirmed": True,
            "received_deliveries": 2,
            "last_client_receipt_at": 1790856000.0,
        }
        base.update(overrides)
        return base

    def test_exact_current_registered_device_build_receipt_passes(self):
        out = verify_push_health(self._payload(), expected_build="4.7-47")
        self.assertTrue(out["physical_e2e_confirmed"])
        self.assertTrue(all(out["checks"].values()))

    def test_old_self_test_build_receipt_never_passes_current_build(self):
        out = verify_push_health(
            self._payload(
                latest_self_test_build="4.6-46",
                registration_build_matches_self_test=False,
                current_build_physical_e2e_confirmed=False,
            ),
            expected_build="4.7-47",
        )
        self.assertFalse(out["physical_e2e_confirmed"])
        self.assertFalse(out["checks"]["latest_self_test_build_matches"])
        self.assertFalse(out["checks"]["registered_and_self_test_build_match"])

    def test_old_registered_build_never_attests_new_self_test(self):
        out = verify_push_health(
            self._payload(
                latest_registered_client_build="4.6-46",
                registration_build_matches_self_test=False,
                current_build_physical_e2e_confirmed=False,
            ),
            expected_build="4.7-47",
        )
        self.assertFalse(out["physical_e2e_confirmed"])
        self.assertFalse(out["checks"]["latest_registered_client_build_matches"])
        self.assertFalse(out["checks"]["registered_and_self_test_build_match"])

    def test_same_build_from_different_device_fails_closed(self):
        out = verify_push_health(
            self._payload(
                registration_device_matches_self_test=False,
                current_build_physical_e2e_confirmed=False,
            ),
            expected_build="4.7-47",
        )
        self.assertFalse(out["physical_e2e_confirmed"])
        self.assertFalse(out["checks"]["registration_device_matches_self_test"])
        self.assertTrue(out["checks"]["registered_and_self_test_build_match"])

    def test_unobserved_registration_fails_closed(self):
        out = verify_push_health(
            self._payload(
                registration_build_observed=False,
                current_build_physical_e2e_confirmed=False,
            ),
            expected_build="4.7-47",
        )
        self.assertFalse(out["physical_e2e_confirmed"])
        self.assertFalse(out["checks"]["registration_build_observed"])

    def test_registration_contract_drift_fails_closed(self):
        out = verify_push_health(
            self._payload(
                registration_build_contract="legacy-contract",
                current_build_physical_e2e_confirmed=False,
            ),
            expected_build="4.7-47",
        )
        self.assertFalse(out["physical_e2e_confirmed"])
        self.assertFalse(out["checks"]["registration_build_contract_matches"])

    def test_self_test_trigger_contract_drift_fails_closed(self):
        out = verify_push_health(
            self._payload(
                self_test_trigger_contract="legacy-trigger",
                current_build_physical_e2e_confirmed=False,
            ),
            expected_build="4.7-47",
        )
        self.assertFalse(out["physical_e2e_confirmed"])
        self.assertFalse(out["checks"]["self_test_trigger_contract_matches"])

    def test_binding_contract_drift_fails_closed(self):
        out = verify_push_health(
            self._payload(
                physical_e2e_binding_contract="legacy-binding",
                current_build_physical_e2e_confirmed=False,
            ),
            expected_build="4.7-47",
        )
        self.assertFalse(out["physical_e2e_confirmed"])
        self.assertFalse(out["checks"]["physical_e2e_binding_contract_matches"])

    def test_provider_send_without_receipt_fails(self):
        out = verify_push_health(
            self._payload(
                latest_self_test_receipt_confirmed=False,
                current_build_physical_e2e_confirmed=False,
                received_deliveries=1,
                last_client_receipt_at=1790856000.0,
            ),
            expected_build="4.7-47",
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
            expected_build="4.7-47",
        )
        self.assertFalse(out["physical_e2e_confirmed"])
        self.assertTrue(out["checks"]["received_delivery_count_positive"])

    def test_receipt_timestamp_is_required(self):
        out = verify_push_health(
            self._payload(last_client_receipt_at=None),
            expected_build="4.7-47",
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
                expected_build="4.7-47",
            )
            self.assertFalse(out["physical_e2e_confirmed"])

    def test_invalid_expected_build_fails_closed(self):
        with self.assertRaises(PhysicalE2EVerificationError):
            verify_push_health(self._payload(), expected_build="")
        with self.assertRaises(PhysicalE2EVerificationError):
            verify_push_health(self._payload(), expected_build="4.7/47")


if __name__ == "__main__":
    unittest.main()
