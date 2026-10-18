"""Offline synthetic checks: archived regression source drift must fail closed."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import research_v1_runtime_archived_source_gate as gate
import research_v1_runtime_ci as ci


class ArchivedRegressionSourcesTest(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.mock_hashes = {}
        for i, filename in enumerate(gate.ARCHIVED_GIT_BLOBS):
            content = ("synthetic immutable source file " + str(i) + "\n").encode()
            (self.root / filename).write_bytes(content)
            self.mock_hashes[filename] = gate.git_blob_sha1(content)
        pin = patch.dict(gate.ARCHIVED_GIT_BLOBS, self.mock_hashes, clear=True)
        pin.start()
        self.addCleanup(pin.stop)
        self.mock_impl_hashes = {}
        for i, filename in enumerate(gate.ARCHIVED_DIRECT_IMPLEMENTATION_BLOBS):
            content = ("synthetic implementation bytes " + str(i) + "\\n").encode()
            (self.root / filename).write_bytes(content)
            self.mock_impl_hashes[filename] = gate.git_blob_sha1(content)
        pinned_impl = patch.dict(
            gate.ARCHIVED_DIRECT_IMPLEMENTATION_BLOBS, self.mock_impl_hashes, clear=True
        )
        pinned_impl.start()
        self.addCleanup(pinned_impl.stop)

    def test_git_blob_exact_object_identity(self):
        # Independent git-hash-object reference: blob of b'hello\\n'.
        self.assertEqual(gate.git_blob_sha1(b"hello\n"),
                         "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_unchanged_archived_sources_admitted_for_offline_regression_only(self):
        verdict = gate.validate_source_definitions(self.root)
        self.assertTrue(verdict["git_blob_shas_verified"])
        self.assertEqual(verdict["archived_regression_source_files"], 8)
        self.assertEqual(verdict["archived_direct_implementation_files"], 9)
        self.assertIs(verdict["all_transitive_imports_pinned"], False)
        for key in ("source_pit_admitted", "profitability_evaluated",
                    "holdout_accessed", "ordering"):
            self.assertIs(verdict[key], False)

    def test_same_named_test_source_body_replacement_rejected(self):
        file = self.root / "test_research_v1_core.py"
        file.write_bytes(file.read_bytes() + b"\ndef test_same_name(): pass\n")
        with self.assertRaises(gate.SourceDriftError):
            gate.validate_source_definitions(self.root)

    def test_unchanged_test_name_but_changed_implementation_rejected(self):
        implementation = self.root / "research_v1_portfolio.py"
        implementation.write_bytes(implementation.read_bytes() + b"\\n# changed algorithm\\n")
        with self.assertRaises(gate.SourceDriftError):
            gate.validate_source_definitions(self.root)

    def test_missing_or_relinked_implementation_fails_closed(self):
        implementation = self.root / "research_v1_pit_run_purged.py"
        implementation.unlink()
        with self.assertRaises(gate.SourceDriftError):
            gate.validate_source_definitions(self.root)
        implementation.symlink_to(self.root / "research_v1_core.py")
        with self.assertRaises(gate.SourceDriftError):
            gate.validate_source_definitions(self.root)

    def test_fake_implementation_blob_manifest_is_not_sufficient(self):
        # One file silently removed from a locally weakened manifest should
        # not be treated as a proof of all direct implementations. This
        # control pins the independent expected manifest cardinality.
        self.assertEqual(len(gate.ARCHIVED_DIRECT_IMPLEMENTATION_BLOBS), 9)

    def test_requirements_dependency_version_change_rejected(self):
        (self.root / "requirements-indexalert-runtime-ci.txt").write_bytes(
            b"pytest==0.0.0\n"
        )
        with self.assertRaises(gate.SourceDriftError):
            gate.validate_source_definitions(self.root)

    def test_missing_or_symlinked_test_source_rejected(self):
        file = self.root / "test_research_v1_purged.py"
        file.unlink()
        with self.assertRaises(gate.SourceDriftError):
            gate.validate_source_definitions(self.root)
        file.symlink_to(self.root / "test_research_v1_core.py")
        with self.assertRaises(gate.SourceDriftError):
            gate.validate_source_definitions(self.root)

    def test_suite_remapping_and_expectations_change_rejected(self):
        with patch.dict(ci.SUITES, {"cost": ("test_research_v1_core.py",)}, clear=True):
            with self.assertRaises(gate.SourceDriftError):
                gate.validate_source_definitions(self.root)
        with patch.dict(ci.PINNED_CASES, {"all": (3, "0"*64)}, clear=True):
            with self.assertRaises(gate.SourceDriftError):
                gate.validate_source_definitions(self.root)

    def test_bad_source_root_rejected(self):
        missing = self.root / "not_present"
        with self.assertRaises(gate.SourceDriftError):
            gate.validate_source_definitions(missing)
        (self.root / "alias").symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(gate.SourceDriftError):
            gate.validate_source_definitions(self.root / "alias")


if __name__ == "__main__":
    unittest.main()
