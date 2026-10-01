from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import pandas as pd
import pytest

from research_v1_execution_sufficiency_protocol import (
    validate_execution_sufficiency_protocol,
)
from research_v1_execution_sufficiency_assessment import (
    assess_execution_sufficiency,
    load_frozen_project_protocol,
)


ROOT = Path(__file__).parent


def _evidence(n=600, bad_slippage=False, over_capacity=False):
    rows = []
    start = datetime(2026, 10, 5, 0, 0, tzinfo=timezone.utc)
    for i in range(n):
        # At most three observations per decision date, consistent with frozen Top3.
        day = start + timedelta(days=i // 3)
        rec = day + timedelta(hours=1)
        submitted = rec + timedelta(seconds=1)
        open_px = 10000.0
        slip_bps = 25.0 if bad_slippage else 2.0
        fill_px = open_px * (1 + slip_bps / 10000)
        adv = 200_000_000.0 if not over_capacity else 100_000_000.0
        rows.append({
            "decision_date": day.date().isoformat(),
            "symbol": f"{i % 50:06d}",
            "side": "BUY",
            "recommendation_at": rec.isoformat(),
            "order_submitted_at": submitted.isoformat(),
            "requested_qty": 9,
            "filled_qty": 9,
            "first_fill_at": (submitted + timedelta(seconds=5)).isoformat(),
            "final_fill_at": (submitted + timedelta(seconds=5)).isoformat(),
            "avg_fill_price": fill_px,
            "reference_open": open_px,
            "markout_5m_price": fill_px * 1.0002,
            "markout_30m_price": fill_px * 1.0004,
            "markout_close_price": fill_px * 1.001,
            "source": "PROSPECTIVE_LIVE_EXECUTION_LOG",
            "ingested_at": (submitted + timedelta(seconds=10)).isoformat(),
            "observation_id": f"obs-{i}",
            "decision_policy_id": "INDEXALERT-H5-FROZEN-DECISION-v1",
            "execution_policy_id": "INDEXALERT-LIVE-EXECUTION-v1",
            "recommendation_expires_at": (rec + timedelta(seconds=60)).isoformat(),
            "order_outcome_at": (submitted + timedelta(seconds=5)).isoformat(),
            "order_expiry_at": (submitted + timedelta(seconds=60)).isoformat(),
            "reference_adv20_krw": adv,
            "capacity_reference_available_at": (rec - timedelta(seconds=1)).isoformat(),
            "entry_slippage_budget_bps": 5.0,
            "cost_budget_at": (rec - timedelta(seconds=1)).isoformat(),
            "modeled_fees_tax_bps": 3.0,
            "actual_fees_tax_bps": 2.9,
            "unknown_order_outcome": False,
            "reconciliation_resolved": True,
            "risk_limit_breach": False,
        })
    return pd.DataFrame(rows)


def test_frozen_project_protocol_document_hash_matches():
    p, doc = load_frozen_project_protocol(ROOT)
    out = validate_execution_sufficiency_protocol(p, protocol_document_text=doc)
    assert out["protocol_structurally_valid"] is True
    assert out["protocol_document_sha256_verified"] is True
    assert out["protocol"]["minimum_live_observations"] == 600
    assert out["protocol"]["minimum_distinct_decision_dates"] == 200
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_synthetic_fixture_can_exercise_pass_path_but_never_authorizes_promotion():
    p, doc = load_frozen_project_protocol(ROOT)
    out = assess_execution_sufficiency(_evidence(), p, protocol_document_text=doc)
    # Unit-test fixtures validate only the evaluator path; they are never project evidence.
    assert out["empirical_execution_sufficiency_assessed"] is True
    assert out["empirical_execution_blocker_closed"] is True
    assert out["failed_gates"] == []
    assert out["promotion_ready"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_insufficient_sample_fails_without_relaxing_thresholds():
    p, doc = load_frozen_project_protocol(ROOT)
    out = assess_execution_sufficiency(_evidence(300), p, protocol_document_text=doc)
    assert out["empirical_execution_blocker_closed"] is False
    assert "minimum_live_observations" in out["failed_gates"]
    assert "minimum_distinct_decision_dates" in out["failed_gates"]


def test_excess_slippage_and_capacity_breach_fail_closed():
    p, doc = load_frozen_project_protocol(ROOT)
    out = assess_execution_sufficiency(
        _evidence(bad_slippage=True), p, protocol_document_text=doc
    )
    assert out["empirical_execution_blocker_closed"] is False
    assert "mean_excess_slippage_ucb95" in out["failed_gates"]
    assert "slippage_budget_ratio_p95" in out["failed_gates"]

    out2 = assess_execution_sufficiency(
        _evidence(over_capacity=True), p, protocol_document_text=doc
    )
    assert out2["empirical_execution_blocker_closed"] is False
    assert "zero_capacity_breaches" in out2["failed_gates"]


def test_protocol_frozen_after_live_is_rejected():
    p, doc = load_frozen_project_protocol(ROOT)
    p = dict(p)
    p["frozen_at"] = "2027-01-01T00:00:00+00:00"
    with pytest.raises(Exception, match="before the first LIVE"):
        assess_execution_sufficiency(_evidence(), p, protocol_document_text=doc)
