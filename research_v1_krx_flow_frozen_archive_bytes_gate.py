"""Read-only *in-memory* byte verification of original private KRX flow files.

The 2026-10-03 historical worker persisted private manifest/state JSON with
write_private_json: UTF-8, sort_keys=True, indent=2, ensure_ascii=False and a
trailing newline; returned metadata_sha256 is SHA256 of these EXACT bytes.
A current-state task count or recomputed internal task-ID fingerprint alone
does not authenticate those originally pinned manifest bytes.

This module takes bytes supplied by the already-approved KRX source owner.
It neither reads a filesystem nor has any network, secrets or deployment hooks.
Actual origin of caller-supplied bytes and 2022 as-published vintage remain
separate external evidence, not inferred by this code.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from research_v1_krx_flow_existing_private_checkpoint_inventory import (
    FROZEN_FLOW_COUNT,
    FROZEN_HALT_COUNT,
    FROZEN_PRIVATE_MANIFEST_METADATA_SHA256,
    FROZEN_TASK_SET_SHA256,
    _verify_original_execution_prefix,
    summarise_existing_flow_checkpoints,
)


class KRXArchivedSourceBytesError(ValueError):
    """Fixed error codes; no source bytes, symbols or private identifiers."""


def _require(ok: bool, code: str) -> None:
    if not ok:
        raise KRXArchivedSourceBytesError(code)


def _decode_original_private_json_bytes(payload: bytes) -> dict[str, Any]:
    _require(type(payload) is bytes, "PRIVATE_JSON_BYTES_REQUIRED")
    try:
        obj = json.loads(payload.decode("utf-8", errors="strict"))
    except (UnicodeError, ValueError):
        raise KRXArchivedSourceBytesError("PRIVATE_JSON_BYTES_INVALID") from None
    _require(type(obj) is dict, "PRIVATE_JSON_OBJECT_REQUIRED")
    # Canonical writer serialization, NOT raw received source CSV serialization.
    canonical = (
        json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2,
                   default=str) + "\n"
    ).encode("utf-8")
    _require(payload == canonical, "PRIVATE_JSON_WRITER_ENCODING_DRIFT")
    return obj


def audit_private_krx_flow_archived_snapshot_bytes(
    *,
    private_manifest_bytes: bytes,
    private_phase_state_bytes: bytes,
    expected_manifest_byte_sha256: str,
    expected_task_set_fingerprint_sha256: str,
    expected_flow_requests: int,
    expected_halt_requests: int,
    expected_completed_requests: int,
) -> dict[str, Any]:
    """Validate one fully pinned historical checkpoint *snapshot* by content.

    Test-only parameters do not authorize alternate production provenance;
    the frozen public entrypoint below calls this with the 2026-10-03 constants.
    """
    _require(type(expected_manifest_byte_sha256) is str
             and len(expected_manifest_byte_sha256) == 64,
             "MANIFEST_SHA_PIN_INVALID")
    _require(type(private_manifest_bytes) is bytes,
             "PRIVATE_MANIFEST_BYTES_REQUIRED")
    manifest_sha = hashlib.sha256(private_manifest_bytes).hexdigest()
    _require(manifest_sha == expected_manifest_byte_sha256,
             "FROZEN_ORIGINAL_MANIFEST_BYTES_SHA_DRIFT")
    manifest = _decode_original_private_json_bytes(private_manifest_bytes)
    state = _decode_original_private_json_bytes(private_phase_state_bytes)
    # Original frozen 2026-10-03 historical batch-state writer:
    # research_v1_krx_historical_batch_state.initialize_phase_state and
    # record_task_completion persist a strictly metadata-only 18-key map.
    # State content does NOT have an independently pinned original file SHA,
    # so reject malicious extras (including raw identifiers and asserted
    # trading permission), altered version and any changed security gates.
    expected_original_state_fields = {
        "state_version", "plan_id", "execution_contract_id", "phase",
        "status", "expected_task_count", "task_set_fingerprint_sha256",
        "expected_task_ids_sha256", "completed", "completed_task_count",
        "failed_task_count", "phase_complete", "source_gate_c_closed",
        "source_gate_d_closed", "source_gate_e_closed",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized", "live_trading_authorized",
    }
    _require(set(state) == expected_original_state_fields,
             "FROZEN_ORIGINAL_PHASE_STATE_FIELDS_DRIFT")
    _require(state["state_version"] == "2026-10-02.v1",
             "FROZEN_ORIGINAL_PHASE_STATE_VERSION_DRIFT")
    for flag in (
        "source_gate_c_closed", "source_gate_d_closed",
        "source_gate_e_closed", "feature_performance_testing_authorized",
        "sealed_holdout_authorized", "live_trading_authorized",
    ):
        _require(state[flag] is False,
                 "FROZEN_ORIGINAL_PHASE_AUTHORITY_DRIFT")
    counts = summarise_existing_flow_checkpoints(
        manifest, state,
        expected_by_kind={
            "investor_trading_individual_daily": expected_flow_requests,
            "trading_halt": expected_halt_requests,
        },
        expected_task_fingerprint_sha256=expected_task_set_fingerprint_sha256,
    )
    _require(type(expected_completed_requests) is int
             and counts["completed_tasks"] == expected_completed_requests,
             "FROZEN_ORIGINAL_COMPLETION_COUNT_DRIFT")
    _require(state.get("status") == "IN_PROGRESS"
             and state.get("phase_complete") is False
             and state.get("failed_task_count") == 0,
             "FROZEN_ORIGINAL_PHASE_STATUS_DRIFT")
    prefix = _verify_original_execution_prefix(
        manifest, state, expected_flow_count=expected_flow_requests,
    )
    _require(counts["investor_flow_completed_checkpoints"]
             == prefix["flow_completed_by_verified_prefix"],
             "PRIVATE_FLOW_COMPLETION_COUNT_INCONSISTENT")
    result = {
        **counts, **prefix,
        "evidence_class": "IN_MEMORY_FROZEN_PRIVATE_ARCHIVE_BYTES_AUDIT",
        "original_manifest_file_bytes_match_frozen_sha256": True,
        "original_manifest_and_state_bytes_match_original_writer": True,
        "phase_state_snapshot_completed_count_matches_recorded_evidence": True,
        "phase_state_byte_sha256_computed_but_not_exposed": True,
        "source_owner_private_mount_file_bytes_directly_read_here": False,
        "private_phase_state_independently_externally_authenticated": False,
        "original_2022_flow_raw_data_sha256_reverified": False,
        "original_2022_as_published_vintage_verified": False,
        "source_admitted": False,
        "performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "ordering_enabled": False,
        "network_request_attempted": False,
        "raw_rows_or_identifiers_emitted": False,
    }
    return result


def audit_frozen_2026_10_03_private_krx_flow_snapshot(
    *,
    private_manifest_bytes: bytes,
    private_phase_state_bytes: bytes,
) -> dict[str, Any]:
    """Original immutable 14,296/11,750 checkpoint evidence only.

    This entrypoint cannot be called with a looser task set or alternate
    completion count. If any later KRX resume changed state, obtain a
    separately authorized and pinned provenance record; never infer success.
    """
    return audit_private_krx_flow_archived_snapshot_bytes(
        private_manifest_bytes=private_manifest_bytes,
        private_phase_state_bytes=private_phase_state_bytes,
        expected_manifest_byte_sha256=FROZEN_PRIVATE_MANIFEST_METADATA_SHA256,
        expected_task_set_fingerprint_sha256=FROZEN_TASK_SET_SHA256,
        expected_flow_requests=FROZEN_FLOW_COUNT,
        expected_halt_requests=FROZEN_HALT_COUNT,
        expected_completed_requests=11750,
    )
