"""End-to-end synthetic prospective session commit tests; no network/order use."""
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from research_v1_context import CONTEXT_FEATURES
from research_v1_prospective_frozen_producer import (
    FIRST_TEST_START_ORDINAL,
    FROZEN_CALENDAR_ORIGIN_SESSION,
    FROZEN_TEST_BLOCK_STARTS,
    fit_frozen_model_for_target,
)
from research_v1_prospective_session_commit import (
    ProspectiveSessionCommitError,
    commit_structural_prospective_session,
    validate_session_manifest,
)


ROOT = Path(__file__).parent
EVIDENCE = json.loads(
    (ROOT / "INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.json").read_text(
        encoding="utf-8"
    )
)


def sessions(n=800):
    values = [pd.Timestamp(FROZEN_CALENDAR_ORIGIN_SESSION)]
    for ordinal, expected_text in sorted(FROZEN_TEST_BLOCK_STARTS.items()):
        if ordinal >= n:
            break
        expected = pd.Timestamp(expected_text)
        while len(values) < ordinal:
            candidate = values[-1] + pd.Timedelta(days=1)
            if candidate >= expected:
                raise AssertionError("synthetic calendar cannot satisfy milestone")
            values.append(candidate)
        values.append(expected)
    while len(values) < n:
        values.append(values[-1] + pd.Timedelta(days=1))
    return [d.strftime("%Y-%m-%d") for d in values]


def supervised(calendar):
    rng = np.random.default_rng(20261008)
    symbols = ["000001", "000002", "000003", "000004"]
    rows = []
    for day in pd.to_datetime(calendar):
        for j, symbol in enumerate(symbols):
            vals = {
                k: float(v)
                for k, v in zip(
                    CONTEXT_FEATURES,
                    rng.normal(size=len(CONTEXT_FEATURES)),
                )
            }
            vals["vol20_rank"] = (j + 1) / len(symbols)
            rows.append({
                "decision_date": day,
                "symbol": symbol,
                "fh_label_available": True,
                "fh_net_return": float(rng.normal(scale=0.015)),
                **vals,
            })
    return pd.DataFrame(rows)


def master_rows():
    rows = []
    for i, symbol in enumerate(["000001", "000002", "000003", "000004"], start=1):
        rows.append({
            "ISU_CD": f"KR7{i:011d}"[-12:],
            "ISU_SRT_CD": symbol,
            "ISU_NM": f"테스트{i}",
            "ISU_ABBRV": f"테스트{i}",
            "ISU_ENG_NM": f"TEST{i}",
            "LIST_DD": "20000101",
            "MKT_TP_NM": "KOSPI",
            "SECUGRP_NM": "주권",
            "SECT_TP_NM": "",
            "KIND_STKCERT_TP_NM": "보통주",
            "PARVAL": "100",
            "LIST_SHRS": "1000000",
        })
    return rows


def daily_rows(target):
    bas = target.replace("-", "")
    rows = []
    for i, symbol in enumerate(["000001", "000002", "000003", "000004"], start=1):
        close = 10000 + i * 100
        rows.append({
            "BAS_DD": bas,
            "ISU_CD": symbol,
            "ISU_NM": f"테스트{i}",
            "MKT_NM": "KOSPI",
            "SECT_TP_NM": "",
            "TDD_CLSPRC": str(close),
            "FLUC_RT": str(0.10 * i),
            "CMPPREVDD_PRC": "10",
            "TDD_OPNPRC": str(close - 20),
            "TDD_HGPRC": str(close + 30),
            "TDD_LWPRC": str(close - 40),
            "ACC_TRDVOL": str(1000 * i),
            "ACC_TRDVAL": str(close * 1000 * i),
            "MKTCAP": "1000000000",
            "LIST_SHRS": "1000000",
        })
    return rows


def raw(rows):
    return json.dumps({"OutBlock_1": rows}, ensure_ascii=False).encode("utf-8")


def history(calendar, target):
    symbols = ["000001", "000002", "000003", "000004"]
    target_ts = pd.Timestamp(target)
    prior = [pd.Timestamp(x) for x in calendar if pd.Timestamp(x) < target_ts][-35:]
    rows = []
    for d_i, day in enumerate(prior):
        for i, symbol in enumerate(symbols, start=1):
            base = 9000 + i * 100 + d_i
            rows.append({
                "decision_date": day,
                "symbol": symbol,
                "open": float(base),
                "high": float(base + 30),
                "low": float(base - 30),
                "close": float(base + 10),
                "volume": float(1000 + i),
                "value": float((base + 10) * (1000 + i)),
                "krx_change_return": float(0.001 * i),
                "available_at": day.strftime("%Y-%m-%d") + "T18:00:00+09:00",
            })
    return pd.DataFrame(rows)


class ProspectiveSessionCommitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calendar = sessions()
        cls.target = cls.calendar[FIRST_TEST_START_ORDINAL + 12]
        cls.supervised = supervised(cls.calendar)
        cls.history = history(cls.calendar, cls.target)
        cls.daily = raw(daily_rows(cls.target))
        cls.master = raw(master_rows())
        cls.daily_seen = cls.target + "T17:10:05+09:00"
        cls.master_seen = cls.target + "T17:10:06+09:00"
        cls.decision_at = cls.target + "T18:00:00+09:00"
        cls.captured_at = cls.target + "T18:00:05+09:00"

    def run_commit(
        self,
        root,
        history_raw=None,
        supervised_frame=None,
        prebuilt_model_bundle=None,
    ):
        selected_supervised = (
            None
            if prebuilt_model_bundle is not None
            else (self.supervised if supervised_frame is None else supervised_frame)
        )
        return commit_structural_prospective_session(
            daily_raw=self.daily,
            master_raw=self.master,
            daily_retrieved_at=self.daily_seen,
            master_retrieved_at=self.master_seen,
            connectivity_evidence=EVIDENCE,
            history_raw=self.history if history_raw is None else history_raw,
            supervised_frame=selected_supervised,
            prebuilt_model_bundle=prebuilt_model_bundle,
            session_calendar=self.calendar,
            target_session=self.target,
            decision_at=self.decision_at,
            captured_at=self.captured_at,
            root=str(root),
            git_worktree=str(root.parent / "git"),
        )

    def test_full_structural_transaction_commits_only_non_authorizing_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            (base / "git").mkdir()
            root = base / "private"
            out = self.run_commit(root)
            self.assertTrue(out["structural_session_committed"])
            self.assertFalse(out["fresh_alpha_observation_admitted"])
            self.assertFalse(out["live_order_authorized"])
            manifest_path = root / f"session-{self.target}.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            checked = validate_session_manifest(manifest)
            self.assertTrue(checked["valid"])
            self.assertTrue((root / f"source-{self.target}.json").exists())
            self.assertTrue((root / f"input-{self.target}.json").exists())
            self.assertTrue((root / f"producer-{self.target}.json").exists())
            self.assertTrue((root / f"decision-{self.target}.json").exists())
            self.assertTrue(any(root.glob("model-bundle-*.json")))

    def test_prebuilt_frozen_bundle_commits_without_refit_input(self):
        fitted = fit_frozen_model_for_target(
            self.supervised,
            session_calendar=self.calendar,
            target_session=self.target,
        )
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            (base / "git").mkdir()
            root = base / "private"
            out = self.run_commit(
                root,
                prebuilt_model_bundle=fitted["model_bundle"],
            )
            self.assertEqual(
                out["model_bundle_sha256"],
                fitted["model_bundle"]["model_bundle_sha256"],
            )
            self.assertTrue(out["structural_session_committed"])
            self.assertFalse(out["fresh_alpha_observation_admitted"])
            manifest = json.loads(
                (root / f"session-{self.target}.json").read_text(encoding="utf-8")
            )
            self.assertFalse(manifest["independent_model_admission_verified"])
            self.assertFalse(manifest["live_order_authorized"])

    def test_identical_retry_is_idempotent_at_every_same_session_boundary(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            (base / "git").mkdir()
            root = base / "private"
            first = self.run_commit(root)
            second = self.run_commit(root)
            self.assertEqual(
                first["session_manifest_sha256"],
                second["session_manifest_sha256"],
            )
            self.assertEqual(
                first["decision_capture_sha256"],
                second["decision_capture_sha256"],
            )

    def test_failure_after_source_storage_never_creates_final_session_manifest(self):
        broken = self.supervised.copy()
        broken = broken[
            broken["decision_date"]
            < pd.Timestamp(self.calendar[100])
        ].copy()
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            (base / "git").mkdir()
            root = base / "private"
            with self.assertRaises(Exception):
                self.run_commit(root, supervised_frame=broken)
            self.assertTrue((root / f"source-{self.target}.json").exists())
            self.assertFalse((root / f"session-{self.target}.json").exists())
            self.assertFalse((root / f"decision-{self.target}.json").exists())

    def test_history_cannot_smuggle_target_or_future_rows(self):
        bad = self.history.copy()
        row = bad.iloc[[0]].copy()
        row["decision_date"] = pd.Timestamp(self.target)
        bad = pd.concat([bad, row], ignore_index=True)
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            (base / "git").mkdir()
            with self.assertRaisesRegex(
                ProspectiveSessionCommitError, "only sessions before"
            ):
                self.run_commit(base / "private", history_raw=bad)
            self.assertFalse((base / "private").exists())

    def test_manifest_authority_escalation_breaks_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            (base / "git").mkdir()
            root = base / "private"
            self.run_commit(root)
            manifest = json.loads(
                (root / f"session-{self.target}.json").read_text(encoding="utf-8")
            )
            manifest["live_order_authorized"] = True
            with self.assertRaises(ProspectiveSessionCommitError):
                validate_session_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
