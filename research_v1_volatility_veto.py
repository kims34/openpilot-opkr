"""No-backfill volatility risk-veto sensitivity for purged PIT candidates.

For every model, the original decision-time top-K is frozen first.  The risk
veto may only REMOVE a high-volatility name from that set; it may never promote
rank 4+ merely to refill a slot.  This matches IndexAlert's 0..3 admission rule.

The same prespecified caps are applied to three simple candidates:
- barrier-label market-context logistic,
- PIT-safe path-context logistic,
- fixed-horizon positive-net logistic.
No hyperparameter search is introduced.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from research_v1_context import add_context
from research_v1_fixed_horizon_label import add_fixed_horizon_target, purged_predict as fixed_horizon_predict
from research_v1_holdaware import evaluate_topk_only
from research_v1_path_context import PATH_CONTEXT_FEATURES, add_path_features, purged_predict as path_predict
from research_v1_pit_run_purged import _walk_forward_pit
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel

VOL_CAPS = [1.0, 0.90, 0.80]


def view(result):
    ex = result.get("executable_set", {})
    port = result.get("portfolio", {})
    return {
        "trades": int(ex.get("trades") or 0),
        "mean_gross_return": float(ex.get("mean_gross_return") or 0.0),
        "mean_cost_return": float(ex.get("mean_cost_return") or 0.0),
        "mean_net_return": float(ex.get("mean_net_return") or 0.0),
        "profit_factor": float(ex.get("profit_factor") or 0.0),
        "expected_shortfall_95": float(ex.get("trade_expected_shortfall_95") or 0.0),
        "cluster_low": float(ex.get("cluster_bootstrap_95_low") or 0.0),
        "cluster_high": float(ex.get("cluster_bootstrap_95_high") or 0.0),
        "total_return": float(port.get("total_return") or 0.0),
        "max_drawdown": float(port.get("max_drawdown") or 0.0),
    }


def freeze_original_topk(pred: pd.DataFrame, top_k: int) -> pd.DataFrame:
    return (
        pred.sort_values(["decision_date", "score"], ascending=[True, False])
        .groupby("decision_date", group_keys=False)
        .head(top_k)
        .copy()
    )


def evaluate_veto_family(name, pred, risk, record_map, raw, horizon, top_k):
    frozen = freeze_original_topk(pred, top_k)
    frozen = frozen.merge(risk, on=["decision_date", "symbol"], how="left", validate="one_to_one")
    all_test_dates = int(pred["decision_date"].nunique())
    rows = []
    for cap in VOL_CAPS:
        eligible = frozen[frozen["vol20_rank"].fillna(1.0) <= cap].copy()
        result, selected, _ = evaluate_topk_only(eligible, record_map, raw, horizon, top_k)
        row = {
            "model": name,
            "max_vol20_rank_allowed": cap,
            "original_topk_rows": int(len(frozen)),
            "rows_after_veto": int(len(eligible)),
            "vetoed_original_topk_rows": int(len(frozen) - len(eligible)),
            "selected_rows": int(len(selected)),
            "all_test_dates": all_test_dates,
            **view(result),
        }
        rows.append(row)
    base = rows[0]
    for row in rows:
        row["delta_vs_no_veto"] = {
            "mean_net_return": row["mean_net_return"] - base["mean_net_return"],
            "profit_factor": row["profit_factor"] - base["profit_factor"],
            "expected_shortfall_95": row["expected_shortfall_95"] - base["expected_shortfall_95"],
            "max_drawdown": row["max_drawdown"] - base["max_drawdown"],
            "trades": row["trades"] - base["trades"],
        }
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit")
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_v1")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_vol_veto")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--target", type=float, default=0.04)
    ap.add_argument("--stop", type=float, default=-0.025)
    ap.add_argument("--participation", type=float, default=0.0005)
    ap.add_argument("--train-days", type=int, default=200)
    ap.add_argument("--test-days", type=int, default=40)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    frame, record_map, diag, meta = load_or_build(
        raw, Path(args.supervised_cache),
        horizon=args.horizon, target_return=args.target, stop_return=args.stop,
        participation=args.participation, commission_round_trip_bps=3.0,
    )
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    context = add_context(frame)
    risk = frame[["decision_date", "symbol", "vol20_rank"]].copy()

    barrier_pred = _walk_forward_pit(
        context, "logistic_context", args.train_days, args.test_days,
        context=True, purge_days=args.horizon,
    )

    enriched = add_path_features(raw, context)
    path_pred = path_predict(
        enriched, PATH_CONTEXT_FEATURES,
        train_days=args.train_days, test_days=args.test_days,
        purge_days=args.horizon, model_name="logistic_path_context",
    )

    fixed_frame = add_fixed_horizon_target(raw, context, record_map, args.horizon)
    fixed_pred = fixed_horizon_predict(
        fixed_frame, target_col="fh_positive_net", kind="logistic",
        train_days=args.train_days, test_days=args.test_days, purge_days=args.horizon,
    )

    families = {
        "barrier_context": barrier_pred,
        "path_context": path_pred,
        "fixed_horizon_logistic": fixed_pred,
    }
    results = {
        name: evaluate_veto_family(name, pred, risk, record_map, raw, args.horizon, args.top_k)
        for name, pred in families.items()
    }

    report = {
        "evaluation_stage": "PIT_PRELIMINARY_PURGED_VOLATILITY_RISK_VETO_NO_BACKFILL",
        "model_scores_held_fixed": True,
        "original_topk_frozen_before_veto": True,
        "backfill_after_veto": False,
        "veto_caps_prespecified": VOL_CAPS,
        "hyperparameter_search": False,
        "supervised_cache": meta,
        "label_diagnostics": diag,
        "results_by_model": results,
        "interpretation": (
            "The veto can only remove an original top-K candidate. It cannot promote lower-ranked names. "
            "A cap is useful only if tail/MDD improve without destroying net utility or reducing coverage to a trivial level."
        ),
    }
    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    flat = [row for rows in results.values() for row in rows]
    pd.DataFrame(flat).to_csv(out / "comparison.csv", index=False)
    print("VOLATILITY_VETO=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
