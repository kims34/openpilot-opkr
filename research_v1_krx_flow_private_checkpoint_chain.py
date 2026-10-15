"""Offline proof of an ORIGINAL per-request KRX 2022 flow checkpoint chain.

For an already-authorized KRX source owner to run with bytes that stay INSIDE
their protected private environment. Does no filesystem IO or network access.
Pin each original source: raw object -> 2022 dataframe digest -> receipt ->
acquisition manifest -> checkpoint -> existing phase-task completion.

A self-consistent stored chain is not an independent authority of first KRX
publication, 2022 as-published PIT or original phase-state immutability.
No identifiers, request hashes, numeric values or private paths are emitted.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from research_v1_krx_flow_pandas_payload_integrity import (
    verify_2022_krx_flow_pandas_payload,
)

FAMILY = "KRX_INVESTOR_FLOW"
DATASET = "MDCSTAT02303"
ROUTE = "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION"
CHECKPOINT_VERSION = "2026-10-02.v1"
MANIFEST_VERSION = "2026-10-02.v1"


class KRXPrivateCheckpointChainError(ValueError):
    """Error messages are static codes without issuer/secret data."""


def _need(condition: bool, code: str) -> None:
    if not condition:
        raise KRXPrivateCheckpointChainError(code)


def _json_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(
        value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), default=str,
    ).encode("utf-8")).hexdigest()


def _private_json_from_writer(raw: bytes) -> dict[str, Any]:
    _need(type(raw) is bytes, "ORIGINAL_PRIVATE_JSON_BYTES_REQUIRED")
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, ValueError):
        raise KRXPrivateCheckpointChainError(
            "ORIGINAL_PRIVATE_JSON_INVALID"
        ) from None
    _need(type(value) is dict, "ORIGINAL_PRIVATE_JSON_NOT_OBJECT")
    serialized = (json.dumps(
        value, ensure_ascii=False, sort_keys=True,
        indent=2, default=str,
    ) + "\n").encode("utf-8")
    _need(serialized == raw, "ORIGINAL_PRIVATE_JSON_WRITER_BYTE_DRIFT")
    return value


def verify_2022_krx_private_full_checkpoint_chain(
    *,
    original_raw_bytes: bytes,
    acquisition_receipt_bytes: bytes,
    acquisition_manifest_bytes: bytes,
    request_checkpoint_bytes: bytes,
    canonical_request: Mapping[str, Any],
    frozen_task: Mapping[str, Any],
    phase_completion: Mapping[str, Any],
) -> dict[str, Any]:
    """Check original saved artifact chain using pinned pandas/NumPy versions.

    Raw bytes are never moved or written; synthetic CI is not an actual
    private-volume audit. This cannot infer external trusted file provenance.
    """
    receipt = _private_json_from_writer(acquisition_receipt_bytes)
    manifest = _private_json_from_writer(acquisition_manifest_bytes)
    checkpoint = _private_json_from_writer(request_checkpoint_bytes)

    # Existing verifier checks raw original SHA, frozen task ID/issuer/year,
    # canonical request SHA, net-buy value mode, EUC-KR shape and all daily
    # dates, then independently recreates original pandas schema+row hashes.
    prior = verify_2022_krx_flow_pandas_payload(
        original_raw_bytes=original_raw_bytes,
        acquisition_receipt=receipt,
        completion=phase_completion,
        canonical_request=canonical_request,
        frozen_task=frozen_task,
    )
    raw_digest = hashlib.sha256(original_raw_bytes).hexdigest()
    request_sha = _json_sha(dict(canonical_request))
    receipt_fp = receipt["receipt_fingerprint_sha256"]
    receipt_bytes_sha = hashlib.sha256(acquisition_receipt_bytes).hexdigest()
    manifest_bytes_sha = hashlib.sha256(acquisition_manifest_bytes).hexdigest()

    # The original acquisition manifest separately SHA-anchors the original
    # serialized receipt FILE, which is stronger than only hashing a receipt
    # JSON body. All manifest fields mirror the original 2026-10-03 worker.
    _need(set(manifest) == {
        "manifest_version", "source_family", "dataset_identifier",
        "request_metadata_sha256", "transport_status", "retrieved_at",
        "raw_object_sha256", "raw_bytes_size", "response_schema_sha256",
        "response_payload_sha256", "receipt_fingerprint_sha256",
        "receipt_metadata_sha256", "raw_rows_emitted",
        "sealed_holdout_authorized", "live_trading_authorized",
    }, "ORIGINAL_ACQUISITION_MANIFEST_FIELDS_DRIFT")
    _need(manifest["manifest_version"] == MANIFEST_VERSION
          and manifest["source_family"] == FAMILY
          and manifest["dataset_identifier"] == DATASET
          and type(manifest["transport_status"]) is str
          and bool(manifest["transport_status"].strip()),
          "ORIGINAL_ACQUISITION_MANIFEST_ROUTE_DRIFT")
    expected_manifest = {
        "request_metadata_sha256": request_sha,
        "retrieved_at": receipt["retrieved_at"],
        "raw_object_sha256": raw_digest,
        "raw_bytes_size": len(original_raw_bytes),
        "response_schema_sha256": receipt["response_schema_sha256"],
        "response_payload_sha256": receipt["response_payload_sha256"],
        "receipt_fingerprint_sha256": receipt_fp,
        "receipt_metadata_sha256": receipt_bytes_sha,
    }
    _need(all(manifest.get(key) == expected for key, expected
              in expected_manifest.items()),
          "ORIGINAL_ACQUISITION_MANIFEST_RECEIPT_OR_RAW_DRIFT")
    _need(manifest["raw_rows_emitted"] is False
          and manifest["sealed_holdout_authorized"] is False
          and manifest["live_trading_authorized"] is False,
          "ORIGINAL_ACQUISITION_MANIFEST_AUTHORITY_DRIFT")

    # Checkpoint path names are immutable derivations of the original
    # request SHA and original receipt body SHA; no caller-supplied path
    # or filesystem navigation is accepted in the verifier.
    expected_receipt_relpath = (
        f"receipts/{FAMILY}/{DATASET}/{receipt_fp}.json"
    )
    expected_manifest_relpath = (
        f"manifests/{FAMILY}/{DATASET}/"
        f"{request_sha}-{receipt_fp}.json"
    )
    _need(set(checkpoint) == {
        "checkpoint_version", "state", "source_family",
        "dataset_identifier", "request_metadata_sha256",
        "raw_object_sha256", "raw_bytes_size",
        "receipt_relpath", "receipt_fingerprint_sha256",
        "manifest_relpath", "manifest_metadata_sha256",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized", "live_trading_authorized",
    }, "ORIGINAL_REQUEST_CHECKPOINT_FIELDS_DRIFT")
    _need(checkpoint["checkpoint_version"] == CHECKPOINT_VERSION
          and checkpoint["state"] == "COMPLETE"
          and checkpoint["source_family"] == FAMILY
          and checkpoint["dataset_identifier"] == DATASET,
          "ORIGINAL_REQUEST_CHECKPOINT_STATE_DRIFT")
    expected_checkpoint = {
        "request_metadata_sha256": request_sha,
        "raw_object_sha256": raw_digest,
        "raw_bytes_size": len(original_raw_bytes),
        "receipt_relpath": expected_receipt_relpath,
        "receipt_fingerprint_sha256": receipt_fp,
        "manifest_relpath": expected_manifest_relpath,
        "manifest_metadata_sha256": manifest_bytes_sha,
    }
    _need(all(checkpoint.get(key) == expected for key, expected
              in expected_checkpoint.items()),
          "ORIGINAL_REQUEST_CHECKPOINT_MANIFEST_OR_RECEIPT_DRIFT")
    _need(checkpoint["feature_performance_testing_authorized"] is False
          and checkpoint["sealed_holdout_authorized"] is False
          and checkpoint["live_trading_authorized"] is False,
          "ORIGINAL_REQUEST_CHECKPOINT_AUTHORITY_DRIFT")

    return {
        **prior,
        "checked_type": "KRX_2022_PRIVATE_ORIGINAL_FULL_CHECKPOINT_CHAIN",
        "original_receipt_file_bytes_sha_matches_manifest": True,
        "original_manifest_file_bytes_sha_matches_checkpoint": True,
        "original_checkpoint_receipt_path_is_sha_derived": True,
        "original_checkpoint_manifest_path_is_sha_derived": True,
        "original_raw_bytes_match_private_checkpoint_and_completion": True,
        "original_pandas_content_hash_recomputed_and_matches_receipt": True,
        "original_archive_external_file_origin_authenticated": False,
        "original_phase_state_file_byte_fingerprint_pinned": False,
        "original_2022_as_published_vintage_verified": False,
        "provider_authenticity_independently_verified": False,
        "historical_correction_lineage_verified": False,
        "source_admitted": False,
        "performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "ordering_enabled": False,
        "network_request_attempted": False,
        "source_numeric_rows_or_identifiers_emitted": False,
    }
