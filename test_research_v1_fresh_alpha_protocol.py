import copy
import unittest

from research_v1_fresh_alpha_protocol import (
    eligible_decision_timestamp,
    load_protocol,
    validate_protocol,
)


class FreshAlphaProspectiveProtocolTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = load_protocol()

    def test_frozen_protocol_is_valid_and_non_authoritative(self):
        out = validate_protocol(self.protocol)
        self.assertTrue(out["valid"], out["blockers"])
        self.assertFalse(out["formal_shadow_s1"])
        self.assertFalse(out["promotion_authority"])
        self.assertFalse(out["live_order_authorized"])

    def test_only_strictly_future_decisions_are_eligible(self):
        self.assertFalse(
            eligible_decision_timestamp("2026-10-06T22:54:25Z", self.protocol)
        )
        self.assertFalse(
            eligible_decision_timestamp("2026-10-06T22:54:26Z", self.protocol)
        )
        self.assertTrue(
            eligible_decision_timestamp("2026-10-06T22:54:27Z", self.protocol)
        )

    def test_naive_or_malformed_time_fails_closed(self):
        self.assertFalse(
            eligible_decision_timestamp("2026-10-07T07:55:00", self.protocol)
        )
        self.assertFalse(eligible_decision_timestamp("not-a-time", self.protocol))

    def test_gate_weakening_invalidates_protocol(self):
        for key in (
            "historical_backfill_forbidden",
            "consumed_v1_holdout_forbidden",
            "parameter_retuning_within_protocol_forbidden",
        ):
            with self.subTest(key=key):
                p = copy.deepcopy(self.protocol)
                p[key] = False
                out = validate_protocol(p)
                self.assertFalse(out["valid"])
                self.assertIn("REQUIRED_TRUE:" + key, out["blockers"])

    def test_authority_flags_cannot_be_enabled(self):
        for key in (
            "formal_shadow_s1",
            "fresh_confirmation_s2",
            "promotion_authority",
            "live_order_authorized",
        ):
            with self.subTest(key=key):
                p = copy.deepcopy(self.protocol)
                p[key] = True
                out = validate_protocol(p)
                self.assertFalse(out["valid"])
                self.assertIn("REQUIRED_FALSE:" + key, out["blockers"])

    def test_checkpoint_and_wf_contract_are_frozen(self):
        p = copy.deepcopy(self.protocol)
        p["checkpoints_completed_krx_sessions"] = [63, 126]
        self.assertFalse(validate_protocol(p)["valid"])

        p = copy.deepcopy(self.protocol)
        p["anchored_walk_forward_reference"]["train_sessions"] = 252
        self.assertFalse(validate_protocol(p)["valid"])


if __name__ == "__main__":
    unittest.main()
