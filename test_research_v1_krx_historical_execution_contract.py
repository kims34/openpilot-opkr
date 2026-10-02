import json
from pathlib import Path

import pytest

from research_v1_krx_historical_execution_contract import (
    KRXHistoricalExecutionContractError,
    validate_execution_contract,
    validate_file,
)

PATH = Path("INDEXALERT_KRX_HISTORICAL_EXECUTION_CONTRACT.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_execution_contract_is_private_and_nonexecuting():
    out = validate_file()
    assert out["valid"] is True
    assert out["contract_id"] == "INDEXALERT-KRX-HIST-EXEC-v2"
    assert out["plan_id"] == "INDEXALERT-KRX-HIST-ACQ-v3"
    assert out["rights_to_acquire"] is True
    assert out["bulk_network_execution_authorized_by_user"] is False
    assert out["private_persistent_storage_required"] is True
    assert out["raw_publication_forbidden"] is True
    assert out["gate_c_closed"] is False
    assert out["gate_d_closed"] is False
    assert out["gate_e_closed"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


@pytest.mark.parametrize(
    "path,key",
    [
        (("repository_context",), "raw_data_in_repository_forbidden"),
        (("execution_isolation",), "dedicated_one_shot_worker_required"),
        (("execution_isolation",), "production_web_process_must_not_run_bulk_job"),
        (("private_storage",), "raw_artifact_upload_to_github_forbidden"),
        (("private_storage",), "raw_rows_in_actions_logs_forbidden"),
        (("source_capture",), "raw_response_bytes_required"),
        (("checkpoint_and_resume",), "resume_only_from_verified_raw_object_and_receipt"),
    ],
)
def test_safety_guards_cannot_be_disabled(path, key):
    data = _data()
    node = data
    for part in path:
        node = node[part]
    node[key] = False
    with pytest.raises(KRXHistoricalExecutionContractError, match="guard lost|requirement lost|prohibition lost"):
        validate_execution_contract(data)


def test_bulk_execution_cannot_be_pre_authorized():
    data = _data()
    data["authority"]["bulk_network_execution_authorized_by_user"] = True
    with pytest.raises(KRXHistoricalExecutionContractError, match="illegally true"):
        validate_execution_contract(data)


def test_bulk_consent_sentinel_is_frozen_to_plan_v3():
    data = _data()
    data["execution_isolation"]["exact_consent_sentinel"] = "yes"
    with pytest.raises(KRXHistoricalExecutionContractError, match="sentinel drift"):
        validate_execution_contract(data)


def test_credentials_and_raw_rows_remain_forbidden_public_output():
    data = _data()
    data["forbidden_public_output"].remove("KRX_PW")
    with pytest.raises(KRXHistoricalExecutionContractError, match="KRX_PW"):
        validate_execution_contract(data)


def test_cleanup_source_correction_is_frozen():
    data = _data()
    correction = data["source_contract_correction"]
    assert correction["historical_cleanup_source"] == "MDCSTAT23801 delisted-history cleanup-period fields"
    assert correction["current_cleanup_reconciliation_source"] == "MDCSTAT23701 mktId=ALL snapshot"
    assert correction["mdcstat237_historical_date_window_assumption_forbidden"] is True

    data = _data()
    data["source_contract_correction"]["mdcstat237_historical_date_window_assumption_forbidden"] = False
    with pytest.raises(KRXHistoricalExecutionContractError, match="prohibition lost"):
        validate_execution_contract(data)
