from research_v1_krx_investor_flow_probe import (
    _canonical_sha256 as investor_fingerprint,
    source_gate_audit as investor_gate_audit,
)
from research_v1_krx_status_source_probe import (
    _canonical_sha256 as status_fingerprint,
    source_gate_audit as status_gate_audit,
)


def test_status_probe_without_credentials_blocks_gate_a():
    out = status_gate_audit(session_configured=False)
    assert out["gates"]["A"]["status"] == "BLOCKED"
    assert out["gates"]["C"]["status"] == "BLOCKED"
    assert out["gates"]["D"]["status"] == "BLOCKED"
    assert out["all_source_gates_pass"] is False
    assert out["source_contract_closed_for_declared_scope"] is False
    assert out["sealed_holdout_authorized_by_source_audit_alone"] is False


def test_status_probe_with_credentials_still_cannot_close_contract():
    out = status_gate_audit(session_configured=True)
    assert out["gates"]["A"]["status"] == "PARTIAL"
    assert all(out["gates"][gate]["status"] != "PASS" for gate in "ABCDEF")
    assert out["source_contract_closed_for_declared_scope"] is False
    assert out["alpha_or_final_judge_promotion_authorized"] is False


def test_investor_probe_without_credentials_blocks_gate_a_and_performance_path():
    out = investor_gate_audit(session_configured=False)
    assert out["gates"]["A"]["status"] == "BLOCKED"
    assert out["gates"]["C"]["status"] == "BLOCKED"
    assert out["gates"]["D"]["status"] == "PARTIAL"
    assert out["all_source_gates_pass"] is False
    assert out["live_trading_authorized_by_source_audit_alone"] is False


def test_investor_probe_with_credentials_remains_source_open():
    out = investor_gate_audit(session_configured=True)
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
