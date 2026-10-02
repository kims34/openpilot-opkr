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


def _prepared_data():
    data = _data()
    data["status"] = "PREPARED_SCOPE_FROZEN_EXECUTION_NOT_AUTHORIZED"
    data["predecessor"]["current_observed_complete"] = True
    data["predecessor"]["completion_evidence_id"] = (
        "INDEXALERT-KRX-PER-SECURITY-HISTORY-EXEC-2026-10-03-v1"
    )
    data["preparation_evidence_id"] = "INDEXALERT-KRX-STATUS-ECONOMICS-PREP-v1"
    data["preparation_gate"]["prepared_task_count"] = 7
    data["preparation_gate"]["prepared_task_set_fingerprint_sha256"] = "a" * 64
    data["preparation_gate"]["prepared_private_manifest_metadata_sha256"] = "b" * 64
    data["preparation_gate"]["preparation_complete"] = True
    data["preparation_gate"]["execution_scope_frozen"] = True
    data["preparation_gate"]["network_request_attempted"] = False
    data["preparation_gate"]["raw_rows_emitted"] = False
    data["preparation_gate"]["security_identifiers_emitted"] = False
    data["preparation_gate"]["exact_status_economics_ready"] = False
    return data


def test_prepared_scope_is_frozen_without_execution_authority():
    out = validate_contract(_prepared_data())
    assert out["valid"] is True
    assert out["prepared_task_count"] == 7
    assert out["preparation_complete"] is True
    assert out["execution_scope_frozen"] is True
    assert out["authorized"] is False


def test_prepared_scope_requires_predecessor_evidence_and_positive_count():
    data = _prepared_data()
    data["predecessor"]["completion_evidence_id"] = "wrong"
    with pytest.raises(KRXStatusEconomicsConsentError, match="completion evidence drift"):
        validate_contract(data)

    data = _prepared_data()
    data["preparation_gate"]["prepared_task_count"] = 0
    with pytest.raises(KRXStatusEconomicsConsentError, match="must be positive"):
        validate_contract(data)


def test_prepared_scope_requires_hashes_and_network_free_prepare():
    data = _prepared_data()
    data["preparation_gate"]["prepared_task_set_fingerprint_sha256"] = "0" * 63
    with pytest.raises(KRXStatusEconomicsConsentError, match="must be SHA-256"):
        validate_contract(data)

    data = _prepared_data()
    data["preparation_gate"]["network_request_attempted"] = True
    with pytest.raises(KRXStatusEconomicsConsentError, match="attempted network"):
        validate_contract(data)


def test_prepared_scope_cannot_claim_exact_economics_or_execution_authority():
    data = _prepared_data()
    data["preparation_gate"]["exact_status_economics_ready"] = True
    with pytest.raises(KRXStatusEconomicsConsentError, match="illegally ready"):
        validate_contract(data)

    data = _prepared_data()
    data["authority"]["status_economics_execution_authorized"] = True
    with pytest.raises(KRXStatusEconomicsConsentError, match="illegally true"):
        validate_contract(data)


def test_shell_rejects_prepared_fields_before_transition():
    data = _data()
    data["preparation_gate"]["prepared_task_set_fingerprint_sha256"] = "a" * 64
    with pytest.raises(KRXStatusEconomicsConsentError, match="prematurely frozen"):
        validate_contract(data)
