"""PIT-specific label construction for IndexAlert Research v1.

Decision-time candidates are retained even when the next regular open later turns
out to be unavailable. Such rows have features and `entry_fillable=False` but no
training label. This prevents future knowledge of a no-fill from changing the
ranking that existed on the decision day. Training uses labelled rows only;
replay ranks all decision-time rows and leaves a slot empty when a selected name
cannot fill.

If a bar disappears after a successful entry, PIT Preliminary books a
conservative planned-stop loss at the first missing market session. Final Judge
work must replace that approximation with exact delisting/halt economics.

The default same-bar ambiguity policy remains conservative stop-first.  An
explicit target-first option exists only to measure an optimistic upper bound;
it must never be treated as executable evidence without intraday first-hit data.

KOSPI statutory sell taxes are applied by entry year for historical fidelity.
Round-trip broker commission is a separate parameter.  `explicit_bps` remains as
an override for controlled sensitivity experiments only.
"""
from __future__ import annotations

from collections import Counter

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


def kospi_statutory_sell_tax_bps(day) -> float:
    """Historical KOSPI sell-side statutory tax in basis points.

    Includes securities transaction tax plus the 15bp rural special tax.
    Schedule used by the current research range:
      2021-2022: 8bp + 15bp = 23bp
      2023:      5bp + 15bp = 20bp
      2024:      3bp + 15bp = 18bp
      2025:      0bp + 15bp = 15bp
      2026:      5bp + 15bp = 20bp
    For dates after 2026 the current 2026 statutory rate is carried forward only
    as a placeholder and must be re-verified before any future-date Judge run.
    """
    year = pd.Timestamp(day).year
    if year <= 2020:
        raise ValueError(f"KOSPI statutory tax schedule not encoded before 2021: {day}")
    if year <= 2022:
        return 23.0
    if year == 2023:
        return 20.0
    if year == 2024:
        return 18.0
    if year == 2025:
        return 15.0
    return 20.0


def _synthetic_missing_future_stop(
    *, decision_day, entry_day, missing_day, symbol, score, entry_price,
    horizon, target_return, stop_return, cost_return,
) -> DecisionRecord:
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


def _feature_item(row, decision_ts, symbol: str) -> dict:
    item = {
        "decision_date": decision_ts,
        "symbol": symbol,
    }
    item.update({f: float(getattr(row, f)) for f in FEATURES})
    return item


def make_pit_supervised(
    raw_panel: pd.DataFrame,
    horizon: int = 5,
    target_return: float = 0.04,
    stop_return: float = -0.025,
    half_spread_bps: float = 4.0,
    explicit_bps: float | None = None,
    commission_round_trip_bps: float = 3.0,
    participation: float = 0.0005,
    impact_coefficient: float = 0.10,
    ambiguity_resolution_policy: str = "stop_first",
):
    if ambiguity_resolution_policy not in {"stop_first", "target_first"}:
        raise ValueError("ambiguity_resolution_policy must be stop_first or target_first")
    if commission_round_trip_bps < 0:
        raise ValueError("commission_round_trip_bps must be non-negative")

    x = add_features(raw_panel)
    x["log_adv20"] = np.log1p(x["adv20"].clip(lower=0))
    for col in ["ret5", "ret20", "vol20", "adv20"]:
        x[f"{col}_rank"] = x.groupby("decision_date")[col].rank(pct=True)

    dates, date_to_pos, by_symbol = build_lookup(x)
    rows = []
    record_map = {}
    explicit_cost_counts: Counter[str] = Counter()
    diagnostics = {
        "ambiguous_same_bar": 0,
        "entry_no_fill": 0,
        "entry_no_fill_retained_in_decision_universe": 0,
        "post_entry_missing_future_bar_conservative_stop": 0,
        "insufficient_global_future_horizon": 0,
        "eligible_rows_with_labels": 0,
        "eligible_rows_without_label_no_fill": 0,
        "ambiguity_policy": (
            "stop_first_conservative" if ambiguity_resolution_policy == "stop_first"
            else "target_first_optimistic_upper_bound_only"
        ),
        "entry_no_fill_policy": "retain_for_ranking_leave_slot_empty_no_retroactive_backfill",
        "post_entry_gap_policy": "planned_stop_on_first_missing_market_session_preliminary",
        "cost_policy": (
            "fixed_explicit_bps_override" if explicit_bps is not None
            else "historical_KOSPI_statutory_sell_tax_by_entry_year_plus_round_trip_commission"
        ),
        "half_spread_bps_one_way": float(half_spread_bps),
        "commission_round_trip_bps": float(commission_round_trip_bps),
        "fixed_explicit_bps_override": float(explicit_bps) if explicit_bps is not None else None,
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

        symbol = str(row.symbol)
        item = _feature_item(row, decision_ts, symbol)
        hist = by_symbol.get(row.symbol)
        entry_ts = pd.Timestamp(future_dates[0])
        if hist is None:
            entry_row = None
        else:
            try:
                entry_row = hist.loc[entry_ts]
            except KeyError:
                entry_row = None

        if entry_row is None:
            diagnostics["entry_no_fill"] += 1
            diagnostics["entry_no_fill_retained_in_decision_universe"] += 1
            diagnostics["eligible_rows_without_label_no_fill"] += 1
            item.update({
                "label_positive_net": np.nan,
                "net_return": np.nan,
                "label_available": False,
                "entry_fillable": False,
                "ambiguous_same_bar": False,
                "post_entry_missing_future": False,
            })
            rows.append(item)
            continue

        if explicit_bps is None:
            statutory_bps = kospi_statutory_sell_tax_bps(entry_ts)
            applied_explicit_bps = statutory_bps + float(commission_round_trip_bps)
            explicit_cost_counts[f"{entry_ts.year}:{applied_explicit_bps:.1f}"] += 1
        else:
            applied_explicit_bps = float(explicit_bps)
            explicit_cost_counts[f"override:{applied_explicit_bps:.1f}"] += 1

        cost = cost_model_return(
            half_spread_bps,
            applied_explicit_bps,
            float(row.vol20),
            participation,
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
                rec = economic_outcome(
                    **kwargs,
                    ambiguous_policy=ambiguity_resolution_policy,
                )
                was_ambiguous = True

        key = (decision_day, symbol)
        record_map[key] = rec
        item.update({
            "label_positive_net": int(rec.net_return > 0),
            "net_return": float(rec.net_return),
            "label_available": True,
            "entry_fillable": True,
            "ambiguous_same_bar": bool(was_ambiguous),
            "post_entry_missing_future": bool(first_missing_ts is not None),
        })
        rows.append(item)
        diagnostics["eligible_rows_with_labels"] += 1

    diagnostics["applied_explicit_cost_bps_counts"] = dict(sorted(explicit_cost_counts.items()))
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame = frame.sort_values(["decision_date", "symbol"]).reset_index(drop=True)
    return frame, record_map, diagnostics
