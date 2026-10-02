import json
from pathlib import Path

import pytest

from research_v1_krx_historical_railway_readiness import (
    KRXHistoricalRailwayReadinessError,
    validate_file,
    validate_readiness,
)

PATH = Path("INDEXALERT_KRX_HISTORICAL_RAILWAY_READINESS_EVIDENCE.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_railway_readiness_is_provisioned_but_not_bulk_ready():
    out = validate_file()
    assert out["valid"] is True
    assert out["evidence_stage"] == "PREFLIGHT_PROVISIONED"
    assert out["worker_service_exists"] is True
    assert out["dedicated_worker_volume_exists"] is True
    assert out["worker_only_secrets_configured"] is True
    assert out["preflight_infrastructure_ready"] is True
    assert out["infrastructure_ready_for_bulk_execution"] is False
    assert out["service_creation_authorized"] is True
    assert out["volume_creation_or_attachment_authorized"] is True
    assert out["worker_secret_configuration_authorized"] is False
    assert out["bulk_network_execution_authorized_by_user"] is False
    assert out["expected_scope_network_execution_authorized_by_user"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_production_runtime_volume_cannot_be_reused():
    data = _data()
    data["production_runtime_volume_reuse_allowed"] = True
    with pytest.raises(KRXHistoricalRailwayReadinessError, match="reuse illegally allowed"):
        validate_readiness(data)


def test_preflight_evidence_requires_worker_and_dedicated_volume():
    data = _data()
    data["worker_service_exists"] = False
    with pytest.raises(KRXHistoricalRailwayReadinessError, match="requires worker service"):
        validate_readiness(data)

    data = _data()
    data["dedicated_worker_volume_exists"] = False
    with pytest.raises(KRXHistoricalRailwayReadinessError, match="requires dedicated worker volume"):
        validate_readiness(data)

    data = _data()
    data["observed_services"] = [
        x for x in data["observed_services"]
        if x.get("name") != "indexalert-krx-historical-worker"
    ]
    with pytest.raises(KRXHistoricalRailwayReadinessError, match="worker observation missing"):
        validate_readiness(data)


def test_preflight_evidence_cannot_authorize_network_execution():
    for key in (
        "worker_secret_configuration_authorized",
        "bulk_network_execution_authorized_by_user",
        "expected_scope_network_execution_authorized_by_user",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        data = _data()
        data["authority"][key] = True
        with pytest.raises(KRXHistoricalRailwayReadinessError, match="illegally true"):
            validate_readiness(data)


def test_secret_ready_snapshot_requires_all_three_presence_flags_and_absent_bulk_consent():
    data = _data()
    req = data["required_worker"]
    assert set(req["required_secret_names"]) == {"KRX_ID", "KRX_PW", "KRX_AUTH_KEY"}
    assert req["required_nonsecret_variables"]["KRX_PRIVATE_RAW_DIR"] == "/data/indexalert/krx-historical-v3"
    assert req["required_nonsecret_variables"]["INDEXALERT_KRX_HIST_WORKER_ROLE"] == "DEDICATED_ONE_SHOT"
    assert req["bulk_consent_env"] == "KRX_HISTORICAL_ACQUISITION_CONSENT"
    assert req["bulk_consent_must_be_absent_initially"] is True
    assert data["worker_only_secrets_configured"] is True
    preflight = data["runtime_preflight"]
    assert preflight["krx_id_present"] is True
    assert preflight["krx_pw_present"] is True
    assert preflight["krx_openapi_auth_key_present"] is True
    assert preflight["explicit_execution_consent_present"] is False
    assert preflight["network_request_attempted"] is False


def test_secret_ready_snapshot_fails_closed_on_incomplete_secret_evidence():
    data = _data()
    data["runtime_preflight"]["krx_pw_present"] = False
    with pytest.raises(KRXHistoricalRailwayReadinessError, match="secret presence evidence incomplete"):
        validate_readiness(data)


def test_worker_shape_remains_isolated_and_one_shot():
    data = _data()
    worker = next(x for x in data["observed_services"] if x.get("name") == "indexalert-krx-historical-worker")
    assert worker["volume_mount"] == "/data"
    assert worker["public_domain"] is False
    assert worker["cron"] is False
    assert worker["restart_policy"] == "NEVER"
    assert worker["dockerfile"] == "Dockerfile.krx-historical-worker"
    assert worker["start_command"] == "python research_v1_krx_historical_worker_entrypoint.py"
    assert worker["corrected_preflight_deployment_status"] == "SUCCESS"
