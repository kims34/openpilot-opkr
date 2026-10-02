"""Offline-safe execution core for one private KRX historical request.

The core has no built-in network client. A caller must inject a fetcher callable.
Before the fetcher can be invoked, the frozen historical-acquisition preflight
must pass, including exact execution consent and a safe private raw directory.
Raw bytes, receipt metadata and checkpoint state are kept in the private store.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable, Mapping

import pandas as pd

from research_v1_krx_acquisition_batch import verify_receipt_fingerprint
from research_v1_krx_acquisition_receipt import (
    _sha256,
    build_acquisition_receipt,
    canonical_request_metadata,
)
from research_v1_krx_auth_preflight import DATA_MARKETPLACE_ROUTE
from research_v1_krx_authorization_evidence import validate_authorization_evidence
from research_v1_krx_historical_acquisition_preflight import (
    evaluate_historical_acquisition_preflight,
)
from research_v1_krx_openapi_connectivity_evidence import (
    validate_file as validate_openapi_evidence_file,
)
from research_v1_krx_private_store import (
    KRXPrivateStoreError,
    read_private_json,
    validate_private_root,
    verify_raw_object,
    write_private_json,
    write_raw_object,
)


class KRXHistoricalWorkerError(ValueError):
    pass


@dataclass(frozen=True)
class FetchResult:
    raw_bytes: bytes
    response_frame: pd.DataFrame
    retrieved_at: str
    transport_status: str
    network_request_attempted: bool


OPENAPI_ROUTE = "KRX_OPENAPI_APPROVED_SERVICE"

AUTH_FILES = {
    "KRX_SECURITY_STATUS": (
        Path("INDEXALERT_KRX_AUTH_EVIDENCE_SECURITY_STATUS.json"),
        "INTERNAL_RESEARCH_AND_FINAL_JUDGE_INPUT_PREPARATION",
    ),
    "KRX_INVESTOR_FLOW": (
        Path("INDEXALERT_KRX_AUTH_EVIDENCE_INVESTOR_FLOW.json"),
        "INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION",
    ),
}


def _safe_component(value: str) -> str:
    text = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in str(value))
    if not text or text in {".", ".."}:
        raise KRXHistoricalWorkerError("unsafe path component")
    return text


def _load_auth_record(
    source_family: str,
    *,
    evaluation_time: datetime,
) -> dict[str, Any]:
    if source_family not in AUTH_FILES:
        raise KRXHistoricalWorkerError(f"unsupported source family: {source_family}")
    path, scope = AUTH_FILES[source_family]
    raw = json.loads(path.read_text(encoding="utf-8"))
    out = validate_authorization_evidence(
        raw,
        expected_source_family=source_family,
        expected_access_route=DATA_MARKETPLACE_ROUTE,
        expected_intended_use_scope=scope,
        evaluation_time=evaluation_time,
        expected_reference=str(raw["evidence_reference"]),
    )
    if not out["sufficient_for_tiny_probe_preflight"]:
        raise KRXHistoricalWorkerError(
            f"authorization evidence invalid: {out['reason_codes']}"
        )
    return {
        "scope": scope,
        "reference": out["record"]["evidence_reference"],
        "fingerprint": out["record_fingerprint_sha256"],
    }


def _load_provenance(
    source_family: str,
    access_route: str,
    *,
    evaluation_time: datetime,
) -> dict[str, Any]:
    if access_route == DATA_MARKETPLACE_ROUTE:
        return _load_auth_record(source_family, evaluation_time=evaluation_time)

    if access_route == OPENAPI_ROUTE:
        if source_family != "KRX_SECURITY_STATUS":
            raise KRXHistoricalWorkerError(
                "historical OpenAPI route is restricted to KRX_SECURITY_STATUS identity support"
            )
        evidence = validate_openapi_evidence_file()
        return {
            "scope": "INTERNAL_RESEARCH_AND_FINAL_JUDGE_INPUT_PREPARATION",
            "reference": evidence["evidence_id"],
            "fingerprint": evidence["evidence_fingerprint_sha256"],
        }

    raise KRXHistoricalWorkerError(f"unsupported access route: {access_route}")


def _checkpoint_relpath(
    source_family: str,
    access_route: str,
    dataset_identifier: str,
    request_sha: str,
) -> str:
    return (
        "checkpoints/"
        f"{_safe_component(source_family)}/"
        f"{_safe_component(access_route)}/"
        f"{_safe_component(dataset_identifier)}/"
        f"{request_sha}.json"
    )


def _resume_if_complete(
    *,
    root: str,
    checkpoint_relpath: str,
    git_worktree: str | None,
) -> dict[str, Any] | None:
    base = validate_private_root(root, git_worktree=git_worktree)
    target = base / checkpoint_relpath
    if not target.exists():
        return None

    checkpoint = read_private_json(
        root,
        checkpoint_relpath,
        git_worktree=git_worktree,
    )["value"]
    if checkpoint.get("state") != "COMPLETE":
        raise KRXHistoricalWorkerError("existing checkpoint is not COMPLETE")

    raw = verify_raw_object(
        root,
        str(checkpoint["raw_object_sha256"]),
        expected_size=int(checkpoint["raw_bytes_size"]),
        git_worktree=git_worktree,
    )
    receipt_info = read_private_json(
        root,
        str(checkpoint["receipt_relpath"]),
        git_worktree=git_worktree,
    )
    receipt = receipt_info["value"]
    receipt_fp = verify_receipt_fingerprint(receipt)
    if receipt_fp != checkpoint["receipt_fingerprint_sha256"]:
        raise KRXHistoricalWorkerError("checkpoint receipt fingerprint mismatch")
    if raw["raw_object_sha256"] != checkpoint["raw_object_sha256"]:
        raise KRXHistoricalWorkerError("checkpoint raw object fingerprint mismatch")

    return {
        "completed": True,
        "resumed": True,
        "request_metadata_sha256": checkpoint["request_metadata_sha256"],
        "raw_object_sha256": checkpoint["raw_object_sha256"],
        "raw_bytes_size": int(checkpoint["raw_bytes_size"]),
        "response_rows": int(receipt["response_rows"]),
        "response_schema_sha256": receipt["response_schema_sha256"],
        "response_payload_sha256": receipt["response_payload_sha256"],
        "receipt_fingerprint_sha256": receipt_fp,
        "raw_rows_emitted": False,
        "network_request_attempted": False,
    }


def execute_private_request(
    *,
    environment: Mapping[str, str],
    git_worktree: str,
    source_family: str,
    dataset_identifier: str,
    access_route: str = DATA_MARKETPLACE_ROUTE,
    request_metadata: Mapping[str, Any],
    client_revision: str,
    fetcher: Callable[[Mapping[str, Any]], FetchResult],
    evaluation_time: datetime | None = None,
) -> dict[str, Any]:
    """Execute one request only after all bulk-acquisition safety gates pass.

    The caller-supplied fetcher is invoked exactly once for a non-resumed request.
    The public return object contains hashes/counts only; never raw rows/bytes.
    """
    now = evaluation_time or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise KRXHistoricalWorkerError("evaluation_time must be timezone-aware")

    preflight = evaluate_historical_acquisition_preflight(
        environment=environment,
        git_worktree=git_worktree,
    )
    if not preflight["historical_acquisition_network_execution_authorized"]:
        raise KRXHistoricalWorkerError(
            f"historical acquisition preflight blocked: {preflight['missing_requirements']}"
        )

    root = str(environment.get("KRX_PRIVATE_RAW_DIR") or "").strip()
    validate_private_root(root, git_worktree=git_worktree)

    request = canonical_request_metadata(request_metadata)
    request_sha = _sha256(request)
    if access_route == OPENAPI_ROUTE and dataset_identifier != "stk_isu_base_info":
        raise KRXHistoricalWorkerError(
            "historical OpenAPI worker permits only stk_isu_base_info"
        )

    checkpoint_rel = _checkpoint_relpath(
        source_family,
        access_route,
        dataset_identifier,
        request_sha,
    )

    resumed = _resume_if_complete(
        root=root,
        checkpoint_relpath=checkpoint_rel,
        git_worktree=git_worktree,
    )
    if resumed is not None:
        return resumed

    auth = _load_provenance(
        source_family,
        access_route,
        evaluation_time=now,
    )

    result = fetcher(request)
    if not isinstance(result, FetchResult):
        raise KRXHistoricalWorkerError("fetcher must return FetchResult")
    if not isinstance(result.raw_bytes, (bytes, bytearray)):
        raise KRXHistoricalWorkerError("fetcher raw_bytes must be bytes")
    if not isinstance(result.response_frame, pd.DataFrame):
        raise KRXHistoricalWorkerError("fetcher response_frame must be a DataFrame")
    if not str(result.transport_status).strip():
        raise KRXHistoricalWorkerError("transport_status must be non-empty")
    if not isinstance(result.network_request_attempted, bool):
        raise KRXHistoricalWorkerError("network_request_attempted must be boolean")

    raw = write_raw_object(
        root,
        bytes(result.raw_bytes),
        git_worktree=git_worktree,
    )

    receipt = build_acquisition_receipt(
        source_family=source_family,
        intended_use_scope=auth["scope"],
        access_route=access_route,
        dataset_identifier=dataset_identifier,
        authorization_evidence_reference=auth["reference"],
        authorization_evidence_fingerprint_sha256=auth["fingerprint"],
        client_revision=client_revision,
        retrieved_at=result.retrieved_at,
        request_metadata=request,
        response_frame=result.response_frame,
    )
    if receipt["request_metadata_sha256"] != request_sha:
        raise KRXHistoricalWorkerError("request fingerprint mismatch after receipt build")

    family_dir = _safe_component(source_family)
    dataset_dir = _safe_component(dataset_identifier)
    receipt_rel = (
        f"receipts/{family_dir}/{dataset_dir}/"
        f"{receipt['receipt_fingerprint_sha256']}.json"
    )
    receipt_written = write_private_json(
        root,
        receipt_rel,
        receipt,
        git_worktree=git_worktree,
    )

    manifest = {
        "manifest_version": "2026-10-02.v1",
        "source_family": source_family,
        "dataset_identifier": dataset_identifier,
        "request_metadata_sha256": request_sha,
        "transport_status": str(result.transport_status),
        "retrieved_at": receipt["retrieved_at"],
        "raw_object_sha256": raw["raw_object_sha256"],
        "raw_bytes_size": raw["raw_bytes_size"],
        "response_schema_sha256": receipt["response_schema_sha256"],
        "response_payload_sha256": receipt["response_payload_sha256"],
        "receipt_fingerprint_sha256": receipt["receipt_fingerprint_sha256"],
        "receipt_metadata_sha256": receipt_written["metadata_sha256"],
        "raw_rows_emitted": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
    manifest_rel = (
        f"manifests/{family_dir}/{dataset_dir}/"
        f"{request_sha}-{receipt['receipt_fingerprint_sha256']}.json"
    )
    manifest_written = write_private_json(
        root,
        manifest_rel,
        manifest,
        git_worktree=git_worktree,
    )

    checkpoint = {
        "checkpoint_version": "2026-10-02.v1",
        "state": "COMPLETE",
        "source_family": source_family,
        "dataset_identifier": dataset_identifier,
        "request_metadata_sha256": request_sha,
        "raw_object_sha256": raw["raw_object_sha256"],
        "raw_bytes_size": raw["raw_bytes_size"],
        "receipt_relpath": receipt_rel,
        "receipt_fingerprint_sha256": receipt["receipt_fingerprint_sha256"],
        "manifest_relpath": manifest_rel,
        "manifest_metadata_sha256": manifest_written["metadata_sha256"],
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
    write_private_json(
        root,
        checkpoint_rel,
        checkpoint,
        git_worktree=git_worktree,
    )

    return {
        "completed": True,
        "resumed": False,
        "request_metadata_sha256": request_sha,
        "raw_object_sha256": raw["raw_object_sha256"],
        "raw_bytes_size": raw["raw_bytes_size"],
        "response_rows": int(receipt["response_rows"]),
        "response_schema_sha256": receipt["response_schema_sha256"],
        "response_payload_sha256": receipt["response_payload_sha256"],
        "receipt_fingerprint_sha256": receipt["receipt_fingerprint_sha256"],
        "manifest_metadata_sha256": manifest_written["metadata_sha256"],
        "raw_rows_emitted": False,
        "network_request_attempted": result.network_request_attempted,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
