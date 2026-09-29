"""CA-safe daily path-feature challenger for long-history Distributional NetEV.

Development-only, one prespecified feature-family test.  The mean model,
selection-conditioned q25/q50/q75 calibration, train/cal/test windows, five-day
purge, NetEV>0 admission, strict original Top3 and no-backfill policy are
unchanged.  Only decision-close path information is added.

Corporate-action safety:
- opening gap uses KRX base price reconstructed as close/(1+FLUC_RT), not the
  prior raw close;
- intraday return/range/close-location are same-session price ratios;
- value surprise uses only current and prior trading values.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_distributional_long_history import _evaluate_selected
from research_v1_distributional_netev import _fixed_record_map
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_selected_calibration import (
    _evaluate_with_runner,
    selected_calibration_walk_forward,
)
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel

CA_PATH_FEATURES = [
    "gap1_ca",
    "intraday_ret1",
    "range1",
    "close_location1",
    "value_surprise20_log",
    "gap1_ca_rank",
    "intraday_ret1_rank",
    "range1_rank",
    "value_surprise20_rank",
]
PATH_CONTEXT_FEATURES = CONTEXT_FEATURES + CA_PATH_FEATURES


def add_ca_safe_path_features(raw: pd.DataFrame, supervised: pd.DataFrame) -> pd.DataFrame:
    required = {
        "decision_date", "symbol", "open", "high", "low", "close", "value",
        "krx_change_return",
    }
    missing = required.difference(raw.columns)
    if missing:
        raise ValueError(f"CA-safe path features require {sorted(missing)}")

    x = raw.copy().sort_values(["symbol", "decision_date"]).reset_index(drop=True)
    g = x.groupby("symbol", sort=False)
    x["prior_value20"] = g["value"].transform(
        lambda s: s.shift(1).rolling(20, min_periods=20).median()
    )

    krx_ret = pd.to_numeric(x["krx_change_return"], errors="coerce")
    denom = 1.0 + krx_ret
    x["krx_base_price"] = np.where(denom > 0, x["close"].astype(float) / denom, np.nan)
    x["gap1_ca"] = x["open"].astype(float) / x["krx_base_price"] - 1.0
    x["intraday_ret1"] = x["close"].astype(float) / x["open"].astype(float) - 1.0
    x["range1"] = x["high"].astype(float) / x["low"].astype(float) - 1.0
    day_range = x["high"].astype(float) - x["low"].astype(float)
    x["close_location1"] = np.where(
        day_range > 0,
        (x["close"].astype(float) - x["low"].astype(float)) / day_range,
        0.5,
    )
    ratio = (x["value"].astype(float) + 1.0) / (x["prior_value20"].astype(float) + 1.0)
    x["value_surprise20_log"] = np.log(ratio.clip(lower=1e-8))

    for col, rank_name in [
        ("gap1_ca", "gap1_ca_rank"),
        ("intraday_ret1", "intraday_ret1_rank"),
        ("range1", "range1_rank"),
        ("value_surprise20_log", "value_surprise20_rank"),
    ]:
        x[rank_name] = x.groupby("decision_date")[col].rank(pct=True)

    keep = ["decision_date", "symbol"] + CA_PATH_FEATURES
    return supervised.merge(x[keep], on=["decision_date", "symbol"], how="left", validate="one_to_one")


def _current_snapshot(selected: pd.DataFrame, all_dates: list[pd.Timestamp], sessions: int = 504) -> dict:
    if not all_dates:
        return {"sessions": 0, "records": 0}
    recent = all_dates[-min(int(sessions), len(all_dates)):]
    start = recent[0].date()
    end = recent[-1].date()
    if selected.empty:
        return {"start": str(start), "end": str(end), "sessions": len(recent), "records": 0}
    d = pd.to_datetime(selected["decision_date"]).dt.date
    sub = selected[(d >= start) & (d <= end)].copy()
    if sub.empty:
        return {"start": str(start), "end": str(end), "sessions": len(recent), "records": 0}
    net = pd.to_numeric(sub["fh_net_return"], errors="coerce").dropna()
    gains = float(net[net > 0].sum())
    losses = float(-net[net < 0].sum())
    return {
        "start": str(start),
        "end": str(end),
        "sessions": len(recent),
        "records": int(len(net)),
        "mean_net_return": float(net.mean()) if len(net) else 0.0,
        "positive_rate": float((net > 0).mean()) if len(net) else 0.0,
        "profit_factor": float(gains / losses) if losses > 0 else (float("inf") if gains > 0 else 0.0),
    }


def _promotion_view(result: dict) -> dict:
    gated = result["market_eligibility_overlay"]
    m = gated["metrics"]
    extreme = gated["extreme_day_dependency"].get("remove_best_days", {})
    best5 = extreme.get("5", {}).get("metrics", {})
    return {
        "trades": int(m.get("trades", 0)),
        "mean_net_return": float(m.get("mean_net_return", 0.0)),
        "profit_factor": float(m.get("profit_factor", 0.0)),
        "cluster_bootstrap_95_low": float(m.get("cluster_bootstrap_95_low", 0.0)),
        "expected_shortfall_95": float(m.get("trade_expected_shortfall_95", 0.0)),
        "max_drawdown": float(gated.get("portfolio", {}).get("max_drawdown", 0.0)),
        "best5_removed_mean_net_return": float(best5.get("mean_net_return", 0.0)),
        "best5_removed_profit_factor": float(best5.get("profit_factor", 0.0)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit_long")
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_long_v3_ca_fp")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_distributional_path_ca")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--train-days", type=int, default=504)
    ap.add_argument("--cal-days", type=int, default=126)
    ap.add_argument("--test-days", type=int, default=126)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    frame, legacy_map, label_diag, cache_meta = load_or_build(
        raw,
        Path(args.supervised_cache),
        horizon=args.horizon,
        target_return=0.04,
        stop_return=-0.025,
        participation=0.0005,
        commission_round_trip_bps=3.0,
    )
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    context = add_context(frame)
    enriched = add_ca_safe_path_features(raw, context)
    z = add_fixed_horizon_target(raw, enriched, legacy_map, args.horizon)
    fixed_map = _fixed_record_map(z, args.horizon)

    runner = lambda zz, **kw: selected_calibration_walk_forward(zz, top_k=args.top_k, **kw)
    reference, _, reference_gate_selected = _evaluate_with_runner(
        z, fixed_map, raw,
        name="all_context_selection_conditioned_q25_reference",
        features=CONTEXT_FEATURES,
        runner=runner,
        train_days=args.train_days,
        cal_days=args.cal_days,
        test_days=args.test_days,
        horizon=args.horizon,
        top_k=args.top_k,
    )
    challenger, _, challenger_gate_selected = _evaluate_with_runner(
        z, fixed_map, raw,
        name="all_context_plus_ca_path_selection_conditioned_q25",
        features=PATH_CONTEXT_FEATURES,
        runner=runner,
        train_days=args.train_days,
        cal_days=args.cal_days,
        test_days=args.test_days,
        horizon=args.horizon,
        top_k=args.top_k,
    )

    dates = sorted(pd.Timestamp(x) for x in z["decision_date"].drop_duplicates())
    ref_view = _promotion_view(reference)
    ch_view = _promotion_view(challenger)
    ref_recent = _current_snapshot(reference_gate_selected, dates, 504)
    ch_recent = _current_snapshot(challenger_gate_selected, dates, 504)
    deltas = {k: ch_view[k] - ref_view[k] for k in ch_view}

    existing_promotion_rules_pass = bool(
        ch_view["mean_net_return"] > 0
        and ch_view["profit_factor"] > 1
        and ch_view["cluster_bootstrap_95_low"] > 0
        and ch_view["best5_removed_mean_net_return"] > 0
        and ch_view["best5_removed_profit_factor"] > 1
        and ch_recent.get("records", 0) > 0
        and ch_recent.get("mean_net_return", 0.0) > 0
    )

    report = {
        "evaluation_stage": "DEVELOPMENTAL_CA_SAFE_PATH_FEATURE_FAMILY_CHALLENGER_NOT_HOLDOUT",
        "history_start": str(raw["decision_date"].min().date()),
        "history_end": str(raw["decision_date"].max().date()),
        "protocol": {
            "model_changed": False,
            "quantile_levels_changed": False,
            "selection_calibration_changed": False,
            "admission_threshold_changed": False,
            "top_k_changed": False,
            "cost_model_changed": False,
            "only_change": "add_one_prespecified_CA_safe_daily_path_feature_family",
            "path_family_was_previously_motivated_in_development": True,
            "promotion_allowed": False,
        },
        "path_features": CA_PATH_FEATURES,
        "supervised_cache": cache_meta,
        "label_diagnostics": label_diag,
        "reference": reference,
        "challenger": challenger,
        "reference_promotion_view": ref_view,
        "challenger_promotion_view": ch_view,
        "delta_challenger_minus_reference": deltas,
        "reference_latest_504_sessions": ref_recent,
        "challenger_latest_504_sessions": ch_recent,
        "existing_promotion_rules_pass": existing_promotion_rules_pass,
        "classification": (
            "DEVELOPMENTAL_PATH_SIGNAL_WORTH_FURTHER_FALSIFICATION"
            if existing_promotion_rules_pass
            else "DEVELOPMENTAL_PATH_SIGNAL_NOT_PROMOTABLE"
        ),
        "guardrail": (
            "This family was motivated by earlier development results, so even a pass here is not sealed evidence. "
            "Do not tune path definitions, q25, TopK, costs or windows from this result."
        ),
    }

    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    reference_gate_selected.to_csv(out / "reference_normal_market_selected.csv", index=False)
    challenger_gate_selected.to_csv(out / "challenger_normal_market_selected.csv", index=False)
    print("CA_SAFE_PATH_CHALLENGER=" + json.dumps(report, ensure_ascii=False, default=str), flush=True)


if __name__ == "__main__":
    main()
