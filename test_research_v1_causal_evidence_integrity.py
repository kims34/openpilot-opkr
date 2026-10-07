"""Synthetic regressions: no private market data, performance trial or network."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from research_v1_fixed_horizon_label import (
    IncompleteFixedHorizonEvidence,
    add_fixed_horizon_target,
)
from research_v1_pit_labels import make_pit_supervised
from research_v1_supervised_cache import (
    CACHE_VERSION, REQUIRED_FEATURE_RETURN_POLICY, SupervisedCachePolicyMismatch,
    _source_fingerprint, load_or_build,
)


def synthetic_panel():
    dates = pd.bdate_range("2026-01-05", periods=45)
    raw = pd.DataFrame([
        dict(decision_date=d, symbol=s, open=100.0+i, high=(100.0+i)*1.01,
             low=(100.0+i)*.99, close=100.0+i, volume=1_000_000.,
             value=1_000_000_000., krx_change_return=.001+(.0001 if i%2 else 0),
             point_in_time_universe=True)
        for s in ("SYNTH_A", "SYNTH_B") for i, d in enumerate(dates)
    ])
    return dates, raw


class FixedHorizonCompletenessTest(unittest.TestCase):
    def setUp(self):
        self.dates, self.raw = synthetic_panel()
        self.decision = self.dates[30]

    def prepared(self, raw):
        frame, records, _ = make_pit_supervised(raw, horizon=5)
        frame = frame[frame.decision_date.eq(self.decision)].copy()
        records = {key: rec for key, rec in records.items() if key[0] == self.decision.date()}
        return frame, records

    def test_entered_position_with_missing_exit_blocks_whole_evaluation(self):
        raw = self.raw[~(self.raw.symbol.eq("SYNTH_A") & self.raw.decision_date.eq(self.dates[35]))]
        frame, records = self.prepared(raw)
        self.assertEqual(records[(self.decision.date(), "SYNTH_A")].outcome, "STOP_DATA_GAP")
        with self.assertRaises(IncompleteFixedHorizonEvidence):
            add_fixed_horizon_target(raw, frame, records, 5)

    def test_missing_internal_bar_blocks_even_when_both_endpoints_exist(self):
        raw = self.raw[~(self.raw.symbol.eq("SYNTH_A") & self.raw.decision_date.eq(self.dates[33]))]
        frame, records = self.prepared(raw)
        with self.assertRaises(IncompleteFixedHorizonEvidence):
            add_fixed_horizon_target(raw, frame, records, 5)

    def test_missing_or_invalid_internal_return_cannot_be_bridged(self):
        for invalid in (np.nan, np.inf, -1.0):
            with self.subTest(invalid=invalid):
                raw = self.raw.copy()
                raw.loc[raw.symbol.eq("SYNTH_A") & raw.decision_date.eq(self.dates[33]), "krx_change_return"] = invalid
                frame, records = self.prepared(raw)
                with self.assertRaises(IncompleteFixedHorizonEvidence):
                    add_fixed_horizon_target(raw, frame, records, 5)

    def test_real_no_entry_remains_unlabelled_without_inventing_a_loss(self):
        raw = self.raw[~(self.raw.symbol.eq("SYNTH_A") & self.raw.decision_date.eq(self.dates[31]))]
        frame, records = self.prepared(raw)
        self.assertNotIn((self.decision.date(), "SYNTH_A"), records)
        z = add_fixed_horizon_target(raw, frame, records, 5)
        row = z[z.symbol.eq("SYNTH_A")].iloc[0]
        self.assertFalse(row.fh_label_available)
        self.assertTrue(pd.isna(row.fh_net_return))

    def test_complete_path_preserves_original_h5_values(self):
        frame, records = self.prepared(self.raw)
        z = add_fixed_horizon_target(self.raw, frame, records, 5)
        expected = np.prod([1+.001+(.0001 if i%2 else 0) for i in range(32, 36)])-1
        for row in z.itertuples():
            self.assertTrue(row.fh_label_available)
            self.assertAlmostEqual(row.fh_gross_return, expected, places=12)
            self.assertAlmostEqual(row.fh_net_return, expected-records[(self.decision.date(), row.symbol)].cost_return, places=12)
        self.assertFalse(any(c.startswith("_fh_") for c in z.columns))


class CachePolicyIsolationTest(unittest.TestCase):
    POLICY = dict(horizon=5, target_return=.04, stop_return=-.025,
                  participation=.0005, commission_round_trip_bps=3.)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        _, self.raw = synthetic_panel()
        self.meta = dict(version=CACHE_VERSION,
                         feature_return_policy=REQUIRED_FEATURE_RETURN_POLICY,
                         source_fingerprint=_source_fingerprint(self.raw),
                         diagnostics={}, **self.POLICY)
        self.write_meta()
        (self.root / "supervised.parquet").write_bytes(b"SYNTHETIC_PARQUET_PLACEHOLDER")

    def write_meta(self):
        (self.root / "meta.json").write_text(json.dumps(self.meta), encoding="utf-8")

    def assert_rejected_without_read_or_rebuild(self, **requested):
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        with patch("research_v1_supervised_cache.pd.read_parquet") as reader, \
             patch("research_v1_supervised_cache.build_cache") as builder:
            with self.assertRaises(SupervisedCachePolicyMismatch):
                load_or_build(self.raw, self.root, **requested)
            reader.assert_not_called()
            builder.assert_not_called()
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_every_requested_label_or_cost_parameter_is_bound_before_read(self):
        for field, value in dict(horizon=10, target_return=.08, stop_return=-.05,
                                 participation=.001, commission_round_trip_bps=300.).items():
            with self.subTest(field=field):
                self.assert_rejected_without_read_or_rebuild(**{field: value})

    def test_missing_policy_metadata_does_not_delete_existing_evidence(self):
        del self.meta["horizon"]
        self.write_meta()
        self.assert_rejected_without_read_or_rebuild()

    def test_policy_mismatch_is_not_hidden_by_stale_source_rebuild(self):
        self.meta["source_fingerprint"] = {"stale": True}
        self.write_meta()
        self.assert_rejected_without_read_or_rebuild(horizon=10)

    def test_matching_defaults_and_explicit_policy_use_existing_cache(self):
        cached = pd.DataFrame({"decision_date": [self.raw.decision_date.iloc[0]]})
        with patch("research_v1_supervised_cache.pd.read_parquet", return_value=cached.copy()) as reader, \
             patch("research_v1_supervised_cache.build_cache") as builder:
            result = load_or_build(self.raw, self.root)
            self.assertEqual(result[3]["horizon"], 5)
            load_or_build(self.raw, self.root, **self.POLICY)
            self.assertEqual(reader.call_count, 2)
            builder.assert_not_called()

    def test_unknown_policy_argument_fails_on_cache_hit(self):
        with self.assertRaises(TypeError):
            load_or_build(self.raw, self.root, commission_typo=300.)


if __name__ == "__main__":
    unittest.main()
