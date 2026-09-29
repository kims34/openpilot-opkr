"""Daily mark-to-market portfolio simulator for IndexAlert Research v1.

This converts overlapping trade candidates into an explicit capital path. The
v1 policy uses one horizon-sized sleeve per entry day: with a 5-session horizon,
up to 20% of current equity is allocated to that day's accepted candidates,
equal-weighted within the sleeve. Existing symbols are not pyramided while open.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from math import sqrt
from typing import Sequence

import numpy as np
import pandas as pd

from research_v1_core import DecisionRecord, expected_shortfall


@dataclass
class _Lot:
    record: DecisionRecord
    shares: float
    entry_notional: float


@dataclass(frozen=True)
class PortfolioSummary:
    sessions: int
    start_equity: float
    end_equity: float
    total_return: float
    cagr_252: float
    max_drawdown: float
    daily_expected_shortfall_95: float
    daily_expected_shortfall_99: float
    annualized_volatility: float
    sharpe_0rf: float
    average_cash_weight: float
    average_gross_exposure: float
    max_concurrent_positions: int
    entries_executed: int
    duplicate_entries_suppressed: int
    insufficient_cash_entries: int


def _mdd_from_equity(values: Sequence[float]) -> float:
    peak = -np.inf
    worst = 0.0
    for value in values:
        v = float(value)
        peak = max(peak, v)
        if peak > 0:
            worst = min(worst, v / peak - 1.0)
    return float(worst)


def filter_executable_records(
    records: Sequence[DecisionRecord],
    suppress_duplicate_symbols: bool = True,
) -> tuple[list[DecisionRecord], int]:
    """Return the exact signal records eligible to become portfolio entries.

    A symbol already open at the start of an entry day cannot be pyramided. If
    the existing lot exits later on that same day, the new entry is still
    suppressed because the portfolio simulator enters before processing exits.
    """
    ordered = sorted(records, key=lambda r: (r.entry_day, -float(r.score), r.symbol))
    if not suppress_duplicate_symbols:
        return list(ordered), 0
    active_until: dict[str, date] = {}
    kept: list[DecisionRecord] = []
    skipped = 0
    for rec in ordered:
        prev_exit = active_until.get(rec.symbol)
        if prev_exit is not None and prev_exit >= rec.entry_day:
            skipped += 1
            continue
        kept.append(rec)
        active_until[rec.symbol] = rec.exit_day
    return kept, skipped


def simulate_portfolio(
    panel: pd.DataFrame,
    records: Sequence[DecisionRecord],
    horizon: int,
    initial_equity: float = 1.0,
    daily_cohort_fraction: float | None = None,
    suppress_duplicate_symbols: bool = True,
    evaluation_start: date | None = None,
    evaluation_end: date | None = None,
) -> tuple[pd.DataFrame, PortfolioSummary]:
    if horizon <= 0:
        raise ValueError("horizon must be positive")
    if initial_equity <= 0:
        raise ValueError("initial_equity must be positive")
    if daily_cohort_fraction is None:
        daily_cohort_fraction = 1.0 / horizon
    if not 0 < daily_cohort_fraction <= 1:
        raise ValueError("daily_cohort_fraction must be in (0,1]")

    p = panel.copy()
    p["decision_date"] = pd.to_datetime(p["decision_date"])
    all_sessions = sorted({pd.Timestamp(x).date() for x in p["decision_date"].unique()})
    if not all_sessions:
        raise RuntimeError("panel has no sessions")

    filtered_records, prefiltered_duplicates = filter_executable_records(
        records, suppress_duplicate_symbols=suppress_duplicate_symbols
    )

    if evaluation_start is None:
        evaluation_start = min((r.entry_day for r in filtered_records), default=all_sessions[0])
    if evaluation_end is None:
        evaluation_end = max((r.exit_day for r in filtered_records), default=evaluation_start)
    if evaluation_end < evaluation_start:
        raise ValueError("evaluation_end precedes evaluation_start")
    sessions = [d for d in all_sessions if evaluation_start <= d <= evaluation_end]
    if not sessions:
        empty = pd.DataFrame(columns=["date", "equity", "cash", "cash_weight", "gross_exposure", "positions", "daily_return"])
        summary = PortfolioSummary(
            sessions=0,
            start_equity=float(initial_equity),
            end_equity=float(initial_equity),
            total_return=0.0,
            cagr_252=0.0,
            max_drawdown=0.0,
            daily_expected_shortfall_95=0.0,
            daily_expected_shortfall_99=0.0,
            annualized_volatility=0.0,
            sharpe_0rf=0.0,
            average_cash_weight=1.0,
            average_gross_exposure=0.0,
            max_concurrent_positions=0,
            entries_executed=0,
            duplicate_entries_suppressed=int(prefiltered_duplicates),
            insufficient_cash_entries=0,
        )
        return empty, summary

    close_map = {
        (pd.Timestamp(r.decision_date).date(), str(r.symbol)): float(r.close)
        for r in p.itertuples(index=False)
    }
    entries: dict[date, list[DecisionRecord]] = {}
    for rec in filtered_records:
        entries.setdefault(rec.entry_day, []).append(rec)
    for d in entries:
        entries[d].sort(key=lambda r: r.score, reverse=True)

    cash = float(initial_equity)
    active: list[_Lot] = []
    path: list[dict] = []
    prev_equity = float(initial_equity)
    cash_skips = 0
    entries_executed = 0
    max_positions = 0

    for day in sessions:
        todays = entries.get(day, [])

        # One daily sleeve, equal-weighted across today's accepted candidates.
        cohort_budget = prev_equity * daily_cohort_fraction
        per_trade_budget = cohort_budget / len(todays) if todays else 0.0
        for rec in todays:
            entry_cost_rate = max(0.0, rec.cost_return) / 2.0
            affordable_notional = cash / (1.0 + entry_cost_rate) if cash > 0 else 0.0
            notional = min(per_trade_budget, affordable_notional)
            if notional <= 1e-12:
                cash_skips += 1
                continue
            shares = notional / rec.entry_price
            cash -= notional * (1.0 + entry_cost_rate)
            active.append(_Lot(rec, shares, notional))
            entries_executed += 1

        # Intraday exits are realized before the end-of-day mark. Cost is split
        # 50/50 between entry and exit until market-specific fee timing is wired.
        survivors: list[_Lot] = []
        for lot in active:
            if lot.record.exit_day == day:
                exit_cost_rate = max(0.0, lot.record.cost_return) / 2.0
                gross_proceeds = lot.shares * lot.record.exit_price
                cash += gross_proceeds - lot.entry_notional * exit_cost_rate
            else:
                survivors.append(lot)
        active = survivors

        market_value = 0.0
        for lot in active:
            key = (day, lot.record.symbol)
            if key not in close_map:
                raise RuntimeError(f"missing mark price for {lot.record.symbol} on {day}")
            market_value += lot.shares * close_map[key]

        equity = cash + market_value
        cash_weight = cash / equity if equity > 0 else 0.0
        exposure = market_value / equity if equity > 0 else 0.0
        daily_return = equity / prev_equity - 1.0 if prev_equity > 0 else 0.0
        max_positions = max(max_positions, len(active))
        path.append({
            "date": day.isoformat(),
            "equity": equity,
            "cash": cash,
            "cash_weight": cash_weight,
            "gross_exposure": exposure,
            "positions": len(active),
            "daily_return": daily_return,
        })
        prev_equity = equity

    df = pd.DataFrame(path)
    end_equity = float(df.iloc[-1]["equity"])
    total_return = end_equity / initial_equity - 1.0
    n = len(df)
    cagr = (end_equity / initial_equity) ** (252.0 / max(1, n - 1)) - 1.0 if end_equity > 0 else -1.0
    dret = df["daily_return"].to_numpy(dtype=float)
    vol_daily = float(np.std(dret, ddof=1)) if len(dret) > 1 else 0.0
    vol_ann = vol_daily * sqrt(252.0)
    sharpe = float(np.mean(dret) / vol_daily * sqrt(252.0)) if vol_daily > 0 else 0.0
    summary = PortfolioSummary(
        sessions=n,
        start_equity=float(initial_equity),
        end_equity=end_equity,
        total_return=float(total_return),
        cagr_252=float(cagr),
        max_drawdown=_mdd_from_equity(df["equity"].tolist()),
        daily_expected_shortfall_95=expected_shortfall(dret.tolist(), 0.95),
        daily_expected_shortfall_99=expected_shortfall(dret.tolist(), 0.99),
        annualized_volatility=float(vol_ann),
        sharpe_0rf=sharpe,
        average_cash_weight=float(df["cash_weight"].mean()),
        average_gross_exposure=float(df["gross_exposure"].mean()),
        max_concurrent_positions=int(max_positions),
        entries_executed=int(entries_executed),
        duplicate_entries_suppressed=int(prefiltered_duplicates),
        insufficient_cash_entries=int(cash_skips),
    )
    return df, summary


def summary_dict(summary: PortfolioSummary) -> dict:
    return asdict(summary)
