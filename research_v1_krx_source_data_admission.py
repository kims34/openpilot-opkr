"""Fail-closed admission gate for KRX-derived research source data.

This module composes already-audited source governance, acquisition provenance,
PIT lineage and exact coverage evidence. It decides only whether one source
dataset is structurally admissible for the *next governance review*.

It deliberately never authorizes a feature-performance experiment, sealed
holdout, promotion or live trading. Experiment ledger/preregistration and all
statistical/execution gates remain separate.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from research_v1_krx_acquisition_receipt import _sha256
from research_v1_krx_public_evidence import (
    PUBLIC_EVIDENCE_VERSION,
    public_evidence_fingerprint_sha256,
)


class KRXSourceDataAdmissionError(ValueError):
    """Raised when composed source evidence is malformed, mixed or tampered."""


BATCH_BODY_FIELDS = (
    "batch_version",
    "source_family",
    "intended_use_scope",
    "access_route",
    "dataset_identifier",
    "authorization_evidence_reference",
    "client_revision",
    "response_schema_sha256",
    "public_contract_evidence_version",
    "public_contract_evidence_fingerprint_sha256",
    "receipt_count",
    "total_response_rows",
    "receipt_fingerprints_sha256",
    "coverage_validated",
    "pit_lineage_validated",
    "alpha_or_final_judge_promotion_authorized",
    "sealed_holdout_authorized",
    "live_trading_authorized",
)


@dataclass(frozen=True)
class KRXSourceDataAdmission:
    source_family: str
    intended_use_scope: str
    dataset_identifier: str
    source_contract_closed: bool
    acquisition_batch_integrity_valid: bool
    public_contract_evidence_current: bool
    pit_lineage_structurally_valid: bool
    historical_coverage_structurally_complete: bool
    source_family_and_scope_consistent: bool
    source_data_structurally_admissible: bool
    eligible_for_experiment_registry_review: bool
    feature_performance_testing_authorized: bool
    sealed_holdout_authorized: bool
    alpha_or_final_judge_promotion_authorized: bool
    live_trading_authorized: bool


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise KRXSourceDataAdmissionError(f"{label} must be a mapping")
    return value


def _verify_batch(batch: Mapping[str, Any]) -> bool:
    missing = [field for field in BATCH_BODY_FIELDS if field not in batch]
    if missing:
        raise KRXSourceDataAdmissionError(f"batch manifest missing required fields: {missing}")
    claimed = str(batch.get("batch_fingerprint_sha256") or "").strip().lower()
    if len(claimed) != 64 or any(ch not in "0123456789abcdef" for ch in claimed):
        raise KRXSourceDataAdmissionError("batch fingerprint is missing or malformed")
    body = {field: batch[field] for field in BATCH_BODY_FIELDS}
    if claimed != _sha256(body):
        raise KRXSourceDataAdmissionError("batch fingerprint mismatch; manifest may be tampered")
    if int(batch["receipt_count"]) <= 0:
        raise KRXSourceDataAdmissionError("batch must contain at least one receipt")
    fps = list(batch["receipt_fingerprints_sha256"])
    if len(fps) != int(batch["receipt_count"]) or len(fps) != len(set(fps)):
        raise KRXSourceDataAdmissionError("batch receipt fingerprints are incomplete or duplicated")
    for forbidden in (
        "alpha_or_final_judge_promotion_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        if bool(batch[forbidden]):
            raise KRXSourceDataAdmissionError(f"batch illegally claims authority: {forbidden}")
    return True


def assess_investor_flow_source_data_admission(
    *,
    source_gate_audit: Mapping[str, Any],
    acquisition_batch_manifest: Mapping[str, Any],
    lineage_audit: Mapping[str, Any],
    coverage_audit: Mapping[str, Any],
) -> dict[str, Any]:
    """Compose investor-flow source evidence without granting performance authority."""
    gates = _mapping(source_gate_audit, "source_gate_audit")
    batch = _mapping(acquisition_batch_manifest, "acquisition_batch_manifest")
    lineage = _mapping(lineage_audit, "lineage_audit")
    coverage = _mapping(coverage_audit, "coverage_audit")

    if gates.get("contract") != "INDEXALERT_KRX_SOURCE_GATES_A_TO_F":
        raise KRXSourceDataAdmissionError("unexpected source-gate contract")
    if gates.get("source_family") != "KRX_INVESTOR_FLOW":
        raise KRXSourceDataAdmissionError("source-gate audit is not KRX_INVESTOR_FLOW")
    if batch.get("source_family") != "KRX_INVESTOR_FLOW":
        raise KRXSourceDataAdmissionError("acquisition batch is not KRX_INVESTOR_FLOW")

    batch_valid = _verify_batch(batch)
    public_current = bool(
        batch.get("public_contract_evidence_version") == PUBLIC_EVIDENCE_VERSION
        and batch.get("public_contract_evidence_fingerprint_sha256")
        == public_evidence_fingerprint_sha256()
        and lineage.get("public_contract_evidence_matches_current") is True
    )
    source_closed = bool(
        gates.get("all_source_gates_pass") is True
        and gates.get("source_contract_closed_for_declared_scope") is True
    )
    lineage_valid = bool(lineage.get("lineage_structurally_valid") is True)
    coverage_complete = bool(coverage.get("coverage_structurally_complete") is True)
    family_scope_consistent = bool(
        gates.get("source_family") == batch.get("source_family") == "KRX_INVESTOR_FLOW"
        and str(gates.get("intended_use_scope") or "")
        == str(batch.get("intended_use_scope") or "")
        and bool(str(gates.get("intended_use_scope") or "").strip())
    )

    structurally_admissible = bool(
        source_closed
        and batch_valid
        and public_current
        and lineage_valid
        and coverage_complete
        and family_scope_consistent
    )
    result = KRXSourceDataAdmission(
        source_family="KRX_INVESTOR_FLOW",
        intended_use_scope=str(gates.get("intended_use_scope") or ""),
        dataset_identifier=str(batch.get("dataset_identifier") or ""),
        source_contract_closed=source_closed,
        acquisition_batch_integrity_valid=batch_valid,
        public_contract_evidence_current=public_current,
        pit_lineage_structurally_valid=lineage_valid,
        historical_coverage_structurally_complete=coverage_complete,
        source_family_and_scope_consistent=family_scope_consistent,
        source_data_structurally_admissible=structurally_admissible,
        eligible_for_experiment_registry_review=structurally_admissible,
        # The experiment ledger/preregistration, statistical protocol and all
        # promotion gates remain separate; this module never grants them.
        feature_performance_testing_authorized=False,
        sealed_holdout_authorized=False,
        alpha_or_final_judge_promotion_authorized=False,
        live_trading_authorized=False,
    )
    out = asdict(result)
    out["blocking_conditions"] = [
        name
        for name, ok in (
            ("SOURCE_CONTRACT_A_TO_F_NOT_CLOSED", source_closed),
            ("ACQUISITION_BATCH_INTEGRITY_INVALID", batch_valid),
            ("PUBLIC_CONTRACT_EVIDENCE_NOT_CURRENT", public_current),
            ("PIT_LINEAGE_NOT_STRUCTURALLY_VALID", lineage_valid),
            ("HISTORICAL_COVERAGE_NOT_STRUCTURALLY_COMPLETE", coverage_complete),
            ("SOURCE_FAMILY_OR_USE_SCOPE_MISMATCH", family_scope_consistent),
        )
        if not ok
    ]
    out["guardrail"] = (
        "Structural source-data admission is only eligibility for the next governance review. "
        "It never authorizes feature-performance testing, sealed holdout, promotion or live trading."
    )
    return out
