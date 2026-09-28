"""Common-like security-scope challenger for IndexAlert PIT preliminary research.

This intentionally does NOT promote the dataset to final Judge status.  It asks a
narrow diagnostic question: does removing preferred-share-like securities using
an explicit conservative heuristic materially change the current best simple
market-context model?
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from research_v1_context import add_context
from research_v1_data_policy import dataset_status
from research_v1_holdaware import evaluate_topk_only
from research_v1_pit_labels import make_pit_supervised
from research_v1_pit_run import _grade
from research_v1_pit_run_purged import _walk_forward_pit
from research_v1_security_scope import filter_common_like_heuristic
from run_research_v1 import load_panel


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _candidate_row(name: str, candidate: dict) -> dict:
    ex = candidate.get("executable_set", {})
    port = candidate.get("portfolio", {})
    return {
        "name": name,
        "trades": int(ex.get("trades") or 0),
        "mean_gross_return": float(ex.get("mean_gross_return") or 0.0),
        "mean_cost_return": float(ex.get("mean_cost_return") or 0.0),
        "mean_net_return": float(ex.get("mean_net_return") or 0.0),
        "profit_factor": float(ex.get("profit_factor") or 0.0),
        "cluster_low": float(ex.get("cluster_bootstrap_95_low") or 0.0),
        "cluster_high": float(ex.get("cluster_bootstrap_95_high") or 0.0),
        "total_return": float(port.get("total_return") or 0.0),
        "max_drawdown": float(port.get("max_drawdown") or 0.0),
        **_grade(candidate),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_commonlike")
    ap.add_argument("--full-pit-result", default="research_results/marcap_pit/compact.json")
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
        raise RuntimeError("common-like challenger requires PIT membership data")

    common_raw, scope_diag = filter_common_like_heuristic(raw)
    if bool(common_raw.get("common_stock_identity_validated", pd.Series([False])).fillna(False).astype(bool).all()):
        raise RuntimeError("heuristic scope must not claim validated common-stock identity")

    frame, record_map, label_diag = make_pit_supervised(
        common_raw,
        horizon=args.horizon,
        target_return=args.target,
        stop_return=args.stop,
        participation=args.participation,
    )
    before_liquidity = len(frame)
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    context_frame = add_context(frame)

    pred = _walk_forward_pit(
        context_frame,
        "logistic_context",
        args.train_days,
        args.test_days,
        context=True,
        purge_days=args.horizon,
    )
    candidate, _, _ = evaluate_topk_only(
        pred, record_map, common_raw, args.horizon, args.top_k
    )
    candidate["objective"] = "probability_positive_net_return_plus_simple_market_context"
    candidate["admission_rule"] = (
        "PURGED_COMMON_LIKE_HEURISTIC_DIAGNOSTIC__original_top3_fixed_at_decision__"
        "no_fill_leaves_empty_slot"
    )
    candidate["purge_days"] = int(args.horizon)
    candidate["security_scope_identity_validated"] = False
    candidate["security_scope_heuristic_only"] = True

    current = _candidate_row("common_like_logistic_context_top3_only", candidate)
    full = _load_json(Path(args.full_pit_result))
    full_match = next(
        (r for r in full.get("ranking", []) if r.get("name") == "logistic_context_top3_only"),
        None,
    )
    delta = None
    if full_match:
        delta = {
            "mean_net_return": current["mean_net_return"] - float(full_match.get("mean_net_return") or 0.0),
            "profit_factor": current["profit_factor"] - float(full_match.get("profit_factor") or 0.0),
            "cluster_low": current["cluster_low"] - float(full_match.get("cluster_low") or 0.0),
            "total_return": current["total_return"] - float(full_match.get("total_return") or 0.0),
            "max_drawdown": current["max_drawdown"] - float(full_match.get("max_drawdown") or 0.0),
            "trade_count": current["trades"] - int(full_match.get("trades") or 0),
        }

    report = {
        "evaluation_stage": "PIT_PRELIMINARY_SCOPE_CHALLENGER_PURGED",
        "judge_eligible": False,
        "purge_days": int(args.horizon),
        "judge_blocker": "security-scope filter is heuristic; official point-in-time common-stock identity is not validated",
        "scope_diagnostic": scope_diag,
        "full_raw_rows": int(len(raw)),
        "common_like_raw_rows": int(len(common_raw)),
        "full_raw_symbols": int(raw["symbol"].nunique()),
        "common_like_raw_symbols": int(common_raw["symbol"].nunique()),
        "decision_rows_before_liquidity_gate": int(before_liquidity),
        "decision_rows_after_liquidity_gate": int(len(frame)),
        "decision_dates": int(frame["decision_date"].nunique()) if not frame.empty else 0,
        "label_diagnostics": label_diag,
        "candidate": current,
        "full_universe_reference": full_match,
        "delta_vs_full_logistic_context": delta,
        "interpretation_rule": (
            "Treat improvement only as a scope hypothesis. Do not promote or mark identity validated; "
            "official security-master confirmation is still required."
        ),
    }

    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame([current]).to_csv(out / "candidate.csv", index=False)
    print("COMMONLIKE_COMPACT=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
