"""Exit-policy comparison for IndexAlert distributional research.

This diagnostic freezes the already-declared fixed-horizon Distributional NetEV
admission signal and separates three realised-outcome policies:

A) corporate-action-safe forced D+5 hold (current forecast/evaluation target),
B) legacy raw-OHLC +4%/-2.5% barrier (diagnostic only),
C) corporate-action-safe economic-OHLC +4%/-2.5% barrier with gap-through fills.

No target/stop or admission threshold is tuned here.  The comparison is run both
on an identical paired cohort (keys selected by policy A) and as a policy-
consistent stateful replay.  Policy C is the candidate execution evaluator; the
legacy raw barrier is retained only to quantify corporate-action distortion.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_core import AmbiguousFirstHit, Bar, DecisionRecord, economic_outcome
from research_v1_distributional_ablation import MARKET, RESID
from research_v1_distributional_netev import (
    _calendar_splits,
    _cost_stress,
    _fixed_record_map,
    _metric,
    _portfolio,
    distributional_walk_forward,
    freeze_original_topk,
)
from research_v1_fixed_horizon_label import add_fixed_horizon_target, build_economic_mark_panel
from research_v1_ml import stateful_select_records
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel

FEATURE_FAMILIES = {
    "all_context": CONTEXT_FEATURES,
    "context_only": MARKET + RESID,
}


def build_economic_ohlc_panel(raw: pd.DataFrame) -> pd.DataFrame:
    """Put each day's raw OHLC on the continuous KRX economic-price index.

    KRX FLUC_RT supplies the corporate-action-adjusted close-to-close return.
    Multiplying all raw intraday prices by economic_close/raw_close preserves the
    day's OHLC geometry while avoiding mechanical split/rights barrier hits.
    """
    x = build_economic_mark_panel(raw)
    raw_close = pd.to_numeric(x["close"], errors="coerce")
    scale = pd.to_numeric(x["economic_close"], errors="coerce") / raw_close
    scale = scale.where((scale > 0) & np.isfinite(scale))
    for src, dst in (
        ("open", "economic_open"),
        ("high", "economic_high"),
        ("low", "economic_low"),
        ("close", "economic_close_ohlc"),
    ):
        x[dst] = pd.to_numeric(x[src], errors="coerce") * scale
    # The independently constructed close must agree numerically.
    close_gap = (x["economic_close_ohlc"] - x["economic_close"]).abs()
    finite = close_gap[np.isfinite(close_gap)]
    if len(finite) and float(finite.max()) > 1e-10:
        raise RuntimeError("economic OHLC scaling failed close-index identity")
    # Floating-point scaling can make an exact raw high==close become smaller by
    # ~1e-16.  Normalize the economic bar to preserve OHLC ordering without
    # changing any economically meaningful level.
    x["economic_high"] = pd.concat(
        [x["economic_high"], x["economic_open"], x["economic_close"]], axis=1
    ).max(axis=1)
    x["economic_low"] = pd.concat(
        [x["economic_low"], x["economic_open"], x["economic_close"]], axis=1
    ).min(axis=1)
    x["economic_close_ohlc"] = x["economic_close"]
    return x


def _data_gap_stop(
    base: DecisionRecord,
    *,
    entry_price: float,
    missing_day,
    horizon: int,
    target_return: float,
    stop_return: float,
) -> DecisionRecord:
    exit_price = float(entry_price) * (1.0 + float(stop_return))
    gross = float(stop_return)
    return DecisionRecord(
        decision_day=base.decision_day,
        entry_day=base.entry_day,
        symbol=base.symbol,
        score=float(base.score),
        entry_price=float(entry_price),
        horizon=int(horizon),
        target_return=float(target_return),
        stop_return=float(stop_return),
        cost_return=float(base.cost_return),
        outcome="STOP_DATA_GAP_CA_SAFE",
        gross_return=gross,
        net_return=gross - float(base.cost_return),
        exit_day=pd.Timestamp(missing_day).date(),
        exit_price=exit_price,
    )


def build_ca_safe_barrier_record_map(
    raw: pd.DataFrame,
    legacy_map: dict,
    *,
    horizon: int,
    target_return: float,
    stop_return: float,
    ambiguity_policy: str = "stop_first",
) -> tuple[dict, dict]:
    """Re-evaluate predeclared barriers on corporate-action-safe economic OHLC.

    `economic_outcome` already implements gap-through-stop/target fills at the
    next executable open and stop-first handling can be requested for same-bar
    first-hit ambiguity.  Costs are copied from the PIT legacy record so the only
    intended change is the price axis used for barrier execution.
    """
    if ambiguity_policy not in {"stop_first", "target_first"}:
        raise ValueError("unsupported ambiguity policy")
    econ = build_economic_ohlc_panel(raw)
    dates = sorted(pd.Timestamp(x) for x in econ["decision_date"].drop_duplicates())
    date_pos = {d: i for i, d in enumerate(dates)}
    by_symbol = {
        str(symbol): g.sort_values("decision_date").set_index("decision_date")
        for symbol, g in econ.groupby("symbol", sort=False)
    }
    out = {}
    diag = {
        "source_records": int(len(legacy_map)),
        "built_records": 0,
        "missing_decision_date": 0,
        "insufficient_global_future_horizon": 0,
        "missing_entry_economic_ohlc": 0,
        "post_entry_missing_future_bar_conservative_stop": 0,
        "ambiguous_same_bar_stop_first": 0,
        "policy": "KRX_FLUC_RT_ECONOMIC_OHLC__GAP_AT_OPEN__SAME_BAR_STOP_FIRST",
    }
    need = ["economic_open", "economic_high", "economic_low", "economic_close"]

    for (decision_day, symbol), base in legacy_map.items():
        d = pd.Timestamp(decision_day)
        pos = date_pos.get(d)
        if pos is None:
            diag["missing_decision_date"] += 1
            continue
        future_dates = dates[pos + 1:pos + 1 + int(horizon)]
        if len(future_dates) < int(horizon):
            diag["insufficient_global_future_horizon"] += 1
            continue
        hist = by_symbol.get(str(symbol))
        if hist is None:
            diag["missing_entry_economic_ohlc"] += 1
            continue

        bars = []
        first_missing = None
        for fday in future_dates:
            try:
                r = hist.loc[fday]
            except KeyError:
                first_missing = fday
                break
            vals = [r[c] for c in need]
            if any(pd.isna(v) or not np.isfinite(float(v)) or float(v) <= 0 for v in vals):
                first_missing = fday
                break
            bars.append(Bar(
                day=fday.date(),
                open=float(r.economic_open),
                high=float(r.economic_high),
                low=float(r.economic_low),
                close=float(r.economic_close),
                volume=float(getattr(r, "volume", 0.0) or 0.0),
                value=float(getattr(r, "value", 0.0) or 0.0),
            ))

        if not bars:
            diag["missing_entry_economic_ohlc"] += 1
            continue
        entry_price = float(bars[0].open)
        if first_missing is not None:
            diag["post_entry_missing_future_bar_conservative_stop"] += 1
            rec = _data_gap_stop(
                base,
                entry_price=entry_price,
                missing_day=first_missing,
                horizon=horizon,
                target_return=target_return,
                stop_return=stop_return,
            )
        else:
            kwargs = dict(
                decision_day=base.decision_day,
                symbol=str(symbol),
                score=float(base.score),
                entry_price=entry_price,
                future_bars=bars,
                target_return=float(target_return),
                stop_return=float(stop_return),
                round_trip_cost_return=float(base.cost_return),
            )
            try:
                rec = economic_outcome(**kwargs)
            except AmbiguousFirstHit:
                if ambiguity_policy == "stop_first":
                    diag["ambiguous_same_bar_stop_first"] += 1
                rec = economic_outcome(**kwargs, ambiguous_policy=ambiguity_policy)
        out[(base.decision_day, str(symbol))] = rec

    diag["built_records"] = int(len(out))
    return out, diag


def _records_for_selected(selected: pd.DataFrame, record_map: dict) -> tuple[list, set]:
    records = []
    missing = set()
    if selected.empty:
        return records, missing
    for row in selected.itertuples(index=False):
        key = (pd.Timestamp(row.decision_date).date(), str(row.symbol))
        base = record_map.get(key)
        if base is None:
            missing.add(key)
            continue
        records.append(base.__class__(**{**asdict(base), "score": float(row.score)}))
    return records, missing


def _records_for_keys(selected: pd.DataFrame, record_map: dict, allowed_keys: set) -> list:
    records = []
    if selected.empty:
        return records
    for row in selected.itertuples(index=False):
        key = (pd.Timestamp(row.decision_date).date(), str(row.symbol))
        if key not in allowed_keys:
            continue
        base = record_map[key]
        records.append(base.__class__(**{**asdict(base), "score": float(row.score)}))
    return records


def _key_set(selected: pd.DataFrame, record_map: dict) -> set:
    if selected.empty:
        return set()
    return {
        (pd.Timestamp(r.decision_date).date(), str(r.symbol))
        for r in selected.itertuples(index=False)
        if (pd.Timestamp(r.decision_date).date(), str(r.symbol)) in record_map
    }


def _extreme_day_dependency(records: list) -> dict:
    if not records:
        return {"baseline": _metric([]), "remove_best_days": {}}
    by_day = {}
    for rec in records:
        by_day.setdefault(rec.decision_day, []).append(rec)
    ranked = sorted(
        by_day,
        key=lambda d: float(np.mean([r.net_return for r in by_day[d]])),
        reverse=True,
    )
    out = {"baseline": _metric(records), "remove_best_days": {}}
    for n in (1, 3, 5):
        removed = set(ranked[:n])
        kept = [r for r in records if r.decision_day not in removed]
        out["remove_best_days"][str(n)] = {
            "removed_dates": [str(d) for d in ranked[:n]],
            "remaining_records": int(len(kept)),
            "metrics": _metric(kept),
        }
    return out


def _tail(records: list) -> dict:
    if not records:
        return {"min": 0.0, "p01": 0.0, "p05": 0.0, "p50": 0.0, "max": 0.0}
    x = np.asarray([r.net_return for r in records], dtype=float)
    return {
        "min": float(np.min(x)),
        "p01": float(np.quantile(x, 0.01)),
        "p05": float(np.quantile(x, 0.05)),
        "p50": float(np.quantile(x, 0.50)),
        "max": float(np.max(x)),
    }


def _policy_summary(raw, records: list, pred: pd.DataFrame, horizon: int, ca_safe_prices: bool) -> dict:
    result = {
        "metrics": _metric(records),
        "cost_stress": _cost_stress(records),
        "calendar_year_splits": _calendar_splits(records),
        "extreme_day_dependency": _extreme_day_dependency(records),
        "tail_quantiles": _tail(records),
    }
    if ca_safe_prices:
        result["portfolio"] = _portfolio(raw, records, pred, horizon)
    else:
        result["portfolio"] = {
            "available": False,
            "reason": "raw-price shares/marks are not corporate-action-safe; trade-level diagnostic only",
        }
    return result


def _paired_differences(selected: pd.DataFrame, raw_map: dict, ca_map: dict, allowed: set) -> pd.DataFrame:
    rows = []
    if selected.empty:
        return pd.DataFrame()
    for r in selected.itertuples(index=False):
        key = (pd.Timestamp(r.decision_date).date(), str(r.symbol))
        if key not in allowed:
            continue
        a = raw_map[key]
        b = ca_map[key]
        rows.append({
            "decision_date": key[0],
            "symbol": key[1],
            "score": float(r.score),
            "raw_barrier_outcome": a.outcome,
            "ca_barrier_outcome": b.outcome,
            "raw_barrier_net_return": float(a.net_return),
            "ca_barrier_net_return": float(b.net_return),
            "ca_minus_raw_net": float(b.net_return - a.net_return),
            "raw_exit_day": a.exit_day,
            "ca_exit_day": b.exit_day,
        })
    return pd.DataFrame(rows)


def run_family(
    *, raw, z, fixed_map, raw_barrier_map, ca_barrier_map, features,
    top_k, horizon, train_days, cal_days, test_days,
):
    pred, folds = distributional_walk_forward(
        z,
        train_days=train_days,
        cal_days=cal_days,
        test_days=test_days,
        purge_days=horizon,
        features=features,
    )
    if pred.empty:
        raise RuntimeError("distributional walk-forward produced no predictions")
    eligible = pred[pred["netev_low"] > 0].copy()
    frozen = freeze_original_topk(eligible, top_k)

    fixed_state_records, fixed_selected, fixed_sel_diag = stateful_select_records(
        frozen, fixed_map, top_k=top_k, threshold=0.0,
    )
    raw_state_records, raw_selected, raw_sel_diag = stateful_select_records(
        frozen, raw_barrier_map, top_k=top_k, threshold=0.0,
    )
    ca_state_records, ca_selected, ca_sel_diag = stateful_select_records(
        frozen, ca_barrier_map, top_k=top_k, threshold=0.0,
    )

    # Paired cohort: keys produced by the existing forced-D+5 stateful selector,
    # then intersect maps so every exit policy is measured on identical names.
    fixed_keys = _key_set(fixed_selected, fixed_map)
    paired_keys = fixed_keys & set(raw_barrier_map) & set(ca_barrier_map)
    fixed_paired = _records_for_keys(fixed_selected, fixed_map, paired_keys)
    raw_paired = _records_for_keys(fixed_selected, raw_barrier_map, paired_keys)
    ca_paired = _records_for_keys(fixed_selected, ca_barrier_map, paired_keys)
    paired_diff = _paired_differences(fixed_selected, raw_barrier_map, ca_barrier_map, paired_keys)

    raw_ca_changed = 0
    raw_ca_gt_1pct = 0
    if not paired_diff.empty:
        raw_ca_changed = int((paired_diff["raw_barrier_outcome"] != paired_diff["ca_barrier_outcome"]).sum())
        raw_ca_gt_1pct = int((paired_diff["ca_minus_raw_net"].abs() > 0.01).sum())

    return {
        "folds": folds,
        "test_dates": int(pred["decision_date"].nunique()),
        "eligible_rows": int(len(eligible)),
        "frozen_topk_rows": int(len(frozen)),
        "paired": {
            "common_keys": int(len(paired_keys)),
            "forced_d5_ca_safe": _policy_summary(raw, fixed_paired, pred, horizon, True),
            "raw_gap_aware_barrier_diagnostic": _policy_summary(raw, raw_paired, pred, horizon, False),
            "ca_safe_gap_aware_barrier": _policy_summary(raw, ca_paired, pred, horizon, True),
            "raw_vs_ca_barrier": {
                "outcome_changed_count": raw_ca_changed,
                "abs_net_difference_gt_1pct_count": raw_ca_gt_1pct,
            },
        },
        "policy_consistent_stateful": {
            "forced_d5_ca_safe": {
                "selection": fixed_sel_diag,
                "selected_records": int(len(fixed_state_records)),
                "trade_days": int(fixed_selected["decision_date"].nunique()) if not fixed_selected.empty else 0,
                **_policy_summary(raw, fixed_state_records, pred, horizon, True),
            },
            "raw_gap_aware_barrier_diagnostic": {
                "selection": raw_sel_diag,
                "selected_records": int(len(raw_state_records)),
                "trade_days": int(raw_selected["decision_date"].nunique()) if not raw_selected.empty else 0,
                **_policy_summary(raw, raw_state_records, pred, horizon, False),
            },
            "ca_safe_gap_aware_barrier": {
                "selection": ca_sel_diag,
                "selected_records": int(len(ca_state_records)),
                "trade_days": int(ca_selected["decision_date"].nunique()) if not ca_selected.empty else 0,
                **_policy_summary(raw, ca_state_records, pred, horizon, True),
            },
        },
        "selected_frames": {
            "fixed": fixed_selected,
            "raw": raw_selected,
            "ca": ca_selected,
            "paired_diff": paired_diff,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    ap.add_argument("--supervised-cache", required=True)
    ap.add_argument("--result-dir", required=True)
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--target", type=float, default=0.04)
    ap.add_argument("--stop", type=float, default=-0.025)
    ap.add_argument("--participation", type=float, default=0.0005)
    ap.add_argument("--train-days", type=int, default=160)
    ap.add_argument("--cal-days", type=int, default=40)
    ap.add_argument("--test-days", type=int, default=40)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    frame, raw_barrier_map, label_diag, cache_meta = load_or_build(
        raw,
        Path(args.supervised_cache),
        horizon=args.horizon,
        target_return=args.target,
        stop_return=args.stop,
        participation=args.participation,
        commission_round_trip_bps=3.0,
    )
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    z = add_fixed_horizon_target(raw, add_context(frame), raw_barrier_map, args.horizon)
    fixed_map = _fixed_record_map(z, args.horizon)
    ca_barrier_map, ca_diag = build_ca_safe_barrier_record_map(
        raw,
        raw_barrier_map,
        horizon=args.horizon,
        target_return=args.target,
        stop_return=args.stop,
        ambiguity_policy="stop_first",
    )

    out_dir = Path(args.result_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "evaluation_stage": "PIT_PRELIMINARY_EXIT_POLICY_ISOLATION_CA_SAFE",
        "forecast_target": "corporate_action_safe_next_open_to_Dplus5_close_cost_adjusted_net_return",
        "admission_rule": "netev_low_gt_0__freeze_original_top3__blocked_slot_stays_empty",
        "exit_policies": {
            "A": "forced_Dplus5_on_KRX_FLUC_RT_economic_index",
            "B": "legacy_raw_OHLC_gap_aware_4pct_target_minus2p5pct_stop_DIAGNOSTIC_ONLY",
            "C": "KRX_FLUC_RT_economic_OHLC_gap_aware_4pct_target_minus2p5pct_stop",
        },
        "predeclared_parameters": {
            "target_return": args.target,
            "stop_return": args.stop,
            "horizon": args.horizon,
            "top_k": args.top_k,
            "train_days": args.train_days,
            "cal_days": args.cal_days,
            "test_days": args.test_days,
        },
        "no_parameter_search": True,
        "supervised_cache": cache_meta,
        "legacy_label_diagnostics": label_diag,
        "ca_safe_barrier_diagnostics": ca_diag,
        "models": {},
    }

    for name, features in FEATURE_FAMILIES.items():
        result = run_family(
            raw=raw,
            z=z,
            fixed_map=fixed_map,
            raw_barrier_map=raw_barrier_map,
            ca_barrier_map=ca_barrier_map,
            features=features,
            top_k=args.top_k,
            horizon=args.horizon,
            train_days=args.train_days,
            cal_days=args.cal_days,
            test_days=args.test_days,
        )
        frames = result.pop("selected_frames")
        report["models"][name] = result
        for key, df in frames.items():
            if isinstance(df, pd.DataFrame):
                df.to_csv(out_dir / f"{name}_{key}.csv", index=False)

    report["interpretation_contract"] = {
        "forced_d5": "forecast/opportunity label; not automatically accepted as final execution policy",
        "raw_barrier": "diagnostic only because raw price levels can be discontinuous across corporate actions",
        "ca_safe_barrier": "candidate realistic evaluator; adoption still requires long OOS robustness",
        "paired": "isolates exit-policy effect on identical selected keys",
        "policy_consistent_stateful": "shows full replay effect when earlier exits change future symbol availability",
        "judge_eligible": False,
        "judge_blockers": [
            "exact common-stock identity not yet fully validated",
            "exact halt/delisting economics not yet fully validated",
            "exit-policy comparator is preliminary research, not a sealed Judge",
        ],
    }
    (out_dir / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("EXIT_POLICY_COMPARE=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
