"""Run IndexAlert baseline research on a cached KOSPI-like daily panel.

The report propagates data-lineage eligibility. A non-PIT smoke dataset can
exercise the same engine, but its metrics are never labeled Judge-eligible.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from research_v1_core import (
    AmbiguousFirstHit,
    Bar,
    cost_model_return,
    date_cluster_bootstrap_mean,
    economic_outcome,
    summarize,
)
from research_v1_portfolio import simulate_portfolio, summary_dict

DEFAULT_CACHE = Path("research_data/krx_daily")
RESULT_DIR = Path("research_results")


def load_panel(cache_dir: Path = DEFAULT_CACHE) -> pd.DataFrame:
    files = sorted(p for p in cache_dir.glob("*.parquet") if p.is_file())
    if not files:
        raise RuntimeError(f"no parquet data in {cache_dir}")
    frames = [pd.read_parquet(p) for p in files]
    x = pd.concat(frames, ignore_index=True)
    x["decision_date"] = pd.to_datetime(x["decision_date"])
    return x.sort_values(["decision_date", "symbol"]).reset_index(drop=True)


def add_features(panel: pd.DataFrame) -> pd.DataFrame:
    x = panel.copy().sort_values(["symbol", "decision_date"]).reset_index(drop=True)
    g = x.groupby("symbol", sort=False, group_keys=False)
    x["ret1"] = g["close"].pct_change(1)
    x["ret5"] = g["close"].pct_change(5)
    x["ret20"] = g["close"].pct_change(20)
    x["vol20"] = x.groupby("symbol", sort=False)["ret1"].transform(
        lambda s: s.rolling(20, min_periods=20).std(ddof=0)
    )
    x["adv20"] = x.groupby("symbol", sort=False)["value"].transform(
        lambda s: s.rolling(20, min_periods=20).median()
    )
    return x


def _rank_day(day: pd.DataFrame, strategy: str) -> pd.DataFrame:
    d = day.copy().dropna(subset=["ret5", "ret20", "adv20", "vol20"])
    if d.empty:
        return d
    liq_cut = d["adv20"].quantile(0.20)
    d = d[d["adv20"] >= liq_cut].copy()
    if strategy == "momentum5":
        d["score"] = d["ret5"]
    elif strategy == "momentum20":
        d["score"] = d["ret20"]
    elif strategy == "momentum20_liquidity":
        d["score"] = 0.8 * d["ret20"].rank(pct=True) + 0.2 * d["adv20"].rank(pct=True)
    else:
        raise ValueError(strategy)
    return d.sort_values("score", ascending=False)


def build_lookup(panel: pd.DataFrame):
    dates = sorted(panel["decision_date"].drop_duplicates())
    date_to_pos = {pd.Timestamp(d): i for i, d in enumerate(dates)}
    by_symbol = {s: g.set_index("decision_date").sort_index() for s, g in panel.groupby("symbol")}
    return dates, date_to_pos, by_symbol


def _record_for_row(
    row,
    decision_date,
    dates,
    date_to_pos,
    by_symbol,
    horizon,
    target_return,
    stop_return,
    half_spread_bps,
    explicit_bps,
    participation,
    impact_coefficient,
):
    symbol = row["symbol"]
    pos = date_to_pos[pd.Timestamp(decision_date)]
    future_dates = dates[pos + 1: pos + 1 + horizon]
    if len(future_dates) < horizon:
        return None, False, "short_future"
    hist = by_symbol.get(symbol)
    if hist is None:
        return None, False, "missing_symbol"
    try:
        entry_row = hist.loc[pd.Timestamp(future_dates[0])]
    except KeyError:
        return None, False, "missing_entry"
    future = []
    for d in future_dates:
        try:
            r = hist.loc[pd.Timestamp(d)]
        except KeyError:
            return None, False, "missing_future_bar"
        future.append(Bar(
            day=pd.Timestamp(d).date(), open=float(r.open), high=float(r.high),
            low=float(r.low), close=float(r.close), volume=float(r.volume), value=float(r.value),
        ))
    cost = cost_model_return(
        half_spread_bps=half_spread_bps,
        tax_commission_bps=explicit_bps,
        volatility=float(row["vol20"]),
        participation=participation,
        impact_coefficient=impact_coefficient,
    )
    kwargs = dict(
        decision_day=pd.Timestamp(decision_date).date(), symbol=symbol,
        score=float(row["score"]), entry_price=float(entry_row.open), future_bars=future,
        target_return=target_return, stop_return=stop_return,
        round_trip_cost_return=cost,
    )
    try:
        return economic_outcome(**kwargs), False, None
    except AmbiguousFirstHit:
        return economic_outcome(**kwargs, ambiguous_policy="stop_first"), True, None


def run_strategy(
    panel: pd.DataFrame,
    strategy: str,
    top_k: int = 3,
    horizon: int = 5,
    target_return: float = 0.04,
    stop_return: float = -0.025,
    half_spread_bps: float = 4.0,
    explicit_bps: float = 23.0,
    participation: float = 0.0005,
    impact_coefficient: float = 0.10,
):
    dates, date_to_pos, by_symbol = build_lookup(panel)
    signal_records = []
    executable_records = []
    active_until = {}
    ambiguous_keys = set()
    skipped_keys = set()
    signal_candidates = 0
    execution_candidates_scanned = 0
    blocked = 0
    backfilled = 0

    for decision_date, day in panel.groupby("decision_date", sort=True):
        ranked = _rank_day(day, strategy)
        if ranked.empty:
            continue
        cache = {}

        def get_rec(idx, row):
            key = (pd.Timestamp(decision_date).date(), str(row["symbol"]))
            if key not in cache:
                rec, amb, skip_reason = _record_for_row(
                    row, decision_date, dates, date_to_pos, by_symbol, horizon,
                    target_return, stop_return, half_spread_bps, explicit_bps,
                    participation, impact_coefficient,
                )
                cache[key] = rec
                if amb:
                    ambiguous_keys.add(key)
                if skip_reason:
                    skipped_keys.add(key)
            return cache[key]

        # Diagnostic signal set: unadjusted top-K ranking.
        for idx, row in ranked.head(top_k).iterrows():
            signal_candidates += 1
            rec = get_rec(idx, row)
            if rec is not None:
                signal_records.append(rec)

        # Executable set: respect already-open positions and backfill with the
        # next eligible rank instead of shrinking the daily cohort.
        picked = 0
        for rank, (idx, row) in enumerate(ranked.iterrows(), start=1):
            if picked >= top_k:
                break
            execution_candidates_scanned += 1
            rec = get_rec(idx, row)
            if rec is None:
                continue
            prev_exit = active_until.get(rec.symbol)
            if prev_exit is not None and prev_exit >= rec.entry_day:
                blocked += 1
                continue
            executable_records.append(rec)
            active_until[rec.symbol] = rec.exit_day
            if rank > top_k:
                backfilled += 1
            picked += 1

    decision_days = len({r.decision_day for r in signal_records})
    return signal_records, executable_records, {
        "signal_candidates_considered": signal_candidates,
        "execution_candidates_scanned": execution_candidates_scanned,
        "ambiguous": len(ambiguous_keys),
        "ambiguous_rate_signal": float(len(ambiguous_keys) / max(1, len(signal_records))),
        "ambiguous_primary_policy": "stop_first_conservative_no_future_filter",
        "skipped": len(skipped_keys),
        "active_position_candidates_blocked": blocked,
        "backfill_selections": backfilled,
        "decision_days_with_signal_records": decision_days,
        "avg_signal_records_per_decision_day": float(len(signal_records) / decision_days) if decision_days else 0.0,
    }


def _metric_block(records):
    m = summarize(records)
    point, lo, hi = date_cluster_bootstrap_mean(records) if records else (0.0, 0.0, 0.0)
    return {
        **asdict(m),
        "cluster_bootstrap_mean_net_return": point,
        "cluster_bootstrap_95_low": lo,
        "cluster_bootstrap_95_high": hi,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=str(DEFAULT_CACHE))
    ap.add_argument("--result-dir", default=str(RESULT_DIR))
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--target", type=float, default=0.04)
    ap.add_argument("--stop", type=float, default=-0.025)
    ap.add_argument("--participation", type=float, default=0.0005)
    args = ap.parse_args()

    raw_panel = load_panel(Path(args.cache))
    pit = bool(raw_panel.get("point_in_time_universe", pd.Series([False])).fillna(False).astype(bool).all())
    source_values = sorted(set(raw_panel["source"].dropna().astype(str))) if "source" in raw_panel else ["unknown"]
    panel = add_features(raw_panel)
    out_dir = Path(args.result_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "judge_version": "KR-KOSPI-JUDGE-v1.0",
        "judge_eligible": pit,
        "result_class": "JUDGE" if pit else "SMOKE_NONPIT",
        "point_in_time_universe": pit,
        "survivorship_bias_possible": not pit,
        "source": source_values,
        "data_start": str(panel["decision_date"].min().date()),
        "data_end": str(panel["decision_date"].max().date()),
        "rows": int(len(panel)),
        "symbols": int(panel["symbol"].nunique()),
        "strategies": {},
        "portfolio_policy": {
            "initial_equity": 1.0,
            "daily_cohort_fraction": 1.0 / args.horizon,
            "allocation_within_cohort": "equal_weight",
            "active_symbol_selection": "exclude_then_backfill_next_rank",
            "cost_timing": "round_trip_cost_split_50_50_entry_exit",
            "marking": "daily_close_until_realized_exit_price",
        },
        "assumptions": {
            "entry": "next_regular_open",
            "horizon_sessions": args.horizon,
            "target_return": args.target,
            "stop_return": args.stop,
            "bottom_liquidity_excluded": 0.20,
            "participation_ADV": args.participation,
            "ambiguous_same_day_target_stop": "stop_first_conservative_primary",
            "gap_through_stop": "next/open executable price",
        },
    }

    for strategy in ["momentum5", "momentum20", "momentum20_liquidity"]:
        signal_records, executable_records, diag = run_strategy(
            panel, strategy, top_k=args.top_k, horizon=args.horizon,
            target_return=args.target, stop_return=args.stop, participation=args.participation,
        )
        eval_start = min((r.entry_day for r in executable_records), default=None)
        eval_end = max((r.exit_day for r in executable_records), default=None)
        portfolio_path, portfolio_summary = simulate_portfolio(
            raw_panel, executable_records, horizon=args.horizon, initial_equity=1.0,
            daily_cohort_fraction=1.0 / args.horizon, suppress_duplicate_symbols=False,
            evaluation_start=eval_start, evaluation_end=eval_end,
        )
        report["strategies"][strategy] = {
            "signal_set": _metric_block(signal_records),
            "executable_set": _metric_block(executable_records),
            "portfolio": summary_dict(portfolio_summary),
            **diag,
        }
        pd.DataFrame([asdict(r) for r in signal_records]).to_csv(out_dir / f"{strategy}_signals.csv", index=False)
        pd.DataFrame([asdict(r) for r in executable_records]).to_csv(out_dir / f"{strategy}_executed.csv", index=False)
        portfolio_path.to_csv(out_dir / f"{strategy}_portfolio.csv", index=False)

    if not pit:
        report["warning"] = "Smoke metrics are pipeline diagnostics only; do not use for strategy selection or performance claims."
    (out_dir / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
