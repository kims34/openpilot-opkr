"""Synthetic-only adversarial candidate-vs-archive source lineage tests."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import research_v1_runtime_archived_source_gate as archived
import research_v1_runtime_candidate_merge_gate as candidate


class CandidateMergeLineageTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.orig = {}
        self.impl = {}
        self.changed = {}
        for group, target in (
            (archived.ARCHIVED_GIT_BLOBS, self.orig),
            (archived.ARCHIVED_DIRECT_IMPLEMENTATION_BLOBS, self.impl),
            (candidate.EXACT_UPSTREAM_CHANGED_BLOBS, self.changed),
        ):
            for name in group:
                if name in target:
                    continue
                payload = ("synthetic candidate file " + name + "\n").encode()
                # candidate version differs from archived manifest on purpose
                if name == "research_v1_runtime_manifest.py" and target is self.changed:
                    payload += b"no-follow new candidate"
                target[name] = archived.git_blob_sha1(payload)
                (self.root / name).write_bytes(payload)
        # Synthetic source manifest must refer to the synthetic archived
        # body, not the real immutable Git blob from production evidence.
        baseline_manifest = self.impl["research_v1_runtime_manifest.py"]
        self.staged = []
        for obj, replacements in (
            (archived.ARCHIVED_GIT_BLOBS, self.orig),
            (archived.ARCHIVED_DIRECT_IMPLEMENTATION_BLOBS, self.impl),
            (candidate.EXACT_UPSTREAM_CHANGED_BLOBS, self.changed),
        ):
            p = patch.dict(obj, replacements, clear=True)
            p.start()
            self.addCleanup(p.stop)
        original_anchor = candidate.EXPECTED_CURRENT_ARCHIVED_MANIFEST
        candidate.EXPECTED_CURRENT_ARCHIVED_MANIFEST = baseline_manifest
        self.addCleanup(setattr, candidate, "EXPECTED_CURRENT_ARCHIVED_MANIFEST", original_anchor)

    def check(self, **changes):
        request = dict(
            root=self.root,
            base_ref=candidate.APPROVED_SCOPE_BASE_REF,
            head_ref=candidate.APPROVED_SCOPE_HEAD_REF,
            base_head_sha=candidate.EXACT_UPSTREAM_HEAD,
            event_name="pull_request",
        )
        request.update(changes)
        return candidate.check_candidate(**request)

    def test_specific_reviewed_candidate_proof_not_trading_or_merge_authority(self):
        out = self.check()
        self.assertEqual(out["checked_files"], 20)
        self.assertFalse(out["candidate_approved_for_merge"])
        self.assertFalse(out["original_archived_manifest_replayed_without_change"])
        self.assertFalse(out["profitability_evaluated"])
        self.assertFalse(out["ordering"])

    def test_moved_upstream_head_must_not_reuse_proof(self):
        with self.assertRaises(candidate.CandidateLineageError):
            self.check(base_head_sha="f" * 40)

    def test_unreviewed_branch_or_push_mode_must_not_reuse_proof(self):
        for changes in (dict(base_ref="main"),
                        dict(head_ref="index-alert-research-v1"),
                        dict(event_name="push")):
            with self.subTest(changes=changes), self.assertRaises(candidate.CandidateLineageError):
                self.check(**changes)

    def test_changed_candidate_security_manifest_fails(self):
        f = self.root / "research_v1_runtime_manifest.py"
        f.write_bytes(f.read_bytes() + b"new unreviewed manifest variant")
        with self.assertRaises(candidate.CandidateLineageError):
            self.check()

    def test_archive_test_body_or_direct_calculation_mutation_fails(self):
        for name in ("test_research_v1_core.py", "research_v1_portfolio.py",
                     "research_v1_ml.py", "requirements-indexalert-runtime-ci.txt"):
            f = self.root / name
            before = f.read_bytes()
            f.write_bytes(before + b"changed")
            with self.subTest(filename=name), self.assertRaises(candidate.CandidateLineageError):
                self.check()
            f.write_bytes(before)

    def test_candidate_control_file_missing_or_symlinked_fails(self):
        f = self.root / "test_research_v1_runtime_ci_integrity.py"
        f.unlink()
        with self.assertRaises(candidate.CandidateLineageError):
            self.check()
        f.symlink_to(self.root / "test_research_v1_core.py")
        with self.assertRaises(candidate.CandidateLineageError):
            self.check()

    def test_archived_manifest_reference_frozen(self):
        # The candidate cannot be renamed the original archived baseline.
        candidate.EXPECTED_CURRENT_ARCHIVED_MANIFEST = "a" * 40
        with self.assertRaises(candidate.CandidateLineageError):
            self.check()


if __name__ == "__main__":
    unittest.main()
