"""IndexAlert Research v1 core.

PIT-first daily research engine for KOSPI and US equity experiments.
This module intentionally starts with simple baselines and executable economic
outcomes before any complex model is allowed into the tournament.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import isfinite, sqrt
from typing import Iterable, Sequence

import numpy as np


JUDGE_VERSION = "KR-KOSPI-JUDGE-v1.0"
RESEARCH_VERSION = "indexalert-research-v1.0"


@dataclass(frozen=True)
class Bar:
    day: date
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    value: float = 0.0

    def validate(self) -> None:
        vals = (self.open, self.high, self.low, self.close)
        if not all(isfinite(float(v)) and float(v) > 0 for v in vals):
            raise ValueError(f"invalid OHLC for {self.day}")
        if self.low > min(self.open, self.close) or self.high < max(self.open, self.close):
            raise ValueError(f"OHLC ordering violation for {self.day}")
        if self.low > self.high:
            raise ValueError(f"low > high for {self.day}")
        if self.volume < 0 or self.value < 0:
            raise ValueError(f"negative volume/value for {self.day}")


@dataclass(frozen=True)
class DecisionRecord:
    decision_day: date
    symbol: str
    score: float
    entry_price: float
    horizon: int
    target_return: float
    stop_return: float
    cost_return: float
    outcome: str
    gross_return: float
    net_return: float
    exit_day: date
    exit_price: float


@dataclass(frozen=True)
class MetricSummary:
    trades: int
    mean_gross_return: float
    mean_cost_return: float
    mean_net_return: float
    win_rate: float
    profit_factor: float
    trade_expected_shortfall_95: float
    target_rate: float
    stop_rate: float
    time_rate: float


class AmbiguousFirstHit(RuntimeError):
    pass


def pct_change(a: float, b: float) -> float:
    if a <= 0 or b <= 0:
        raise ValueError("prices must be positive")
    return b / a - 1.0


def momentum_score(bars: Sequence[Bar], lookback: int) -> float:
    if lookback <= 0 or len(bars) < lookback + 1:
        raise ValueError("not enough history")
    return pct_change(bars[-lookback - 1].close, bars[-1].close)


def liquidity_score(bars: Sequence[Bar], lookback: int = 20) -> float:
    if len(bars) < lookback:
        raise ValueError("not enough history")
    vals = [float(x.value or (x.close * x.volume)) for x in bars[-lookback:]]
    vals = [x for x in vals if isfinite(x) and x >= 0]
    if not vals:
        return 0.0
    return float(np.median(vals))


def realized_volatility(bars: Sequence[Bar], lookback: int = 20) -> float:
    if len(bars) < lookback + 1:
        raise ValueError("not enough history")
    closes = np.asarray([x.close for x in bars[-lookback - 1:]], dtype=float)
    rets = closes[1:] / closes[:-1] - 1.0
    return float(np.std(rets, ddof=0))


def classify_first_hit(
    future_bars: Sequence[Bar],
    entry_price: float,
    target_return: float,
    stop_return: float,
) -> tuple[str, Bar, float]:
    """Return TARGET/STOP/TIME using only information observable in the bars.

    If target and stop are both touched in the same daily bar, their order is
    unknowable from OHLC and the observation is explicitly AMBIGUOUS.
    Gap-through stops use the first executable open rather than the planned stop.
    """
    if not future_bars:
        raise ValueError("future_bars required")
    target = entry_price * (1.0 + target_return)
    stop = entry_price * (1.0 + stop_return)
    for bar in future_bars:
        bar.validate()
        if bar.open <= stop:
            return "STOP", bar, bar.open
        if bar.open >= target:
            return "TARGET", bar, bar.open
        hit_target = bar.high >= target
        hit_stop = bar.low <= stop
        if hit_target and hit_stop:
            raise AmbiguousFirstHit(f"both barriers touched on {bar.day}")
        if hit_target:
            return "TARGET", bar, target
        if hit_stop:
            return "STOP", bar, stop
    last = future_bars[-1]
    return "TIME", last, last.close


def economic_outcome(
    decision_day: date,
    symbol: str,
    score: float,
    entry_price: float,
    future_bars: Sequence[Bar],
    target_return: float,
    stop_return: float,
    round_trip_cost_return: float,
) -> DecisionRecord:
    outcome, exit_bar, exit_price = classify_first_hit(
        future_bars, entry_price, target_return, stop_return
    )
    gross = pct_change(entry_price, exit_price)
    net = gross - round_trip_cost_return
    return DecisionRecord(
        decision_day=decision_day,
        symbol=symbol,
        score=float(score),
        entry_price=float(entry_price),
        horizon=len(future_bars),
        target_return=float(target_return),
        stop_return=float(stop_return),
        cost_return=float(round_trip_cost_return),
        outcome=outcome,
        gross_return=float(gross),
        net_return=float(net),
        exit_day=exit_bar.day,
        exit_price=float(exit_price),
    )


def max_drawdown(returns: Sequence[float]) -> float:
    """Generic non-overlapping return-series MDD helper.

    Do not apply this directly to overlapping DecisionRecord rows. A real
    portfolio MDD requires a daily mark-to-market portfolio path and allocation
    policy. It remains here for that future portfolio simulator.
    """
    wealth = 1.0
    peak = 1.0
    worst = 0.0
    for r in returns:
        wealth *= 1.0 + float(r)
        peak = max(peak, wealth)
        dd = wealth / peak - 1.0
        worst = min(worst, dd)
    return float(worst)


def expected_shortfall(returns: Sequence[float], alpha: float = 0.95) -> float:
    if not returns:
        return 0.0
    xs = np.sort(np.asarray(returns, dtype=float))
    count = max(1, int(np.ceil((1.0 - alpha) * len(xs))))
    return float(np.mean(xs[:count]))


def summarize(records: Sequence[DecisionRecord]) -> MetricSummary:
    """Summarize trade-level outcomes only.

    Portfolio drawdown is intentionally excluded because these records can
    overlap in calendar time. Compounding them sequentially would create a
    fictitious portfolio path and grossly overstate drawdown.
    """
    if not records:
        return MetricSummary(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    net = np.asarray([x.net_return for x in records], dtype=float)
    gross = np.asarray([x.gross_return for x in records], dtype=float)
    costs = np.asarray([x.cost_return for x in records], dtype=float)
    gains = float(net[net > 0].sum())
    losses = float(-net[net < 0].sum())
    pf = gains / losses if losses > 0 else (float("inf") if gains > 0 else 0.0)
    outcomes = [x.outcome for x in records]
    n = len(records)
    return MetricSummary(
        trades=n,
        mean_gross_return=float(np.mean(gross)),
        mean_cost_return=float(np.mean(costs)),
        mean_net_return=float(np.mean(net)),
        win_rate=float(np.mean(net > 0)),
        profit_factor=float(pf),
        trade_expected_shortfall_95=expected_shortfall(net.tolist(), 0.95),
        target_rate=float(sum(x == "TARGET" for x in outcomes) / n),
        stop_rate=float(sum(x == "STOP" for x in outcomes) / n),
        time_rate=float(sum(x == "TIME" for x in outcomes) / n),
    )


def date_cluster_bootstrap_mean(
    records: Sequence[DecisionRecord],
    samples: int = 2000,
    seed: int = 20260928,
) -> tuple[float, float, float]:
    """Cluster bootstrap by decision date, not by stock row."""
    if not records:
        return 0.0, 0.0, 0.0
    by_day: dict[date, list[float]] = {}
    for row in records:
        by_day.setdefault(row.decision_day, []).append(row.net_return)
    days = sorted(by_day)
    day_means = np.asarray([np.mean(by_day[d]) for d in days], dtype=float)
    if len(day_means) == 1:
        m = float(day_means[0])
        return m, m, m
    rng = np.random.default_rng(seed)
    draws = np.empty(samples, dtype=float)
    for i in range(samples):
        idx = rng.integers(0, len(day_means), size=len(day_means))
        draws[i] = float(np.mean(day_means[idx]))
    point = float(np.mean(day_means))
    lo, hi = np.quantile(draws, [0.025, 0.975])
    return point, float(lo), float(hi)


def cost_model_return(
    half_spread_bps: float,
    tax_commission_bps: float,
    volatility: float,
    participation: float,
    impact_coefficient: float = 0.10,
) -> float:
    """Simple capacity-aware round-trip cost model.

    impact ~= c * sigma * sqrt(Q/ADV), applied conservatively to each side.
    Coefficient is a placeholder that must be estimated per market before a
    profitability claim is accepted by the Judge.
    """
    if participation < 0:
        raise ValueError("participation must be non-negative")
    explicit = (2.0 * half_spread_bps + tax_commission_bps) / 10000.0
    impact_one_way = impact_coefficient * max(0.0, volatility) * sqrt(participation)
    return float(explicit + 2.0 * impact_one_way)


def choose_top_k(
    scored: Iterable[tuple[str, float]],
    k: int = 3,
    minimum_score: float | None = None,
) -> list[tuple[str, float]]:
    rows = sorted(scored, key=lambda x: x[1], reverse=True)
    if minimum_score is not None:
        rows = [x for x in rows if x[1] >= minimum_score]
    return rows[: max(0, k)]
