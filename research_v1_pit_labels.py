"""PIT-specific supervised label construction for IndexAlert Research v1.

Key property: a security is never removed from training/selection because we
learned from the future that one of its later daily bars disappeared. Entry-day
absence is a genuine no-fill. If a bar disappears *after* entry, the preliminary
research path records a conservative stop-like loss on the first missing market
session and surfaces the count explicitly. Final Judge work must later replace
this approximation with security-master delisting/halt economics.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd

from research_v1_core import (
    AmbiguousFirstHit,
    Bar,
    DecisionRecord,
    cost_model_return,
    economic_outcome,
)
from run_research_v1 import add_features, build_lookup

FEATURES = [
    "ret1", "ret5", "ret20", "vol20", "log_adv20",
    "ret5_rank", "ret20_rank", "vol20_rank", "adv20_rank",
]


def _synthetic_missing_future_stop(
    *, decision_day, entry_day, missing_day, symbol, score, entry_price,
    horizon, target_return, stop_return, cost_return,
) -> DecisionRecord:
    """Conservative preliminary treatment for an unresolved post-entry data gap.

    The economic exit is booked at the planned stop, not at zero. This avoids
    future-information deletion while remaining explicitly preliminary. A final
    Judge must replace this approximation with actual delisting/halt economics.
    """
    exit_price = float(entry_price) * (1.0 + float(stop_return))
    gross = float(stop_return)
    return DecisionRecord(
        decision_day=decision_day,
        entry_day=entry_day,
        symbol=str(symbol),
        score=float(score),
        entry_price=float(entry_price),
        horizon=int(horizon),
        target_return=float(target_return),
        stop_return=float(stop_return),
        cost_return=float(cost_return),
        outcome="STOP_DATA_GAP",
        gross_return=gross,
        net_return=gross - float(cost_return),
        exit_day=missing_day,
        exit_price=exit_price,
    )


def make_pit_supervised(
    raw_panel: pd.DataFrame,
    horizon: int = 5,
    target_return: float = 0.04,
    stop_return: float = -0.025,
    half_spread_bps: float = 4.0,
    explicit_bps: float = 23.0,
    participation: float = 0.0005,
    impact_coefficient: float = 0.10,
):
    x = add_features(raw_panel)
    x["log_adv20"] = np.log1p(x["adv20"].clip(lower=0))
    for col in ["ret5", "ret20", "vol20", "adv20"]:
        x[f"{col}_rank"] = x.groupby("decision_date")[col].rank(pct=True)

    dates, date_to_pos, by_symbol = build_lookup(x)
    rows = []
    record_map = {}
    diagnostics = {
        "ambiguous_same_bar": 0,
        "entry_no_fill": 0,
        "post_entry_missing_future_bar_conservative_stop": 0,
        "insufficient_global_future_horizon": 0,
        "eligible_rows_with_labels": 0,
        "ambiguity_policy": "stop_first_conservative",
        "post_entry_gap_policy": "planned_stop_on_first_missing_market_session_preliminary",
    }

    for row in x.itertuples(index=False):
        vals = [getattr(row, f) for f in FEATURES]
        if any(pd.isna(v) for v in vals):
            continue
        decision_ts = pd.Timestamp(row.decision_date)
        pos = date_to_pos[decision_ts]
        future_dates = dates[pos + 1: pos + 1 + horizon]
        if len(future_dates) < horizon:
            diagnostics["insufficient_global_future_horizon"] += 1
            continue

        hist = by_symbol.get(row.symbol)
        if hist is None:
            diagnostics["entry_no_fill"] += 1
            continue
        entry_ts = pd.Timestamp(future_dates[0])
        try:
            entry_row = hist.loc[entry_ts]
        except KeyError:
            # If it cannot trade at the planned next-open entry, there is no fill.
            diagnostics["entry_no_fill"] += 1
            continue

        cost = cost_model_return(
            half_spread_bps, explicit_bps, float(row.vol20), participation,
            impact_coefficient,
        )
        future = []
        first_missing_ts = None
        for d in future_dates:
            dts = pd.Timestamp(d)
            try:
                r = hist.loc[dts]
            except KeyError:
                first_missing_ts = dts
                break
            future.append(Bar(
                day=dts.date(), open=float(r.open), high=float(r.high),
                low=float(r.low), close=float(r.close), volume=float(r.volume),
                value=float(r.value),
            ))

        decision_day = decision_ts.date()
        entry_day = entry_ts.date()
        symbol = str(row.symbol)
        score = 0.0
        if first_missing_ts is not None:
            diagnostics["post_entry_missing_future_bar_conservative_stop"] += 1
            rec = _synthetic_missing_future_stop(
                decision_day=decision_day,
                entry_day=entry_day,
                missing_day=first_missing_ts.date(),
                symbol=symbol,
                score=score,
                entry_price=float(entry_row.open),
                horizon=horizon,
                target_return=target_return,
                stop_return=stop_return,
                cost_return=cost,
            )
            was_ambiguous = False
        else:
            kwargs = dict(
                decision_day=decision_day, symbol=symbol, score=score,
                entry_price=float(entry_row.open), future_bars=future,
                target_return=target_return, stop_return=stop_return,
                round_trip_cost_return=cost,
            )
            try:
                rec = economic_outcome(**kwargs)
                was_ambiguous = False
            except AmbiguousFirstHit:
                diagnostics["ambiguous_same_bar"] += 1
                rec = economic_outcome(**kwargs, ambiguous_policy="stop_first")
                was_ambiguous = True

        key = (decision_day, symbol)
        record_map[key] = rec
        item = {
            "decision_date": decision_ts,
            "symbol": symbol,
            "label_positive_net": int(rec.net_return > 0),
            "net_return": float(rec.net_return),
            "ambiguous_same_bar": bool(was_ambiguous),
            "post_entry_missing_future": bool(first_missing_ts is not None),
        }
        item.update({f: float(getattr(row, f)) for f in FEATURES})
        rows.append(item)
        diagnostics["eligible_rows_with_labels"] += 1

    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame = frame.sort_values(["decision_date", "symbol"]).reset_index(drop=True)
    return frame, record_map, diagnostics
