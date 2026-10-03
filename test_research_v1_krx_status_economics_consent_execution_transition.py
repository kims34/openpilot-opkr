import json
from pathlib import Path

import pytest

from research_v1_krx_status_economics_consent import (
    KRXStatusEconomicsConsentError,
    validate_contract,
)

PATH = Path("INDEXALERT_KRX_STATUS_ECONOMICS_CONSENT_CONTRACT.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def _prepared():
    data = _data()
    data["status"] = "PREPARED_SCOPE_FROZEN_EXECUTION_NOT_AUTHORIZED"
    data["predecessor"]["current_observed_complete"] = True
    data["predecessor"]["completion_evidence_id"] = (
        "INDEXALERT-KRX-PER-SECURITY-HISTORY-EXEC-2026-10-03-v1"
    )
    data["preparation_evidence_id"] = "INDEXALERT-KRX-STATUS-ECONOMICS-PREP-v1"
    gate = data["preparation_gate"]
    gate["prepared_task_count"] = 5
    gate["prepared_task_set_fingerprint_sha256"] = "a" * 64
    gate["prepared_private_manifest_metadata_sha256"] = "b" * 64
    gate["preparation_complete"] = True
    gate["execution_scope_frozen"] = True
    gate["network_request_attempted"] = False
    gate["raw_rows_emitted"] = False
    gate["security_identifiers_emitted"] = False
    gate["exact_status_economics_ready"] = False
    return data


def _in_progress():
    data = _prepared()
    data["status"] = "USER_AUTHORIZED_EXECUTION_IN_PROGRESS"
    data["user_authorization"].update(
        {
            "authorized": True,
            "consumed": False,
            "received_date_kst": "2099-01-01",
            "consumed_for_deployment_id": "future-deployment",
            "source_revision": "future-revision",
        }
    )
    data["authority"]["status_economics_execution_authorized"] = True
    data["execution"] = {
        "deployment_id": "future-deployment",
        "source_revision": "future-revision",
        "mode": "EXECUTE_STATUS_ECONOMICS",
        "task_count": 5,
        "task_set_fingerprint_sha256": "a" * 64,
        "private_manifest_metadata_sha256": "b" * 64,
        "execution_status": "IN_PROGRESS",
    }
    return data


def _complete():
    data = _in_progress()
    data["status"] = "EXECUTION_COMPLETE_AUTHORITY_CONSUMED"
    data["user_authorization"]["authorized"] = False
    data["user_authorization"]["consumed"] = True
    data["authority"]["status_economics_execution_authorized"] = False
    data["execution"]["execution_status"] = "COMPLETE"
    data["completion"] = {
        "evidence_id": "INDEXALERT-KRX-STATUS-ECONOMICS-EXEC-v1",
        "completed_task_count": 5,
        "failed_task_count": 0,
        "phase_status": "COMPLETE",
        "phase_complete": True,
        "task_set_fingerprint_sha256": "a" * 64,
        "private_batch_metadata_sha256": "c" * 64,
        "bulk_execution_consent_disabled_again": True,
        "status_economics_consent_disabled_again": True,
        "start_command_restored_to_preflight_only": True,
        "preflight_network_request_attempted_false": True,
        "exact_status_economics_ready": False,
        "realized_fill_economics_proven": False,
        "realized_recovery_cashflows_proven": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "expected_scope_network_execution_authorized": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "shadow_s1_authorized": False,
        "genuine_live_authorized": False,
        "live_trading_authorized": False,
    }
    return data


def test_future_in_progress_requires_explicit_bound_authorization_record():
    out = validate_contract(_in_progress())
    assert out["valid"] is True
    assert out["authorized"] is True
    assert out["completed"] is False
    assert out["authority_consumed"] is False

    data = _in_progress()
    data["user_authorization"]["received_date_kst"] = ""
    with pytest.raises(KRXStatusEconomicsConsentError, match="authorization date required"):
        validate_contract(data)

    data = _in_progress()
    data["execution"]["deployment_id"] = "different"
    with pytest.raises(KRXStatusEconomicsConsentError, match="execution deployment drift"):
        validate_contract(data)


def test_future_in_progress_requires_exact_prepared_scope_binding():
    data = _in_progress()
    data["execution"]["task_count"] = 4
    with pytest.raises(KRXStatusEconomicsConsentError, match="execution task count drift"):
        validate_contract(data)

    data = _in_progress()
    data["execution"]["task_set_fingerprint_sha256"] = "0" * 64
    with pytest.raises(KRXStatusEconomicsConsentError, match="fingerprint drift"):
        validate_contract(data)

    data = _in_progress()
    data["execution"]["private_manifest_metadata_sha256"] = "0" * 64
    with pytest.raises(KRXStatusEconomicsConsentError, match="manifest hash drift"):
        validate_contract(data)


def test_future_complete_consumes_authority_and_preserves_boundaries():
    out = validate_contract(_complete())
    assert out["valid"] is True
    assert out["authorized"] is False
    assert out["completed"] is True
    assert out["authority_consumed"] is True
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False

    data = _complete()
    data["user_authorization"]["consumed"] = False
    with pytest.raises(KRXStatusEconomicsConsentError, match="not marked consumed"):
        validate_contract(data)

    data = _complete()
    data["authority"]["status_economics_execution_authorized"] = True
    with pytest.raises(KRXStatusEconomicsConsentError, match="still active"):
        validate_contract(data)


def test_future_complete_rejects_incomplete_or_realized_economics_claims():
    data = _complete()
    data["completion"]["completed_task_count"] = 4
    with pytest.raises(KRXStatusEconomicsConsentError, match="completion task count drift"):
        validate_contract(data)

    data = _complete()
    data["completion"]["realized_fill_economics_proven"] = True
    with pytest.raises(KRXStatusEconomicsConsentError, match="illegally true"):
        validate_contract(data)

    data = _complete()
    data["completion"]["sealed_holdout_authorized"] = True
    with pytest.raises(KRXStatusEconomicsConsentError, match="illegally true"):
        validate_contract(data)


def test_current_shell_cannot_jump_to_execution_without_preparation():
    data = _data()
    data["status"] = "USER_AUTHORIZED_EXECUTION_IN_PROGRESS"
    data["user_authorization"]["authorized"] = True
    with pytest.raises(KRXStatusEconomicsConsentError):
        validate_contract(data)
