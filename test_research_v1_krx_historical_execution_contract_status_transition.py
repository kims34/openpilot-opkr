import json
from pathlib import Path

import pytest

from research_v1_krx_historical_execution_contract import (
    KRXHistoricalExecutionContractError,
    validate_execution_contract,
)

PATH = Path("INDEXALERT_KRX_HISTORICAL_EXECUTION_CONTRACT.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def _prepared():
    data = _data()
    stage = data["stage_specific_authority"]["status_economics"]
    stage["preparation_complete"] = True
    stage["preparation_evidence_id"] = "INDEXALERT-KRX-STATUS-ECONOMICS-PREP-v1"
    stage["predecessor_completion_evidence_id"] = (
        "INDEXALERT-KRX-PER-SECURITY-HISTORY-EXEC-2026-10-03-v1"
    )
    stage["prepared_task_count"] = 5
    stage["prepared_task_set_fingerprint_sha256"] = "a" * 64
    stage["prepared_private_task_manifest_metadata_sha256"] = "b" * 64
    return data


def test_status_economics_shell_is_explicitly_unprepared():
    data = _data()
    stage = data["stage_specific_authority"]["status_economics"]
    assert stage["preparation_complete"] is False
    assert stage["prepared_task_count"] is None
    assert stage["prepared_task_set_fingerprint_sha256"] is None
    assert stage["prepared_private_task_manifest_metadata_sha256"] is None
    assert stage["network_request_attempted_during_prepare"] is False
    assert stage["exact_prepared_scope_required"] is True
    assert validate_execution_contract(data)["valid"] is True


def test_status_economics_prepared_scope_can_be_frozen_without_authority():
    data = _prepared()
    out = validate_execution_contract(data)
    assert out["valid"] is True
    stage = data["stage_specific_authority"]["status_economics"]
    assert stage["prepared_task_count"] == 5
    assert stage["currently_authorized"] is False
    assert stage["exact_status_economics_claim_allowed"] is False
    assert stage["later_stage_auto_authorization"] is False


def test_status_economics_prepared_scope_requires_evidence_and_positive_count():
    data = _prepared()
    data["stage_specific_authority"]["status_economics"]["preparation_evidence_id"] = "wrong"
    with pytest.raises(KRXHistoricalExecutionContractError, match="preparation evidence binding drift"):
        validate_execution_contract(data)

    data = _prepared()
    data["stage_specific_authority"]["status_economics"]["prepared_task_count"] = 0
    with pytest.raises(KRXHistoricalExecutionContractError, match="must be positive"):
        validate_execution_contract(data)


def test_status_economics_prepared_scope_requires_valid_hashes():
    data = _prepared()
    data["stage_specific_authority"]["status_economics"][
        "prepared_task_set_fingerprint_sha256"
    ] = "0" * 63
    with pytest.raises(KRXHistoricalExecutionContractError, match="task-set SHA-256 invalid"):
        validate_execution_contract(data)

    data = _prepared()
    data["stage_specific_authority"]["status_economics"][
        "prepared_private_task_manifest_metadata_sha256"
    ] = "z" * 64
    with pytest.raises(KRXHistoricalExecutionContractError, match="manifest SHA-256 invalid"):
        validate_execution_contract(data)


def test_status_economics_shell_rejects_premature_prepared_values():
    data = _data()
    data["stage_specific_authority"]["status_economics"]["prepared_task_count"] = 1
    with pytest.raises(KRXHistoricalExecutionContractError, match="prematurely frozen"):
        validate_execution_contract(data)
