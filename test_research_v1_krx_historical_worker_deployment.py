import json
from pathlib import Path

import pytest

from research_v1_krx_historical_worker_deployment import (
    KRXHistoricalWorkerDeploymentError,
    validate_deployment_contract,
    validate_files,
    validate_worker_dockerfile,
    validate_worker_requirements,
)


CONTRACT = Path("INDEXALERT_KRX_HISTORICAL_WORKER_DEPLOYMENT_CONTRACT.json")
DOCKERFILE = Path("Dockerfile.krx-historical-worker")
REQUIREMENTS = Path("requirements-krx-historical-worker.txt")


def _data():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_committed_worker_deployment_is_preflight_only_and_nonexecuting():
    out = validate_files()
    assert out["contract"]["valid"] is True
    assert out["contract"]["preflight_only_by_default"] is True
    assert out["contract"]["dedicated_volume_required"] is True
    assert out["contract"]["service_creation_authorized"] is False
    assert out["contract"]["volume_creation_or_attachment_authorized"] is False
    assert out["contract"]["bulk_network_execution_authorized_by_user"] is False
    assert out["requirements"]["pinned_client"] is True
    assert out["requirements"]["pinned_client_commit"] == "e6ebac9b71482db127348d8a08ebc6743aa3b50e"
    assert out["dockerfile"]["default_mode"] == "PREFLIGHT_ONLY"
    assert out["dockerfile"]["public_port_exposed"] is False
    assert out["dockerfile"]["bulk_execute_in_default_cmd"] is False
    data = _data()
    assert data["start_contract"]["execute_identity_standard_code_binding_command"].endswith(
        "--execute-identity-standard-code-binding"
    )
    assert data["start_contract"][
        "execute_identity_standard_code_binding_forbidden_until_user_bulk_approval"
    ] is True
    assert data["start_contract"]["prepare_per_security_history_command"].endswith(
        "--prepare-per-security-history"
    )
    assert data["start_contract"]["prepare_per_security_history_network_request_attempted"] is False
    assert data["start_contract"]["prepare_per_security_history_bulk_consent_required"] is False
    assert data["start_contract"]["prepare_per_security_history_requires_completed_identity_binding"] is True
    assert data["start_contract"]["prepare_per_security_history_requires_dedicated_worker_private_volume"] is True
    assert data["start_contract"]["prepare_status_economics_command"].endswith(
        "--prepare-status-economics"
    )
    assert data["start_contract"]["prepare_status_economics_network_request_attempted"] is False
    assert data["start_contract"]["prepare_status_economics_bulk_consent_required"] is False
    assert data["start_contract"]["prepare_status_economics_requires_completed_per_security_history"] is True
    assert data["start_contract"]["prepare_status_economics_exact_realized_economics_claim_allowed"] is False
    assert data["start_contract"]["execute_status_economics_command"].endswith(
        "--execute-status-economics"
    )
    assert data["start_contract"]["execute_status_economics_forbidden_until_user_bulk_approval"] is True
    assert data["start_contract"]["execute_status_economics_requires_prepared_private_manifest"] is True
    assert data["start_contract"]["execute_status_economics_requires_completed_per_security_history"] is True
    assert data["start_contract"]["execute_status_economics_exact_realized_economics_claim_allowed"] is False
    assert data["start_contract"]["execute_per_security_history_command"].endswith(
        "--execute-per-security-history"
    )
    assert data["start_contract"]["execute_per_security_history_forbidden_until_user_bulk_approval"] is True
    assert data["start_contract"]["execute_per_security_history_requires_prepared_private_manifest"] is True
    assert data["start_contract"]["execute_per_security_history_requires_completed_identity_binding"] is True
    assert data["start_contract"]["prepare_status_economics_command"].endswith(
        "--prepare-status-economics"
    )
    assert data["start_contract"]["prepare_status_economics_network_request_attempted"] is False
    assert data["start_contract"]["prepare_status_economics_bulk_consent_required"] is False
    assert data["start_contract"]["prepare_status_economics_requires_completed_per_security_history"] is True
    assert data["start_contract"]["prepare_status_economics_exact_realized_economics_claim_allowed"] is False


def test_worker_deployment_cannot_self_authorize_cloud_or_bulk_actions():
    for key in (
        "service_creation_authorized",
        "volume_creation_or_attachment_authorized",
        "bulk_network_execution_authorized_by_user",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        data = _data()
        data["authority"][key] = True
        with pytest.raises(KRXHistoricalWorkerDeploymentError, match="illegally true"):
            validate_deployment_contract(data)


def test_volume_must_be_dedicated_and_under_data():
    data = _data()
    data["required_volume"]["sharing_with_public_runtime_forbidden"] = False
    with pytest.raises(KRXHistoricalWorkerDeploymentError, match="sharing prohibition"):
        validate_deployment_contract(data)

    data = _data()
    data["required_volume"]["raw_root"] = "/tmp/krx"
    with pytest.raises(KRXHistoricalWorkerDeploymentError, match="raw root drift"):
        validate_deployment_contract(data)


def test_dockerfile_cannot_default_to_network_execution_or_bake_secrets():
    text = DOCKERFILE.read_text(encoding="utf-8")
    bad = text.replace(
        'CMD ["python", "research_v1_krx_historical_worker_entrypoint.py"]',
        'CMD ["python", "research_v1_krx_historical_worker_entrypoint.py", "--execute-identity-seed"]',
    )
    with pytest.raises(KRXHistoricalWorkerDeploymentError, match="preflight-only|must not execute"):
        validate_worker_dockerfile(bad)

    bad = text + "\nENV KRX_ID=forbidden\n"
    with pytest.raises(KRXHistoricalWorkerDeploymentError, match="forbidden"):
        validate_worker_dockerfile(bad)


def test_bulk_consent_must_be_absent_during_initial_deployment():
    data = _data()
    data["execution_consent"]["must_be_absent_during_initial_preflight_deployment"] = False
    with pytest.raises(KRXHistoricalWorkerDeploymentError, match="consent absence"):
        validate_deployment_contract(data)


def test_worker_requirements_must_pin_exact_krx_client_commit():
    text = REQUIREMENTS.read_text(encoding="utf-8")
    out = validate_worker_requirements(text)
    assert out["valid"] is True
    assert out["pinned_client_commit"] == "e6ebac9b71482db127348d8a08ebc6743aa3b50e"

    bad = text.replace(
        "e6ebac9b71482db127348d8a08ebc6743aa3b50e",
        "0000000000000000000000000000000000000000",
    )
    with pytest.raises(KRXHistoricalWorkerDeploymentError, match="pinned KRX client"):
        validate_worker_requirements(bad)
