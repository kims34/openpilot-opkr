"""Run IndexAlert KR-KOSPI Judge v1 baseline research on cached PIT KRX data."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from research_v1_core import Bar, AmbiguousFirstHit, cost_model_return, date_cluster_bootstrap_mean, economic_outcome, summarize
from research_v1_krx import DEFAULT_CACHE, load_panel


RESULT_DIR = Path("research_results")


def add_features(panel: pd.DataFrame) -> pd.DataFrame:
    x = panel.copy().sort_values(["symbol", "decision_date"])
    g = x.groupby("symbol", group_keys=False)
    x["ret5"] = g["close"].pct_change(5)
    x["ret20"] = g["close"].pct_change(20)
    x["vol20"] = g["close"].pct_change().groupby(x["symbol"]).rolling(20).std(ddof=0).reset_index(level=0, drop=True)
    x["adv20"] = g["value"].rolling(20).median().reset_index(level=0, drop=True)
    return x


def _rank_day(day: pd.DataFrame, strategy: str) -> pd.DataFrame:
    d = day.copy()
    d = d.dropna(subset=["ret5", "ret20", "adv20", "vol20"])
    if d.empty:
        return d
    # Primary universe rule: exclude bottom 20% by trailing median value.
    liq_cut = d["adv20"].quantile(0.20)
    d = d[d["adv20"] >= liq_cut]
    if strategy == "momentum5":
        d["score"] = d["ret5"]
    elif strategy == "momentum20":
        d["score"] = d["ret20"]
    elif strategy == "momentum20_liquidity":
        # Preserve simple interpretability: average cross-sectional percentile ranks.
        d["score"] = 0.8 * d["ret20"].rank(pct=True) + 0.2 * d["adv20"].rank(pct=True)
    else:
        raise ValueError(strategy)
    return d.sort_values("score", ascending=False)


def build_lookup(panel: pd.DataFrame):
    dates = sorted(panel["decision_date"].drop_duplicates())
    date_to_pos = {pd.Timestamp(d): i for i, d in enumerate(dates)}
    by_symbol = {s: g.set_index("decision_date").sort_index() for s, g in panel.groupby("symbol")}
    return dates, date_to_pos, by_symbol


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
    records = []
    ambiguous = 0
    skipped = 0
    for decision_date, day in panel.groupby("decision_date", sort=True):
        ranked = _rank_day(day, strategy)
        if ranked.empty:
            continue
        for _, row in ranked.head(top_k).iterrows():
            symbol = row["symbol"]
            pos = date_to_pos[pd.Timestamp(decision_date)]
            if pos + 1 >= len(dates):
                continue
            future_dates = dates[pos + 1: pos + 1 + horizon]
            if len(future_dates) < horizon:
                continue
            hist = by_symbol.get(symbol)
            if hist is None:
                skipped += 1
                continue
            # Entry is next regular-session open; no same-close fantasy fill.
            try:
                entry_row = hist.loc[pd.Timestamp(future_dates[0])]
            except KeyError:
                skipped += 1
                continue
            future = []
            valid = True
            for d in future_dates:
                try:
                    r = hist.loc[pd.Timestamp(d)]
                except KeyError:
                    valid = False
                    break
                future.append(Bar(
                    day=pd.Timestamp(d).date(), open=float(r.open), high=float(r.high), low=float(r.low),
                    close=float(r.close), volume=float(r.volume), value=float(r.value),
                ))
            if not valid:
                skipped += 1
                continue
            cost = cost_model_return(
                half_spread_bps=half_spread_bps,
                tax_commission_bps=explicit_bps,
                volatility=float(row["vol20"]),
                participation=participation,
                impact_coefficient=impact_coefficient,
            )
            try:
                rec = economic_outcome(
                    decision_day=pd.Timestamp(decision_date).date(), symbol=symbol, score=float(row["score"]),
                    entry_price=float(entry_row.open), future_bars=future,
                    target_return=target_return, stop_return=stop_return, round_trip_cost_return=cost,
                )
            except AmbiguousFirstHit:
                ambiguous += 1
                continue
            records.append(rec)
    return records, {"ambiguous": ambiguous, "skipped": skipped}


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

    panel = add_features(load_panel(Path(args.cache)))
    out_dir = Path(args.result_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "judge_version": "KR-KOSPI-JUDGE-v1.0",
        "data_start": str(panel["decision_date"].min().date()),
        "data_end": str(panel["decision_date"].max().date()),
        "rows": int(len(panel)),
        "strategies": {},
        "assumptions": {
            "entry": "next_regular_open",
            "horizon_sessions": args.horizon,
            "target_return": args.target,
            "stop_return": args.stop,
            "bottom_liquidity_excluded": 0.20,
            "participation_ADV": args.participation,
            "ambiguous_same_day_target_stop": "exclude_primary",
            "gap_through_stop": "next/open executable price",
        },
    }

    for strategy in ["momentum5", "momentum20", "momentum20_liquidity"]:
        records, diag = run_strategy(
            panel, strategy, top_k=args.top_k, horizon=args.horizon,
            target_return=args.target, stop_return=args.stop, participation=args.participation,
        )
        metrics = summarize(records)
        point, lo, hi = date_cluster_bootstrap_mean(records)
        report["strategies"][strategy] = {
            **asdict(metrics),
            "cluster_bootstrap_mean": point,
            "cluster_bootstrap_95_low": lo,
            "cluster_bootstrap_95_high": hi,
            **diag,
        }
        pd.DataFrame([asdict(r) for r in records]).to_csv(out_dir / f"{strategy}_trades.csv", index=False)

    (out_dir / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
