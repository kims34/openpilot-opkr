import copy
import unittest

from research_v1_prospective_chronology_anchor import (
    MAX_ANCHOR_LAG_SECONDS,
    ProspectiveChronologyAnchorError,
    assess_external_github_commit,
    build_anchor_record,
    validate_anchor_record,
)


def record():
    return build_anchor_record(
        session="2026-10-08",
        decision_at="2026-10-08T09:00:00+00:00",
        source_receipt_sha256="a"*64,
        input_snapshot_sha256="b"*64,
        producer_binding_sha256="c"*64,
        model_bundle_sha256="d"*64,
        decision_capture_sha256="e"*64,
        session_manifest_sha256="f"*64,
        workflow_ref_commit="1"*40,
        workflow_run_id=123456789,
        workflow_run_attempt=1,
    )


class ProspectiveChronologyAnchorTest(unittest.TestCase):
    def test_hash_only_record_discloses_no_positions_and_grants_no_authority(self):
        out = record()
        checked = validate_anchor_record(out)
        self.assertTrue(checked["valid"])
        self.assertFalse(out["security_identifiers_disclosed"])
        self.assertFalse(out["ranked_scores_disclosed"])
        self.assertFalse(out["selected_candidates_disclosed"])
        self.assertFalse(out["outcomes_attached"])
        self.assertFalse(out["independent_chronology_admission_verified"])
        self.assertFalse(out["fresh_alpha_observation_admitted"])
        self.assertFalse(out["live_order_authorized"])
        forbidden_payload_keys = {
            "symbol", "symbols", "score", "scores", "ranked_scores",
            "selected_candidates", "outcome", "outcomes",
        }
        self.assertTrue(forbidden_payload_keys.isdisjoint(out.keys()))

    def test_workflow_run_identity_requires_positive_exact_integers(self):
        for field, value in (
            ("workflow_run_id", 0),
            ("workflow_run_attempt", -1),
            ("workflow_run_id", True),
            ("workflow_run_attempt", 1.0),
        ):
            out = record()
            out[field] = value
            with self.assertRaises(ProspectiveChronologyAnchorError):
                validate_anchor_record(out)

    def test_external_commit_time_can_satisfy_structure_but_not_self_admit(self):
        out = assess_external_github_commit(
            record(),
            commit_sha="2"*40,
            commit_created_at="2026-10-08T09:05:00+00:00",
        )
        self.assertTrue(out["chronology_conditions_structurally_satisfied"])
        self.assertEqual(out["blockers"], [])
        self.assertFalse(out["independent_chronology_admission_verified"])

    def test_predecision_or_late_anchor_is_blocked(self):
        before = assess_external_github_commit(
            record(),
            commit_sha="2"*40,
            commit_created_at="2026-10-08T08:59:59+00:00",
        )
        self.assertFalse(before["chronology_conditions_structurally_satisfied"])
        self.assertIn("GITHUB_COMMIT_PRECEDES_DECLARED_DECISION", before["blockers"])
        late_seconds = MAX_ANCHOR_LAG_SECONDS + 1
        late = assess_external_github_commit(
            record(),
            commit_sha="2"*40,
            commit_created_at="2026-10-08T15:00:01+00:00",
        )
        self.assertEqual(late["anchor_lag_seconds"], float(late_seconds))
        self.assertIn("GITHUB_ANCHOR_LAG_EXCEEDS_6H", late["blockers"])

    def test_tamper_or_authority_escalation_breaks_hash_validation(self):
        out = record()
        changed = copy.deepcopy(out)
        changed["live_order_authorized"] = True
        with self.assertRaises(ProspectiveChronologyAnchorError):
            validate_anchor_record(changed)
        changed = copy.deepcopy(out)
        changed["decision_capture_sha256"] = "0"*64
        with self.assertRaisesRegex(ProspectiveChronologyAnchorError, "fingerprint"):
            validate_anchor_record(changed)


if __name__ == "__main__":
    unittest.main()
