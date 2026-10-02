"""Public-safe builder/validator for network-free STATUS_ECONOMICS preparation evidence.

Offline-only. It accepts only aggregate summaries/hashes and cannot authorize
network execution, exact fill/recovery economics, sealed holdout, or live
trading.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

PER_SECURITY_EXPECTED_TASK_COUNT = 14296
PER_SECURITY_EXPECTED_TASK_SET_SHA256 = "fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38"
EVIDENCE_ID = "INDEXALERT-KRX-STATUS-ECONOMICS-PREP-v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class KRXStatusEconomicsPreparationEvidenceError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXStatusEconomicsPreparationEvidenceError(msg)


def _sha(value: Any, field: str) -> str:
    text = str(value or "").strip().lower()
    _require(bool(SHA256_RE.fullmatch(text)), f"{field} must be SHA-256")
    return text


def _require_per_security_complete(summary: Mapping[str, Any]) -> None:
    _require(summary.get("phase") == "PER_SECURITY_HISTORY", "predecessor phase drift")
    _require(summary.get("status") == "COMPLETE", "predecessor is not COMPLETE")
    _require(summary.get("phase_complete") is True, "predecessor phase_complete lost")
    _require(
        int(summary.get("expected_task_count", -1)) == PER_SECURITY_EXPECTED_TASK_COUNT,
        "predecessor expected count drift",
    )
    _require(
        int(summary.get("completed_task_count", -1)) == PER_SECURITY_EXPECTED_TASK_COUNT,
        "predecessor completed count drift",
    )
    _require(int(summary.get("failed_task_count", -1)) == 0, "predecessor has failures")
    _require(
        _sha(summary.get("task_set_fingerprint_sha256"), "predecessor task_set_fingerprint_sha256")
        == PER_SECURITY_EXPECTED_TASK_SET_SHA256,
        "predecessor task-set fingerprint drift",
    )


def build_preparation_evidence(
    *,
    predecessor_summary: Mapping[str, Any],
    preparation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Build evidence only from exact predecessor completion + network-free prepare."""
    _require_per_security_complete(predecessor_summary)

    _require(preparation_result.get("mode") == "PREPARE_STATUS_ECONOMICS", "prepare mode drift")
    task_count = int(preparation_result.get("task_count", -1))
    _require(task_count > 0, "status-economics prepared task set is empty")
    _require(
        int(preparation_result.get("cleanup_price_task_count", -1)) == task_count,
        "cleanup-price task count drift",
    )
    _require(
        int(preparation_result.get("delisted_episode_count", -1)) >= task_count,
        "delisted episode count invalid",
    )
    _require(
        int(preparation_result.get("delisted_without_cleanup_interval_count", -1)) >= 0,
        "delisted-without-cleanup count invalid",
    )

    task_fp = _sha(
        preparation_result.get("task_set_fingerprint_sha256"),
        "task_set_fingerprint_sha256",
    )
    manifest_sha = _sha(
        preparation_result.get("private_task_manifest_metadata_sha256"),
        "private_task_manifest_metadata_sha256",
    )
    _require(
        preparation_result.get("private_task_manifest_relpath")
        == "task_manifests/status-economics-v3.json",
        "private manifest relpath drift",
    )
    _require(preparation_result.get("phase_status") == "PENDING", "prepared phase status drift")
    _require(preparation_result.get("phase_complete") is False, "prepared phase cannot be complete")
    _require(
        preparation_result.get("network_request_attempted") is False,
        "status-economics preparation attempted network",
    )
    _require(
        preparation_result.get("security_identifiers_emitted") is False,
        "security identifiers emitted",
    )
    _require(preparation_result.get("raw_rows_emitted") is False, "raw rows emitted")
    _require(
        preparation_result.get("exact_status_economics_ready") is False,
        "exact status economics illegally claimed ready",
    )
    for key in (
        "source_gate_c_closed",
        "source_gate_d_closed",
        "source_gate_e_closed",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(preparation_result.get(key) is False, f"{key} illegally true")

    return {
        "schema_version": "1",
        "evidence_id": EVIDENCE_ID,
        "stage": "STATUS_ECONOMICS",
        "status": "PREPARED_NETWORK_FREE_EXECUTION_NOT_AUTHORIZED",
        "predecessor": {
            "phase": "PER_SECURITY_HISTORY",
            "task_count": PER_SECURITY_EXPECTED_TASK_COUNT,
            "task_set_fingerprint_sha256": PER_SECURITY_EXPECTED_TASK_SET_SHA256,
            "phase_complete": True,
            "failed_task_count": 0,
        },
        "preparation": {
            "task_count": task_count,
            "delisted_episode_count": int(preparation_result["delisted_episode_count"]),
            "cleanup_price_task_count": int(preparation_result["cleanup_price_task_count"]),
            "delisted_without_cleanup_interval_count": int(
                preparation_result["delisted_without_cleanup_interval_count"]
            ),
            "task_set_fingerprint_sha256": task_fp,
            "private_task_manifest_metadata_sha256": manifest_sha,
            "private_task_manifest_relpath": preparation_result[
                "private_task_manifest_relpath"
            ],
            "phase_status": "PENDING",
            "phase_complete": False,
            "network_request_attempted": False,
            "security_identifiers_emitted": False,
            "raw_rows_emitted": False,
            "exact_status_economics_ready": False,
        },
        "authority": {
            "status_economics_execution_authorized": False,
            "expected_scope_network_execution_authorized": False,
            "feature_performance_testing_authorized": False,
            "sealed_holdout_authorized": False,
            "genuine_live_authorized": False,
            "live_trading_authorized": False,
        },
    }


def validate_evidence(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "evidence must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(data.get("evidence_id") == EVIDENCE_ID, "evidence_id drift")
    _require(data.get("stage") == "STATUS_ECONOMICS", "stage drift")
    _require(
        data.get("status") == "PREPARED_NETWORK_FREE_EXECUTION_NOT_AUTHORIZED",
        "status drift",
    )

    predecessor = data.get("predecessor") or {}
    _require_per_security_complete({
        "phase": predecessor.get("phase"),
        "status": "COMPLETE" if predecessor.get("phase_complete") is True else "PENDING",
        "phase_complete": predecessor.get("phase_complete"),
        "expected_task_count": predecessor.get("task_count"),
        "completed_task_count": predecessor.get("task_count"),
        "failed_task_count": predecessor.get("failed_task_count"),
        "task_set_fingerprint_sha256": predecessor.get("task_set_fingerprint_sha256"),
    })

    prep = data.get("preparation") or {}
    task_count = int(prep.get("task_count", -1))
    _require(task_count > 0, "prepared task set is empty")
    _require(int(prep.get("cleanup_price_task_count", -1)) == task_count, "cleanup task count drift")
    _require(int(prep.get("delisted_episode_count", -1)) >= task_count, "delisted count invalid")
    _require(int(prep.get("delisted_without_cleanup_interval_count", -1)) >= 0, "missing cleanup count invalid")
    _sha(prep.get("task_set_fingerprint_sha256"), "task_set_fingerprint_sha256")
    _sha(prep.get("private_task_manifest_metadata_sha256"), "private_task_manifest_metadata_sha256")
    _require(
        prep.get("private_task_manifest_relpath") == "task_manifests/status-economics-v3.json",
        "private manifest relpath drift",
    )
    _require(prep.get("phase_status") == "PENDING", "phase status drift")
    _require(prep.get("phase_complete") is False, "phase_complete illegally true")
    _require(prep.get("network_request_attempted") is False, "network attempted during preparation")
    _require(prep.get("security_identifiers_emitted") is False, "identifiers emitted")
    _require(prep.get("raw_rows_emitted") is False, "raw rows emitted")
    _require(prep.get("exact_status_economics_ready") is False, "exact economics illegally ready")

    authority = data.get("authority") or {}
    for key in (
        "status_economics_execution_authorized",
        "expected_scope_network_execution_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    ):
        _require(authority.get(key) is False, f"{key} illegally true")

    return {
        "valid": True,
        "task_count": task_count,
        "network_request_attempted": False,
        "status_economics_execution_authorized": False,
        "exact_status_economics_ready": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
