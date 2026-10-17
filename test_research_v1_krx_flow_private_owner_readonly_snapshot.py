"""Synthetic owner-only file-access tests; never mount private KRX in CI."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

from research_v1_krx_flow_private_owner_readonly_snapshot import (
    KRXPrivateOwnerReadOnlyError,
    audit_owner_frozen_2026_10_03_private_snapshot,
    main,
    read_protected_krx_original_manifest_and_phase_state,
)
from research_v1_krx_flow_frozen_archive_bytes_gate import (
    audit_private_krx_flow_archived_snapshot_bytes,
)
from test_research_v1_krx_flow_frozen_archive_bytes_gate import original_fixture


class ReadOnlyKRXOwnerSnapshotTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.worktree = base / "worktree"
        self.worktree.mkdir()
        self.root = base / "sealed_data"
        self.root.mkdir(mode=0o700)
        (self.root / "task_manifests").mkdir(mode=0o700)
        (self.root / "batch_state").mkdir(mode=0o700)
        self.synthetic = original_fixture()
        self.manifest = self.root / "task_manifests" / "per-security-history-v3.json"
        self.state = self.root / "batch_state" / "PER_SECURITY_HISTORY.json"
        self.manifest.write_bytes(self.synthetic["private_manifest_bytes"])
        self.state.write_bytes(self.synthetic["private_phase_state_bytes"])
        os.chmod(self.manifest, 0o600)
        os.chmod(self.state, 0o600)

    def read(self):
        return read_protected_krx_original_manifest_and_phase_state(
            private_root=str(self.root), git_worktree=str(self.worktree)
        )

    def test_file_reads_reproduce_original_unchanged_bytes_and_mode(self):
        stat_before = [(p.stat().st_mtime_ns, stat.S_IMODE(p.stat().st_mode))
                       for p in (self.manifest, self.state)]
        first, second = self.read()
        self.assertEqual(first, self.synthetic["private_manifest_bytes"])
        self.assertEqual(second, self.synthetic["private_phase_state_bytes"])
        stat_after = [(p.stat().st_mtime_ns, stat.S_IMODE(p.stat().st_mode))
                      for p in (self.manifest, self.state)]
        self.assertEqual(stat_before, stat_after)
        result = audit_private_krx_flow_archived_snapshot_bytes(
            private_manifest_bytes=first,
            private_phase_state_bytes=second,
            **{k: v for k, v in self.synthetic.items()
               if k not in {"private_manifest_bytes", "private_phase_state_bytes"}},
        )
        self.assertEqual(result["investor_flow_completed_checkpoints"], 3)
        self.assertFalse(result["source_admitted"])

    def test_entrypoint_never_allows_synthetic_to_override_production_SHA(self):
        with self.assertRaisesRegex(Exception, "MANIFEST_BYTES_SHA_DRIFT"):
            audit_owner_frozen_2026_10_03_private_snapshot(
                private_root=str(self.root), git_worktree=str(self.worktree)
            )

    def test_positive_wrapper_only_with_injected_synthetic_auditor(self):
        def synthetic_verifier(*, private_manifest_bytes, private_phase_state_bytes):
            return audit_private_krx_flow_archived_snapshot_bytes(
                private_manifest_bytes=private_manifest_bytes,
                private_phase_state_bytes=private_phase_state_bytes,
                **{k: v for k, v in self.synthetic.items()
                   if k not in {"private_manifest_bytes", "private_phase_state_bytes"}},
            )
        with patch(
            "research_v1_krx_flow_private_owner_readonly_snapshot."
            "audit_frozen_2026_10_03_private_krx_flow_snapshot",
            side_effect=synthetic_verifier,
        ):
            result = audit_owner_frozen_2026_10_03_private_snapshot(
                private_root=str(self.root), git_worktree=str(self.worktree)
            )
        self.assertEqual(result["snapshot_audit_status"], "PASSED_INTERNAL_ARCHIVE_CHECKS")
        self.assertFalse(result["source_admitted"])
        self.assertFalse(result["source_owner_private_manifest_storage_origin_verified"])
        self.assertNotIn("KR7005930003", str(result))

    def test_relative_root_denied(self):
        with self.assertRaisesRegex(KRXPrivateOwnerReadOnlyError, "NOT_ABSOLUTE"):
            read_protected_krx_original_manifest_and_phase_state(
                private_root="sealed_data", git_worktree=str(self.worktree))

    def test_git_worktree_as_root_denied(self):
        with self.assertRaisesRegex(KRXPrivateOwnerReadOnlyError, "INSIDE_GIT_WORKTREE"):
            read_protected_krx_original_manifest_and_phase_state(
                private_root=str(self.worktree), git_worktree=str(self.worktree))

    def test_private_root_under_worktree_denied(self):
        inside = self.worktree / "secret"
        inside.mkdir()
        with self.assertRaisesRegex(KRXPrivateOwnerReadOnlyError, "INSIDE_GIT_WORKTREE"):
            read_protected_krx_original_manifest_and_phase_state(
                private_root=str(inside), git_worktree=str(self.worktree))

    def test_public_named_root_rejected(self):
        public = Path(self.temp.name) / "public"
        public.mkdir()
        with self.assertRaisesRegex(KRXPrivateOwnerReadOnlyError, "IN_PUBLIC_TREE"):
            read_protected_krx_original_manifest_and_phase_state(
                private_root=str(public), git_worktree=str(self.worktree))

    def test_symlink_private_root_denied(self):
        alias = Path(self.temp.name) / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(KRXPrivateOwnerReadOnlyError, "SYMLINK_REJECTED"):
            read_protected_krx_original_manifest_and_phase_state(
                private_root=str(alias), git_worktree=str(self.worktree))

    def test_symlink_original_manifest_denied(self):
        victim = self.root / "fake.json"
        victim.write_bytes(self.manifest.read_bytes())
        self.manifest.unlink()
        self.manifest.symlink_to(victim)
        with self.assertRaisesRegex(KRXPrivateOwnerReadOnlyError, "SYMLINK_REJECTED"):
            self.read()

    def test_non_private_file_mode_denied_without_chmod(self):
        os.chmod(self.manifest, 0o644)
        with self.assertRaisesRegex(KRXPrivateOwnerReadOnlyError, "PERMISSION_DRIFT"):
            self.read()
        self.assertEqual(stat.S_IMODE(self.manifest.stat().st_mode), 0o644)

    def test_missing_original_state_fail_closed(self):
        self.state.unlink()
        with self.assertRaisesRegex(KRXPrivateOwnerReadOnlyError, "READ_DENIED_OR_MISSING"):
            self.read()

    def test_directory_mislabelled_as_original_state_denied(self):
        self.state.unlink()
        self.state.mkdir()
        with self.assertRaisesRegex(KRXPrivateOwnerReadOnlyError, "NOT_REGULAR_FILE"):
            self.read()

    def test_main_stdout_only_fixed_safe_error_when_private_root_missing(self):
        out = io.StringIO()
        with patch.dict(os.environ, {"KRX_PRIVATE_RAW_DIR": ""}), redirect_stdout(out):
            self.assertEqual(main(), 2)
        data = json.loads(out.getvalue())
        self.assertEqual(data["snapshot_audit_status"], "BLOCKED")
        self.assertFalse(data["source_admitted"])
        self.assertFalse(data["network_request_attempted"])
        self.assertNotIn(str(self.root), out.getvalue())

    def test_main_does_not_print_real_paths_or_task_data_on_failed_pin(self):
        out = io.StringIO()
        with patch.dict(os.environ, {"KRX_PRIVATE_RAW_DIR": str(self.root)}):
            with patch("research_v1_krx_flow_private_owner_readonly_snapshot.Path.cwd",
                       return_value=self.worktree):
                with redirect_stdout(out):
                    self.assertEqual(main(), 2)
        self.assertEqual(json.loads(out.getvalue())["snapshot_audit_status"], "BLOCKED")
        self.assertNotIn(str(self.root), out.getvalue())
        self.assertNotIn("task_id", out.getvalue())
        self.assertNotIn("KR700593", out.getvalue())


if __name__ == "__main__":
    unittest.main()
