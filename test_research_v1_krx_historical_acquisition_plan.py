import json
from pathlib import Path

import pytest

from research_v1_krx_historical_acquisition_plan import (
    KRXHistoricalPlanError,
    validate_file,
    validate_plan,
)

PATH=Path("INDEXALERT_KRX_HISTORICAL_ACQUISITION_PLAN.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_plan_v2_is_frozen_stable_identity_and_nonexecuting():
    out=validate_file()
    assert out["valid"] is True
    assert out["plan_id"] == "INDEXALERT-KRX-HIST-ACQ-v3"
    assert len(out["plan_fingerprint_sha256"]) == 64
    assert out["rights_to_acquire"] is True
    assert out["network_execution_authorized"] is False
    assert out["gate_c_closed"] is False
    assert out["gate_d_closed"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_v1_was_superseded_before_bulk_execution():
    data=_data()
    assert data["supersedes_plan_id"] == "INDEXALERT-KRX-HIST-ACQ-v1"
    assert data["superseded_before_any_bulk_network_execution"] is True


def test_plan_cannot_self_authorize_bulk_execution():
    data=_data()
    data["authority"]["bulk_network_execution_authorized_by_user"]=True
    with pytest.raises(KRXHistoricalPlanError,match="illegally true"):
        validate_plan(data)


def test_stable_standard_code_identity_rules_are_mandatory():
    data=_data()
    data["phases"]["identity_seed"]["identity_rules"]["standard_code_required_for_every_episode"]=False
    with pytest.raises(KRXHistoricalPlanError,match="standard-code requirement lost"):
        validate_plan(data)

    data=_data()
    data["phases"]["identity_seed"]["dynamic_standard_code_snapshots"]["no_fallback_from_later_snapshot"]=False
    with pytest.raises(KRXHistoricalPlanError,match="later-snapshot fallback guard lost"):
        validate_plan(data)


def test_research_window_halt_chunking_and_investor_pit_are_frozen():
    data=_data()
    data["research_required_period"]["start"]="2014-01-01"
    with pytest.raises(KRXHistoricalPlanError,match="research start drift"):
        validate_plan(data)

    data=_data()
    data["phases"]["status_history"]["trading_halt"]["route_max_period_days"]=731
    with pytest.raises(KRXHistoricalPlanError,match="halt max-period drift"):
        validate_plan(data)

    data=_data()
    data["phases"]["investor_flow_history"]["pit_publication_floor"]="15:30 Asia/Seoul"
    with pytest.raises(KRXHistoricalPlanError,match="PIT floor drift"):
        validate_plan(data)
