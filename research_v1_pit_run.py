"""PIT-preliminary KOSPI tournament on a historical daily membership panel.

Core replay rules:
- every decision-time feature row can be ranked, including names that will later
  be unavailable at the next open;
- model training uses only rows whose future economic label is actually known;
- the original top-3 is fixed at decision time; a next-open no-fill leaves an
  empty slot and never promotes rank 4 with future knowledge;
- same trailing ADV20 bottom-20% exclusion is applied to every candidate model;
- direct-net-return models admit only positive predicted net return and at most
  the original top-3 eligible names;
- same-bar target/stop is conservative stop-first;
- post-entry missing bars remain as conservative stop-like outcomes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from research_v1_context import CONTEXT_FEATURES, _pipe as _context_pipe, add_context
from research_v1_core import date_cluster_bootstrap_mean, summarize
from research_v1_data_policy import dataset_status
from research_v1_holdaware import evaluate_topk_only
from research_v1_ml import (
    FEATURES,
    _classification_pipeline,
    _regression_pipeline,
    stateful_select_records,
)
from research_v1_pit_labels import make_pit_supervised
from research_v1_portfolio import simulate_portfolio, summary_dict
from run_research_v1 import load_panel


def _metric_block(records):
    m = summarize(records)
    point, lo, hi = date_cluster_bootstrap_mean(records) if records else (0.0, 0.0, 0.0)
    return {
        **m.__dict__,
        "cluster_bootstrap_mean_net_return": point,
        "cluster_bootstrap_95_low": lo,
        "cluster_bootstrap_95_high": hi,
    }


def _portfolio(raw, records, horizon, all_dates):
    if len(all_dates):
        eval_start = pd.Timestamp(min(all_dates)).date()
        eval_end = max(
            pd.Timestamp(max(all_dates)).date(),
            max((r.exit_day for r in records), default=pd.Timestamp(max(all_dates)).date()),
        )
    else:
        eval_start = eval_end = None
    _, port = simulate_portfolio(
        raw, records, horizon=horizon, initial_equity=1.0,
        daily_cohort_fraction=1.0 / horizon, suppress_duplicate_symbols=False,
        evaluation_start=eval_start, evaluation_end=eval_end,
    )
    return summary_dict(port)


def _baseline_from_frame(raw, frame, record_map, strategy, top_k, horizon):
    scored = frame.copy()
    if strategy == "momentum5":
        scored["score"] = scored["ret5"]
    elif strategy == "momentum20":
        scored["score"] = scored["ret20"]
    elif strategy == "momentum20_liquidity":
        scored["score"] = 0.8 * scored["ret20_rank"] + 0.2 * scored["adv20_rank"]
    else:
        raise ValueError(strategy)

    limited = (
        scored.sort_values(["decision_date", "score"], ascending=[True, False])
        .groupby("decision_date", group_keys=False)
        .head(top_k)
        .copy()
    )
    executed, selected, diag = stateful_select_records(
        limited, record_map, top_k=top_k, threshold=None, active_until={}
    )
    signals = []
    no_fill_topk = 0
    for row in limited.itertuples(index=False):
        key = (pd.Timestamp(row.decision_date).date(), str(row.symbol))
        base = record_map.get(key)
        if base is None:
            no_fill_topk += 1
            continue
        signals.append(base.__class__(**{**base.__dict__, "score": float(row.score)}))
    return {
        "signal_set": _metric_block(signals),
        "executable_set": _metric_block(executed),
        "portfolio": _portfolio(raw, executed, horizon, list(scored["decision_date"].unique())),
        **diag,
        "decision_topk_no_fill_slots": int(no_fill_topk),
        "selection_policy": "original_top3_fixed_at_decision__no_fill_leaves_empty_slot",
        "test_dates": int(scored["decision_date"].nunique()),
        "trade_days": int(selected["decision_date"].nunique()) if not selected.empty else 0,
        "trade_day_coverage": float(selected["decision_date"].nunique() / scored["decision_date"].nunique()) if not selected.empty else 0.0,
    }


def _walk_forward_pit(frame: pd.DataFrame, kind: str, train_days: int, test_days: int, context: bool = False):
    """Fit labelled past rows, score every decision-time row in each test block."""
    dates = sorted(pd.Timestamp(x) for x in frame["decision_date"].drop_duplicates())
    out = []
    start = train_days
    feature_cols = CONTEXT_FEATURES if context else FEATURES
    while start < len(dates):
        test_block = dates[start:start + test_days]
        if not test_block:
            break
        train_block = dates[:start]
        train_all = frame[frame["decision_date"].isin(train_block)]
        train = train_all[train_all["label_available"].fillna(False).astype(bool)].copy()
        test = frame[frame["decision_date"].isin(test_block)].copy()
        if train.empty or test.empty:
            start += test_days
            continue

        if context:
            pipe = _context_pipe(kind)
        elif kind == "logistic_l2":
            pipe = _classification_pipeline("logistic_l2")
        elif kind == "ridge_net":
            pipe = _regression_pipeline()
        else:
            raise ValueError(kind)

        if kind.startswith("logistic"):
            y = train["label_positive_net"].astype(int)
            if y.nunique() < 2:
                start += test_days
                continue
            pipe.fit(train[feature_cols], y)
            test["score"] = pipe.predict_proba(test[feature_cols])[:, 1]
        else:
            pipe.fit(train[feature_cols], train["net_return"].astype(float))
            test["score"] = pipe.predict(test[feature_cols])

        test["model"] = kind
        test["train_end"] = train_block[-1]
        keep = [
            "decision_date", "symbol", "label_positive_net", "net_return",
            "label_available", "entry_fillable", "ambiguous_same_bar",
            "post_entry_missing_future", "score", "model", "train_end",
        ]
        out.append(test[keep])
        start += test_days
    if not out:
        return pd.DataFrame()
    return pd.concat(out, ignore_index=True).sort_values(
        ["decision_date", "score"], ascending=[True, False]
    )


def _evaluate_positive_net(raw, pred, record_map, horizon, top_k):
    if pred.empty:
        return {}, pd.DataFrame()
    positive = pred[pred["score"] > 0].copy()
    limited = (
        positive.sort_values(["decision_date", "score"], ascending=[True, False])
        .groupby("decision_date", group_keys=False)
        .head(top_k)
        .copy()
    )
    recs, selected, diag = stateful_select_records(
        limited, record_map, top_k=top_k, threshold=None, active_until={}
    )
    m = _metric_block(recs)
    topk_no_fill = int(sum(
        (pd.Timestamp(r.decision_date).date(), str(r.symbol)) not in record_map
        for r in limited.itertuples(index=False)
    ))
    return {
        "objective": "direct_cost_adjusted_net_return",
        "admission_rule": "predicted_net_gt_0_then_original_top3__no_fill_leaves_empty_slot",
        "executable_set": m,
        "portfolio": _portfolio(raw, recs, horizon, list(pred["decision_date"].unique())),
        **diag,
        "decision_topk_no_fill_slots": topk_no_fill,
        "prediction_rows": int(len(pred)),
        "selected_executable_rows": int(len(recs)),
        "test_dates": int(pred["decision_date"].nunique()),
        "trade_days": int(selected["decision_date"].nunique()) if not selected.empty else 0,
        "trade_day_coverage": float(selected["decision_date"].nunique() / pred["decision_date"].nunique()) if not selected.empty else 0.0,
    }, selected


def _selective_abstention_pit(raw, frame, record_map, horizon, top_k, train_days=160, cal_days=40, test_days=40):
    """Calibration-selected threshold with decision-time no-fill rows retained.

    Threshold choices are fixed coverage candidates. A threshold is permitted
    only when calibration *executable* trades have a positive date-cluster 95%
    lower bound. Otherwise that fold remains cash.
    """
    dates = sorted(pd.Timestamp(x) for x in frame["decision_date"].drop_duplicates())
    all_recs = []
    fold_log = []
    live_state = {}
    start = train_days + cal_days
    test_dates_seen = []
    while start < len(dates):
        train_block = dates[:start - cal_days]
        cal_block = dates[start - cal_days:start]
        test_block = dates[start:start + test_days]
        if not test_block:
            break
        train = frame[frame["decision_date"].isin(train_block)]
        train = train[train["label_available"].fillna(False).astype(bool)]
        cal = frame[frame["decision_date"].isin(cal_block)].copy()
        test = frame[frame["decision_date"].isin(test_block)].copy()
        test_dates_seen.extend(test_block)
        if train.empty or cal.empty or test.empty or train["label_positive_net"].nunique() < 2:
            start += test_days
            continue
        model = _classification_pipeline("logistic_l2")
        model.fit(train[FEATURES], train["label_positive_net"].astype(int))
        cal["score"] = model.predict_proba(cal[FEATURES])[:, 1]
        test["score"] = model.predict_proba(test[FEATURES])[:, 1]

        candidates = []
        for cov in [0.05, 0.10, 0.20, 0.30, 0.40]:
            threshold = float(np.quantile(cal["score"].to_numpy(dtype=float), 1.0 - cov))
            eligible = cal[cal["score"] >= threshold]
            limited = (
                eligible.sort_values(["decision_date", "score"], ascending=[True, False])
                .groupby("decision_date", group_keys=False).head(top_k)
            )
            recs, _, _ = stateful_select_records(limited, record_map, top_k=top_k, active_until={})
            if len(recs) < 30:
                continue
            point, lo, hi = date_cluster_bootstrap_mean(recs, samples=1000, seed=20260928)
            candidates.append({
                "coverage": cov, "threshold": threshold, "trades": len(recs),
                "point": point, "low": lo, "high": hi,
                "mean": summarize(recs).mean_net_return,
            })
        valid = [x for x in candidates if x["low"] > 0]
        if not valid:
            fold_log.append({"test_start": str(test_block[0].date()), "threshold": None, "reason": "no_positive_calibration_lcb"})
            start += test_days
            continue
        chosen = max(valid, key=lambda x: (x["low"], x["mean"]))
        eligible_test = test[test["score"] >= chosen["threshold"]]
        limited_test = (
            eligible_test.sort_values(["decision_date", "score"], ascending=[True, False])
            .groupby("decision_date", group_keys=False).head(top_k)
        )
        recs, _, _ = stateful_select_records(
            limited_test, record_map, top_k=top_k, active_until=live_state
        )
        all_recs.extend(recs)
        fold_log.append({
            "test_start": str(test_block[0].date()), "threshold": chosen["threshold"],
            "calibration": chosen, "test_trades": len(recs),
        })
        start += test_days

    return {
        "objective": "probability_positive_net_return",
        "admission_rule": "calibration_positive_cluster_LCB__original_top3__no_fill_empty_slot",
        "executable_set": _metric_block(all_recs),
        "portfolio": _portfolio(raw, all_recs, horizon, test_dates_seen),
        "test_dates": len(set(test_dates_seen)),
        "trade_days": len({r.decision_day for r in all_recs}),
        "trade_day_coverage": float(len({r.decision_day for r in all_recs}) / len(set(test_dates_seen))) if test_dates_seen else 0.0,
        "folds": fold_log,
    }


def _grade(candidate):
    ex = candidate.get("executable_set", {})
    p = candidate.get("portfolio", {})
    trades = int(ex.get("trades") or 0)
    net = float(ex.get("mean_net_return") or 0.0)
    pf = float(ex.get("profit_factor") or 0.0)
    lo = float(ex.get("cluster_bootstrap_95_low") or 0.0)
    mdd = float(p.get("max_drawdown") or 0.0)
    if trades == 0:
        return {"grade": "NO_TRADE_FAIL_CLOSED", "issues": ["No trades admitted."]}
    issues = []
    if net <= 0: issues.append("mean_net_return_not_positive")
    if pf <= 1.0: issues.append("profit_factor_not_above_1")
    if lo <= 0: issues.append("date_cluster_95pct_lower_bound_not_positive")
    if mdd <= -0.10: issues.append("max_drawdown_worse_than_10pct")
    if not issues:
        return {"grade": "PIT_PRELIMINARY_PROMISING", "issues": []}
    if net > 0 and pf > 1:
        return {"grade": "PIT_PRELIMINARY_INSUFFICIENT_CONFIDENCE", "issues": issues}
    return {"grade": "PIT_PRELIMINARY_NOT_SUITABLE_YET", "issues": issues}


def _compact(report):
    return {
        "evaluation_stage": report.get("evaluation_stage"),
        "data_start": report.get("data_start"),
        "data_end": report.get("data_end"),
        "raw_rows": report.get("raw_rows"),
        "raw_symbols": report.get("raw_symbols"),
        "decision_rows": report.get("decision_rows_after_liquidity_gate"),
        "decision_dates": report.get("decision_dates"),
        "diagnostics": report.get("diagnostics"),
        "overall": report.get("overall_preliminary_assessment"),
        "ranking": report.get("conservative_ranking"),
        "blockers": report.get("final_judge_blockers"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit")
    ap.add_argument("--result-dir", default="research_results/marcap_pit")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--target", type=float, default=0.04)
    ap.add_argument("--stop", type=float, default=-0.025)
    ap.add_argument("--participation", type=float, default=0.0005)
    ap.add_argument("--train-days", type=int, default=200)
    ap.add_argument("--test-days", type=int, default=40)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    status = dataset_status(raw)
    if not status["point_in_time_universe"]:
        raise RuntimeError("PIT runner requires point_in_time_universe=True")

    frame, record_map, diag = make_pit_supervised(
        raw, horizon=args.horizon, target_return=args.target,
        stop_return=args.stop, participation=args.participation,
    )
    before = len(frame)
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)

    report = {
        "judge_version": "KR-KOSPI-JUDGE-v1.0",
        **status,
        "evaluation_stage": "PIT_PRELIMINARY",
        "final_judge_blockers": [
            "common_stock_identity_not_validated" if not status["common_stock_identity_validated"] else None,
            "post_entry_missing_bar_uses_preliminary_planned_stop_not_exact_delisting_halt_value",
            "daily_OHLC_same_bar_barrier_order_uses_conservative_stop_first",
        ],
        "data_start": str(raw["decision_date"].min().date()),
        "data_end": str(raw["decision_date"].max().date()),
        "raw_rows": int(len(raw)),
        "raw_symbols": int(raw["symbol"].nunique()),
        "decision_rows_before_liquidity_gate": int(before),
        "decision_rows_after_liquidity_gate": int(len(frame)),
        "decision_dates": int(frame["decision_date"].nunique()),
        "labelled_training_rows": int(frame["label_available"].fillna(False).sum()),
        "decision_time_no_fill_rows": int((~frame["entry_fillable"].fillna(False)).sum()),
        "liquidity_policy": "trailing_ADV20_same_date_bottom_20pct_excluded_for_all_models",
        "diagnostics": diag,
        "candidates": {},
    }
    report["final_judge_blockers"] = [x for x in report["final_judge_blockers"] if x]

    for strategy in ["momentum5", "momentum20", "momentum20_liquidity"]:
        report["candidates"][f"baseline_{strategy}"] = _baseline_from_frame(
            raw, frame, record_map, strategy, args.top_k, args.horizon
        )

    log_pred = _walk_forward_pit(frame, "logistic_l2", args.train_days, args.test_days)
    log_result, _, _ = evaluate_topk_only(log_pred, record_map, raw, args.horizon, args.top_k)
    log_result["objective"] = "probability_positive_net_return"
    log_result["admission_rule"] = "original_top3_fixed_at_decision__no_fill_empty_slot"
    report["candidates"]["logistic_l2_top3_only"] = log_result

    ridge_pred = _walk_forward_pit(frame, "ridge_net", args.train_days, args.test_days)
    ridge_result, _ = _evaluate_positive_net(raw, ridge_pred, record_map, args.horizon, args.top_k)
    report["candidates"]["ridge_net_positive_only"] = ridge_result

    context_frame = add_context(frame)
    context_log = _walk_forward_pit(context_frame, "logistic_context", args.train_days, args.test_days, context=True)
    result, _, _ = evaluate_topk_only(context_log, record_map, raw, args.horizon, args.top_k)
    result["objective"] = "probability_positive_net_return_plus_simple_market_context"
    result["admission_rule"] = "original_top3_fixed_at_decision__no_fill_empty_slot"
    report["candidates"]["logistic_context_top3_only"] = result

    context_ridge = _walk_forward_pit(context_frame, "ridge_context", args.train_days, args.test_days, context=True)
    result, _ = _evaluate_positive_net(raw, context_ridge, record_map, args.horizon, args.top_k)
    result["objective"] = "direct_net_return_plus_simple_market_context"
    report["candidates"]["ridge_context_positive_only"] = result

    report["candidates"]["logistic_calibrated_abstention"] = _selective_abstention_pit(
        raw, frame, record_map, args.horizon, args.top_k,
        train_days=max(100, args.train_days - 40), cal_days=40, test_days=args.test_days,
    )

    grades = {name: _grade(c) for name, c in report["candidates"].items()}
    report["grades"] = grades
    ranked = []
    for name, c in report["candidates"].items():
        ex = c.get("executable_set", {})
        port = c.get("portfolio", {})
        ranked.append({
            "name": name,
            "trades": int(ex.get("trades") or 0),
            "mean_net_return": float(ex.get("mean_net_return") or 0.0),
            "profit_factor": float(ex.get("profit_factor") or 0.0),
            "cluster_low": float(ex.get("cluster_bootstrap_95_low") or 0.0),
            "cluster_high": float(ex.get("cluster_bootstrap_95_high") or 0.0),
            "total_return": float(port.get("total_return") or 0.0),
            "max_drawdown": float(port.get("max_drawdown") or 0.0),
            **grades[name],
        })
    ranked.sort(key=lambda x: (x["cluster_low"], x["mean_net_return"], x["profit_factor"]), reverse=True)
    report["conservative_ranking"] = ranked
    report["overall_preliminary_assessment"] = (
        "AT_LEAST_ONE_PRELIMINARY_PROMISING_CANDIDATE"
        if any(x["grade"] == "PIT_PRELIMINARY_PROMISING" for x in ranked)
        else "NO_ROBUST_SHORT_TERM_EDGE_YET"
    )
    report["warning"] = (
        "Historical PIT membership and decision-time no-fill ranking are now replayed without retroactive promotion. "
        "Final Judge still requires validated common-stock identity and exact delisting/halt economics."
    )

    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    compact = _compact(report)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "compact.json").write_text(json.dumps(compact, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame(ranked).to_csv(out / "candidate_comparison.csv", index=False)
    print("PIT_COMPACT=" + json.dumps(compact, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
