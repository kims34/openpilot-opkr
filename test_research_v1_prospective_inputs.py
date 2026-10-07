"""Synthetic tests; no actual signals, market collection or trading."""
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_pit_labels import make_pit_supervised
from research_v1_prospective_inputs import (
    ProspectiveInputError, build_current_session_inputs, store_input_snapshot,
)
from test_research_v1_causal_evidence_integrity import synthetic_panel


class ProspectiveInputsTest(unittest.TestCase):
    def setUp(self):
        self.dates, self.raw = synthetic_panel()
        self.raw["available_at"] = self.raw.decision_date.dt.strftime("%Y-%m-%d") + "T17:00:00+09:00"
        self.at = self.dates[-1].strftime("%Y-%m-%d") + "T18:00:00+09:00"

    def build(self, raw=None, at=None):
        return build_current_session_inputs(self.raw if raw is None else raw, decision_at=self.at if at is None else at)

    def test_current_session_needs_no_future_prices_or_labels(self):
        snapshot = self.build()
        self.assertEqual(snapshot["session"], self.dates[-1].strftime("%Y-%m-%d"))
        self.assertEqual(set(snapshot["features"].decision_date), {self.dates[-1]})
        self.assertEqual(len(snapshot["features"]), 2)
        self.assertFalse(snapshot["decision_recorded"])
        self.assertFalse(snapshot["no_trade_recorded"])
        self.assertFalse(snapshot["independent_source_admission_verified"])

    def test_future_rows_and_outcome_columns_cannot_change_inputs(self):
        original = self.build()
        future = self.raw.iloc[:1].copy()
        future["decision_date"] = self.dates[-1] + pd.Timedelta(days=3)
        future["available_at"] = "not-a-timestamp"
        future["close"] = -999
        mixed = pd.concat([self.raw, future], ignore_index=True)
        mixed["fh_net_return"] = 9999
        mixed["entry_fillable"] = False
        changed = self.build(mixed)
        self.assertEqual(original["input_sha256"], changed["input_sha256"])
        pd.testing.assert_frame_equal(original["features"], changed["features"])

    def test_mature_date_features_match_frozen_reference(self):
        frame, _, _ = make_pit_supervised(self.raw, horizon=5)
        reference = add_context(frame[frame.adv20_rank >= .20].copy())
        day = self.dates[30]
        result = self.build(at=day.strftime("%Y-%m-%d")+"T18:00:00+09:00")
        expected = reference[reference.decision_date.eq(day)].sort_values("symbol").reset_index(drop=True)
        pd.testing.assert_frame_equal(result["features"], expected[["decision_date", "symbol", *CONTEXT_FEATURES]])

    def test_late_row_rejects_whole_cross_section_instead_of_reranking(self):
        raw = self.raw.copy()
        raw.loc[raw.index[-1], "available_at"] = self.dates[-1].strftime("%Y-%m-%d")+"T19:00:00+09:00"
        with self.assertRaises(ProspectiveInputError):
            self.build(raw)

    def test_stale_or_insufficient_inputs_cannot_be_no_trade(self):
        with self.assertRaises(ProspectiveInputError):
            self.build(at=(self.dates[-1]+pd.Timedelta(days=3)).strftime("%Y-%m-%d")+"T18:00:00+09:00")
        with self.assertRaises(ProspectiveInputError):
            self.build(self.raw[self.raw.decision_date.eq(self.dates[-1])])

    def test_duplicate_and_naive_availability_fail(self):
        with self.assertRaises(ProspectiveInputError):
            self.build(pd.concat([self.raw, self.raw.iloc[:1]], ignore_index=True))
        raw = self.raw.copy()
        raw.loc[raw.index[0], "available_at"] = "2026-01-05T17:00:00"
        with self.assertRaises(ProspectiveInputError):
            self.build(raw)

    def test_order_insensitive_input_identity(self):
        original = self.build()
        shuffled = self.build(self.raw.sample(frac=1, random_state=7))
        self.assertEqual(original["input_sha256"], shuffled["input_sha256"])
        pd.testing.assert_frame_equal(original["features"], shuffled["features"])

    def test_private_checkpoint_retries_preserve_original_and_reject_conflict(self):
        with tempfile.TemporaryDirectory() as folder:
            git = Path(folder)/"git"
            git.mkdir()
            root = Path(folder)/"private"
            snapshot = self.build()
            first = store_input_snapshot(snapshot, root=str(root), git_worktree=str(git))
            again = store_input_snapshot(snapshot, root=str(root), git_worktree=str(git))
            self.assertTrue(first["created"])
            self.assertFalse(again["created"])
            self.assertEqual(first["snapshot_sha256"], again["snapshot_sha256"])
            target = root/f"input-{snapshot['session']}.json"
            original = target.read_bytes()
            conflicting = dict(snapshot, input_sha256="0"*64)
            with self.assertRaises(ProspectiveInputError):
                store_input_snapshot(conflicting, root=str(root), git_worktree=str(git))
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            self.assertFalse(any(p.name.startswith(".input-") for p in root.iterdir()))
            with self.assertRaises(ValueError):
                store_input_snapshot(snapshot, root=str(git/"inputs"), git_worktree=str(git))


if __name__ == "__main__":
    unittest.main()
