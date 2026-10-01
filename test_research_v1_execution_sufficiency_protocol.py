from datetime import datetime, timezone
import json

import pytest

from research_v1_execution_sufficiency_protocol import (
    ExecutionSufficiencyProtocolError,
    parse_and_validate_execution_sufficiency_protocol_json,
    validate_execution_sufficiency_protocol,
)


FIRST_LIVE = datetime(2026, 10, 10, 0, 0, tzinfo=timezone.utc)


def _protocol(**overrides):
    # Test-only illustrative thresholds. They are not project promotion policy.
    base = {
        "schema_version": "1",
        "protocol_id": "TEST-EXEC-SUFFICIENCY-001",
        "frozen_at": "2026-10-01T00:00:00+00:00",
        "protocol_document_sha256": "a" * 64,
        "minimum_live_observations": 20,
        "minimum_distinct_decision_dates": 10,
        "minimum_filled_observations": 10,
        "minimum_no_fill_observations": 0,
        "minimum_partial_fill_observations": 0,
        "required_markout_horizons": ["5m", "30m", "close"],
        "require_slippage_evidence": True,
        "require_latency_evidence": True,
        "require_capacity_evidence": True,
        "require_tail_evidence": True,
        "rationale": "Test-only preregistration fixture; not a project threshold decision.",
    }
    base.update(overrides)
    return base


def test_valid_protocol_is_only_preregistration_not_sufficiency_evidence():
    out = validate_execution_sufficiency_protocol(
        _protocol(), first_live_recommendation_at=FIRST_LIVE
    )
    assert out["protocol_structurally_valid"] is True
    assert out["preregistered_before_first_live_observation"] is True
    assert len(out["protocol_fingerprint_sha256"]) == 64
    assert out["empirical_execution_sufficiency_assessed"] is False
    assert out["empirical_execution_blocker_closed"] is False
    assert out["promotion_ready"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_protocol_frozen_at_or_after_first_live_is_rejected_as_post_hoc():
    with pytest.raises(ExecutionSufficiencyProtocolError, match="before the first LIVE"):
        validate_execution_sufficiency_protocol(
            _protocol(frozen_at="2026-10-10T00:00:00+00:00"),
            first_live_recommendation_at=FIRST_LIVE,
        )
    with pytest.raises(ExecutionSufficiencyProtocolError, match="before the first LIVE"):
        validate_execution_sufficiency_protocol(
            _protocol(frozen_at="2026-10-11T00:00:00+00:00"),
            first_live_recommendation_at=FIRST_LIVE,
        )


def test_protocol_can_be_registered_before_any_live_observation_exists():
    out = validate_execution_sufficiency_protocol(_protocol())
    assert out["preregistered_before_first_live_observation"] is None
    assert out["first_live_recommendation_at"] is None
    assert out["empirical_execution_blocker_closed"] is False


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("minimum_live_observations", 0, "must be >= 1"),
        ("minimum_distinct_decision_dates", 21, "cannot exceed"),
        ("minimum_filled_observations", 21, "cannot exceed"),
        ("minimum_no_fill_observations", 21, "cannot exceed"),
        ("minimum_partial_fill_observations", 11, "cannot exceed"),
    ],
)
def test_incoherent_numeric_criteria_fail_closed(field, value, match):
    with pytest.raises(ExecutionSufficiencyProtocolError, match=match):
        validate_execution_sufficiency_protocol(_protocol(**{field: value}))


def test_required_evidence_dimensions_cannot_be_disabled():
    for field in [
        "require_slippage_evidence",
        "require_latency_evidence",
        "require_capacity_evidence",
        "require_tail_evidence",
    ]:
        with pytest.raises(ExecutionSufficiencyProtocolError, match="must be true"):
            validate_execution_sufficiency_protocol(_protocol(**{field: False}))


def test_markouts_must_include_5m_30m_and_close():
    with pytest.raises(ExecutionSufficiencyProtocolError, match="include 5m, 30m and close"):
        validate_execution_sufficiency_protocol(
            _protocol(required_markout_horizons=["5m", "close"])
        )
    with pytest.raises(ExecutionSufficiencyProtocolError, match="duplicates"):
        validate_execution_sufficiency_protocol(
            _protocol(required_markout_horizons=["5m", "30m", "close", "5m"])
        )


def test_protocol_document_hash_and_times_are_strict():
    with pytest.raises(ExecutionSufficiencyProtocolError, match="64-character"):
        validate_execution_sufficiency_protocol(
            _protocol(protocol_document_sha256="abc")
        )
    with pytest.raises(ExecutionSufficiencyProtocolError, match="timezone-aware"):
        validate_execution_sufficiency_protocol(
            _protocol(frozen_at="2026-10-01T00:00:00")
        )
    with pytest.raises(ExecutionSufficiencyProtocolError, match="timezone-aware"):
        validate_execution_sufficiency_protocol(
            _protocol(),
            first_live_recommendation_at=datetime(2026, 10, 10, 0, 0),
        )


def test_unknown_fields_are_rejected():
    p = _protocol()
    p["observed_best_fill_ratio"] = 0.99
    with pytest.raises(ExecutionSufficiencyProtocolError, match="unsupported fields"):
        validate_execution_sufficiency_protocol(p)


def test_json_parser_is_fail_closed():
    with pytest.raises(ExecutionSufficiencyProtocolError, match="not configured"):
        parse_and_validate_execution_sufficiency_protocol_json("")
    with pytest.raises(ExecutionSufficiencyProtocolError, match="must be an object"):
        parse_and_validate_execution_sufficiency_protocol_json("[]")

    out = parse_and_validate_execution_sufficiency_protocol_json(
        json.dumps(_protocol()),
        first_live_recommendation_at=FIRST_LIVE,
    )
    assert out["protocol_structurally_valid"] is True
    assert out["empirical_execution_blocker_closed"] is False
