"""Synthetic tests for the exact freeze-anchor anchored-WF producer schedule."""
import copy
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from research_v1_context import CONTEXT_FEATURES
from research_v1_prospective_frozen_producer import (
    CALIBRATION_SESSIONS,
    FIRST_TEST_START_ORDINAL,
    FREEZE_ANCHOR_COMMIT,
    REFIT_POLICY_ID,
    TEST_SESSIONS,
    FrozenProspectiveProducerError,
    fit_frozen_model_for_target,
    resolve_anchored_schedule,
    store_producer_binding,
    validate_producer_binding,
)


def calendar(n=900):
    return [d.strftime("%Y-%m-%d") for d in pd.bdate_range("2023-01-02", periods=n)]


def supervised(cal):
    rng = np.random.default_rng(20261008)
    rows = []
    symbols = ["000001", "000002", "000003", "000004"]
    for day in pd.to_datetime(cal):
        for j, symbol in enumerate(symbols):
            feature = rng.normal(size=len(CONTEXT_FEATURES))
            values = {k: float(v) for k, v in zip(CONTEXT_FEATURES, feature)}
            # vol20_rank is a rank feature and must remain in [0,1] for calibration.
            values["vol20_rank"] = (j + 1) / len(symbols)
            rows.append({
                "decision_date": day,
                "symbol": symbol,
                "fh_label_available": True,
                "fh_net_return": float(rng.normal(scale=0.02)),
                **values,
            })
    return pd.DataFrame(rows)


class FrozenProspectiveProducerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sessions = calendar()
        cls.z = supervised(cls.sessions)

    def test_schedule_exactly_matches_freeze_anchor_block_arithmetic(self):
        target = self.sessions[FIRST_TEST_START_ORDINAL + 7]
        out = resolve_anchored_schedule(self.sessions, target_session=target)
        self.assertEqual(out["test_block_index"], 0)
        self.assertEqual(out["test_block_start_ordinal"], 640)
        self.assertEqual(out["actual_train_sessions"], 504)
        self.assertEqual(out["calibration_sessions"], 126)
        self.assertEqual(out["target_ordinal_in_test_block"], 7)
        self.assertEqual(out["train_end_session"], self.sessions[503])
        self.assertEqual(out["calibration_start_session"], self.sessions[509])
        self.assertEqual(out["calibration_end_session"], self.sessions[634])
        self.assertEqual(out["test_block_start_session"], self.sessions[640])

        second = resolve_anchored_schedule(
            self.sessions,
            target_session=self.sessions[FIRST_TEST_START_ORDINAL + TEST_SESSIONS + 3],
        )
        self.assertEqual(second["test_block_index"], 1)
        self.assertEqual(second["actual_train_sessions"], 630)
        self.assertEqual(second["test_block_start_ordinal"], 766)

    def test_frozen_fit_binds_exact_anchor_code_and_schedule_without_authority(self):
        target = self.sessions[FIRST_TEST_START_ORDINAL + 11]
        out = fit_frozen_model_for_target(
            self.z, session_calendar=self.sessions, target_session=target
        )
        binding, bundle = out["producer_binding"], out["model_bundle"]
        valid = validate_producer_binding(binding, bundle, target_session=target)
        self.assertTrue(valid["valid"])
        self.assertEqual(binding["freeze_anchor_commit"], FREEZE_ANCHOR_COMMIT)
        self.assertEqual(binding["refit_policy_id"], REFIT_POLICY_ID)
        self.assertEqual(bundle["fit_code_commit"], FREEZE_ANCHOR_COMMIT)
        self.assertEqual(bundle["refit_policy_id"], REFIT_POLICY_ID)
        self.assertFalse(binding["consumed_v1_holdout_used"])
        self.assertFalse(binding["current_session_features_consumed_for_fit"])
        self.assertFalse(binding["current_or_test_outcomes_consumed_for_fit"])
        self.assertFalse(binding["independent_model_admission_verified"])
        self.assertFalse(binding["fresh_alpha_observation_admitted"])
        self.assertFalse(binding["live_order_authorized"])

    def test_mutating_current_or_test_outcomes_cannot_change_model_or_binding(self):
        target_index = FIRST_TEST_START_ORDINAL + 20
        target = self.sessions[target_index]
        first = fit_frozen_model_for_target(
            self.z, session_calendar=self.sessions, target_session=target
        )
        changed = self.z.copy()
        test_dates = set(pd.to_datetime(
            self.sessions[FIRST_TEST_START_ORDINAL:FIRST_TEST_START_ORDINAL + TEST_SESSIONS]
        ))
        mask = changed["decision_date"].isin(test_dates)
        changed.loc[mask, "fh_net_return"] = 999.0
        second = fit_frozen_model_for_target(
            changed, session_calendar=self.sessions, target_session=target
        )
        self.assertEqual(
            first["model_bundle"]["model_bundle_sha256"],
            second["model_bundle"]["model_bundle_sha256"],
        )
        self.assertEqual(
            first["producer_binding"]["producer_binding_sha256"],
            second["producer_binding"]["producer_binding_sha256"],
        )

    def test_mutating_calibration_outcome_changes_binding(self):
        target = self.sessions[FIRST_TEST_START_ORDINAL + 2]
        first = fit_frozen_model_for_target(
            self.z, session_calendar=self.sessions, target_session=target
        )
        changed = self.z.copy()
        cal_day = pd.Timestamp(self.sessions[509])
        idx = changed.index[changed["decision_date"].eq(cal_day)][0]
        changed.loc[idx, "fh_net_return"] = (
            float(changed.loc[idx, "fh_net_return"]) + 0.5
        )
        second = fit_frozen_model_for_target(
            changed, session_calendar=self.sessions, target_session=target
        )
        self.assertNotEqual(
            first["producer_binding"]["calibration_input_sha256"],
            second["producer_binding"]["calibration_input_sha256"],
        )

    def test_pre_first_test_target_and_tamper_fail_closed(self):
        with self.assertRaisesRegex(
            FrozenProspectiveProducerError, "precedes first"
        ):
            resolve_anchored_schedule(
                self.sessions,
                target_session=self.sessions[FIRST_TEST_START_ORDINAL - 1],
            )
        target = self.sessions[FIRST_TEST_START_ORDINAL + 1]
        out = fit_frozen_model_for_target(
            self.z, session_calendar=self.sessions, target_session=target
        )
        changed = copy.deepcopy(out["producer_binding"])
        changed["live_order_authorized"] = True
        with self.assertRaises(FrozenProspectiveProducerError):
            validate_producer_binding(changed, out["model_bundle"])

    def test_private_binding_store_is_append_only_and_idempotent(self):
        target = self.sessions[FIRST_TEST_START_ORDINAL + 5]
        out = fit_frozen_model_for_target(
            self.z, session_calendar=self.sessions, target_session=target
        )
        with tempfile.TemporaryDirectory() as folder:
            git = Path(folder) / "git"
            git.mkdir()
            root = Path(folder) / "private"
            a = store_producer_binding(
                out["producer_binding"], out["model_bundle"],
                root=str(root), git_worktree=str(git),
            )
            b = store_producer_binding(
                out["producer_binding"], out["model_bundle"],
                root=str(root), git_worktree=str(git),
            )
            self.assertTrue(a["created"])
            self.assertFalse(b["created"])
            p = root / f"producer-{target}.json"
            self.assertEqual(p.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
