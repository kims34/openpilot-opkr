import json
from pathlib import Path

import pytest

from research_v1_krx_worker_provisioning_evidence import (
    KRXWorkerProvisioningEvidenceError,
    validate_file,
    validate_provisioning_evidence,
)

PATH = Path("INDEXALERT_KRX_WORKER_PROVISIONING_READINESS_EVIDENCE.json")

def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))

def test_committed_provisioning_evidence_is_read_only_and_blocked():
    out=validate_file()
    assert out["valid"] is True
    assert out["worker_service_present"] is False
    assert out["dedicated_worker_volume_present"] is False
    assert out["runtime_volume_reuse_allowed"] is False
    assert out["service_creation_authorized"] is False
    assert out["volume_creation_or_attachment_authorized"] is False
    assert out["bulk_network_execution_authorized_by_user"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False

def test_runtime_volume_cannot_be_reused_for_worker():
    data=_data()
    data["existing_public_runtime_volume"]["reuse_for_historical_worker_forbidden"]=False
    with pytest.raises(KRXWorkerProvisioningEvidenceError, match="runtime volume reuse guard lost"):
        validate_provisioning_evidence(data)

def test_provisioning_snapshot_cannot_self_authorize_mutation():
    for key in (
        "service_creation_authorized",
        "volume_creation_or_attachment_authorized",
        "worker_secret_configuration_authorized",
    ):
        data=_data()
        data["authority"][key]=True
        with pytest.raises(KRXWorkerProvisioningEvidenceError, match="illegally true"):
            validate_provisioning_evidence(data)

def test_bulk_or_expected_scope_execution_cannot_be_pre_authorized():
    for key in (
        "bulk_network_execution_authorized_by_user",
        "expected_scope_network_execution_authorized_by_user",
    ):
        data=_data()
        data["authority"][key]=True
        with pytest.raises(KRXWorkerProvisioningEvidenceError, match="illegally true"):
            validate_provisioning_evidence(data)
