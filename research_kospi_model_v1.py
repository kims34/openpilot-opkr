"""IndexAlert KOSPI research v1 model tournament.

Consumes the PIT daily database built by research_kospi_baseline.py and compares
simple momentum baselines with a deliberately small regularized logistic model.
The target is an executable next-session-open entry and 1/2/3/5-session close
exit.  Selection is cross-sectional TOP3 per decision date; evaluation includes
several round-trip cost stresses.

This is a research challenger, never a production trading signal.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import research_kospi_baseline as base

HORIZONS = (1, 2, 3, 5)
TRAIN_DAYS = 1260          # about five trading years
TEST_DAYS = 63             # about one quarter
PURGE_DAYS = 5
TOP_K = 3
BASE_COST = 0.0025
FEATURE_VERSION = "kospi-close-core-v1"
MODEL_VERSION = "logistic-l2-v1"

FEATURE_NAMES = (
    "mom1",
    "mom5",
    "mom20",
    "vol20",
    "downside_vol20",
    "intraday_return",
    "gap_from_prev_close",
    "value_surprise20",
    "mom20_rank",
    "liquidity_rank",
)


@dataclass
class Observation:
    decision_index: int
    decision_date: str
    ticker: str
    x: Tuple[float, ...]
    mom5: float
    mom20: float
    mom20_liq: float
    returns: Dict[int, float]


def _pct_rank(values: Dict[str, float]) -> Dict[str, float]:
    ordered = sorted(values.items(), key=lambda kv: (kv[1], kv[0]))
    if len(ordered) <= 1:
        return {k: 0.5 for k, _ in ordered}
    return {k: i / (len(ordered) - 1) for i, (k, _) in enumerate(ordered)}


def _std(xs: List[float]) -> float:
    return statistics.pstdev(xs) if len(xs) >= 2 else 0.0


def _median(xs: List[float]) -> float:
    return statistics.median(xs) if xs else 0.0


def _finite_tuple(xs):
    out = tuple(float(x) for x in xs)
    return out if all(math.isfinite(x) for x in out) else None


def build_observations(days: List[str], store: base.ResearchStore) -> List[Observation]:
    daily = {d: store.read_date(d) for d in days}
    history: Dict[str, List[Tuple[str, base.Bar]]] = defaultdict(list)
    observations: List[Observation] = []

    for i, d in enumerate(days):
        current = daily[d]
        raw = {}
        mom20_for_rank = {}
        liq_for_rank = {}

        for ticker, bar in current.items():
            rows = history.get(ticker, [])
            if len(rows) < 21:
                continue
            prev = rows[-1][1]
            if prev.close <= 0 or bar.open <= 0 or bar.close <= 0:
                continue

            closes = [r[1].close for r in rows[-21:]] + [bar.close]
            # Quarantine likely split/merger discontinuities until the CA layer is complete.
            bad_jump = any(a > 0 and abs(b / a - 1.0) >= 0.45 for a, b in zip(closes, closes[1:]))
            if bad_jump:
                continue

            rets20 = [closes[j] / closes[j - 1] - 1.0 for j in range(len(closes) - 20, len(closes))]
            downside = [min(0.0, r) for r in rets20]
            values20 = [r[1].value for r in rows[-20:]]
            median_value = _median(values20)
            if median_value <= 0:
                continue

            m1 = bar.close / prev.close - 1.0
            m5 = bar.close / rows[-5][1].close - 1.0
            m20 = bar.close / rows[-20][1].close - 1.0
            vol20 = _std(rets20)
            dvol20 = math.sqrt(sum(r * r for r in downside) / len(downside)) if downside else 0.0
            intraday = bar.close / bar.open - 1.0
            gap = bar.open / prev.close - 1.0
            value_surprise = bar.value / median_value - 1.0

            raw[ticker] = {
                "mom1": m1,
                "mom5": m5,
                "mom20": m20,
                "vol20": vol20,
                "downside_vol20": dvol20,
                "intraday_return": intraday,
                "gap_from_prev_close": gap,
                "value_surprise20": value_surprise,
                "median_value": median_value,
            }
            mom20_for_rank[ticker] = m20
            liq_for_rank[ticker] = math.log1p(median_value)

        if raw:
            liquidity_cut = base._percentile((v["median_value"] for v in raw.values()), 0.20)
            eligible = {t: v for t, v in raw.items() if v["median_value"] >= liquidity_cut}
            if len(eligible) >= TOP_K:
                r20 = _pct_rank({t: mom20_for_rank[t] for t in eligible})
                rliq = _pct_rank({t: liq_for_rank[t] for t in eligible})
                for ticker, f in eligible.items():
                    if i + 1 >= len(days):
                        continue
                    entry = daily[days[i + 1]].get(ticker)
                    if not entry or entry.open <= 0:
                        continue
                    outcome = {}
                    for h in HORIZONS:
                        exit_i = i + h
                        if exit_i >= len(days):
                            continue
                        exit_bar = daily[days[exit_i]].get(ticker)
                        if exit_bar and exit_bar.close > 0:
                            outcome[h] = exit_bar.close / entry.open - 1.0
                    if not outcome:
                        continue
                    x = _finite_tuple((
                        f["mom1"], f["mom5"], f["mom20"], f["vol20"],
                        f["downside_vol20"], f["intraday_return"],
                        f["gap_from_prev_close"], f["value_surprise20"],
                        r20[ticker], rliq[ticker],
                    ))
                    if x is None:
                        continue
                    observations.append(Observation(
                        decision_index=i,
                        decision_date=d,
                        ticker=ticker,
                        x=x,
                        mom5=f["mom5"],
                        mom20=f["mom20"],
                        mom20_liq=0.80 * r20[ticker] + 0.20 * rliq[ticker],
                        returns=outcome,
                    ))

        for ticker, bar in current.items():
            history[ticker].append((d, bar))

    return observations


def _summarize(vals: List[float]):
    if not vals:
        return {"n": 0}
    gains = sum(x for x in vals if x > 0)
    losses = -sum(x for x in vals if x < 0)
    pf = gains / losses if losses > 0 else None
    return {
        "n": len(vals),
        "mean": sum(vals) / len(vals),
        "median": statistics.median(vals),
        "precision_positive": sum(x > 0 for x in vals) / len(vals),
        "profit_factor": pf,
        "p10": base._percentile(vals, 0.10),
        "p90": base._percentile(vals, 0.90),
    }


def _max_dd(daily: List[float]):
    return base._max_drawdown(daily) if daily else None


def _brier(prob: List[float], y: List[int]):
    return sum((p - yy) ** 2 for p, yy in zip(prob, y)) / len(y) if y else None


def _model():
    return Pipeline([
        ("scale", StandardScaler()),
        ("lr", LogisticRegression(C=0.25, penalty="l2", solver="lbfgs", max_iter=300)),
    ])


def walk_forward(days: List[str], observations: List[Observation]):
    by_index: Dict[int, List[Observation]] = defaultdict(list)
    for o in observations:
        by_index[o.decision_index].append(o)

    first_test = TRAIN_DAYS + PURGE_DAYS
    fold_starts = list(range(first_test, max(first_test, len(days) - 1), TEST_DAYS))
    trade_returns = {
        name: {h: {cost: [] for cost in base.COST_SCENARIOS} for h in HORIZONS}
        for name in ("mom5", "mom20", "mom20_liq", "logistic")
    }
    portfolio_returns = {
        name: {h: {cost: [] for cost in base.COST_SCENARIOS} for h in HORIZONS}
        for name in trade_returns
    }
    brier_rows = {h: {"p": [], "y": []} for h in HORIZONS}
    folds = []

    for fold_no, test_start in enumerate(fold_starts, 1):
        test_end = min(test_start + TEST_DAYS, len(days) - 1)
        train_end = test_start - PURGE_DAYS
        train_start = max(21, train_end - TRAIN_DAYS)
        if train_end - train_start < TRAIN_DAYS * 0.90:
            continue

        train_obs = [o for idx in range(train_start, train_end) for o in by_index.get(idx, [])]
        test_indices = range(test_start, test_end)
        if not train_obs:
            continue

        models = {}
        for h in HORIZONS:
            usable = [o for o in train_obs if h in o.returns]
            X = [o.x for o in usable]
            y = [1 if o.returns[h] - BASE_COST > 0 else 0 for o in usable]
            if len(X) < 5000 or len(set(y)) < 2:
                continue
            m = _model()
            m.fit(X, y)
            models[h] = m

        if not models:
            continue

        folds.append({
            "fold": fold_no,
            "train_from": days[train_start],
            "train_to": days[train_end - 1],
            "test_from": days[test_start],
            "test_to": days[test_end - 1],
            "train_rows": len(train_obs),
        })

        for idx in test_indices:
            rows = by_index.get(idx, [])
            if len(rows) < TOP_K:
                continue
            baseline_scores = {
                "mom5": {o.ticker: o.mom5 for o in rows},
                "mom20": {o.ticker: o.mom20 for o in rows},
                "mom20_liq": {o.ticker: o.mom20_liq for o in rows},
            }
            by_ticker = {o.ticker: o for o in rows}

            for h, m in models.items():
                valid = [o for o in rows if h in o.returns]
                if len(valid) < TOP_K:
                    continue
                probs = m.predict_proba([o.x for o in valid])[:, 1].tolist()
                prob_map = {o.ticker: p for o, p in zip(valid, probs)}
                y_all = [1 if o.returns[h] - BASE_COST > 0 else 0 for o in valid]
                brier_rows[h]["p"].extend(probs)
                brier_rows[h]["y"].extend(y_all)

                score_maps = dict(baseline_scores)
                score_maps["logistic"] = prob_map
                for name, smap in score_maps.items():
                    candidates = [t for t in smap if t in by_ticker and h in by_ticker[t].returns]
                    top = sorted(candidates, key=lambda t: (smap[t], t), reverse=True)[:TOP_K]
                    if not top:
                        continue
                    for cost_name, cost in base.COST_SCENARIOS.items():
                        vals = [by_ticker[t].returns[h] - cost for t in top]
                        trade_returns[name][h][cost_name].extend(vals)
                        portfolio_returns[name][h][cost_name].append(sum(vals) / len(vals))

    report = {"models": {}, "brier": {}, "folds": folds}
    for name in trade_returns:
        report["models"][name] = {"horizons": {}}
        for h in HORIZONS:
            report["models"][name]["horizons"][str(h)] = {}
            for cost_name in base.COST_SCENARIOS:
                trades = trade_returns[name][h][cost_name]
                daily = portfolio_returns[name][h][cost_name]
                report["models"][name]["horizons"][str(h)][cost_name] = {
                    **_summarize(trades),
                    "portfolio_days": len(daily),
                    "mean_portfolio_daily": sum(daily) / len(daily) if daily else None,
                    "precision_positive_days": sum(x > 0 for x in daily) / len(daily) if daily else None,
                    "max_drawdown": _max_dd(daily),
                    "compounded_portfolio_return": math.prod(1.0 + x for x in daily) - 1.0 if daily else None,
                }
    for h in HORIZONS:
        report["brier"][str(h)] = {
            "all_universe": _brier(brier_rows[h]["p"], brier_rows[h]["y"]),
            "n": len(brier_rows[h]["y"]),
            "base_rate": (sum(brier_rows[h]["y"]) / len(brier_rows[h]["y"])) if brier_rows[h]["y"] else None,
        }
    return report


def run(from_date: str, to_date: str, db_path: str):
    start, end = base._ymd(from_date), base._ymd(to_date)
    store = base.ResearchStore(db_path)
    days, build = base.build_dataset(start, end, store)
    observations = build_observations(days, store)
    result = walk_forward(days, observations)
    result.update({
        "market": "KOSPI",
        "from_date": start,
        "to_date": end,
        "trading_days": len(days),
        "observation_rows": len(observations),
        "feature_version": FEATURE_VERSION,
        "feature_names": list(FEATURE_NAMES),
        "model_version": MODEL_VERSION,
        "train_days": TRAIN_DAYS,
        "test_days": TEST_DAYS,
        "purge_days": PURGE_DAYS,
        "top_k": TOP_K,
        "base_label_cost": BASE_COST,
        "cost_scenarios": base.COST_SCENARIOS,
        "data_build": build,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "limitations": [
            "This stage tests daily close features and next-open execution only; +5/+15 minute entry requires intraday history.",
            "Corporate-action windows with >=45% raw discontinuity are quarantined rather than reconstructed.",
            "Cost scenarios are stress assumptions, not yet broker-specific realized transaction-cost estimates.",
            "No abstention gate is applied yet; this is a ranking/model tournament stage.",
        ],
    })
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--from-date", default="20180102")
    p.add_argument("--to-date", default="20260925")
    p.add_argument("--db", default=base.DEFAULT_DB)
    p.add_argument("--output", default="")
    args = p.parse_args()
    payload = run(args.from_date, args.to_date, args.db)
    text = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
