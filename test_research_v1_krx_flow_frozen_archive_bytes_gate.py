"""Adversarial network-free byte-provenance tests for archived 2022 KRX flow."""
from __future__ import annotations

import copy
import json
import unittest

from research_v1_krx_flow_frozen_archive_bytes_gate import (
    KRXArchivedSourceBytesError,
    audit_frozen_2026_10_03_private_krx_flow_snapshot,
    audit_private_krx_flow_archived_snapshot_bytes,
)
from research_v1_krx_flow_existing_private_checkpoint_inventory import _sha
from test_research_v1_krx_flow_existing_private_checkpoint_inventory import (
    FLOW, HALT, sample, receipt,
)


def original_writer_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       default=str) + "\n").encode("utf-8")


def original_fixture():
    manifest, state, task_fp = sample()
    manifest["tasks"].sort(key=lambda task: task["source_family"])
    state["completed"] = {
        item["task_id"]: receipt(item)
        for item in manifest["tasks"][:3]
    }
    state["completed_task_count"] = 3
    state["status"] = "IN_PROGRESS"
    state["phase_complete"] = False
    # Pinned original 2026-10-03 writer, not a mutable current default.
    state["state_version"] = "2026-10-02.v1"
    for key in (
        "source_gate_c_closed", "source_gate_d_closed",
        "source_gate_e_closed", "feature_performance_testing_authorized",
        "sealed_holdout_authorized", "live_trading_authorized",
    ):
        state[key] = False
    mb = original_writer_bytes(manifest)
    sb = original_writer_bytes(state)
    import hashlib
    opts = {
        "expected_manifest_byte_sha256": hashlib.sha256(mb).hexdigest(),
        "expected_task_set_fingerprint_sha256": task_fp,
        "expected_flow_requests": 3,
        "expected_halt_requests": 1,
        "expected_completed_requests": 3,
    }
    return {"private_manifest_bytes": mb, "private_phase_state_bytes": sb, **opts}


class FrozenPrivateArchiveBytesTest(unittest.TestCase):
    def test_complete_flow_prefix_from_original_writer_bytes(self):
        proof = audit_private_krx_flow_archived_snapshot_bytes(**original_fixture())
        self.assertTrue(proof["original_manifest_file_bytes_match_frozen_sha256"])
        self.assertTrue(proof["original_execution_completion_prefix_verified"])
        self.assertEqual(proof["investor_flow_completed_checkpoints"], 3)
        self.assertEqual(proof["year_2022_flow_expected_tasks"], 2)
        self.assertEqual(proof["year_2022_flow_completed_checkpoints"], 2)
        self.assertEqual(proof["remaining_tasks"], 1)
        for k in (
            "source_owner_private_mount_file_bytes_directly_read_here",
            "private_phase_state_independently_externally_authenticated",
            "original_2022_flow_raw_data_sha256_reverified",
            "original_2022_as_published_vintage_verified",
            "source_admitted", "performance_testing_authorized",
            "sealed_holdout_authorized", "ordering_enabled",
            "network_request_attempted", "raw_rows_or_identifiers_emitted",
        ):
            self.assertIs(proof[k], False, k)
        self.assertNotIn("005930", str(proof))
        self.assertNotIn("KR7005930003", str(proof))
        self.assertNotIn("task_id", str(proof))

    def test_state_counterfeit_source_gate_true_is_rejected(self):
        a = original_fixture()
        s = json.loads(a["private_phase_state_bytes"])
        s["source_gate_c_closed"] = True
        a["private_phase_state_bytes"] = original_writer_bytes(s)
        with self.assertRaisesRegex(
            KRXArchivedSourceBytesError, "FROZEN_ORIGINAL_PHASE_AUTHORITY_DRIFT",
        ):
            audit_private_krx_flow_archived_snapshot_bytes(**a)

    def test_state_counterfeit_holdout_or_trading_permission_rejected(self):
        for flag in ("live_trading_authorized",
                     "sealed_holdout_authorized",
                     "feature_performance_testing_authorized"):
            with self.subTest(flag=flag):
                a = original_fixture()
                s = json.loads(a["private_phase_state_bytes"])
                s[flag] = True
                a["private_phase_state_bytes"] = original_writer_bytes(s)
                with self.assertRaisesRegex(
                    KRXArchivedSourceBytesError,
                    "FROZEN_ORIGINAL_PHASE_AUTHORITY_DRIFT",
                ):
                    audit_private_krx_flow_archived_snapshot_bytes(**a)

    def test_unpinned_private_state_version_rejected(self):
        a = original_fixture()
        s = json.loads(a["private_phase_state_bytes"])
        s["state_version"] = "2030-01-01.v1"
        a["private_phase_state_bytes"] = original_writer_bytes(s)
        with self.assertRaisesRegex(
            KRXArchivedSourceBytesError,
            "FROZEN_ORIGINAL_PHASE_STATE_VERSION_DRIFT",
        ):
            audit_private_krx_flow_archived_snapshot_bytes(**a)

    def test_state_extra_private_issuer_and_row_fields_rejected(self):
        a = original_fixture()
        s = json.loads(a["private_phase_state_bytes"])
        s["raw_market_rows"] = [{"isuCd": "KR7005930003"}]
        a["private_phase_state_bytes"] = original_writer_bytes(s)
        with self.assertRaisesRegex(
            KRXArchivedSourceBytesError,
            "FROZEN_ORIGINAL_PHASE_STATE_FIELDS_DRIFT",
        ):
            audit_private_krx_flow_archived_snapshot_bytes(**a)

    def test_state_missing_original_writer_guardrail_rejected(self):
        a = original_fixture()
        s = json.loads(a["private_phase_state_bytes"])
        del s["source_gate_e_closed"]
        a["private_phase_state_bytes"] = original_writer_bytes(s)
        with self.assertRaisesRegex(
            KRXArchivedSourceBytesError,
            "FROZEN_ORIGINAL_PHASE_STATE_FIELDS_DRIFT",
        ):
            audit_private_krx_flow_archived_snapshot_bytes(**a)

    def test_original_frozen_production_wrapper_rejects_synthetic_archive(self):
        a = original_fixture()
        with self.assertRaisesRegex(KRXArchivedSourceBytesError, "MANIFEST_BYTES_SHA_DRIFT"):
            audit_frozen_2026_10_03_private_krx_flow_snapshot(
                private_manifest_bytes=a["private_manifest_bytes"],
                private_phase_state_bytes=a["private_phase_state_bytes"],
            )

    def test_same_internal_manifest_ids_but_different_serialized_bytes_rejected(self):
        a = original_fixture()
        a["private_manifest_bytes"] = a["private_manifest_bytes"].replace(
            b"\n", b"\r\n"
        )
        with self.assertRaisesRegex(KRXArchivedSourceBytesError, "MANIFEST_BYTES_SHA_DRIFT"):
            audit_private_krx_flow_archived_snapshot_bytes(**a)

    def test_rehashed_manifest_bytes_cannot_hide_altered_task_order(self):
        a = original_fixture()
        m = json.loads(a["private_manifest_bytes"])
        m["tasks"].reverse()
        a["private_manifest_bytes"] = original_writer_bytes(m)
        import hashlib
        a["expected_manifest_byte_sha256"] = hashlib.sha256(a["private_manifest_bytes"]).hexdigest()
        with self.assertRaisesRegex(Exception, "ORIGINAL_FLOW_FIRST_TASK_ORDER_DRIFT"):
            audit_private_krx_flow_archived_snapshot_bytes(**a)

    def test_counterfeit_completed_count_with_correct_task_ids_rejected(self):
        a = original_fixture()
        a["expected_completed_requests"] = 4
        with self.assertRaisesRegex(KRXArchivedSourceBytesError, "COMPLETION_COUNT_DRIFT"):
            audit_private_krx_flow_archived_snapshot_bytes(**a)

    def test_missing_completed_prefix_id_rejected_even_if_counts_match(self):
        a = original_fixture()
        m = json.loads(a["private_manifest_bytes"])
        s = json.loads(a["private_phase_state_bytes"])
        s["completed"] = {
            i["task_id"]: receipt(i)
            for i in (m["tasks"][0], m["tasks"][1], m["tasks"][3])
        }
        s["completed_task_count"] = 3
        a["private_phase_state_bytes"] = original_writer_bytes(s)
        with self.assertRaisesRegex(Exception, "NONCONTIGUOUS_ORIGINAL_EXECUTION_PREFIX"):
            audit_private_krx_flow_archived_snapshot_bytes(**a)

    def test_malformed_private_state_json_rejected_safely(self):
        a = original_fixture()
        a["private_phase_state_bytes"] = b'{"completed":'
        with self.assertRaisesRegex(KRXArchivedSourceBytesError, "PRIVATE_JSON_BYTES_INVALID"):
            audit_private_krx_flow_archived_snapshot_bytes(**a)

    def test_state_writer_must_have_same_canonical_bytes(self):
        a = original_fixture()
        a["private_phase_state_bytes"] = a["private_phase_state_bytes"].replace(b"\n", b"\r\n")
        with self.assertRaisesRegex(KRXArchivedSourceBytesError, "PRIVATE_JSON_WRITER_ENCODING_DRIFT"):
            audit_private_krx_flow_archived_snapshot_bytes(**a)

    def test_state_claiming_complete_without_completing_halts_rejected(self):
        a = original_fixture()
        s = json.loads(a["private_phase_state_bytes"])
        s["status"] = "COMPLETE"
        a["private_phase_state_bytes"] = original_writer_bytes(s)
        with self.assertRaisesRegex(KRXArchivedSourceBytesError, "PHASE_STATUS_DRIFT"):
            audit_private_krx_flow_archived_snapshot_bytes(**a)

    def test_state_json_with_not_an_object_is_rejected(self):
        a = original_fixture()
        a["private_phase_state_bytes"] = original_writer_bytes([1, 2, 3])
        with self.assertRaisesRegex(KRXArchivedSourceBytesError, "PRIVATE_JSON_OBJECT_REQUIRED"):
            audit_private_krx_flow_archived_snapshot_bytes(**a)

    def test_manifest_json_bytes_only_does_not_verify_real_provider_payload(self):
        a = original_fixture()
        result = audit_private_krx_flow_archived_snapshot_bytes(**a)
        self.assertFalse(result["original_2022_flow_raw_data_sha256_reverified"])
        self.assertFalse(result["source_admitted"])

    def test_utf8_bom_on_state_rejected(self):
        a = original_fixture()
        a["private_phase_state_bytes"] = b"\xef\xbb\xbf" + a["private_phase_state_bytes"]
        with self.assertRaisesRegex(KRXArchivedSourceBytesError, "PRIVATE_JSON_BYTES_INVALID"):
            audit_private_krx_flow_archived_snapshot_bytes(**a)


if __name__ == "__main__":
    unittest.main()
