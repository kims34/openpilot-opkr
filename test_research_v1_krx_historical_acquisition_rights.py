import json
from pathlib import Path

import pytest

from research_v1_krx_historical_acquisition_rights import (
    KRXHistoricalRightsError,
    validate_file,
    validate_historical_rights,
)

PATH = Path("INDEXALERT_KRX_PERMISSION_REPLY_EVIDENCE.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_current_permission_grants_history_rights_not_execution():
    out = validate_file()
    assert out["valid"] is True
    assert out["rights_authorized"] is True
    assert out["high_frequency_collection_authorized"] is True
    assert out["full_historical_download_rights_authorized"] is True
    assert out["redistribution_authorized"] is False
    assert out["external_sale_authorized"] is False
    assert out["project_network_execution_authorized"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_permission_record_cannot_self_authorize_execution():
    data = _data()
    data["project_classification"]["bulk_historical_network_execution_authorized_by_user"] = True
    with pytest.raises(Exception):
        validate_historical_rights(data)
