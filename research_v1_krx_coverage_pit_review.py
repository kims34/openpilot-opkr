"""Network-free composer for KRX historical coverage/PIT review candidates.

This module consumes audit summaries only. It never acquires data, invents
expected scope, writes source-gate PASS, authorizes performance research, opens
sealed holdout, or enables trading.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

CONTRACT_PATH = Path("INDEXALERT_KRX_COVERAGE_PIT_AUDIT_CONTRACT.json")
CONTRACT_ID = "INDEXALERT-KRX-COVERAGE-PIT-AUDIT-v1"


class KRXCoveragePITReviewError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXCoveragePITReviewError(msg)


def validate_contract(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "contract must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(data.get("contract_id") == CONTRACT_ID, "contract_id drift")
    _require(data.get("bound_historical_plan_id") == "INDEXALERT-KRX-HIST-ACQ-v3", "plan binding drift")
    _require(data.get("expected_scope_contract_id") == "INDEXALERT-KRX-EXPECTED-SCOPE-ATTESTATION-v1", "expected-scope binding drift")
    _require(data.get("phase") == "COVERAGE_PIT_AUDIT", "phase drift")
    _require(data.get("network_request_attempted") is False, "audit must remain network-free")

    prerequisites = data.get("prerequisites")
    _require(isinstance(prerequisites, Mapping), "prerequisite requirements must be an object")
    for key in ["identity_seed_complete","identity_standard_code_binding_complete","per_security_history_complete","status_economics_phase_complete","expected_scope_attestation_complete","all_private_raw_objects_verified","all_request_receipts_verified","all_rows_within_preregistered_request_windows"]:
        _require(prerequisites.get(key) is True, f"prerequisite requirement lost: {key}")
    for section, key, required in [["status_review","gate_c_candidate_requires",["status_identity_coverage.coverage_structurally_complete=true","status_event_integrity.structurally_consistent=true","all trading-halt/delisting/cleanup historical request tasks complete","exact expected-scope contract fingerprint match"]],["status_review","gate_d_candidate_requires",["separate status PIT lineage audit with explicit official availability timestamps","no retrospective retrieval timestamp may be backdated into historical availability"]],["investor_flow_review","gate_c_candidate_requires",["investor_flow_coverage.coverage_structurally_complete=true","validated observed keys exactly match independently attested expected keys","all investor-flow historical request tasks complete"]],["investor_flow_review","gate_d_candidate_requires",["investor_flow_lineage.lineage_structurally_valid=true","event_time <= published_at <= available_at <= ingested_at","official publication-floor rule satisfied for every row"]]]:
        section_data = data.get(section)
        _require(isinstance(section_data, Mapping), f"{section} must be an object")
        _require(section_data.get(key) == required, f"{section}.{key} requirements drift")

    decision = data.get("decision_boundary") or {}
    _require(decision.get("composer_may_emit_gate_review_candidates") is True, "review-candidate capability lost")
    _require(decision.get("composer_may_set_source_gate_pass") is False, "composer may not set gate PASS")
    _require(decision.get("composer_may_close_source_contract") is False, "composer may not close source contract")
    for key in (
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(decision.get(key) is False, f"{key} illegally true")

    _require((data.get("status_review") or {}).get("exact_status_economics_not_inferred_from_price_context") is True, "status-economics guard lost")
    _require((data.get("investor_flow_review") or {}).get("no_zero_flow_synthesis") is True, "zero-flow synthesis guard lost")
    return {
        "valid": True,
        "contract_id": CONTRACT_ID,
        "network_request_attempted": False,
        "source_gate_write_allowed": False,
        "source_contract_close_allowed": False,
    }


def validate_file(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    return validate_contract(json.loads(path.read_text(encoding="utf-8")))


def _bool(mapping: Mapping[str, Any] | None, key: str) -> bool:
    return bool(isinstance(mapping, Mapping) and mapping.get(key) is True)


def assess_review_candidates(
    *,
    prerequisites: Mapping[str, Any],
    provenance_audit: Mapping[str, Any],
    status_identity_coverage: Mapping[str, Any] | None = None,
    status_event_integrity: Mapping[str, Any] | None = None,
    status_pit_lineage: Mapping[str, Any] | None = None,
    investor_flow_coverage: Mapping[str, Any] | None = None,
    investor_flow_lineage: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose already-audited evidence into review candidates only."""
    validate_file()

    required_predecessors = (
        "identity_seed_complete",
        "identity_standard_code_binding_complete",
        "per_security_history_complete",
        "status_economics_phase_complete",
        "expected_scope_attestation_complete",
    )
    predecessor_ok = all(_bool(prerequisites, key) for key in required_predecessors)

    provenance_keys = (
        "all_private_raw_objects_verified",
        "all_request_receipts_verified",
        "all_rows_within_preregistered_request_windows",
        "expected_scope_contract_fingerprint_matches",
    )
    provenance_ok = all(_bool(provenance_audit, key) for key in provenance_keys)

    status_c_inputs = {
        "predecessors_complete": predecessor_ok,
        "provenance_complete": provenance_ok,
        "identity_coverage_complete": _bool(status_identity_coverage, "coverage_structurally_complete"),
        "event_integrity_consistent": _bool(status_event_integrity, "structurally_consistent"),
        "status_request_set_complete": _bool(provenance_audit, "status_request_set_complete"),
    }
    status_c_candidate = all(status_c_inputs.values())

    status_d_inputs = {
        "predecessors_complete": predecessor_ok,
        "provenance_complete": provenance_ok,
        "status_pit_lineage_structurally_valid": _bool(status_pit_lineage, "lineage_structurally_valid"),
        "official_historical_availability_lineage_complete": _bool(status_pit_lineage, "official_historical_availability_lineage_complete"),
        "retrospective_retrieval_not_backdated": _bool(status_pit_lineage, "retrospective_retrieval_not_backdated"),
    }
    status_d_candidate = all(status_d_inputs.values())

    investor_c_inputs = {
        "predecessors_complete": predecessor_ok,
        "provenance_complete": provenance_ok,
        "coverage_complete": _bool(investor_flow_coverage, "coverage_structurally_complete"),
        "investor_request_set_complete": _bool(provenance_audit, "investor_request_set_complete"),
    }
    investor_c_candidate = all(investor_c_inputs.values())

    investor_d_inputs = {
        "predecessors_complete": predecessor_ok,
        "provenance_complete": provenance_ok,
        "lineage_structurally_valid": _bool(investor_flow_lineage, "lineage_structurally_valid"),
        "chronology_valid": _bool(investor_flow_lineage, "chronology_valid"),
        "publication_floor_valid": _bool(investor_flow_lineage, "publication_floor_valid"),
        "public_contract_evidence_current": _bool(investor_flow_lineage, "public_contract_evidence_matches_current"),
    }
    investor_d_candidate = all(investor_d_inputs.values())

    gate_e_candidate = bool(provenance_ok and predecessor_ok)

    def blockers(items: Mapping[str, bool]) -> list[str]:
        return [key for key, ok in items.items() if not ok]

    return {
        "contract_id": CONTRACT_ID,
        "phase": "COVERAGE_PIT_AUDIT",
        "network_request_attempted": False,
        "status_gate_c_review_candidate": status_c_candidate,
        "status_gate_c_blockers": blockers(status_c_inputs),
        "status_gate_d_review_candidate": status_d_candidate,
        "status_gate_d_blockers": blockers(status_d_inputs),
        "investor_flow_gate_c_review_candidate": investor_c_candidate,
        "investor_flow_gate_c_blockers": blockers(investor_c_inputs),
        "investor_flow_gate_d_review_candidate": investor_d_candidate,
        "investor_flow_gate_d_blockers": blockers(investor_d_inputs),
        "gate_e_review_candidate": gate_e_candidate,
        "source_gate_write_allowed": False,
        "source_contract_closed": False,
        "exact_status_economics_ready": False,
        "feature_performance_testing_authorized": False,
        "alpha_or_final_judge_promotion_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
        "guardrail": (
            "Review candidates are evidence for a later source-gate review only. "
            "This composer never writes PASS, never fabricates PIT timestamps or "
            "expected keys, and never infers exact realized status economics from "
            "KRX price context."
        ),
    }
