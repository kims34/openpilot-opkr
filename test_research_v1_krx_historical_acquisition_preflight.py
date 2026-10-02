from research_v1_krx_historical_acquisition_preflight import (
    CONSENT_SENTINEL,
    evaluate_historical_acquisition_preflight,
)


def test_bulk_preflight_blocks_without_exact_execution_consent():
    out=evaluate_historical_acquisition_preflight(
        environment={"KRX_ID":"present","KRX_PW":"present"}
    )
    assert out["rights_authorized"] is True
    assert out["historical_acquisition_network_execution_authorized"] is False
    assert out["network_request_attempted"] is False
    assert out["missing_requirements"] == ["EXPLICIT_HISTORICAL_ACQUISITION_EXECUTION_CONSENT"]
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_bulk_preflight_becomes_ready_only_for_exact_sentinel():
    out=evaluate_historical_acquisition_preflight(
        environment={
            "KRX_ID":"present",
            "KRX_PW":"present",
            "KRX_HISTORICAL_ACQUISITION_CONSENT":CONSENT_SENTINEL,
        }
    )
    assert out["historical_acquisition_network_execution_authorized"] is True
    assert out["network_request_attempted"] is False
    assert out["missing_requirements"] == []


def test_bulk_preflight_rejects_near_miss_consent():
    out=evaluate_historical_acquisition_preflight(
        environment={
            "KRX_ID":"present",
            "KRX_PW":"present",
            "KRX_HISTORICAL_ACQUISITION_CONSENT":"yes",
        }
    )
    assert out["historical_acquisition_network_execution_authorized"] is False
    assert "EXPLICIT_HISTORICAL_ACQUISITION_EXECUTION_CONSENT" in out["missing_requirements"]
