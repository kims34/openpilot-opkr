import json
from pathlib import Path

import pytest

from research_v1_krx_expected_scope_attestation import (
    CONTRACT_ID,
    KRXExpectedScopeAttestationError,
    build_calendar_discovery_plan,
    public_plan_summary,
    validate_contract,
    validate_file,
)

PATH = Path("INDEXALERT_KRX_EXPECTED_SCOPE_ATTESTATION_CONTRACT.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_expected_scope_contract_is_network_free_and_fail_closed():
    out = validate_file()
    assert out["valid"] is True
    assert out["contract_id"] == CONTRACT_ID
    assert out["calendar_date_count"] == 4127
    assert out["network_execution_authorized_by_user"] is False
    assert out["source_gate_c_closed"] is False
    assert out["source_gate_d_closed"] is False
    assert out["source_gate_e_closed"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_calendar_planner_enumerates_dates_without_inventing_trading_sessions():
    tasks = build_calendar_discovery_plan()
    assert len(tasks) == 4127
    assert tasks[0]["requested_date"] == "2015-06-15"
    assert tasks[-1]["requested_date"] == "2026-10-01"
    assert len({x["task_id"] for x in tasks}) == 4127
    assert all(x["trading_day_assumed"] is False for x in tasks)
    assert all(x["network_request_attempted"] is False for x in tasks)
    summary = public_plan_summary()
    assert summary["trading_calendar_inferred"] is False
    assert summary["network_request_attempted"] is False
    assert summary["raw_rows_emitted"] is False
    assert len(summary["task_set_fingerprint_sha256"]) == 64


def test_expected_scope_cannot_be_derived_from_audited_rows_or_pre_authorize_network():
    data = _data()
    data["integrity"]["expected_scope_must_not_be_derived_from_audited_data_marketplace_rows"] = False
    with pytest.raises(KRXExpectedScopeAttestationError, match="guard lost"):
        validate_contract(data)

    data = _data()
    data["execution"]["network_execution_authorized_by_user"] = True
    with pytest.raises(KRXExpectedScopeAttestationError, match="illegally authorized"):
        validate_contract(data)


def test_calendar_count_and_endpoints_are_frozen():
    data = _data()
    data["research_period"]["calendar_date_count"] = 4126
    with pytest.raises(KRXExpectedScopeAttestationError, match="count drift"):
        validate_contract(data)

    data = _data()
    data["official_attestation_sources"]["trading_date_and_trade_scope"]["endpoint"] = "https://example.invalid"
    with pytest.raises(KRXExpectedScopeAttestationError, match="endpoint drift"):
        validate_contract(data)


def test_scope_keys_cannot_be_weakened():
    data = _data()
    data["expected_scope_rules"]["investor_flow"]["key"] = ["event_date", "symbol"]
    with pytest.raises(KRXExpectedScopeAttestationError, match="investor key drift"):
        validate_contract(data)


@pytest.mark.parametrize("section", ["investor_flow", "security_status"])
@pytest.mark.parametrize("value", [False, None, 1, "true"])
def test_scope_fingerprint_output_requirement_must_remain_exact_true(section, value):
    data = _data()
    data["expected_scope_rules"][section]["output_requires_scope_contract_fingerprint"] = value
    with pytest.raises(KRXExpectedScopeAttestationError, match="scope fingerprint requirement lost"):
        validate_contract(data)


@pytest.mark.parametrize("section", ["investor_flow", "security_status"])
def test_scope_fingerprint_output_requirement_cannot_be_removed(section):
    data = _data()
    del data["expected_scope_rules"][section]["output_requires_scope_contract_fingerprint"]
    with pytest.raises(KRXExpectedScopeAttestationError, match="scope fingerprint requirement lost"):
        validate_contract(data)
