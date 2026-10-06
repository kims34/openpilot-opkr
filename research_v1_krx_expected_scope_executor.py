"""Consent-gated executor for independent KRX expected-scope attestation.

This module is separate from the Data Marketplace bulk-acquisition executor.
It may query only the two approved KRX OpenAPI services frozen in
INDEXALERT_KRX_EXPECTED_SCOPE_ATTESTATION_CONTRACT.json.

Public returns are metadata-only. Raw responses, same-date identity rows and
expected-scope keys are written only under the validated private root.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping

import pandas as pd

from research_v1_krx_acquisition_receipt import (
    dataframe_payload_fingerprint,
    schema_fingerprint,
)
from research_v1_krx_expected_scope_attestation import CONTRACT_ID
from research_v1_krx_expected_scope_materializer import (
    materialize_one_date,
    public_date_summary,
)
from research_v1_krx_expected_scope_preflight import (
    evaluate_expected_scope_preflight,
)
from research_v1_krx_historical_fetchers import (
    FetchResult,
    fetch_openapi_raw,
    parse_openapi_raw,
)
from research_v1_krx_private_store import (
    read_private_json,
    verify_raw_object,
    write_private_json,
    write_raw_object,
)


DAILY_ENDPOINT = "https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd"
MASTER_ENDPOINT = "https://data-dbg.krx.co.kr/svc/apis/sto/stk_isu_base_info"
CLIENT_REVISION = "indexalert-krx-expected-scope-v1"


class KRXExpectedScopeExecutorError(RuntimeError):
    pass


def _sha256(value: Any) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _ensure_fetch_result(result: Any) -> FetchResult:
    if not isinstance(result, FetchResult):
        raise KRXExpectedScopeExecutorError("fetcher must return FetchResult")
    if not isinstance(result.response_frame, pd.DataFrame):
        raise KRXExpectedScopeExecutorError("response_frame must be DataFrame")
    if not isinstance(result.raw_bytes, (bytes, bytearray)):
        raise KRXExpectedScopeExecutorError("raw_bytes must be bytes")
    if result.network_request_attempted is not True:
        raise KRXExpectedScopeExecutorError(
            "authorized expected-scope fetch must report network_request_attempted=true"
        )
    if not isinstance(result.transport_status, str) or not result.transport_status.strip():
        raise KRXExpectedScopeExecutorError("transport_status must be a non-empty string")
    if not isinstance(result.retrieved_at, str) or not result.retrieved_at.strip():
        raise KRXExpectedScopeExecutorError("retrieved_at must be timezone-aware string")
    try:
        ts = pd.Timestamp(result.retrieved_at)
    except (TypeError, ValueError, OverflowError) as exc:
        raise KRXExpectedScopeExecutorError("retrieved_at must be timezone-aware string") from exc
    if pd.isna(ts) or ts.tzinfo is None or ts.utcoffset() is None:
        raise KRXExpectedScopeExecutorError("retrieved_at must be timezone-aware")
    try:
        parsed = parse_openapi_raw(bytes(result.raw_bytes))
    except Exception as exc:
        raise KRXExpectedScopeExecutorError("raw response must be valid OpenAPI rows") from exc
    if (
        dataframe_payload_fingerprint(parsed) != dataframe_payload_fingerprint(result.response_frame)
        or schema_fingerprint(list(parsed.columns), [str(x) for x in parsed.dtypes])
        != schema_fingerprint(list(result.response_frame.columns), [str(x) for x in result.response_frame.dtypes])
    ):
        raise KRXExpectedScopeExecutorError("response_frame must match parsed raw response")
    return result


def _persist_response(
    *,
    root: str,
    git_worktree: str,
    dataset_identifier: str,
    requested_date: str,
    endpoint: str,
    result: FetchResult,
) -> dict[str, Any]:
    raw = write_raw_object(
        root,
        bytes(result.raw_bytes),
        git_worktree=git_worktree,
    )
    frame = result.response_frame
    request_meta = {
        "contract_id": CONTRACT_ID,
        "dataset_identifier": dataset_identifier,
        "endpoint": endpoint,
        "method": "GET",
        "params": {"basDd": requested_date},
    }
    request_sha = _sha256(request_meta)
    payload_sha = dataframe_payload_fingerprint(frame)
    schema_sha = schema_fingerprint(
        list(frame.columns),
        [str(x) for x in frame.dtypes],
    )
    receipt = {
        "receipt_version": "2026-10-02.expected-scope-v2",
        "contract_id": CONTRACT_ID,
        "dataset_identifier": dataset_identifier,
        "requested_date": requested_date,
        "request_metadata_sha256": request_sha,
        "retrieved_at": pd.Timestamp(result.retrieved_at).isoformat(),
        "transport_status": result.transport_status,
        "raw_object_sha256": raw["raw_object_sha256"],
        "raw_bytes_size": int(raw["raw_bytes_size"]),
        "response_rows": int(len(frame)),
        "response_schema_sha256": schema_sha,
        "response_payload_sha256": payload_sha,
        "network_request_attempted": True,
        "raw_rows_emitted": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }

    receipt_dir = Path(root) / "expected_scope" / "receipts" / requested_date / dataset_identifier
    if receipt_dir.exists():
        for existing_path in sorted(receipt_dir.glob("*.json")):
            rel_existing = str(existing_path.relative_to(Path(root)))
            wrapped = read_private_json(
                root,
                rel_existing,
                git_worktree=git_worktree,
            )
            existing = wrapped["value"]
            if not isinstance(existing, dict) or existing_path.stem != _sha256(existing):
                raise KRXExpectedScopeExecutorError("existing receipt content address mismatch")
            required = {
                "receipt_version": "2026-10-02.expected-scope-v2",
                "contract_id": CONTRACT_ID,
                "dataset_identifier": dataset_identifier,
                "requested_date": requested_date,
                "request_metadata_sha256": request_sha,
            }
            if any(existing.get(key) != value for key, value in required.items()):
                raise KRXExpectedScopeExecutorError("existing receipt request metadata mismatch")
            if existing.get("network_request_attempted") is not True or any(
                existing.get(key) is not False for key in (
                    "raw_rows_emitted", "source_gate_c_closed", "source_gate_d_closed",
                    "source_gate_e_closed", "feature_performance_testing_authorized",
                    "sealed_holdout_authorized", "live_trading_authorized",
                )
            ):
                raise KRXExpectedScopeExecutorError("existing receipt authority metadata mismatch")
            _ensure_fetch_result(FetchResult(
                raw_bytes=result.raw_bytes,
                response_frame=frame,
                retrieved_at=existing.get("retrieved_at"),
                transport_status=existing.get("transport_status"),
                network_request_attempted=existing.get("network_request_attempted"),
            ))
            if (
                existing.get("response_payload_sha256") != payload_sha
                or existing.get("response_schema_sha256") != schema_sha
                or existing.get("raw_object_sha256") != raw["raw_object_sha256"]
            ):
                raise KRXExpectedScopeExecutorError(
                    "same expected-scope request produced conflicting payload"
                )
            if (
                type(existing.get("response_rows")) is not int
                or existing["response_rows"] != len(frame)
                or type(existing.get("raw_bytes_size")) is not int
                or existing["raw_bytes_size"] != len(result.raw_bytes)
            ):
                raise KRXExpectedScopeExecutorError("existing receipt row/byte count mismatch")
            verify_raw_object(
                root,
                str(existing["raw_object_sha256"]),
                expected_size=int(existing["raw_bytes_size"]),
                git_worktree=git_worktree,
            )
            return {
                **existing,
                "receipt_metadata_sha256": wrapped["metadata_sha256"],
                "receipt_relpath": rel_existing,
                "reused_immutable_receipt": True,
            }

    receipt_fp = _sha256(receipt)
    rel = (
        f"expected_scope/receipts/{requested_date}/{dataset_identifier}/"
        f"{receipt_fp}.json"
    )
    written = write_private_json(
        root,
        rel,
        receipt,
        git_worktree=git_worktree,
    )
    return {
        **receipt,
        "receipt_metadata_sha256": written["metadata_sha256"],
        "receipt_relpath": rel,
        "reused_immutable_receipt": False,
    }


def execute_expected_scope_date(
    *,
    requested_date: str,
    environment: Mapping[str, str],
    git_worktree: str,
    fetcher: Callable[..., FetchResult] = fetch_openapi_raw,
    evaluation_time: datetime | None = None,
) -> dict[str, Any]:
    """Execute one calendar-date attestation under the separate consent gate."""
    preflight = evaluate_expected_scope_preflight(
        environment=environment,
        git_worktree=git_worktree,
    )
    if not preflight["expected_scope_network_execution_authorized"]:
        raise KRXExpectedScopeExecutorError(
            "expected-scope preflight blocked: "
            + ",".join(preflight["missing_requirements"])
        )

    day = str(requested_date).replace("-", "")
    if len(day) != 8 or not day.isdigit():
        raise KRXExpectedScopeExecutorError("requested_date must be YYYYMMDD")

    try:
        datetime.strptime(day, "%Y%m%d")
    except ValueError as exc:
        raise KRXExpectedScopeExecutorError("requested_date must be a valid calendar date") from exc

    now = evaluation_time or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise KRXExpectedScopeExecutorError(
            "evaluation_time must be timezone-aware"
        )

    root = str(environment["KRX_PRIVATE_RAW_DIR"])
    auth_key = str(environment["KRX_AUTH_KEY"])
    daily = _ensure_fetch_result(
        fetcher(
            endpoint=DAILY_ENDPOINT,
            params={"basDd": day},
            auth_key=auth_key,
            network_authorized=True,
            retrieved_at_override=now.isoformat(),
        )
    )
    daily_receipt = _persist_response(
        root=root,
        git_worktree=git_worktree,
        dataset_identifier="stk_bydd_trd",
        requested_date=day,
        endpoint=DAILY_ENDPOINT,
        result=daily,
    )

    master = None
    master_receipt = None
    if not daily.response_frame.empty:
        master = _ensure_fetch_result(
            fetcher(
                endpoint=MASTER_ENDPOINT,
                params={"basDd": day},
                auth_key=auth_key,
                network_authorized=True,
                retrieved_at_override=now.isoformat(),
            )
        )
        master_receipt = _persist_response(
            root=root,
            git_worktree=git_worktree,
            dataset_identifier="stk_isu_base_info",
            requested_date=day,
            endpoint=MASTER_ENDPOINT,
            result=master,
        )

    materialized = materialize_one_date(
        requested_date=day,
        daily_trade=daily.response_frame,
        security_master=(None if master is None else master.response_frame),
    )
    investor_records = materialized["investor_expected_scope"].to_dict(
        orient="records"
    )
    status_records = materialized["status_expected_scope"].to_dict(
        orient="records"
    )
    private_scope = {
        "contract_id": CONTRACT_ID,
        "requested_date": day,
        "official_trading_date_observed": bool(
            materialized["official_trading_date_observed"]
        ),
        "investor_expected_scope": investor_records,
        "status_expected_scope": status_records,
        "daily_receipt_relpath": daily_receipt["receipt_relpath"],
        "master_receipt_relpath": (
            None if master_receipt is None else master_receipt["receipt_relpath"]
        ),
        "network_request_attempted": True,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
    scope_fp = _sha256(private_scope)
    scope_dir = Path(root) / "expected_scope" / "dates" / day
    scope_rel = f"expected_scope/dates/{day}/{scope_fp}.json"
    scope_write = None
    if scope_dir.exists():
        existing_scope_paths = sorted(scope_dir.glob("*.json"))
        for existing_path in existing_scope_paths:
            rel_existing = str(existing_path.relative_to(Path(root)))
            wrapped = read_private_json(
                root,
                rel_existing,
                git_worktree=git_worktree,
            )
            existing_scope = wrapped["value"]
            if existing_path.stem != _sha256(existing_scope):
                raise KRXExpectedScopeExecutorError("existing scope content address mismatch")
            if _sha256(existing_scope) == scope_fp:
                scope_rel = rel_existing
                scope_write = {
                    "metadata_sha256": wrapped["metadata_sha256"],
                    "metadata_relpath": rel_existing,
                }
                break
            raise KRXExpectedScopeExecutorError(
                "same expected-scope date produced conflicting private scope"
            )
    if scope_write is None:
        scope_write = write_private_json(
            root,
            scope_rel,
            private_scope,
            git_worktree=git_worktree,
        )

    safe = public_date_summary(materialized)
    safe.update(
        {
            "mode": "EXECUTE_EXPECTED_SCOPE_DATE",
            "requested_date": day,
            "daily_receipt_fingerprint_sha256": _sha256(daily_receipt),
            "master_request_performed": master_receipt is not None,
            "master_receipt_fingerprint_sha256": (
                None if master_receipt is None else _sha256(master_receipt)
            ),
            "private_scope_metadata_sha256": scope_write["metadata_sha256"],
            "private_scope_relpath": scope_rel,
            "network_request_attempted": True,
            "raw_rows_emitted": False,
            "security_identifiers_emitted": False,
            "source_gate_c_closed": False,
            "source_gate_d_closed": False,
            "source_gate_e_closed": False,
            "feature_performance_testing_authorized": False,
            "sealed_holdout_authorized": False,
            "live_trading_authorized": False,
        }
    )
    return safe
