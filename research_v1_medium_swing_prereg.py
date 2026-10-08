"""Fail-closed integrity validator for M20 fundamental-drift preregistration.

This is research governance only. It cannot run the empirical strategy, mutate
Champion/Core, reuse the consumed v1 holdout, delay/alter Tiny Live, or authorize orders.
"""
from __future__ import annotations

import json
from pathlib import Path

PATH = Path("INDEXALERT_MEDIUM_SWING_M20_PREREG.json")


def load_protocol(path: Path = PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_protocol(p: dict) -> dict:
    blockers: list[str] = []
    exact = {
        "schema_version": "1.0",
        "trial_id": "EXP-2026-10-08-M20-FUNDAMENTAL-DRIFT-01",
        "state": "PREREGISTERED_DATA_GATED",
        "terminal_disposition": "NEW EVIDENCE REQUIRED",
        "strategy_family": "INDEPENDENT_MEDIUM_SWING_FUNDAMENTAL_DRIFT",
        "primary_horizon_sessions": 20,
        "horizon_sweep_forbidden": True,
        "primary_entry": "next_eligible_regular_session_open_after_admissible_decision_close",
        "primary_exit": "DPLUS20_CLOSE",
        "dynamic_stop_takeprofit_in_v1": False,
        "signal_formula": "(operating_profit_q - operating_profit_q_minus_4) / decision_time_market_cap",
        "distinct_from_rejected_h10": True,
        "rejected_h10_retune_forbidden": True,
        "blend_deferred_until_medium_edge_established": True,
        "consumed_project_v1_holdout_forbidden": True,
        "tiny_live_path_must_not_be_delayed": True,
        "champion_core_change_allowed": False,
        "operating_code_change_allowed": False,
        "live_order_authorized": False,
    }
    for key, value in exact.items():
        if p.get(key) != value:
            blockers.append("FROZEN_FIELD_MISMATCH:" + key)

    model = p.get("model")
    if type(model) is not dict or model != {
        "family": "Ridge",
        "alpha": 1.0,
        "selection_conditional_quantiles": [0.25, 0.5, 0.75],
        "admission": "NetEV_low_gt_0",
        "top_k": 3,
        "rank4plus_backfill": False,
        "no_trade_valid": True,
    }:
        blockers.append("MODEL_CONTRACT_MISMATCH")

    wf = p.get("walk_forward")
    if type(wf) is not dict or wf != {
        "train_sessions": 504,
        "calibration_sessions": 126,
        "test_sessions": 126,
        "purge_sessions": 20,
        "embargo_sessions": 20,
    }:
        blockers.append("WALK_FORWARD_CONTRACT_MISMATCH")

    cpcv = p.get("cpcv")
    if type(cpcv) is not dict or cpcv != {
        "groups": 6,
        "test_groups_per_case": 2,
        "calibration_groups_per_case": 1,
        "train_groups_per_case": 3,
        "secondary_diagnostic_only": True,
    }:
        blockers.append("CPCV_CONTRACT_MISMATCH")

    required = set(p.get("required_new_pit_evidence") or [])
    expected = {
        "official_opendart_disclosure_identity_and_corp_to_krx_mapping",
        "pit_safe_disclosure_availability",
        "quarterly_operating_profit_and_q_minus_4_lineage",
        "decision_time_market_cap",
        "krx_security_status_tradability_and_affected_position_economics",
    }
    if required != expected:
        blockers.append("PIT_EVIDENCE_REQUIREMENTS_MISMATCH")

    forbidden = p.get("additional_signal_families_forbidden")
    if forbidden != ["analyst_consensus", "news_sentiment", "investor_flow", "alternate_earnings_metric"]:
        blockers.append("SIGNAL_FAMILY_BOUNDARY_MISMATCH")

    cost = p.get("cost_policy")
    if type(cost) is not dict:
        blockers.append("COST_POLICY_REQUIRED")
    else:
        if cost.get("date_aware_statutory_tax") is not True:
            blockers.append("DATE_AWARE_TAX_REQUIRED")
        if cost.get("commission_allowance") is not True:
            blockers.append("COMMISSION_REQUIRED")
        if cost.get("spread_impact_allowance") is not True:
            blockers.append("SPREAD_IMPACT_REQUIRED")
        if cost.get("participation_of_adv_reference") != 0.0005:
            blockers.append("PARTICIPATION_REFERENCE_MISMATCH")
        if cost.get("two_x_cost_stress_required") is not True:
            blockers.append("TWO_X_COST_STRESS_REQUIRED")

    return {
        "valid": not blockers,
        "blockers": blockers,
        "performance_run_authorized": False,
        "holdout_authorized": False,
        "champion_change_allowed": False,
        "tiny_live_path_change_allowed": False,
        "live_order_authorized": False,
    }


if __name__ == "__main__":
    print(json.dumps(validate_protocol(load_protocol()), sort_keys=True))
