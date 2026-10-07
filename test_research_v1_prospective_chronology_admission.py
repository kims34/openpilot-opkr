"""Synthetic/private chronology admission tests with mocked GitHub API reads."""
import base64
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from research_v1_prospective_chronology_anchor import build_anchor_record
from research_v1_prospective_chronology_admission import (
    ProspectiveChronologyAdmissionError,
    verify_session_chronology_online,
)
from research_v1_prospective_session_commit import (
    commit_structural_prospective_session,
)
from test_research_v1_prospective_session_commit import (
    EVIDENCE,
    daily_rows,
    history,
    master_rows,
    raw,
    sessions,
    supervised,
)
from research_v1_prospective_frozen_producer import FIRST_TEST_START_ORDINAL


class ProspectiveChronologyAdmissionTest(unittest.TestCase):
    def setUp(self):
        self.calendar = sessions()
        self.target = self.calendar[FIRST_TEST_START_ORDINAL + 12]
        self.supervised = supervised(self.calendar)
        self.history = history(self.calendar, self.target)
        self.daily = raw(daily_rows(self.target))
        self.master = raw(master_rows())
        self.decision_at = self.target + "T18:00:00+09:00"
        self.run_id = 987654321
        self.run_attempt = 1
        self.workflow_ref = "1" * 40

    def _private_session(self, base):
        git = base / "git"
        git.mkdir()
        root = base / "private"
        out = commit_structural_prospective_session(
            daily_raw=self.daily,
            master_raw=self.master,
            daily_retrieved_at=self.target + "T17:10:05+09:00",
            master_retrieved_at=self.target + "T17:10:06+09:00",
            connectivity_evidence=EVIDENCE,
            history_raw=self.history,
            supervised_frame=self.supervised,
            session_calendar=self.calendar,
            target_session=self.target,
            decision_at=self.decision_at,
            captured_at=self.target + "T18:00:05+09:00",
            root=str(root),
            git_worktree=str(git),
        )
        manifest = json.loads(
            (root / f"session-{self.target}.json").read_text(encoding="utf-8")
        )
        decision = json.loads(
            (root / f"decision-{self.target}.json").read_text(encoding="utf-8")
        )
        record = build_anchor_record(
            session=self.target,
            decision_at=self.decision_at,
            source_receipt_sha256=out["source_receipt_sha256"],
            input_snapshot_sha256=out["input_snapshot_sha256"],
            producer_binding_sha256=out["producer_binding_sha256"],
            model_bundle_sha256=out["model_bundle_sha256"],
            decision_capture_sha256=out["decision_capture_sha256"],
            session_manifest_sha256=out["session_manifest_sha256"],
            workflow_ref_commit=self.workflow_ref,
            workflow_run_id=self.run_id,
            workflow_run_attempt=self.run_attempt,
        )
        return git, root, manifest, decision, record

    def _responses(self, record, *, created_at=None, run_overrides=None,
                   commit_overrides=None, content_record=None, commits_count=1):
        created_at = created_at or (
            pd.Timestamp(self.decision_at).tz_convert("UTC")
            + pd.Timedelta(minutes=5)
        ).isoformat()
        run = {
            "id": self.run_id,
            "run_attempt": self.run_attempt,
            "name": "IndexAlert Prospective Chronology Anchor",
            "path": ".github/workflows/indexalert-prospective-chronology-anchor.yml",
            "event": "workflow_dispatch",
            "status": "completed",
            "conclusion": "success",
            "head_sha": self.workflow_ref,
            "created_at": created_at,
        }
        run.update(run_overrides or {})
        commit_sha = "2" * 40
        commits = [{"sha": commit_sha} for _ in range(commits_count)]
        payload = json.dumps(
            content_record or record,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8") + b"\n"
        content = {
            "encoding": "base64",
            "content": base64.b64encode(payload).decode("ascii"),
        }
        commit = {
            "sha": commit_sha,
            "committer": {"login": "github-actions[bot]"},
            "commit": {
                "message": (
                    f"Anchor prospective session {self.target} "
                    f"(run {self.run_id})"
                ),
                "committer": {
                    "date": (
                        pd.Timestamp(created_at) + pd.Timedelta(minutes=1)
                    ).isoformat()
                },
            },
        }
        if commit_overrides:
            commit.update(commit_overrides)
        return run, commits, content, commit

    def _getter(self, run, commits, content, commit):
        def fake(path, *, params=None):
            if path.endswith(f"/actions/runs/{self.run_id}"):
                return run
            if path.endswith("/commits") and params and "path" in params:
                return commits
            if "/contents/prospective_anchors/" in path:
                return content
            if path.endswith("/commits/" + "2" * 40):
                return commit
            raise AssertionError((path, params))
        return fake

    def test_live_github_server_evidence_can_admit_chronology_only(self):
        with tempfile.TemporaryDirectory() as folder:
            git, root, _, _, record = self._private_session(Path(folder))
            responses = self._responses(record)
            with patch(
                "research_v1_prospective_chronology_admission._github_get_json",
                side_effect=self._getter(*responses),
            ):
                out = verify_session_chronology_online(
                    session=self.target,
                    root=str(root),
                    git_worktree=str(git),
                )
        self.assertTrue(out["private_components_bound"])
        self.assertTrue(out["github_server_chronology_verified"])
        self.assertTrue(out["independent_chronology_admission_verified"])
        self.assertFalse(out["independent_source_admission_verified"])
        self.assertFalse(out["independent_model_admission_verified"])
        self.assertFalse(out["fresh_alpha_observation_admitted"])
        self.assertFalse(out["formal_shadow_s1"])
        self.assertFalse(out["promotion_authority"])
        self.assertFalse(out["live_order_authorized"])

    def test_wrong_workflow_run_or_late_server_timestamp_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            git, root, _, _, record = self._private_session(Path(folder))
            bad_run = self._responses(
                record, run_overrides={"head_sha": "9" * 40}
            )
            with patch(
                "research_v1_prospective_chronology_admission._github_get_json",
                side_effect=self._getter(*bad_run),
            ):
                with self.assertRaisesRegex(
                    ProspectiveChronologyAdmissionError, "head_sha"
                ):
                    verify_session_chronology_online(
                        session=self.target, root=str(root), git_worktree=str(git)
                    )

            late = (
                pd.Timestamp(self.decision_at).tz_convert("UTC")
                + pd.Timedelta(hours=6, seconds=1)
            ).isoformat()
            bad_time = self._responses(record, created_at=late)
            with patch(
                "research_v1_prospective_chronology_admission._github_get_json",
                side_effect=self._getter(*bad_time),
            ):
                with self.assertRaisesRegex(
                    ProspectiveChronologyAdmissionError, "six-hour"
                ):
                    verify_session_chronology_online(
                        session=self.target, root=str(root), git_worktree=str(git)
                    )

    def test_anchor_branch_must_have_exactly_one_commit_for_session_path(self):
        with tempfile.TemporaryDirectory() as folder:
            git, root, _, _, record = self._private_session(Path(folder))
            responses = self._responses(record, commits_count=2)
            with patch(
                "research_v1_prospective_chronology_admission._github_get_json",
                side_effect=self._getter(*responses),
            ):
                with self.assertRaisesRegex(
                    ProspectiveChronologyAdmissionError, "exactly one"
                ):
                    verify_session_chronology_online(
                        session=self.target, root=str(root), git_worktree=str(git)
                    )

    def test_public_anchor_tamper_or_manual_commit_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            git, root, _, _, record = self._private_session(Path(folder))
            changed = copy.deepcopy(record)
            changed["decision_capture_sha256"] = "0" * 64
            responses = self._responses(record, content_record=changed)
            with patch(
                "research_v1_prospective_chronology_admission._github_get_json",
                side_effect=self._getter(*responses),
            ):
                with self.assertRaises(Exception):
                    verify_session_chronology_online(
                        session=self.target, root=str(root), git_worktree=str(git)
                    )

            responses = self._responses(
                record,
                commit_overrides={"committer": {"login": "someone-else"}},
            )
            with patch(
                "research_v1_prospective_chronology_admission._github_get_json",
                side_effect=self._getter(*responses),
            ):
                with self.assertRaisesRegex(
                    ProspectiveChronologyAdmissionError, "github-actions"
                ):
                    verify_session_chronology_online(
                        session=self.target, root=str(root), git_worktree=str(git)
                    )


if __name__ == "__main__":
    unittest.main()
