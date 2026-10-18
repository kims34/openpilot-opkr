"""Synthetic-only local protected-volume specimen audit tests. Never real KRX."""
from __future__ import annotations

from contextlib import redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

from research_v1_krx_flow_private_owner_2022_specimen import (
    KRXPrivateOwnerSpecimenError, _resolved_request,
    audit_2022_original_flow_first_specimen, main,
)
from research_v1_krx_flow_frozen_archive_bytes_gate import (
    audit_private_krx_flow_archived_snapshot_bytes,
)
from test_research_v1_krx_flow_frozen_archive_bytes_gate import (
    original_fixture, original_writer_bytes,
)
from test_research_v1_krx_flow_private_checkpoint_chain import (
    fixture as chain_fixture,
)


class OriginalKRXFirst2022FlowSpecimenTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.root = base / "private_sealed"
        self.root.mkdir(mode=0o700)
        self.worktree = base / "project"
        self.worktree.mkdir(mode=0o700)
        snapshot = original_fixture()
        self.options = {
            k: v for k, v in snapshot.items()
            if k not in {"private_manifest_bytes", "private_phase_state_bytes"}
        }
        self.chain = chain_fixture()
        manifest = json.loads(snapshot["private_manifest_bytes"])
        state = json.loads(snapshot["private_phase_state_bytes"])
        chosen = next(x for x in manifest["tasks"]
                      if x["source_family"] == "KRX_INVESTOR_FLOW"
                      and x["request_spec"]["params"]["strtDd"] == "20220103")
        self.assertEqual(chosen["task_id"], self.chain["frozen_task"]["task_id"])
        self.assertEqual(_resolved_request(chosen), self.chain["canonical_request"])
        state["completed"][chosen["task_id"]] = self.chain["phase_completion"]
        self.manifest_bytes = original_writer_bytes(manifest)
        self.state_bytes = original_writer_bytes(state)
        self.options["expected_manifest_byte_sha256"] = (
            hashlib.sha256(self.manifest_bytes).hexdigest()
        )
        request_sha = self.chain["phase_completion"]["request_metadata_sha256"]
        receipt_sha = self.chain["phase_completion"]["receipt_fingerprint_sha256"]
        raw_sha = self.chain["phase_completion"]["raw_object_sha256"]
        self.paths = {
            "manifest": ("task_manifests", "per-security-history-v3.json"),
            "state": ("batch_state", "PER_SECURITY_HISTORY.json"),
            "checkpoint": (
                "checkpoints", "KRX_INVESTOR_FLOW",
                "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
                "MDCSTAT02303", request_sha + ".json"
            ),
            "receipt": (
                "receipts", "KRX_INVESTOR_FLOW", "MDCSTAT02303",
                receipt_sha + ".json"
            ),
            "acquisition": (
                "manifests", "KRX_INVESTOR_FLOW", "MDCSTAT02303",
                request_sha + "-" + receipt_sha + ".json"
            ),
            "raw": ("objects", "sha256", raw_sha[:2], raw_sha + ".bin"),
        }
        self.write("manifest", self.manifest_bytes)
        self.write("state", self.state_bytes)
        self.write("checkpoint", self.chain["request_checkpoint_bytes"])
        self.write("receipt", self.chain["acquisition_receipt_bytes"])
        self.write("acquisition", self.chain["acquisition_manifest_bytes"])
        self.write("raw", self.chain["original_raw_bytes"])

    def file(self, key):
        return self.root.joinpath(*self.paths[key])

    def write(self, key, data):
        p = self.file(key)
        p.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        p.write_bytes(data)
        os.chmod(p, 0o600)

    def _snapshot_verifier(self, *, private_manifest_bytes,
                           private_phase_state_bytes):
        return audit_private_krx_flow_archived_snapshot_bytes(
            private_manifest_bytes=private_manifest_bytes,
            private_phase_state_bytes=private_phase_state_bytes,
            **self.options,
        )

    def audit(self):
        with patch(
            "research_v1_krx_flow_private_owner_2022_specimen."
            "audit_frozen_2026_10_03_private_krx_flow_snapshot",
            side_effect=self._snapshot_verifier,
        ):
            return audit_2022_original_flow_first_specimen(
                private_root=str(self.root),
                git_worktree=str(self.worktree),
            )

    def test_one_deterministic_nonempty_original_response_chain_all_hashes_match(self):
        result = self.audit()
        self.assertEqual(result["sample_selection"], "FIRST_ORIGINAL_ORDERED_2022_FLOW_TASK")
        self.assertEqual(result["investor_flow_completed_request_checkpoints"], 3)
        self.assertTrue(result["one_original_2022_raw_object_and_checkpoint_chain_checked"])
        self.assertTrue(result["one_original_2022_pandas_numeric_payload_digest_checked"])
        self.assertTrue(result["sample_response_nonempty"])
        self.assertFalse(result["entire_2022_raw_response_population_verified"])
        for flag in (
            "original_phase_state_snapshot_externally_authenticated",
            "original_2022_as_published_vintage_verified",
            "historical_release_timestamp_verified",
            "historical_correction_lineage_verified",
            "official_trading_calendar_and_issuer_universe_verified",
            "foreign_institution_unit_semantics_verified",
            "source_admitted", "performance_testing_authorized",
            "sealed_holdout_authorized", "ordering_enabled",
            "network_request_attempted", "source_numeric_rows_or_identifiers_emitted",
        ):
            self.assertFalse(result[flag], flag)
        self.assertNotIn("KR7005930003", str(result))
        self.assertNotIn(self.paths["raw"][-1], str(result))

    def test_untrusted_synthetic_files_never_pass_frozen_production_sha(self):
        with self.assertRaisesRegex(Exception, "MANIFEST_BYTES_SHA_DRIFT"):
            audit_2022_original_flow_first_specimen(
                private_root=str(self.root), git_worktree=str(self.worktree),
            )

    def test_modified_original_raw_sha_rejected(self):
        self.write("raw", self.file("raw").read_bytes() + b"tampered")
        with self.assertRaisesRegex(Exception, "ORIGINAL_RAW_OBJECT_BYTE_SHA_DRIFT"):
            self.audit()

    def test_missing_original_request_checkpoint_fails_closed(self):
        self.file("checkpoint").unlink()
        with self.assertRaisesRegex(Exception, "PRIVATE_METADATA_READ_DENIED_OR_MISSING"):
            self.audit()

    def test_original_receipt_file_mutation_fails_closed(self):
        self.write("receipt", self.file("receipt").read_bytes().replace(b"\n", b"\r\n"))
        with self.assertRaisesRegex(Exception, "PRIVATE_JSON_WRITER_BYTE_DRIFT"):
            self.audit()

    def test_original_raw_symlink_denied(self):
        other = self.root / "replacement.csv"
        other.write_bytes(self.chain["original_raw_bytes"])
        self.file("raw").unlink()
        self.file("raw").symlink_to(other)
        with self.assertRaisesRegex(Exception, "PRIVATE_METADATA_SYMLINK_REJECTED"):
            self.audit()

    def test_original_acquisition_manifest_corruption_fails(self):
        data = json.loads(self.file("acquisition").read_bytes())
        data["transport_status"] = "HTTP_205"
        self.write("acquisition", original_writer_bytes(data))
        with self.assertRaisesRegex(Exception, "MANIFEST_OR_RECEIPT_DRIFT"):
            self.audit()

    def test_non_private_root_and_git_worktree_separation(self):
        with self.assertRaisesRegex(Exception, "PRIVATE_ROOT_INSIDE_GIT_WORKTREE"):
            audit_2022_original_flow_first_specimen(
                private_root=str(self.worktree),
                git_worktree=str(self.worktree),
            )

    def test_cli_missing_volume_emits_no_raw_issuer_path(self):
        stdout = io.StringIO()
        with patch.dict(os.environ, {"KRX_PRIVATE_RAW_DIR": ""}), redirect_stdout(stdout):
            status = main()
        self.assertEqual(status, 2)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data["status"], "BLOCKED")
        self.assertFalse(data["source_admitted"])
        self.assertFalse(data["ordering_enabled"])
        self.assertNotIn("KR700593", stdout.getvalue())
        self.assertNotIn(str(self.root), stdout.getvalue())

    def test_dont_accept_unsupported_path_traversal_when_reading_private_files(self):
        from research_v1_krx_flow_private_owner_readonly_snapshot import (
            KRXPrivateOwnerReadOnlyError, _read_exact_private_metadata,
        )
        for pieces in (("objects", "..", "out.json"),
                       ("..", "private.json"),
                       ("objects", "/etc/passwd")):
            with self.subTest(parts=pieces):
                with self.assertRaisesRegex(
                    KRXPrivateOwnerReadOnlyError, "PRIVATE_RELATIVE_PATH_UNSAFE"
                ):
                    _read_exact_private_metadata(self.root, pieces)


if __name__ == "__main__":
    unittest.main()
