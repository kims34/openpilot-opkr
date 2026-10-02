import json
from pathlib import Path
import pytest

from research_v1_krx_worker_provisioning_consent import (
    KRXWorkerProvisioningConsentError,
    validate_contract,
    validate_file,
)

PATH=Path("INDEXALERT_KRX_WORKER_PROVISIONING_CONSENT_CONTRACT.json")

def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))

def test_committed_provisioning_contract_is_not_yet_authorized():
    out=validate_file()
    assert out["valid"] is True
    assert out["provisioning_authorized_by_user"] is False
    assert out["bulk_network_execution_authorized_by_user"] is False
    assert out["expected_scope_network_execution_authorized_by_user"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False

def test_provisioning_contract_cannot_self_authorize_any_action():
    for key in (
        "provisioning_authorized_by_user",
        "worker_service_creation_authorized",
        "dedicated_volume_creation_authorized",
        "worker_secret_configuration_authorized",
        "bulk_network_execution_authorized_by_user",
        "expected_scope_network_execution_authorized_by_user",
    ):
        data=_data()
        data["authority"][key]=True
        with pytest.raises(KRXWorkerProvisioningConsentError, match="illegally true"):
            validate_contract(data)

def test_bulk_and_expected_scope_execution_must_remain_separate():
    data=_data()
    data["explicitly_not_authorized"]=[
        x for x in data["explicitly_not_authorized"]
        if "KRX_HISTORICAL_ACQUISITION_CONSENT" not in x
    ]
    with pytest.raises(KRXWorkerProvisioningConsentError, match="forbidden scope marker missing"):
        validate_contract(data)
