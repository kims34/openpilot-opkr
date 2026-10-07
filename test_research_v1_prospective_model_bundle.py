"""Synthetic model-bundle tests; never project Alpha or trading evidence."""
import copy
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from research_v1_context import CONTEXT_FEATURES
from research_v1_distributional_netev import _pipe
from research_v1_prospective_model_bundle import (
    ProspectiveModelBundleError,
    build_model_bundle,
    store_model_bundle,
    validate_model_bundle,
)


def fitted_model():
    rng = np.random.default_rng(7)
    x = pd.DataFrame(
        rng.normal(size=(80, len(CONTEXT_FEATURES))), columns=CONTEXT_FEATURES
    )
    y = pd.Series(rng.normal(size=len(x)))
    model = _pipe(CONTEXT_FEATURES)
    model.fit(x, y)
    return model, x


def quantiles():
    base = {"low": -0.02, "med": 0.0, "high": 0.02, "n": 126}
    return {
        "__global__": dict(base),
        "low": {**base, "fallback_global": False, "bucket_n": 42},
        "mid": {**base, "fallback_global": False, "bucket_n": 42},
        "high": {**base, "fallback_global": False, "bucket_n": 42},
    }


def bundle():
    model, _ = fitted_model()
    return build_model_bundle(
        model,
        quantiles(),
        training_input_sha256="a" * 64,
        calibration_input_sha256="b" * 64,
        fit_code_commit="c" * 40,
        fit_code_path="research_v1_selected_calibration.py",
        train_end_session="2026-01-30",
        calibration_start_session="2026-02-09",
        calibration_end_session="2026-08-07",
        refit_policy_id="TEST_ONLY_EXPLICIT_CALLER_POLICY",
    )


class ProspectiveModelBundleTest(unittest.TestCase):
    def test_fitted_state_is_pickle_free_hash_bound_and_non_authorizing(self):
        out = bundle()
        self.assertTrue(validate_model_bundle(out)["valid"])
        self.assertEqual(out["feature_columns"], list(CONTEXT_FEATURES))
        self.assertEqual(len(out["ridge_coef"]), len(CONTEXT_FEATURES))
        self.assertTrue(out["model_identity_structurally_bound"])
        self.assertFalse(out["independent_model_admission_verified"])
        self.assertFalse(out["signal_generation_complete"])
        self.assertFalse(out["decision_recorded"])
        self.assertFalse(out["promotion_authority"])
        self.assertFalse(out["live_order_authorized"])
        self.assertNotIn("pickle", str(out).lower())

    def test_bundle_state_reproduces_pipeline_prediction(self):
        model, x = fitted_model()
        out = build_model_bundle(
            model,
            quantiles(),
            training_input_sha256="a" * 64,
            calibration_input_sha256="b" * 64,
            fit_code_commit="c" * 40,
            fit_code_path="research_v1_selected_calibration.py",
            train_end_session="2026-01-30",
            calibration_start_session="2026-02-09",
            calibration_end_session="2026-08-07",
            refit_policy_id="TEST_ONLY_EXPLICIT_CALLER_POLICY",
        )
        row = x.iloc[[3]][CONTEXT_FEATURES].to_numpy(dtype=float)[0]
        filled = np.where(
            np.isnan(row), np.asarray(out["imputer_statistics"]), row
        )
        scaled = (filled - np.asarray(out["scaler_mean"])) / np.asarray(out["scaler_scale"])
        manual = float(np.dot(scaled, np.asarray(out["ridge_coef"])) + out["ridge_intercept"])
        self.assertAlmostEqual(manual, float(model.predict(x.iloc[[3]])[0]), places=12)

    def test_tamper_or_authority_escalation_fails(self):
        original = bundle()
        cases = []
        changed = copy.deepcopy(original)
        changed["ridge_coef"][0] += 0.01
        cases.append(changed)
        changed = copy.deepcopy(original)
        changed["independent_model_admission_verified"] = True
        cases.append(changed)
        changed = copy.deepcopy(original)
        changed["live_order_authorized"] = True
        cases.append(changed)
        for candidate in cases:
            with self.subTest(candidate=candidate):
                with self.assertRaises(ProspectiveModelBundleError):
                    validate_model_bundle(candidate)

    def test_feature_order_and_chronology_are_frozen(self):
        model, _ = fitted_model()
        reversed_features = list(reversed(CONTEXT_FEATURES))
        with self.assertRaisesRegex(ProspectiveModelBundleError, "feature_columns"):
            build_model_bundle(
                model, quantiles(),
                training_input_sha256="a" * 64,
                calibration_input_sha256="b" * 64,
                fit_code_commit="c" * 40,
                fit_code_path="research_v1_selected_calibration.py",
                train_end_session="2026-01-30",
                calibration_start_session="2026-02-09",
                calibration_end_session="2026-08-07",
                refit_policy_id="TEST_ONLY_EXPLICIT_CALLER_POLICY",
                feature_columns=reversed_features,
            )
        with self.assertRaisesRegex(ProspectiveModelBundleError, "chronology"):
            build_model_bundle(
                model, quantiles(),
                training_input_sha256="a" * 64,
                calibration_input_sha256="b" * 64,
                fit_code_commit="c" * 40,
                fit_code_path="research_v1_selected_calibration.py",
                train_end_session="2026-09-01",
                calibration_start_session="2026-02-09",
                calibration_end_session="2026-08-07",
                refit_policy_id="TEST_ONLY_EXPLICIT_CALLER_POLICY",
            )

    def test_unfitted_or_wrong_ridge_fails_closed(self):
        with self.assertRaises(ProspectiveModelBundleError):
            build_model_bundle(
                _pipe(CONTEXT_FEATURES), quantiles(),
                training_input_sha256="a" * 64,
                calibration_input_sha256="b" * 64,
                fit_code_commit="c" * 40,
                fit_code_path="research_v1_selected_calibration.py",
                train_end_session="2026-01-30",
                calibration_start_session="2026-02-09",
                calibration_end_session="2026-08-07",
                refit_policy_id="TEST_ONLY_EXPLICIT_CALLER_POLICY",
            )

    def test_private_storage_is_atomic_idempotent_and_outside_git(self):
        out = bundle()
        with tempfile.TemporaryDirectory() as folder:
            git = Path(folder) / "git"
            git.mkdir()
            root = Path(folder) / "private"
            first = store_model_bundle(out, root=str(root), git_worktree=str(git))
            second = store_model_bundle(out, root=str(root), git_worktree=str(git))
            self.assertTrue(first["created"])
            self.assertFalse(second["created"])
            target = root / f"model-bundle-{out['model_bundle_sha256']}.json"
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            self.assertFalse(any(p.name.startswith(".model-bundle-") for p in root.iterdir()))
            with self.assertRaises(ValueError):
                store_model_bundle(out, root=str(git / "models"), git_worktree=str(git))


if __name__ == "__main__":
    unittest.main()
