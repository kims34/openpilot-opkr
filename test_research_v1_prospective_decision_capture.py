"""Synthetic prospective decision capture tests; no market/network/order use."""
import copy
import hashlib
import json
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
from research_v1_prospective_frozen_producer import (
    CALIBRATION_SOURCE_ID,
    FIT_CODE_PATH,
    FREEZE_ANCHOR_COMMIT,
    FROZEN_CALENDAR_ORIGIN_SESSION,
    FROZEN_CALENDAR_REFERENCE_ACTION_ID,
    REFIT_POLICY_ID,
)
from research_v1_prospective_model_bundle import build_model_bundle
from test_research_v1_causal_evidence_integrity import synthetic_panel


def _quantiles(offset=-0.001):
    base = {
        "low": offset, "med": offset + 0.005, "high": offset + 0.01,
        "n": 126, "source": CALIBRATION_SOURCE_ID,
    }
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
        target_day = pd.Timestamp(self.dates[-1])
        train_end = (target_day - pd.Timedelta(days=120)).strftime("%Y-%m-%d")
        cal_start = (target_day - pd.Timedelta(days=100)).strftime("%Y-%m-%d")
        cal_end = (target_day - pd.Timedelta(days=20)).strftime("%Y-%m-%d")
        self.bundle = build_model_bundle(
            model, _quantiles(),
            training_input_sha256="a" * 64,
            calibration_input_sha256="b" * 64,
            fit_code_commit=FREEZE_ANCHOR_COMMIT,
            fit_code_path=FIT_CODE_PATH,
            train_end_session=train_end,
            calibration_start_session=cal_start,
            calibration_end_session=cal_end,
            refit_policy_id=REFIT_POLICY_ID,
        )
        test_start = "2018-02-19"
        producer_body = {
            "classification": "FROZEN_PRODUCER_BINDING_NOT_ADMITTED",
            "freeze_anchor_commit": FREEZE_ANCHOR_COMMIT,
            "fit_code_path": FIT_CODE_PATH,
            "refit_policy_id": REFIT_POLICY_ID,
            "target_session": target_day.strftime("%Y-%m-%d"),
            "target_session_ordinal": 650,
            "test_block_index": 0,
            "test_block_start_ordinal": 640,
            "test_block_end_ordinal_exclusive": 766,
            "test_block_start_session": test_start,
            "target_ordinal_in_test_block": 10,
            "calendar_origin_session": FROZEN_CALENDAR_ORIGIN_SESSION,
            "calendar_reference_action_id": FROZEN_CALENDAR_REFERENCE_ACTION_ID,
            "calendar_milestones_verified_through_target": True,
            "session_calendar_prefix_sha256": "d" * 64,
            "initial_train_sessions": 504,
            "actual_train_sessions": 504,
            "calibration_sessions": 126,
            "test_sessions": 126,
            "purge_sessions": 5,
            "train_end_session": train_end,
            "calibration_start_session": cal_start,
            "calibration_end_session": cal_end,
            "training_input_sha256": self.bundle["training_input_sha256"],
            "calibration_input_sha256": self.bundle["calibration_input_sha256"],
            "model_bundle_sha256": self.bundle["model_bundle_sha256"],
            "historical_backfill_forbidden": True,
            "consumed_v1_holdout_used": False,
            "current_session_features_consumed_for_fit": False,
            "current_or_test_outcomes_consumed_for_fit": False,
            "independent_model_admission_verified": False,
            "fresh_alpha_observation_admitted": False,
            "promotion_authority": False,
            "live_order_authorized": False,
        }
        producer_sha = hashlib.sha256(
            json.dumps(
                producer_body, sort_keys=True, ensure_ascii=False,
                separators=(",", ":"), allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        self.producer_binding = {
            **producer_body, "producer_binding_sha256": producer_sha
        }
        self.captured_at = self.dates[-1].strftime("%Y-%m-%d") + "T18:00:05+09:00"

    def capture(self, **kwargs):
        return build_decision_capture(
            self.snapshot,
            self.bundle,
            producer_binding=kwargs.get("producer_binding", self.producer_binding),
            input_snapshot_sha256=kwargs.get("input_snapshot_sha256", self.input_digest),
            captured_at=kwargs.get("captured_at", self.captured_at),
        )

    def test_capture_binds_full_ranking_top3_veto_and_never_grants_authority(self):
        out = self.capture()
        self.assertTrue(validate_decision_capture(out)["valid"])
        self.assertEqual(out["input_snapshot_sha256"], self.input_digest)
        self.assertEqual(out["model_bundle_sha256"], self.bundle["model_bundle_sha256"])
        self.assertEqual(
            out["producer_binding_sha256"],
            self.producer_binding["producer_binding_sha256"],
        )
        self.assertEqual(out["producer_refit_policy_id"], REFIT_POLICY_ID)
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

    def test_wrong_or_escalated_producer_binding_fails_before_scoring(self):
        changed = copy.deepcopy(self.producer_binding)
        changed["live_order_authorized"] = True
        with self.assertRaisesRegex(
            ProspectiveDecisionCaptureError, "producer binding"
        ):
            self.capture(producer_binding=changed)

        changed = copy.deepcopy(self.producer_binding)
        changed["target_session"] = (
            pd.Timestamp(self.dates[-1]) - pd.Timedelta(days=1)
        ).strftime("%Y-%m-%d")
        body = dict(changed)
        body.pop("producer_binding_sha256")
        changed["producer_binding_sha256"] = hashlib.sha256(
            json.dumps(
                body, sort_keys=True, ensure_ascii=False,
                separators=(",", ":"), allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        with self.assertRaisesRegex(
            ProspectiveDecisionCaptureError, "producer binding"
        ):
            self.capture(producer_binding=changed)

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
                producer_binding=self.producer_binding,
                input_snapshot_sha256=digest,
                captured_at=self.captured_at,
            )


if __name__ == "__main__":
    unittest.main()
