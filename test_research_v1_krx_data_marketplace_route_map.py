import copy
import json
from pathlib import Path

import pytest

from research_v1_krx_data_marketplace_route_map import (
    KRXRouteMapError,
    validate_file,
    validate_route_map,
)


PATH = Path("INDEXALERT_KRX_DATA_MARKETPLACE_ROUTE_MAP.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_route_map_validates_and_never_grants_authority():
    out = validate_file()
    assert out["valid"] is True
    assert out["pinned_client_commit"] == "e6ebac9b71482db127348d8a08ebc6743aa3b50e"
    assert out["route_count"] == 5
    assert out["gate_a_pass"] is False
    assert out["gate_b_pass"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_route_or_commit_drift_is_rejected():
    data = _data()
    data["pinned_client"]["commit"] = "a" * 40
    with pytest.raises(KRXRouteMapError, match="pinned client commit drift"):
        validate_route_map(data)

    data = _data()
    data["routes"]["trading_halt"]["bld"] = "dbms/MDC/STAT/issue/WRONG"
    with pytest.raises(KRXRouteMapError, match="trading_halt bld drift"):
        validate_route_map(data)


def test_cleanup_route_cannot_invent_historical_window_semantics():
    data = _data()
    data["routes"]["cleanup_trading"]["historical_date_filter_verified"] = True
    with pytest.raises(KRXRouteMapError, match="historical-window semantics illegally promoted"):
        validate_route_map(data)

    data = _data()
    data["routes"]["cleanup_trading"]["required"] = ["strtDd", "endDd"]
    with pytest.raises(KRXRouteMapError, match="cleanup request contract drift"):
        validate_route_map(data)


def test_authority_escalation_is_rejected():
    data = _data()
    data["authority"]["gate_a_pass"] = True
    with pytest.raises(KRXRouteMapError, match="gate_a_pass illegally true"):
        validate_route_map(data)


def test_investor_publication_floor_cannot_drift():
    data = _data()
    data["routes"]["investor_flow_daily"]["pit_publication_floor"] = "15:30 Asia/Seoul"
    with pytest.raises(KRXRouteMapError, match="investor PIT floor drift"):
        validate_route_map(data)
