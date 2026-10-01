"""Fail-closed batch provenance manifest for KRX historical acquisitions.

A batch combines multiple metadata-only acquisition receipts for one exact KRX
dataset contract. It verifies each receipt fingerprint and forbids silent mixing
of source family, intended-use scope, access route, dataset identifier,
authorization evidence reference, validated structured authorization-evidence
record fingerprint, client revision, response schema or public-contract evidence.

This is Gate-E integrity infrastructure only. Batch validity is not source-gate
closure, coverage/PIT evidence, performance authority, holdout authority or
live-trading authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Iterable, Mapping

from research_v1_krx_acquisition_receipt import _sha256
from research_v1_krx_public_evidence import (
    PUBLIC_EVIDENCE_VERSION,
    public_evidence_fingerprint_sha256,
)


class KRXAcquisitionBatchError(ValueError):
    """Raised when receipt provenance is incomplete, mixed or tampered."""


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RECEIPT_BODY_FIELDS = (
    "receipt_version",
    "source_family",
    "intended_use_scope",
    "access_route",
    "dataset_identifier",
    "authorization_evidence_reference",
    "authorization_evidence_fingerprint_sha256",
    "client_revision",
    "retrieved_at",
    "request_metadata_sha256",
    "response_schema_sha256",
    "response_payload_sha256",
    "response_rows",
    "response_columns",
    "public_contract_evidence_version",
    "public_contract_evidence_fingerprint_sha256",
    "alpha_or_final_judge_promotion_authorized",
    "sealed_holdout_authorized",
    "live_trading_authorized",
)


@dataclass(frozen=True)
class KRXAcquisitionBatchManifest:
    batch_version: str
    source_family: str
    intended_use_scope: str
    access_route: str
    dataset_identifier: str
    authorization_evidence_reference: str
    authorization_evidence_fingerprint_sha256: str
    client_revision: str
    response_schema_sha256: str
    public_contract_evidence_version: str
    public_contract_evidence_fingerprint_sha256: str
    receipt_count: int
    total_response_rows: int
    receipt_fingerprints_sha256: tuple[str, ...]
    batch_fingerprint_sha256: str
    coverage_validated: bool
    pit_lineage_validated: bool
    alpha_or_final_judge_promotion_authorized: bool
    sealed_holdout_authorized: bool
    live_trading_authorized: bool


def _body(receipt: Mapping[str, Any]) -> dict[str, Any]:
    missing = [field for field in RECEIPT_BODY_FIELDS if field not in receipt]
    if missing:
        raise KRXAcquisitionBatchError(f"receipt missing required fields: {missing}")
    return {field: receipt[field] for field in RECEIPT_BODY_FIELDS}


def verify_receipt_fingerprint(receipt: Mapping[str, Any]) -> str:
    """Verify one acquisition receipt without trusting its claimed fingerprint."""
    if not isinstance(receipt, Mapping):
        raise KRXAcquisitionBatchError("receipt must be a mapping")
    claimed = str(receipt.get("receipt_fingerprint_sha256") or "").strip().lower()
    if not SHA256_RE.fullmatch(claimed):
        raise KRXAcquisitionBatchError("receipt fingerprint is missing or malformed")
    expected = _sha256(_body(receipt))
    if claimed != expected:
        raise KRXAcquisitionBatchError("receipt fingerprint mismatch; receipt may be tampered")
    auth_fp = str(receipt["authorization_evidence_fingerprint_sha256"]).strip().lower()
    if not SHA256_RE.fullmatch(auth_fp):
        raise KRXAcquisitionBatchError(
            "authorization evidence fingerprint is missing or malformed"
        )
    if str(receipt["receipt_version"]) != "2026-10-01.v2":
        raise KRXAcquisitionBatchError("unsupported acquisition receipt version")
    if bool(receipt["alpha_or_final_judge_promotion_authorized"]):
        raise KRXAcquisitionBatchError("receipt illegally claims promotion authority")
    if bool(receipt["sealed_holdout_authorized"]):
        raise KRXAcquisitionBatchError("receipt illegally claims sealed-holdout authority")
    if bool(receipt["live_trading_authorized"]):
        raise KRXAcquisitionBatchError("receipt illegally claims live-trading authority")
    return claimed


def _single_value(receipts: list[Mapping[str, Any]], field: str) -> Any:
    values = {str(receipt[field]) for receipt in receipts}
    if len(values) != 1:
        raise KRXAcquisitionBatchError(f"batch mixes multiple {field} values")
    return receipts[0][field]


def build_acquisition_batch_manifest(
    receipts: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build an order-independent provenance manifest for one exact dataset."""
    items = list(receipts)
    if not items:
        raise KRXAcquisitionBatchError("acquisition batch is empty")

    fingerprints = [verify_receipt_fingerprint(receipt) for receipt in items]
    if len(fingerprints) != len(set(fingerprints)):
        raise KRXAcquisitionBatchError("acquisition batch contains duplicate receipts")

    source_family = str(_single_value(items, "source_family"))
    intended_use_scope = str(_single_value(items, "intended_use_scope"))
    access_route = str(_single_value(items, "access_route"))
    dataset_identifier = str(_single_value(items, "dataset_identifier"))
    auth_ref = str(_single_value(items, "authorization_evidence_reference"))
    auth_evidence_fp = str(
        _single_value(items, "authorization_evidence_fingerprint_sha256")
    ).lower()
    client_revision = str(_single_value(items, "client_revision"))
    schema_sha = str(_single_value(items, "response_schema_sha256"))
    public_version = str(_single_value(items, "public_contract_evidence_version"))
    public_fp = str(_single_value(items, "public_contract_evidence_fingerprint_sha256"))

    if not SHA256_RE.fullmatch(auth_evidence_fp):
        raise KRXAcquisitionBatchError("batch authorization evidence fingerprint is malformed")
    if public_version != PUBLIC_EVIDENCE_VERSION:
        raise KRXAcquisitionBatchError("batch uses stale public-contract evidence version")
    if public_fp != public_evidence_fingerprint_sha256():
        raise KRXAcquisitionBatchError("batch uses stale public-contract evidence fingerprint")

    sorted_fps = tuple(sorted(fingerprints))
    batch_body = {
        "batch_version": "2026-10-01.v2",
        "source_family": source_family,
        "intended_use_scope": intended_use_scope,
        "access_route": access_route,
        "dataset_identifier": dataset_identifier,
        "authorization_evidence_reference": auth_ref,
        "authorization_evidence_fingerprint_sha256": auth_evidence_fp,
        "client_revision": client_revision,
        "response_schema_sha256": schema_sha,
        "public_contract_evidence_version": public_version,
        "public_contract_evidence_fingerprint_sha256": public_fp,
        "receipt_count": len(items),
        "total_response_rows": int(sum(int(receipt["response_rows"]) for receipt in items)),
        "receipt_fingerprints_sha256": sorted_fps,
        "coverage_validated": False,
        "pit_lineage_validated": False,
        "alpha_or_final_judge_promotion_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
    manifest = KRXAcquisitionBatchManifest(
        **batch_body,
        batch_fingerprint_sha256=_sha256(batch_body),
    )
    out = asdict(manifest)
    out["receipt_fingerprints_sha256"] = list(manifest.receipt_fingerprints_sha256)
    out["guardrail"] = (
        "A valid batch proves only internally consistent acquisition provenance for one dataset contract and one validated structured authorization-evidence record fingerprint. "
        "Coverage, PIT lineage, A-F closure, feature testing, sealed holdout, promotion and live trading remain separate."
    )
    return out
