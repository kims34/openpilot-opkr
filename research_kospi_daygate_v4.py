"""IndexAlert KOSPI v4: genuine day-level abstention gate.

V3 showed that an all-stock 99th-percentile score threshold still admitted
nearly every day because hundreds of names are screened. V4 therefore freezes a
threshold from the *distribution of each training day's maximum model score*.
A future test day is active only when at least one stock exceeds that frozen
threshold. On active days up to three names above threshold are admitted; on all
other days the policy explicitly returns NO TRADE.

Activation quantiles 90/95/99% are predeclared as separate research trials.
Coverage-matched controls trade the same number of names on the same dates using
mom20+liquidity and rev20+liquidity rankings.

Development evidence only: 2018-2026 has already been inspected.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import statistics
from datetime import datetime, timezone
from typing import List

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import research_kospi_clean_v2 as v2

DAY_ACTIVE_RATES = (0.10, 0.05, 0.01)  # threshold at train daily-max q90/q95/q99
CONTROLS = ("mom20_liq", "rev20_liq")
COSTS = v2.COSTS


def make_model():
    return Pipeline([
        ("scale", StandardScaler()),
        ("lr", LogisticRegression(C=0.25, penalty="l2", solver="lbfgs", max_iter=300)),
    ])


def block_boot_ci(vals: List[float], seed: int = 20260928, block: int = 5, draws: int = 1000):
    if len(vals) < 30:
        return [None, None]
    rng = random.Random(seed)
    n = len(vals)
    starts = list(range(max(1, n - block + 1)))
    means = []
    for _ in range(draws):
        sample = []
        while len(sample) < n:
            s = rng.choice(starts)
            sample.extend(vals[s:s + block])
        means.append(statistics.fmean(sample[:n]))
    means.sort()
    return [means[int(0.025 * draws)], means[min(draws - 1, int(0.975 * draws))]]


def summarize(trades, day_returns, eligible_days, counts, fold_means):
    if not day_returns:
        return {"trades": 0, "eligible_days": eligible_days, "trade_days": 0, "coverage_trade_days": 0.0}
    vals = [float(x) for x in trades]
    days = [float(x) for x in day_returns]
    gains = sum(x for x in vals if x > 0)
    losses = -sum(x for x in vals if x < 0)
    return {
        "trades": len(vals),
        "eligible_days": eligible_days,
        "trade_days": len(days),
        "coverage_trade_days": len(days) / eligible_days if eligible_days else None,
        "avg_names_per_trade_day": statistics.fmean(counts) if counts else None,
        "mean_trade": statistics.fmean(vals) if vals else None,
        "median_trade": statistics.median(vals) if vals else None,
        "precision_positive_trade": sum(x > 0 for x in vals) / len(vals) if vals else None,
        "profit_factor": gains / losses if losses > 0 else None,
        "mean_trade_day": statistics.fmean(days),
        "positive_trade_days": sum(x > 0 for x in days) / len(days),
        "block_boot_ci95_mean_trade_day": block_boot_ci(days),
        "fold_mean_median": statistics.median(fold_means) if fold_means else None,
        "fold_mean_min": min(fold_means) if fold_means else None,
        "fold_mean_max": max(fold_means) if fold_means else None,
        "positive_folds": sum(x > 0 for x in fold_means),
        "fold_count": len(fold_means),
    }


def run(obs: pd.DataFrame, n_days: int):
    names = ["logistic"] + list(CONTROLS)
    store = {
        h: {rate: {s: {c: {"trades": [], "days": [], "counts": [], "fold_means": []} for c in COSTS} for s in names}
            for rate in DAY_ACTIVE_RATES}
        for h in v2.HORIZONS
    }
    audit = []
    first_test = v2.TRAIN_DAYS + v2.PURGE_DAYS
    fold_starts = list(range(first_test, n_days - 1, v2.TEST_DAYS))
    total_eligible_days = sum(min(s + v2.TEST_DAYS, n_days - 1) - s for s in fold_starts if s < n_days - 1)

    for fold_no, test_start in enumerate(fold_starts, 1):
        test_end = min(test_start + v2.TEST_DAYS, n_days - 1)
        train_end = test_start - v2.PURGE_DAYS
        train_start = max(0, train_end - v2.TRAIN_DAYS)
        if train_end - train_start < int(v2.TRAIN_DAYS * 0.90):
            continue
        train_all = obs[(obs.decision_idx >= train_start) & (obs.decision_idx < train_end)]
        test_all = obs[(obs.decision_idx >= test_start) & (obs.decision_idx < test_end)]

        for h in v2.HORIZONS:
            rc = f"ret{h}"
            train = train_all.dropna(subset=v2.FEATURES + [rc]).copy()
            test = test_all.dropna(subset=v2.FEATURES + [rc]).copy()
            if len(train) < 5000 or test.empty:
                continue
            y = (train[rc] - v2.LABEL_COST > 0).astype(int)
            if y.nunique() < 2:
                continue
            m = make_model()
            m.fit(train[v2.FEATURES], y)
            train["p"] = m.predict_proba(train[v2.FEATURES])[:, 1]
            test["p"] = m.predict_proba(test[v2.FEATURES])[:, 1]
            train_daily_max = train.groupby("decision_idx", sort=False).p.max().to_numpy()

            for active_rate in DAY_ACTIVE_RATES:
                q = 1.0 - active_rate
                threshold = float(np.quantile(train_daily_max, q))
                fold_vals = {s: {c: [] for c in COSTS} for s in names}
                fold_active = 0
                for _, day in test.groupby("decision_idx", sort=True):
                    admitted = day[day.p >= threshold].nlargest(v2.TOP_K, "p")
                    k = len(admitted)
                    if k == 0:
                        continue
                    fold_active += 1
                    selections = {"logistic": admitted}
                    for ctrl in CONTROLS:
                        selections[ctrl] = day.nlargest(k, ctrl)
                    for strat, chosen in selections.items():
                        gross = chosen[rc].astype(float).tolist()
                        for cname, cost in COSTS.items():
                            vals = [x - cost for x in gross]
                            rec = store[h][active_rate][strat][cname]
                            rec["trades"].extend(vals)
                            rec["days"].append(statistics.fmean(vals))
                            rec["counts"].append(len(vals))
                            fold_vals[strat][cname].append(statistics.fmean(vals))
                audit.append({
                    "fold": fold_no, "horizon": h, "target_active_rate": active_rate,
                    "train_daily_max_quantile": q, "threshold": threshold,
                    "test_active_days": fold_active, "test_days": test_end - test_start,
                })
                for strat in names:
                    for cname, vals in fold_vals[strat].items():
                        if vals:
                            store[h][active_rate][strat][cname]["fold_means"].append(statistics.fmean(vals))

    result = {"policies": {}, "threshold_audit": audit}
    for h in v2.HORIZONS:
        result["policies"][str(h)] = {}
        for rate in DAY_ACTIVE_RATES:
            key = f"train_daily_max_top_{int(rate*100)}pct"
            result["policies"][str(h)][key] = {}
            for strat in store[h][rate]:
                result["policies"][str(h)][key][strat] = {
                    cname: summarize(rec["trades"], rec["days"], total_eligible_days, rec["counts"], rec["fold_means"])
                    for cname, rec in store[h][rate][strat].items()
                }
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--marcap-dir", required=True)
    ap.add_argument("--from-date", default="2018-01-02")
    ap.add_argument("--to-date", default="2026-09-25")
    ap.add_argument("--output", default="research_results/kospi_daygate_v4.json")
    args = ap.parse_args()
    raw = v2.load_data(args.marcap_dir, args.from_date, args.to_date)
    dates = sorted(raw.date.unique())
    obs = v2.engineer(raw)
    result = run(obs, len(dates))
    payload = {
        "research_version": "indexalert-kospi-daygate-v4",
        "parent_model": v2.MODEL_VERSION,
        "universe_version": v2.UNIVERSE_VERSION,
        "from_date": args.from_date, "to_date": args.to_date,
        "trading_days": len(dates), "observation_rows": int(len(obs)),
        "day_active_rates_predeclared": list(DAY_ACTIVE_RATES),
        "threshold_rule": "per-fold quantile of TRAIN daily maximum probabilities only; frozen on test",
        "daily_admission_rule": "NO TRADE unless test name exceeds frozen daily-max threshold; up to 3 names",
        "coverage_matched_controls": list(CONTROLS),
        "cost_scenarios": COSTS,
        "result": result,
        "research_status": "DEVELOPMENT_CONTAMINATED_NOT_SEALED",
        "profitability_validated": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "limitations": [
            "2018-2026 has been inspected during v1-v3 and is development-contaminated.",
            "Three activation rates are tested; selecting one from this result is a research choice requiring future confirmation.",
            "Fixed cost stresses are not yet broker/size-specific realized execution costs.",
            "2/3/5-day results measure trade EV and active-day averages, not a fully capital-constrained overlapping portfolio.",
        ],
    }
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
