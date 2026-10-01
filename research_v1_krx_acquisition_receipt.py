"""Fail-closed, secret-free KRX acquisition receipt manifest.

This module creates metadata-only immutable receipts for future authenticated
historical KRX acquisitions. It does not perform a KRX request and it does not
persist numeric market data. A receipt binds an acquisition to the declared
source family, access route/product, dataset identifier, request parameters,
client revision, the validated structured authorization-evidence record
fingerprint, public-contract evidence version/fingerprint, observed schema and
payload/content fingerprint.

A receipt is Gate-E infrastructure only. Creating a valid receipt does not make
any A-F source gate PASS, does not authorize feature testing, sealed holdout,
promotion or live trading.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re
from typing import Any, Mapping, Sequence

import pandas as pd

from research_v1_krx_public_evidence import (
    PUBLIC_EVIDENCE_VERSION,
    public_evidence_fingerprint_sha256,
)


ALLOWED_SOURCE_FAMILIES = {"KRX_SECURITY_STATUS", "KRX_INVESTOR_FLOW"}
ALLOWED_ACCESS_ROUTES = {
    "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
    "KRX_OPENAPI_APPROVED_SERVICE",
    "KRX_PURCHASED_OR_DISTRIBUTED_PRODUCT",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SECRET_KEY_FRAGMENTS = (
    "password",
    "passwd",
    "pwd",
    "secret",
    "token",
    "auth_key",
    "apikey",
    "api_key",
    "authorization",
    "cookie",
    "sessionid",
    "session_id",
)


class KRXAcquisitionReceiptError(ValueError):
    """Raised when acquisition metadata is incomplete, ambiguous or unsafe."""


@dataclass(frozen=True)
class KRXAcquisitionReceipt:
    receipt_version: str
    source_family: str
    intended_use_scope: str
    access_route: str
    dataset_identifier: str
    authorization_evidence_reference: str
    authorization_evidence_fingerprint_sha256: str
    client_revision: str
    retrieved_at: str
    request_metadata_sha256: str
    response_schema_sha256: str
    response_payload_sha256: str
    response_rows: int
    response_columns: tuple[str, ...]
    public_contract_evidence_version: str
    public_contract_evidence_fingerprint_sha256: str
    receipt_fingerprint_sha256: str
    alpha_or_final_judge_promotion_authorized: bool
    sealed_holdout_authorized: bool
    live_trading_authorized: bool


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require_text(value: Any, field: str) -> str:
    text = str(value).strip()
    if not text:
        raise KRXAcquisitionReceiptError(f"{field} must be non-empty")
    return text


def _require_sha256(value: Any, field: str) -> str:
    text = str(value).strip().lower()
    if not SHA256_RE.fullmatch(text):
        raise KRXAcquisitionReceiptError(
            f"{field} must be a lowercase 64-hex SHA256 fingerprint"
        )
    return text


def _aware_iso(value: Any, field: str) -> str:
    try:
        ts = pd.Timestamp(value)
    except Exception as exc:
        raise KRXAcquisitionReceiptError(
            f"{field} must be a parseable timezone-aware timestamp"
        ) from exc
    if pd.isna(ts) or ts.tzinfo is None or ts.utcoffset() is None:
        raise KRXAcquisitionReceiptError(f"{field} must be timezone-aware")
    return ts.isoformat()


def _secret_like_key(key: Any) -> bool:
    normal = re.sub(r"[^a-z0-9]+", "_", str(key).strip().lower())
    return any(fragment in normal for fragment in SECRET_KEY_FRAGMENTS)


def _validate_secret_free(value: Any, path: str = "request_metadata") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if _secret_like_key(key):
                raise KRXAcquisitionReceiptError(
                    f"secret-like field forbidden in acquisition receipt metadata: {path}.{key}"
                )
            _validate_secret_free(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for idx, child in enumerate(value):
            _validate_secret_free(child, f"{path}[{idx}]")


def canonical_request_metadata(request_metadata: Mapping[str, Any]) -> dict[str, Any]:
    """Return a JSON-canonical, secret-free request-metadata copy."""
    if not isinstance(request_metadata, Mapping) or not request_metadata:
        raise KRXAcquisitionReceiptError("request_metadata must be a non-empty mapping")
    _validate_secret_free(request_metadata)
    try:
        encoded = json.loads(_canonical_bytes(request_metadata).decode("utf-8"))
    except Exception as exc:
        raise KRXAcquisitionReceiptError("request_metadata must be JSON-canonicalizable") from exc
    return encoded


def schema_fingerprint(columns: Sequence[Any], dtypes: Sequence[Any] | None = None) -> str:
    names = [str(x) for x in columns]
    if len(names) != len(set(names)):
        raise KRXAcquisitionReceiptError("response schema contains duplicate column names")
    if dtypes is None:
        dtype_names = ["UNKNOWN"] * len(names)
    else:
        dtype_names = [str(x) for x in dtypes]
        if len(dtype_names) != len(names):
            raise KRXAcquisitionReceiptError("dtypes length must match columns length")
    return _sha256([{"name": n, "dtype": d} for n, d in zip(names, dtype_names)])


def dataframe_payload_fingerprint(frame: pd.DataFrame) -> str:
    """Hash content without writing the numeric payload to a receipt artifact."""
    if frame is None:
        raise KRXAcquisitionReceiptError("response frame is None")
    if frame.columns.duplicated().any():
        raise KRXAcquisitionReceiptError("response frame contains duplicate column names")
    row_hashes = pd.util.hash_pandas_object(frame, index=True).astype("uint64").tolist()
    material = {
        "columns": [str(x) for x in frame.columns],
        "dtypes": [str(x) for x in frame.dtypes],
        "rows": int(len(frame)),
        "row_hashes": [int(x) for x in row_hashes],
    }
    return _sha256(material)


def build_acquisition_receipt(
    *,
    source_family: str,
    intended_use_scope: str,
    access_route: str,
    dataset_identifier: str,
    authorization_evidence_reference: str,
    authorization_evidence_fingerprint_sha256: str,
    client_revision: str,
    retrieved_at: Any,
    request_metadata: Mapping[str, Any],
    response_frame: pd.DataFrame,
    public_contract_evidence_version: str = PUBLIC_EVIDENCE_VERSION,
    public_contract_evidence_fingerprint: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic metadata-only acquisition receipt.

    The authorization reference must be opaque/non-secret. The structured
    authorization record itself is not embedded; its validated canonical
    fingerprint is required so changing the approval record changes every
    downstream receipt/batch fingerprint and cannot be silently mixed.
    """
    family = _require_text(source_family, "source_family")
    if family not in ALLOWED_SOURCE_FAMILIES:
        raise KRXAcquisitionReceiptError(f"unsupported source_family: {family}")
    route = _require_text(access_route, "access_route")
    if route not in ALLOWED_ACCESS_ROUTES:
        raise KRXAcquisitionReceiptError(f"unsupported access_route: {route}")

    scope = _require_text(intended_use_scope, "intended_use_scope")
    dataset = _require_text(dataset_identifier, "dataset_identifier")
    auth_ref = _require_text(
        authorization_evidence_reference, "authorization_evidence_reference"
    )
    if any(marker in auth_ref.lower() for marker in ("password=", "token=", "cookie=", "secret=")):
        raise KRXAcquisitionReceiptError(
            "authorization_evidence_reference must be an opaque non-secret reference"
        )
    auth_evidence_fp = _require_sha256(
        authorization_evidence_fingerprint_sha256,
        "authorization_evidence_fingerprint_sha256",
    )
    revision = _require_text(client_revision, "client_revision")
    retrieved = _aware_iso(retrieved_at, "retrieved_at")
    request = canonical_request_metadata(request_metadata)

    if response_frame is None:
        raise KRXAcquisitionReceiptError("response_frame is required")
    public_version = _require_text(
        public_contract_evidence_version, "public_contract_evidence_version"
    )
    if public_version != PUBLIC_EVIDENCE_VERSION:
        raise KRXAcquisitionReceiptError(
            "public contract evidence version is stale or unexpected"
        )
    current_public_fp = public_evidence_fingerprint_sha256()
    provided_public_fp = (
        current_public_fp
        if public_contract_evidence_fingerprint is None
        else _require_sha256(
            public_contract_evidence_fingerprint,
            "public_contract_evidence_fingerprint",
        )
    )
    if provided_public_fp != current_public_fp:
        raise KRXAcquisitionReceiptError(
            "public contract evidence fingerprint does not match current manifest"
        )

    columns = tuple(str(x) for x in response_frame.columns)
    schema_sha = schema_fingerprint(columns, [str(x) for x in response_frame.dtypes])
    payload_sha = dataframe_payload_fingerprint(response_frame)
    request_sha = _sha256(request)

    body = {
        "receipt_version": "2026-10-01.v2",
        "source_family": family,
        "intended_use_scope": scope,
        "access_route": route,
        "dataset_identifier": dataset,
        "authorization_evidence_reference": auth_ref,
        "authorization_evidence_fingerprint_sha256": auth_evidence_fp,
        "client_revision": revision,
        "retrieved_at": retrieved,
        "request_metadata_sha256": request_sha,
        "response_schema_sha256": schema_sha,
        "response_payload_sha256": payload_sha,
        "response_rows": int(len(response_frame)),
        "response_columns": columns,
        "public_contract_evidence_version": public_version,
        "public_contract_evidence_fingerprint_sha256": current_public_fp,
        "alpha_or_final_judge_promotion_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
    receipt_fp = _sha256(body)
    receipt = KRXAcquisitionReceipt(
        **body,
        receipt_fingerprint_sha256=receipt_fp,
    )
    out = asdict(receipt)
    out["response_columns"] = list(receipt.response_columns)
    out["guardrail"] = (
        "This receipt proves only reproducible provenance/integrity metadata for one acquisition, including the validated structured authorization-record fingerprint. "
        "It does not make any A-F source gate PASS and cannot authorize feature testing, holdout, promotion or live trading."
    )
    return out
