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


def test_committed_railway_readiness_is_not_bulk_ready():
    out = validate_file()
    assert out["valid"] is True
    assert out["worker_service_exists"] is False
    assert out["dedicated_worker_volume_exists"] is False
    assert out["infrastructure_ready_for_bulk_execution"] is False
    assert out["service_creation_authorized"] is False
    assert out["volume_creation_or_attachment_authorized"] is False
    assert out["bulk_network_execution_authorized_by_user"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_production_runtime_volume_cannot_be_reused():
    data = _data()
    data["production_runtime_volume_reuse_allowed"] = True
    with pytest.raises(KRXHistoricalRailwayReadinessError, match="reuse illegally allowed"):
        validate_readiness(data)


def test_worker_or_volume_presence_cannot_be_fabricated():
    data = _data()
    data["worker_service_exists"] = True
    with pytest.raises(KRXHistoricalRailwayReadinessError, match="cannot be claimed present"):
        validate_readiness(data)

    data = _data()
    data["dedicated_worker_volume_exists"] = True
    with pytest.raises(KRXHistoricalRailwayReadinessError, match="cannot be claimed present"):
        validate_readiness(data)


def test_read_only_audit_cannot_authorize_creation_or_execution():
    data = _data()
    data["authority"]["service_creation_authorized"] = True
    with pytest.raises(KRXHistoricalRailwayReadinessError, match="illegally true"):
        validate_readiness(data)

    data = _data()
    data["authority"]["bulk_network_execution_authorized_by_user"] = True
    with pytest.raises(KRXHistoricalRailwayReadinessError, match="illegally true"):
        validate_readiness(data)
