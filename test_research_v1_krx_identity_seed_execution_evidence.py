import json
from pathlib import Path

import pytest

from research_v1_krx_identity_seed_execution_evidence import (
    KRXIdentitySeedExecutionEvidenceError,
    validate_evidence,
    validate_file,
)

PATH = Path("INDEXALERT_KRX_HISTORICAL_IDENTITY_SEED_EXECUTION_EVIDENCE.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_identity_seed_evidence_is_complete_but_non_promotional():
    out = validate_file()
    assert out["valid"] is True
    assert out["mode"] == "EXECUTE_IDENTITY_SEED"
    assert out["task_count"] == 27
    assert out["completed_task_count"] == 27
    assert out["network_request_attempt_count"] == 27
    assert out["phase_complete"] is True
    assert out["source_gate_c_closed"] is False
    assert out["source_gate_d_closed"] is False
    assert out["source_gate_e_closed"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_identity_seed_evidence_rejects_partial_or_extra_execution():
    data = _data()
    data["execution"]["completed_task_count"] = 26
    with pytest.raises(KRXIdentitySeedExecutionEvidenceError, match="completed_task_count"):
        validate_evidence(data)

    data = _data()
    data["execution"]["network_request_attempt_count"] = 28
    with pytest.raises(KRXIdentitySeedExecutionEvidenceError, match="network_request_attempt_count"):
        validate_evidence(data)


def test_identity_seed_evidence_rejects_raw_leak_or_authority_escalation():
    data = _data()
    data["integrity"]["raw_rows_emitted"] = True
    with pytest.raises(KRXIdentitySeedExecutionEvidenceError, match="raw rows"):
        validate_evidence(data)

    for key in (
        "source_gate_c_closed",
        "source_gate_d_closed",
        "source_gate_e_closed",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        data = _data()
        data["post_run_boundary"][key] = True
        with pytest.raises(KRXIdentitySeedExecutionEvidenceError, match="illegally true"):
            validate_evidence(data)


def test_identity_seed_evidence_requires_post_run_lockdown():
    data = _data()
    data["post_run_boundary"]["execution_consent_disabled_again"] = False
    with pytest.raises(KRXIdentitySeedExecutionEvidenceError, match="consent was not disabled"):
        validate_evidence(data)

    data = _data()
    data["post_run_boundary"]["start_command_restored_to_preflight_only"] = False
    with pytest.raises(KRXIdentitySeedExecutionEvidenceError, match="preflight start command"):
        validate_evidence(data)
