"""Synthetic prospective decision capture tests; no market/network/order use."""
import copy
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from research_v1_context import CONTEXT_FEATURES
from research_v1_distributional_netev import _pipe
from research_v1_prospective_decision_capture import (
    ProspectiveDecisionCaptureError,
    build_decision_capture,
    store_decision_capture,
    validate_decision_capture,
)
from research_v1_prospective_inputs import (
    build_current_session_inputs,
    input_snapshot_sha256,
)
from research_v1_prospective_model_bundle import build_model_bundle
from test_research_v1_causal_evidence_integrity import synthetic_panel


def _quantiles(offset=-0.001):
    base = {"low": offset, "med": offset + 0.005, "high": offset + 0.01, "n": 126}
    return {
        "__global__": dict(base),
        "low": {**base, "fallback_global": False, "bucket_n": 42},
        "mid": {**base, "fallback_global": False, "bucket_n": 42},
        "high": {**base, "fallback_global": False, "bucket_n": 42},
    }


class ProspectiveDecisionCaptureTest(unittest.TestCase):
    def setUp(self):
        self.dates, raw = synthetic_panel()
        raw["available_at"] = (
            raw.decision_date.dt.strftime("%Y-%m-%d") + "T17:00:00+09:00"
        )
        self.decision_at = self.dates[-1].strftime("%Y-%m-%d") + "T18:00:00+09:00"
        self.snapshot = build_current_session_inputs(raw, decision_at=self.decision_at)
        self.input_digest = input_snapshot_sha256(self.snapshot)

        rng = np.random.default_rng(9)
        train = pd.DataFrame(
            rng.normal(size=(100, len(CONTEXT_FEATURES))),
            columns=CONTEXT_FEATURES,
        )
        y = pd.Series(rng.normal(scale=0.01, size=len(train)))
        model = _pipe(CONTEXT_FEATURES)
        model.fit(train, y)
        self.bundle = build_model_bundle(
            model, _quantiles(),
            training_input_sha256="a" * 64,
            calibration_input_sha256="b" * 64,
            fit_code_commit="c" * 40,
            fit_code_path="research_v1_selected_calibration.py",
            train_end_session="2026-01-30",
            calibration_start_session="2026-02-09",
            calibration_end_session="2026-08-07",
            refit_policy_id="TEST_ONLY_EXPLICIT_CALLER_POLICY",
        )
        self.captured_at = self.dates[-1].strftime("%Y-%m-%d") + "T18:00:05+09:00"

    def capture(self, **kwargs):
        return build_decision_capture(
            self.snapshot,
            self.bundle,
            input_snapshot_sha256=kwargs.get("input_snapshot_sha256", self.input_digest),
            captured_at=kwargs.get("captured_at", self.captured_at),
        )

    def test_capture_binds_full_ranking_top3_veto_and_never_grants_authority(self):
        out = self.capture()
        self.assertTrue(validate_decision_capture(out)["valid"])
        self.assertEqual(out["input_snapshot_sha256"], self.input_digest)
        self.assertEqual(out["model_bundle_sha256"], self.bundle["model_bundle_sha256"])
        self.assertLessEqual(len(out["original_top3"]), 3)
        self.assertLessEqual(len(out["selected_candidates"]), 3)
        self.assertEqual(out["decision_count"], len(out["selected_candidates"]))
        self.assertEqual(
            out["candidate_no_trade_recorded"], len(out["selected_candidates"]) == 0
        )
        self.assertTrue(out["structural_scoring_complete"])
        self.assertTrue(out["decision_recorded"])
        self.assertFalse(out["independent_source_admission_verified"])
        self.assertFalse(out["independent_model_admission_verified"])
        self.assertFalse(out["independent_chronology_admission_verified"])
        self.assertFalse(out["fresh_alpha_observation_admitted"])
        self.assertFalse(out["formal_shadow_s1"])
        self.assertFalse(out["promotion_authority"])
        self.assertFalse(out["outcome_attached"])
        self.assertFalse(out["live_order_authorized"])

    def test_ranking_is_reproducible_for_identical_input_and_bundle(self):
        a = self.capture()
        b = self.capture()
        self.assertEqual(a["decision_capture_sha256"], b["decision_capture_sha256"])
        self.assertEqual(a["ranked_scores"], b["ranked_scores"])
        self.assertEqual(a["selected_candidates"], b["selected_candidates"])

    def test_wrong_input_hash_or_predecision_capture_fails_closed(self):
        with self.assertRaisesRegex(ProspectiveDecisionCaptureError, "fingerprint"):
            self.capture(input_snapshot_sha256="0" * 64)
        early = self.dates[-1].strftime("%Y-%m-%d") + "T17:59:59+09:00"
        with self.assertRaisesRegex(ProspectiveDecisionCaptureError, "precede"):
            self.capture(captured_at=early)

    def test_tamper_or_authority_escalation_breaks_capture_validation(self):
        original = self.capture()
        changed = copy.deepcopy(original)
        changed["selected_candidates"] = []
        with self.assertRaises(ProspectiveDecisionCaptureError):
            validate_decision_capture(changed)
        changed = copy.deepcopy(original)
        changed["live_order_authorized"] = True
        with self.assertRaises(ProspectiveDecisionCaptureError):
            validate_decision_capture(changed)

    def test_same_session_store_is_append_only_and_idempotent(self):
        first_capture = self.capture()
        later_capture = self.capture(
            captured_at=self.dates[-1].strftime("%Y-%m-%d") + "T18:00:06+09:00"
        )
        with tempfile.TemporaryDirectory() as folder:
            git = Path(folder) / "git"
            git.mkdir()
            root = Path(folder) / "private"
            first = store_decision_capture(
                first_capture, root=str(root), git_worktree=str(git)
            )
            again = store_decision_capture(
                first_capture, root=str(root), git_worktree=str(git)
            )
            self.assertTrue(first["created"])
            self.assertFalse(again["created"])
            target = root / f"decision-{first_capture['session']}.json"
            original = target.read_bytes()
            with self.assertRaisesRegex(
                ProspectiveDecisionCaptureError, "same-session"
            ):
                store_decision_capture(
                    later_capture, root=str(root), git_worktree=str(git)
                )
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            self.assertFalse(any(p.name.startswith(".decision-") for p in root.iterdir()))

    def test_symbol_order_mutation_cannot_change_equal_score_tie_semantics(self):
        snapshot = dict(self.snapshot)
        snapshot["features"] = self.snapshot["features"].iloc[::-1].reset_index(drop=True)
        digest = input_snapshot_sha256(snapshot)
        with self.assertRaisesRegex(ProspectiveDecisionCaptureError, "canonical symbol sort"):
            build_decision_capture(
                snapshot, self.bundle,
                input_snapshot_sha256=digest,
                captured_at=self.captured_at,
            )


if __name__ == "__main__":
    unittest.main()
