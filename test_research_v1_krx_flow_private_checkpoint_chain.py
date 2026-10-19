"""Synthetic-only adversarial tests for the original private KRX 2022 chain."""
from __future__ import annotations

import copy
import hashlib
import json
import unittest

from research_v1_krx_flow_private_checkpoint_chain import (
    KRXPrivateCheckpointChainError,
    verify_2022_krx_private_full_checkpoint_chain,
)
from test_research_v1_krx_flow_pandas_payload_integrity import valid_case


def writer(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       indent=2, default=str) + "\n").encode("utf-8")


def fixture():
    item = valid_case()
    rec = item["acquisition_receipt"]
    raw = item["original_raw_bytes"]
    request_sha = item["completion"]["request_metadata_sha256"]
    receipt_fp = rec["receipt_fingerprint_sha256"]
    raw_sha = hashlib.sha256(raw).hexdigest()
    receipt_bytes = writer(rec)
    manifest = {
        "manifest_version": "2026-10-02.v1",
        "source_family": "KRX_INVESTOR_FLOW",
        "dataset_identifier": "MDCSTAT02303",
        "request_metadata_sha256": request_sha,
        "transport_status": "HTTP_200_CSV",
        "retrieved_at": rec["retrieved_at"],
        "raw_object_sha256": raw_sha,
        "raw_bytes_size": len(raw),
        "response_schema_sha256": rec["response_schema_sha256"],
        "response_payload_sha256": rec["response_payload_sha256"],
        "receipt_fingerprint_sha256": receipt_fp,
        "receipt_metadata_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
        "raw_rows_emitted": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
    manifest_bytes = writer(manifest)
    checkpoint = {
        "checkpoint_version": "2026-10-02.v1",
        "state": "COMPLETE",
        "source_family": "KRX_INVESTOR_FLOW",
        "dataset_identifier": "MDCSTAT02303",
        "request_metadata_sha256": request_sha,
        "raw_object_sha256": raw_sha,
        "raw_bytes_size": len(raw),
        "receipt_relpath": (
            f"receipts/KRX_INVESTOR_FLOW/MDCSTAT02303/{receipt_fp}.json"
        ),
        "receipt_fingerprint_sha256": receipt_fp,
        "manifest_relpath": (
            f"manifests/KRX_INVESTOR_FLOW/MDCSTAT02303/"
            f"{request_sha}-{receipt_fp}.json"
        ),
        "manifest_metadata_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
    return {
        "original_raw_bytes": raw,
        "acquisition_receipt_bytes": receipt_bytes,
        "acquisition_manifest_bytes": manifest_bytes,
        "request_checkpoint_bytes": writer(checkpoint),
        "canonical_request": item["canonical_request"],
        "frozen_task": item["frozen_task"],
        "phase_completion": item["completion"],
    }


def rewrite(item, name, transform):
    key = name + "_bytes"
    value = json.loads(item[key])
    transform(value)
    item[key] = writer(value)


class ProtectedKRXOriginalCheckpointChainTest(unittest.TestCase):
    def test_synthetic_original_checkpoint_receipt_raw_pandas_chain(self):
        proof = verify_2022_krx_private_full_checkpoint_chain(**fixture())
        for flag in (
            "original_receipt_file_bytes_sha_matches_manifest",
            "original_manifest_file_bytes_sha_matches_checkpoint",
            "original_checkpoint_receipt_path_is_sha_derived",
            "original_checkpoint_manifest_path_is_sha_derived",
            "original_raw_bytes_match_private_checkpoint_and_completion",
            "original_pandas_content_hash_recomputed_and_matches_receipt",
        ):
            self.assertIs(proof[flag], True, flag)
        for flag in (
            "original_archive_external_file_origin_authenticated",
            "original_phase_state_file_byte_fingerprint_pinned",
            "original_2022_as_published_vintage_verified",
            "provider_authenticity_independently_verified",
            "historical_correction_lineage_verified",
            "source_admitted", "performance_testing_authorized",
            "sealed_holdout_authorized", "ordering_enabled",
            "network_request_attempted", "source_numeric_rows_or_identifiers_emitted",
        ):
            self.assertIs(proof[flag], False, flag)
        self.assertNotIn("KR7005930003", str(proof))
        self.assertNotIn("f"*64, str(proof))

    def test_receipt_file_byte_representation_mismatch_cannot_pass(self):
        item = fixture()
        item["acquisition_receipt_bytes"] = (
            item["acquisition_receipt_bytes"].replace(b"\n", b"\r\n")
        )
        with self.assertRaisesRegex(
            KRXPrivateCheckpointChainError,
            "ORIGINAL_PRIVATE_JSON_WRITER_BYTE_DRIFT",
        ):
            verify_2022_krx_private_full_checkpoint_chain(**item)

    def test_receipt_json_guardrail_mutation_rejected_before_manifest_sha(self):
        item = fixture()
        rewrite(item, "acquisition_receipt",
                lambda value: value.update({"guardrail": "synthetic"}))
        # Original pinned receipt producer creates this exact safety string.
        # Reject counterfeit safety claims before byte-chain reconciliation.
        with self.assertRaisesRegex(
            Exception, "ORIGINAL_RECEIPT_GUARDRAIL_DRIFT",
        ):
            verify_2022_krx_private_full_checkpoint_chain(**item)

    def test_old_original_checkpoint_rejects_rewritten_manifest(self):
        item = fixture()
        rewrite(item, "acquisition_manifest",
                lambda value: value.update({"transport_status": "HTTP_201"}))
        with self.assertRaisesRegex(
            KRXPrivateCheckpointChainError,
            "ORIGINAL_REQUEST_CHECKPOINT_MANIFEST_OR_RECEIPT_DRIFT",
        ):
            verify_2022_krx_private_full_checkpoint_chain(**item)

    def test_checkpoint_wrong_receipt_path_even_when_receipt_is_authentic(self):
        item = fixture()
        rewrite(item, "request_checkpoint",
                lambda value: value.update({"receipt_relpath": "../outside.json"}))
        with self.assertRaisesRegex(
            KRXPrivateCheckpointChainError,
            "ORIGINAL_REQUEST_CHECKPOINT_MANIFEST_OR_RECEIPT_DRIFT",
        ):
            verify_2022_krx_private_full_checkpoint_chain(**item)

    def test_checkpoint_wrong_manifest_path_rejected(self):
        item = fixture()
        rewrite(item, "request_checkpoint",
                lambda value: value.update({"manifest_relpath": "manifests/forged.json"}))
        with self.assertRaisesRegex(
            KRXPrivateCheckpointChainError,
            "ORIGINAL_REQUEST_CHECKPOINT_MANIFEST_OR_RECEIPT_DRIFT",
        ):
            verify_2022_krx_private_full_checkpoint_chain(**item)

    def test_forged_checkpoint_live_authority_rejected(self):
        item = fixture()
        rewrite(item, "request_checkpoint",
                lambda value: value.update({"live_trading_authorized": True}))
        with self.assertRaisesRegex(
            KRXPrivateCheckpointChainError,
            "ORIGINAL_REQUEST_CHECKPOINT_AUTHORITY_DRIFT",
        ):
            verify_2022_krx_private_full_checkpoint_chain(**item)

    def test_forged_manifest_holdout_authority_rejected(self):
        item = fixture()
        rewrite(item, "acquisition_manifest",
                lambda value: value.update({"sealed_holdout_authorized": True}))
        with self.assertRaisesRegex(
            KRXPrivateCheckpointChainError,
            "ORIGINAL_ACQUISITION_MANIFEST_AUTHORITY_DRIFT",
        ):
            verify_2022_krx_private_full_checkpoint_chain(**item)

    def test_checkpoint_not_complete_does_not_promote_original(self):
        item = fixture()
        rewrite(item, "request_checkpoint",
                lambda value: value.update({"state": "PENDING"}))
        with self.assertRaisesRegex(
            KRXPrivateCheckpointChainError,
            "ORIGINAL_REQUEST_CHECKPOINT_STATE_DRIFT",
        ):
            verify_2022_krx_private_full_checkpoint_chain(**item)

    def test_checkpoint_rejects_extra_untrusted_payload_path_field(self):
        item = fixture()
        rewrite(item, "request_checkpoint",
                lambda value: value.update({"raw_path": "/tmp/private"}))
        with self.assertRaisesRegex(
            KRXPrivateCheckpointChainError,
            "ORIGINAL_REQUEST_CHECKPOINT_FIELDS_DRIFT",
        ):
            verify_2022_krx_private_full_checkpoint_chain(**item)

    def test_non_success_4xx_csv_download_status_rejected_even_if_manifest_rehashed(self):
        item = fixture()
        rewrite(item, "acquisition_manifest",
                lambda value: value.update({"transport_status": "HTTP_403_CSV"}))
        with self.assertRaisesRegex(
            KRXPrivateCheckpointChainError,
            "ORIGINAL_ACQUISITION_MANIFEST_ROUTE_DRIFT"
        ):
            verify_2022_krx_private_full_checkpoint_chain(**item)

    def test_unpinned_json_2xx_download_status_rejected(self):
        item = fixture()
        rewrite(item, "acquisition_manifest",
                lambda value: value.update({"transport_status": "HTTP_200_JSON"}))
        with self.assertRaisesRegex(
            KRXPrivateCheckpointChainError,
            "ORIGINAL_ACQUISITION_MANIFEST_ROUTE_DRIFT"
        ):
            verify_2022_krx_private_full_checkpoint_chain(**item)

    def test_invented_producer_status_or_missing_csv_suffix_rejected(self):
        for bogus in ("SUCCESS", "HTTP_200", "HTTP_500_CSV", "HTTP_200_CSV_FAKE"):
            with self.subTest(status=bogus):
                item = fixture()
                rewrite(item, "acquisition_manifest",
                        lambda value: value.update({"transport_status": bogus}))
                with self.assertRaisesRegex(
                    KRXPrivateCheckpointChainError,
                    "ORIGINAL_ACQUISITION_MANIFEST_ROUTE_DRIFT"
                ):
                    verify_2022_krx_private_full_checkpoint_chain(**item)

    def test_original_2xx_csv_transport_success_is_accepted(self):
        item = fixture()
        rewrite(item, "acquisition_manifest",
                lambda value: value.update({"transport_status": "HTTP_201_CSV"}))
        # Original worker accepts any 2xx transport, not only HTTP 200.
        # Recomputed manifest bytes are also checked by checkpoint; this
        # synthetic test updates its pinned expected metadata digest.
        import hashlib
        rewritten_manifest_sha = hashlib.sha256(
            item["acquisition_manifest_bytes"]
        ).hexdigest()
        rewrite(item, "request_checkpoint",
                lambda value: value.update({
                    "manifest_metadata_sha256": rewritten_manifest_sha
                }))
        out = verify_2022_krx_private_full_checkpoint_chain(**item)
        self.assertTrue(out["original_manifest_file_bytes_sha_matches_checkpoint"])
        self.assertFalse(out["source_admitted"])

    def test_relabelled_request_dataset_is_rejected(self):
        item = fixture()
        rewrite(item, "acquisition_manifest",
                lambda value: value.update({"dataset_identifier": "MDCSTAT02301"}))
        with self.assertRaisesRegex(
            KRXPrivateCheckpointChainError,
            "ORIGINAL_ACQUISITION_MANIFEST_ROUTE_DRIFT",
        ):
            verify_2022_krx_private_full_checkpoint_chain(**item)

    def test_original_raw_numeric_tamper_rejected_before_archive_chain(self):
        item = fixture()
        altered = item["original_raw_bytes"].replace(b",0,0", b",199,0", 1)
        self.assertNotEqual(altered, item["original_raw_bytes"])
        item["original_raw_bytes"] = altered
        with self.assertRaisesRegex(
            Exception, "ORIGINAL_RAW_OBJECT_BYTE_SHA_DRIFT"
        ):
            verify_2022_krx_private_full_checkpoint_chain(**item)


if __name__ == "__main__":
    unittest.main()
