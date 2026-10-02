import json
from pathlib import Path

import pytest

from research_v1_krx_worker_provisioning_consent import (
    KRXWorkerProvisioningConsentError,
    validate_contract,
    validate_file,
)

PATH = Path("INDEXALERT_KRX_WORKER_PROVISIONING_CONSENT_CONTRACT.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_provisioning_contract_records_completed_authorized_preflight_only():
    out = validate_file()
    assert out["valid"] is True
    assert out["provisioning_authorized_by_user"] is True
    assert out["worker_service_creation_authorized"] is True
    assert out["dedicated_volume_creation_authorized"] is True
    assert out["worker_secret_configuration_authorized"] is False
    assert out["bulk_network_execution_authorized_by_user"] is False
    assert out["expected_scope_network_execution_authorized_by_user"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_completed_provisioning_requires_fail_closed_execution_record():
    data = _data()
    data["execution_record"]["network_request_attempted"] = True
    with pytest.raises(KRXWorkerProvisioningConsentError, match="network request illegally attempted"):
        validate_contract(data)

    data = _data()
    data["execution_record"]["historical_acquisition_network_execution_authorized"] = True
    with pytest.raises(KRXWorkerProvisioningConsentError, match="historical acquisition execution illegally authorized"):
        validate_contract(data)

    data = _data()
    data["execution_record"]["preflight_mode"] = "EXECUTE"
    with pytest.raises(KRXWorkerProvisioningConsentError, match="preflight mode drift"):
        validate_contract(data)


def test_provisioning_authority_cannot_expand_into_separate_protected_actions():
    for key in (
        "worker_secret_configuration_authorized",
        "bulk_network_execution_authorized_by_user",
        "expected_scope_network_execution_authorized_by_user",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        data = _data()
        data["authority"][key] = True
        with pytest.raises(KRXWorkerProvisioningConsentError, match="illegally true"):
            validate_contract(data)


def test_authorized_provisioning_requires_matching_creation_authority_and_record():
    data = _data()
    data["authority"]["worker_service_creation_authorized"] = False
    with pytest.raises(KRXWorkerProvisioningConsentError, match="worker service creation authorization missing"):
        validate_contract(data)

    data = _data()
    data["execution_record"]["provisioning_completed"] = False
    with pytest.raises(KRXWorkerProvisioningConsentError, match="completed execution record"):
        validate_contract(data)


def test_bulk_and_expected_scope_execution_must_remain_separate():
    data = _data()
    data["explicitly_not_authorized"] = [
        x for x in data["explicitly_not_authorized"]
        if "KRX_HISTORICAL_ACQUISITION_CONSENT" not in x
    ]
    with pytest.raises(KRXWorkerProvisioningConsentError, match="forbidden scope marker missing"):
        validate_contract(data)
