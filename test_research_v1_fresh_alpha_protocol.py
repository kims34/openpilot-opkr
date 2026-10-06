import copy
import tempfile
import unittest
from pathlib import Path

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

    def test_freeze_anchor_and_frozen_identity_fields_are_exact(self):
        mutations = (
            ("freeze_anchor_commit", "0" * 40, "FREEZE_ANCHOR_COMMIT_MISMATCH"),
            ("freeze_anchor_committed_at_utc", "2026-10-06T22:54:27Z", "FREEZE_ANCHOR_TIME_MISMATCH"),
            ("eligible_chronology", "decision_timestamp_after_freeze", "ELIGIBLE_CHRONOLOGY_MISMATCH"),
            ("data_role", "HISTORICAL_REPLAY", "DATA_ROLE_MISMATCH"),
            ("selection_policy", "OTHER_POLICY", "SELECTION_POLICY_MISMATCH"),
        )
        for key, value, blocker in mutations:
            with self.subTest(key=key):
                p = copy.deepcopy(self.protocol)
                p[key] = value
                out = validate_protocol(p)
                self.assertFalse(out["valid"])
                self.assertIn(blocker, out["blockers"])

    def test_missing_or_extra_protocol_fields_fail_closed(self):
        missing = copy.deepcopy(self.protocol)
        missing.pop("data_role")
        self.assertIn("PROTOCOL_FIELDS_MISMATCH", validate_protocol(missing)["blockers"])
        extra = copy.deepcopy(self.protocol)
        extra["posthoc_override"] = False
        self.assertIn("PROTOCOL_FIELDS_MISMATCH", validate_protocol(extra)["blockers"])

    def test_duplicate_json_keys_are_rejected(self):
        raw = '{"schema_version":"1.0","schema_version":"1.0"}'
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "protocol.json"
            path.write_text(raw, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate protocol JSON key"):
                load_protocol(path)

    def test_timestamp_whitespace_is_not_normalized_into_eligibility(self):
        self.assertFalse(
            eligible_decision_timestamp(" 2026-10-06T22:54:27Z", self.protocol)
        )
        self.assertFalse(
            eligible_decision_timestamp("2026-10-06T22:54:27Z ", self.protocol)
        )

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
