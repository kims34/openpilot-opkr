import pytest

from research_v1_krx_coverage_pit_review import (
    KRXCoveragePITReviewError,
    assess_review_candidates,
    validate_contract,
    validate_file,
)


def _predecessors(all_ok=True):
    return {
        "identity_seed_complete": all_ok,
        "identity_standard_code_binding_complete": all_ok,
        "per_security_history_complete": all_ok,
        "status_economics_phase_complete": all_ok,
        "expected_scope_attestation_complete": all_ok,
    }


def _provenance(all_ok=True):
    return {
        "all_private_raw_objects_verified": all_ok,
        "all_request_receipts_verified": all_ok,
        "all_rows_within_preregistered_request_windows": all_ok,
        "expected_scope_contract_fingerprint_matches": all_ok,
        "status_request_set_complete": all_ok,
        "investor_request_set_complete": all_ok,
    }


def test_contract_is_network_free_and_cannot_write_pass():
    out = validate_file()
    assert out["valid"] is True
    assert out["network_request_attempted"] is False
    assert out["source_gate_write_allowed"] is False
    assert out["source_contract_close_allowed"] is False


def test_complete_structural_inputs_only_create_review_candidates():
    out = assess_review_candidates(
        prerequisites=_predecessors(True),
        provenance_audit=_provenance(True),
        status_identity_coverage={"coverage_structurally_complete": True},
        status_event_integrity={"structurally_consistent": True},
        status_pit_lineage={
            "lineage_structurally_valid": True,
            "official_historical_availability_lineage_complete": True,
            "retrospective_retrieval_not_backdated": True,
        },
        investor_flow_coverage={"coverage_structurally_complete": True},
        investor_flow_lineage={
            "lineage_structurally_valid": True,
            "chronology_valid": True,
            "publication_floor_valid": True,
            "public_contract_evidence_matches_current": True,
        },
    )
    assert out["status_gate_c_review_candidate"] is True
    assert out["status_gate_d_review_candidate"] is True
    assert out["investor_flow_gate_c_review_candidate"] is True
    assert out["investor_flow_gate_d_review_candidate"] is True
    assert out["gate_e_review_candidate"] is True
    assert out["source_gate_write_allowed"] is False
    assert out["source_contract_closed"] is False
    assert out["exact_status_economics_ready"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_missing_expected_scope_or_pit_evidence_stays_blocked_without_inference():
    p = _predecessors(True)
    p["expected_scope_attestation_complete"] = False
    out = assess_review_candidates(
        prerequisites=p,
        provenance_audit=_provenance(True),
        status_identity_coverage={"coverage_structurally_complete": True},
        status_event_integrity={"structurally_consistent": True},
        status_pit_lineage=None,
        investor_flow_coverage={"coverage_structurally_complete": True},
        investor_flow_lineage=None,
    )
    assert out["status_gate_c_review_candidate"] is False
    assert out["status_gate_d_review_candidate"] is False
    assert out["investor_flow_gate_c_review_candidate"] is False
    assert out["investor_flow_gate_d_review_candidate"] is False
    assert "predecessors_complete" in out["status_gate_c_blockers"]
    assert "status_pit_lineage_structurally_valid" in out["status_gate_d_blockers"]
    assert "lineage_structurally_valid" in out["investor_flow_gate_d_blockers"]


def test_retrospective_retrieval_time_cannot_stand_in_for_historical_status_availability():
    out = assess_review_candidates(
        prerequisites=_predecessors(True),
        provenance_audit=_provenance(True),
        status_identity_coverage={"coverage_structurally_complete": True},
        status_event_integrity={"structurally_consistent": True},
        status_pit_lineage={
            "lineage_structurally_valid": True,
            "official_historical_availability_lineage_complete": False,
            "retrospective_retrieval_not_backdated": True,
        },
        investor_flow_coverage={"coverage_structurally_complete": False},
        investor_flow_lineage=None,
    )
    assert out["status_gate_c_review_candidate"] is True
    assert out["status_gate_d_review_candidate"] is False
    assert "official_historical_availability_lineage_complete" in out["status_gate_d_blockers"]


def test_contract_cannot_be_weakened_to_write_gate_pass():
    import json
    from pathlib import Path
    data = json.loads(
        Path("INDEXALERT_KRX_COVERAGE_PIT_AUDIT_CONTRACT.json").read_text(
            encoding="utf-8"
        )
    )
    data["decision_boundary"]["composer_may_set_source_gate_pass"] = True
    with pytest.raises(KRXCoveragePITReviewError, match="may not set gate PASS"):
        validate_contract(data)


@pytest.mark.parametrize("key", ["identity_seed_complete","identity_standard_code_binding_complete","per_security_history_complete","status_economics_phase_complete","expected_scope_attestation_complete","all_private_raw_objects_verified","all_request_receipts_verified","all_rows_within_preregistered_request_windows"])
@pytest.mark.parametrize("value", [False, None, 1, "true"])
def test_contract_rejects_removed_or_non_boolean_prerequisite_requirements(key, value):
    import json
    from pathlib import Path
    data = json.loads(Path("INDEXALERT_KRX_COVERAGE_PIT_AUDIT_CONTRACT.json").read_text())
    data["prerequisites"][key] = value
    with pytest.raises(KRXCoveragePITReviewError, match="prerequisite requirement lost"):
        validate_contract(data)


@pytest.mark.parametrize("key", ["identity_seed_complete","identity_standard_code_binding_complete","per_security_history_complete","status_economics_phase_complete","expected_scope_attestation_complete","all_private_raw_objects_verified","all_request_receipts_verified","all_rows_within_preregistered_request_windows"])
def test_contract_rejects_missing_prerequisite_requirements(key):
    import json
    from pathlib import Path
    data = json.loads(Path("INDEXALERT_KRX_COVERAGE_PIT_AUDIT_CONTRACT.json").read_text())
    del data["prerequisites"][key]
    with pytest.raises(KRXCoveragePITReviewError, match="prerequisite requirement lost"):
        validate_contract(data)


@pytest.mark.parametrize("section,key", [
    ("status_review", "gate_c_candidate_requires"),
    ("status_review", "gate_d_candidate_requires"),
    ("investor_flow_review", "gate_c_candidate_requires"),
    ("investor_flow_review", "gate_d_candidate_requires"),
])
def test_contract_rejects_removed_frozen_review_requirement(section, key):
    import json
    from pathlib import Path
    data = json.loads(Path("INDEXALERT_KRX_COVERAGE_PIT_AUDIT_CONTRACT.json").read_text())
    data[section][key] = data[section][key][:-1]
    with pytest.raises(KRXCoveragePITReviewError, match="requirements drift"):
        validate_contract(data)
