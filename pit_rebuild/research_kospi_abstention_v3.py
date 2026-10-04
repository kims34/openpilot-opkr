"""IndexAlert KOSPI v3: predeclared abstention policy validation.

Purpose: convert the v2 diagnostic probability-tail signal into a causal-ish
walk-forward trading admission policy without looking at future score cutoffs.
For every fold/horizon the Logistic model is fit on the preceding five-year
window.  Thresholds are the 99th/95th/90th percentiles of *training* model
scores only.  On each test date, names above the frozen threshold are ranked by
probability and at most 3 are admitted; zero names is allowed.

Coverage-matched controls select the same number of names on the same dates
using simple mom20+liquidity and rev20+liquidity rankings. This isolates whether
selective Logistic admission contributes beyond merely trading less often.

This is still development evidence because 2018-2026 aggregate diagnostics have
already been inspected. A positive result may nominate a shadow challenger but
cannot by itself promote a production model.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import statistics
from datetime import datetime, timezone
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import research_kospi_clean_v2 as v2

COVERAGES = (0.01, 0.05, 0.10)
CONTROLS = ("mom20_liq", "rev20_liq")
COSTS = v2.COSTS


def model():
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
        sample = sample[:n]
        means.append(statistics.fmean(sample))
    means.sort()
    return [means[int(draws * 0.025)], means[min(draws - 1, int(draws * 0.975))]]


def summarize(trades: List[float], day_returns: List[float], eligible_days: int, selected_counts: List[int], fold_means: List[float]):
    if not trades:
        return {"trades": 0, "eligible_days": eligible_days, "trade_days": 0}
    vals = [float(x) for x in trades]
    days = [float(x) for x in day_returns]
    gains = sum(x for x in vals if x > 0)
    losses = -sum(x for x in vals if x < 0)
    return {
        "trades": len(vals),
        "eligible_days": eligible_days,
        "trade_days": len(days),
        "coverage_trade_days": len(days) / eligible_days if eligible_days else None,
        "avg_names_per_trade_day": statistics.fmean(selected_counts) if selected_counts else None,
        "mean_trade": statistics.fmean(vals),
        "median_trade": statistics.median(vals),
        "precision_positive_trade": sum(x > 0 for x in vals) / len(vals),
        "profit_factor": gains / losses if losses > 0 else None,
        "mean_trade_day": statistics.fmean(days) if days else None,
        "positive_trade_days": sum(x > 0 for x in days) / len(days) if days else None,
        "block_boot_ci95_mean_trade_day": block_boot_ci(days),
        "fold_mean_median": statistics.median(fold_means) if fold_means else None,
        "fold_mean_min": min(fold_means) if fold_means else None,
        "fold_mean_max": max(fold_means) if fold_means else None,
        "positive_folds": sum(x > 0 for x in fold_means) if fold_means else 0,
        "fold_count": len(fold_means),
    }


def run(obs: pd.DataFrame, n_days: int):
    # policy[h][coverage][strategy][cost] -> observations
    policies = {}
    threshold_audit = []
    first_test = v2.TRAIN_DAYS + v2.PURGE_DAYS
    fold_starts = list(range(first_test, n_days - 1, v2.TEST_DAYS))

    for h in v2.HORIZONS:
        policies[h] = {}
        for cov in COVERAGES:
            strategies = ["logistic"] + list(CONTROLS)
            policies[h][cov] = {
                s: {c: {"trades": [], "days": [], "counts": [], "fold_means": []} for c in COSTS}
                for s in strategies
            }

    for fold_no, test_start in enumerate(fold_starts, 1):
        test_end = min(test_start + v2.TEST_DAYS, n_days - 1)
        train_end = test_start - v2.PURGE_DAYS
        train_start = max(0, train_end - v2.TRAIN_DAYS)
        if train_end - train_start < int(v2.TRAIN_DAYS * 0.9):
            continue
        train_all = obs[(obs.decision_idx >= train_start) & (obs.decision_idx < train_end)]
        test_all = obs[(obs.decision_idx >= test_start) & (obs.decision_idx < test_end)]

        for h in v2.HORIZONS:
            ret_col = f"ret{h}"
            train = train_all.dropna(subset=v2.FEATURES + [ret_col]).copy()
            test = test_all.dropna(subset=v2.FEATURES + [ret_col]).copy()
            if len(train) < 5000 or test.empty:
                continue
            y = (train[ret_col] - v2.LABEL_COST > 0).astype(int)
            if y.nunique() < 2:
                continue
            m = model()
            m.fit(train[v2.FEATURES], y)
            train_p = m.predict_proba(train[v2.FEATURES])[:, 1]
            test["logistic"] = m.predict_proba(test[v2.FEATURES])[:, 1]

            for cov in COVERAGES:
                threshold = float(np.quantile(train_p, 1.0 - cov))
                threshold_audit.append({
                    "fold": fold_no, "horizon": h, "coverage_target": cov,
                    "threshold_from_train_only": threshold,
                    "train_from_idx": train_start, "train_to_idx": train_end - 1,
                    "test_from_idx": test_start, "test_to_idx": test_end - 1,
                })

                fold_day_values = {s: {c: [] for c in COSTS} for s in ["logistic"] + list(CONTROLS)}
                for _, day in test.groupby("decision_idx", sort=True):
                    admitted = day[day.logistic >= threshold].nlargest(v2.TOP_K, "logistic")
                    k = len(admitted)
                    if k <= 0:
                        continue
                    selections = {"logistic": admitted}
                    for ctrl in CONTROLS:
                        selections[ctrl] = day.nlargest(k, ctrl)

                    for strat, chosen in selections.items():
                        gross = chosen[ret_col].astype(float).tolist()
                        if not gross:
                            continue
                        for cname, cost in COSTS.items():
                            vals = [x - cost for x in gross]
                            rec = policies[h][cov][strat][cname]
                            rec["trades"].extend(vals)
                            rec["days"].append(statistics.fmean(vals))
                            rec["counts"].append(len(vals))
                            fold_day_values[strat][cname].append(statistics.fmean(vals))

                for strat in fold_day_values:
                    for cname, vals in fold_day_values[strat].items():
                        if vals:
                            policies[h][cov][strat][cname]["fold_means"].append(statistics.fmean(vals))

    out = {"policies": {}, "threshold_audit": threshold_audit}
    # number of unique potential OOS days for denominator, from all folds
    total_eligible_days = sum(min(s + v2.TEST_DAYS, n_days - 1) - s for s in fold_starts if s < n_days - 1)
    for h in v2.HORIZONS:
        out["policies"][str(h)] = {}
        for cov in COVERAGES:
            ckey = f"top_{int(cov*100)}pct_train_threshold"
            out["policies"][str(h)][ckey] = {}
            for strat in policies[h][cov]:
                out["policies"][str(h)][ckey][strat] = {}
                for cname, rec in policies[h][cov][strat].items():
                    out["policies"][str(h)][ckey][strat][cname] = summarize(
                        rec["trades"], rec["days"], total_eligible_days, rec["counts"], rec["fold_means"]
                    )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--marcap-dir", required=True)
    ap.add_argument("--from-date", default="2018-01-02")
    ap.add_argument("--to-date", default="2026-09-25")
    ap.add_argument("--output", default="research_results/kospi_abstention_v3.json")
    args = ap.parse_args()

    raw = v2.load_data(args.marcap_dir, args.from_date, args.to_date)
    dates = sorted(raw.date.unique())
    obs = v2.engineer(raw)
    result = run(obs, len(dates))
    payload = {
        "research_version": "indexalert-kospi-abstention-v3",
        "parent_model": v2.MODEL_VERSION,
        "universe_version": v2.UNIVERSE_VERSION,
        "from_date": args.from_date,
        "to_date": args.to_date,
        "trading_days": len(dates),
        "observation_rows": int(len(obs)),
        "coverages_predeclared": list(COVERAGES),
        "threshold_rule": "per-fold quantile of fitted training scores only; frozen on test",
        "daily_admission_rule": "probability >= frozen threshold; choose up to 3; zero allowed",
        "coverage_matched_controls": list(CONTROLS),
        "cost_scenarios": COSTS,
        "result": result,
        "research_status": "DEVELOPMENT_CONTAMINATED_NOT_SEALED",
        "profitability_validated": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "limitations": [
            "2018-2026 was already inspected in v1/v2; this is challenger development evidence, not a sealed holdout.",
            "Threshold quantiles are predeclared here but all three are tested; choosing one from this run counts as model selection.",
            "Costs remain fixed stress scenarios rather than broker/size-specific realized execution costs.",
            "Overlapping 2/3/5-day recommendations are evaluated as trade EV and clustered trade-day means, not as a fully capital-constrained portfolio.",
        ],
    }
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
