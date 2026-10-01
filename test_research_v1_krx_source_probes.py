from research_v1_krx_investor_flow_probe import (
    _canonical_sha256 as investor_fingerprint,
    _finalise_report as finalise_investor_report,
    source_gate_audit as investor_gate_audit,
)
from research_v1_krx_public_evidence import (
    PUBLIC_EVIDENCE_VERSION,
    public_evidence_fingerprint_sha256,
)
from research_v1_krx_status_source_probe import (
    _canonical_sha256 as status_fingerprint,
    _finalise_report as finalise_status_report,
    source_gate_audit as status_gate_audit,
)


def test_status_probe_without_authorized_request_blocks_gate_a():
    out = status_gate_audit(request_authorized=False)
    assert out["gates"]["A"]["status"] == "BLOCKED"
    assert out["gates"]["C"]["status"] == "BLOCKED"
    assert out["gates"]["D"]["status"] == "BLOCKED"
    assert out["all_source_gates_pass"] is False
    assert out["source_contract_closed_for_declared_scope"] is False
    assert out["sealed_holdout_authorized_by_source_audit_alone"] is False


def test_status_probe_authorized_tiny_request_still_cannot_close_contract():
    out = status_gate_audit(request_authorized=True)
    assert out["gates"]["A"]["status"] == "PARTIAL"
    assert all(out["gates"][gate]["status"] != "PASS" for gate in "ABCDEF")
    assert out["source_contract_closed_for_declared_scope"] is False
    assert out["alpha_or_final_judge_promotion_authorized"] is False


def test_investor_probe_without_authorized_request_blocks_gate_a_and_performance_path():
    out = investor_gate_audit(request_authorized=False)
    assert out["gates"]["A"]["status"] == "BLOCKED"
    assert out["gates"]["C"]["status"] == "BLOCKED"
    assert out["gates"]["D"]["status"] == "PARTIAL"
    assert out["all_source_gates_pass"] is False
    assert out["live_trading_authorized_by_source_audit_alone"] is False


def test_investor_probe_authorized_tiny_request_remains_source_open():
    out = investor_gate_audit(request_authorized=True)
    assert out["gates"]["A"]["status"] == "PARTIAL"
    assert out["source_contract_closed_for_declared_scope"] is False
    assert out["sealed_holdout_authorized_by_source_audit_alone"] is False


def test_probe_fingerprints_are_deterministic_and_content_sensitive():
    x = {"b": 2, "a": [1, 3]}
    same_reordered = {"a": [1, 3], "b": 2}
    changed = {"a": [1, 4], "b": 2}

    assert status_fingerprint(x) == status_fingerprint(same_reordered)
    assert investor_fingerprint(x) == investor_fingerprint(same_reordered)
    assert status_fingerprint(x) != status_fingerprint(changed)
    assert investor_fingerprint(x) != investor_fingerprint(changed)


def test_status_probe_artifact_is_bound_to_public_contract_evidence():
    report = {
        "active_probe_access_route": "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
        "pinned_krx_data_api_commit": "pinned",
        "official_screen_contracts": {"delisted": "MDCSTAT238"},
        "candidate_low_level_blds_not_yet_promoted_to_contract": {"halt": "candidate"},
        "source_route_policy": {"no_auth_substitution": True},
    }
    out = finalise_status_report(report, request_authorized=False)
    assert out["public_contract_evidence_version"] == PUBLIC_EVIDENCE_VERSION
    assert out["public_contract_evidence_fingerprint_sha256"] == public_evidence_fingerprint_sha256()
    assert out["authenticated_request_attempted"] is False
    assert len(out["probe_contract_fingerprint_sha256"]) == 64
    assert len(out["probe_result_fingerprint_sha256"]) == 64


def test_investor_probe_artifact_is_bound_to_public_contract_evidence():
    report = {
        "active_probe_access_route": "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
        "available_at_policy_if_adopted": "after official publication",
        "source_route_policy": {"no_auth_substitution": True},
    }
    out = finalise_investor_report(report, request_authorized=False)
    assert out["public_contract_evidence_version"] == PUBLIC_EVIDENCE_VERSION
    assert out["public_contract_evidence_fingerprint_sha256"] == public_evidence_fingerprint_sha256()
    assert out["feature_performance_testing_authorized"] is False
    assert out["authenticated_request_attempted"] is False
    assert len(out["probe_contract_fingerprint_sha256"]) == 64
    assert len(out["probe_result_fingerprint_sha256"]) == 64
