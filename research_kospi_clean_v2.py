"""IndexAlert KOSPI empirical research v2.

Vectorized, corporate-action-aware development backtest using FinanceData/marcap.
Key changes vs v1:
- KOSPI ordinary-share proxy universe: six-digit codes ending in 0, with SPAC/
  REIT/ETF-like names excluded.
- Feature momentum uses the KRX-published daily change ratio rather than raw
  close/previous-close, avoiding split/right-detachment discontinuities.
- Next-open holding returns use entry-day open->close plus subsequent official
  close-to-close returns, so corporate actions inside a holding window do not
  create fake P&L.
- Adds reversal baselines and OOS probability-tail diagnostics.
- Walk-forward logistic is fit only on preceding ~5 trading years with a 5-day
  purge; tests advance by ~quarter.

This is development evidence, not a deployable signal. The 2018-2026 period is
now considered contaminated for future sealed-holdout claims because results
have been inspected during research.
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

YEARS = range(2018, 2027)
HORIZONS = (1, 2, 3, 5)
TOP_K = 3
TRAIN_DAYS = 1260
TEST_DAYS = 63
PURGE_DAYS = 5
LABEL_COST = 0.0025
COSTS = {"gross": 0.0, "low_10bp": 0.001, "base_25bp": 0.0025, "stress_50bp": 0.005}
MODEL_VERSION = "kospi-clean-logistic-v2"
UNIVERSE_VERSION = "kospi-common-proxy-v2"
EXCLUDE_NAME_PARTS = ("스팩", "SPAC", "리츠", "REIT", "ETF", "ETN", "인버스", "레버리지")
FEATURES = [
    "r1", "mom5", "mom20", "vol20", "downside20", "intraday", "gap_theoretical",
    "value_surprise20", "mom20_rank", "liquidity_rank",
]
BASELINES = ("mom5", "mom20", "rev5", "rev20", "mom20_liq", "rev20_liq")


def _col(df, *names):
    for name in names:
        if name in df.columns:
            return name
    raise KeyError(f"none of columns exist: {names}")


def load_data(marcap_dir: str, from_date: str, to_date: str) -> pd.DataFrame:
    start = pd.Timestamp(from_date)
    end = pd.Timestamp(to_date)
    frames = []
    for year in range(start.year, end.year + 1):
        path = os.path.join(marcap_dir, f"marcap-{year}.parquet")
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        x = pd.read_parquet(path)
        frames.append(x)
    df = pd.concat(frames, ignore_index=True)

    date_c = _col(df, "Date", "date")
    code_c = _col(df, "Code", "code")
    name_c = _col(df, "Name", "name")
    market_c = _col(df, "Market", "market")
    ratio_c = _col(df, "ChagesRatio", "ChangesRatio", "ChangeRatio", "changesRatio")
    amount_c = _col(df, "Amount", "amount")
    open_c = _col(df, "Open", "open")
    close_c = _col(df, "Close", "close")
    high_c = _col(df, "High", "high")
    low_c = _col(df, "Low", "low")

    out = pd.DataFrame({
        "date": pd.to_datetime(df[date_c], errors="coerce"),
        "code": df[code_c].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(6),
        "name": df[name_c].astype(str),
        "market": df[market_c].astype(str).str.upper(),
        "open": pd.to_numeric(df[open_c], errors="coerce"),
        "high": pd.to_numeric(df[high_c], errors="coerce"),
        "low": pd.to_numeric(df[low_c], errors="coerce"),
        "close": pd.to_numeric(df[close_c], errors="coerce"),
        "amount": pd.to_numeric(df[amount_c], errors="coerce"),
        "official_pct": pd.to_numeric(df[ratio_c], errors="coerce"),
    })
    out = out[(out.date >= start) & (out.date <= end) & (out.market == "KOSPI")]
    # KRX stock coding convention: ordinary issues generally end in 0; this is
    # explicitly labelled a proxy because marcap has no historical security-type field.
    out = out[out.code.str.match(r"^\d{5}0$")]
    pat = "|".join(EXCLUDE_NAME_PARTS)
    out = out[~out.name.str.contains(pat, case=False, na=False, regex=True)]
    out = out.dropna(subset=["date", "open", "high", "low", "close", "amount", "official_pct"])
    out = out[(out.open > 0) & (out.close > 0) & (out.amount > 0)]
    out = out[(out.low <= out.open) & (out.open <= out.high) & (out.low <= out.close) & (out.close <= out.high)]
    out["r1"] = out.official_pct / 100.0
    # Values outside a generous band are treated as data-quality errors, not alpha.
    out = out[(out.r1 > -0.36) & (out.r1 < 0.36)]
    out = out.sort_values(["code", "date"]).drop_duplicates(["code", "date"], keep="last")

    dates = sorted(out.date.unique())
    date_to_idx = {pd.Timestamp(d): i for i, d in enumerate(dates)}
    out["day_idx"] = out.date.map(lambda x: date_to_idx[pd.Timestamp(x)]).astype(int)
    return out.reset_index(drop=True)


def engineer(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    g = x.groupby("code", sort=False, group_keys=False)
    x["log_r"] = np.log1p(x.r1.clip(lower=-0.999999))
    x["cumlog"] = g.log_r.cumsum()
    x["hist_count"] = g.cumcount()

    # Rolling features use only information available at the decision close.
    x["mom5"] = np.expm1(g.log_r.rolling(5, min_periods=5).sum().reset_index(level=0, drop=True))
    x["mom20"] = np.expm1(g.log_r.rolling(20, min_periods=20).sum().reset_index(level=0, drop=True))
    x["vol20"] = g.r1.rolling(20, min_periods=20).std(ddof=0).reset_index(level=0, drop=True)
    x["downsq"] = np.minimum(x.r1, 0.0) ** 2
    x["downside20"] = np.sqrt(g.downsq.rolling(20, min_periods=20).mean().reset_index(level=0, drop=True))
    x["amount_med20"] = g.amount.rolling(20, min_periods=20).median().reset_index(level=0, drop=True)
    x["value_surprise20"] = x.amount / x.amount_med20 - 1.0
    x["intraday"] = x.close / x.open - 1.0
    theoretical_prev = x.close / (1.0 + x.r1)
    x["gap_theoretical"] = x.open / theoretical_prev - 1.0

    # Remove bad same-day records after ratios are computed.
    x = x.replace([np.inf, -np.inf], np.nan)
    x = x.dropna(subset=["mom5", "mom20", "vol20", "downside20", "amount_med20", "value_surprise20", "gap_theoretical"])

    # Cross-sectional ranks and 20th percentile liquidity gate are point-in-time.
    x["liquidity_q20"] = x.groupby("date").amount_med20.transform(lambda s: s.quantile(0.20))
    x = x[x.amount_med20 >= x.liquidity_q20]
    x["mom20_rank"] = x.groupby("date").mom20.rank(method="average", pct=True)
    x["liquidity_rank"] = x.groupby("date").amount_med20.rank(method="average", pct=True)
    x["mom20_liq"] = 0.80 * x.mom20_rank + 0.20 * x.liquidity_rank
    x["rev20_liq"] = 0.80 * (1.0 - x.mom20_rank) + 0.20 * x.liquidity_rank
    x["rev5"] = -x.mom5
    x["rev20"] = -x.mom20

    # Exact-next-session entry mapping. A stock absent next market session is not
    # silently shifted to a later row; it is unavailable for that observation.
    entry = x[["code", "day_idx", "intraday", "cumlog"]].copy()
    entry["decision_idx"] = entry.day_idx - 1
    entry = entry.rename(columns={"intraday": "entry_intraday", "cumlog": "entry_cumlog"})
    entry = entry[["code", "decision_idx", "entry_intraday", "entry_cumlog"]]

    base_cols = ["date", "day_idx", "code", "name"] + FEATURES + list(BASELINES)
    obs = x[base_cols].copy().rename(columns={"day_idx": "decision_idx"})
    obs = obs.merge(entry, on=["code", "decision_idx"], how="left", validate="one_to_one")

    for h in HORIZONS:
        exit_df = x[["code", "day_idx", "cumlog"]].copy()
        exit_df["decision_idx"] = exit_df.day_idx - h
        exit_df = exit_df.rename(columns={"cumlog": f"exit_cumlog_{h}"})[["code", "decision_idx", f"exit_cumlog_{h}"]]
        obs = obs.merge(exit_df, on=["code", "decision_idx"], how="left", validate="one_to_one")
        valid = obs.entry_intraday.notna() & obs[f"exit_cumlog_{h}"].notna() & (1.0 + obs.entry_intraday > 0)
        ret = np.full(len(obs), np.nan)
        ret[valid.to_numpy()] = np.expm1(
            np.log1p(obs.loc[valid, "entry_intraday"].to_numpy())
            + obs.loc[valid, f"exit_cumlog_{h}"].to_numpy()
            - obs.loc[valid, "entry_cumlog"].to_numpy()
        )
        obs[f"ret{h}"] = ret
    return obs.replace([np.inf, -np.inf], np.nan)


def _model():
    return Pipeline([
        ("scale", StandardScaler()),
        ("lr", LogisticRegression(C=0.25, penalty="l2", solver="lbfgs", max_iter=300)),
    ])


def _profit_factor(vals):
    gains = sum(v for v in vals if v > 0)
    losses = -sum(v for v in vals if v < 0)
    return gains / losses if losses > 0 else None


def _block_boot_ci(vals: List[float], seed: int = 20260928, block: int = 5, draws: int = 500):
    if len(vals) < 30:
        return [None, None]
    rng = random.Random(seed)
    n = len(vals)
    means = []
    starts = list(range(max(1, n - block + 1)))
    for _ in range(draws):
        sample = []
        while len(sample) < n:
            s = rng.choice(starts)
            sample.extend(vals[s:s + block])
        sample = sample[:n]
        means.append(sum(sample) / n)
    means.sort()
    return [means[int(0.025 * draws)], means[min(draws - 1, int(0.975 * draws))]]


def summarize(trades: List[float], daily: List[float], horizon: int):
    if not trades:
        return {"n": 0}
    t = [float(v) for v in trades]
    d = [float(v) for v in daily]
    out = {
        "n": len(t),
        "mean": statistics.fmean(t),
        "median": statistics.median(t),
        "precision_positive": sum(v > 0 for v in t) / len(t),
        "profit_factor": _profit_factor(t),
        "p10": float(np.quantile(t, 0.10)),
        "p90": float(np.quantile(t, 0.90)),
        "selection_days": len(d),
        "mean_selected_day": statistics.fmean(d) if d else None,
        "positive_selected_days": sum(v > 0 for v in d) / len(d) if d else None,
        "mean_selected_day_block_boot_ci95": _block_boot_ci(d),
    }
    # Only h=1 creates a non-overlapping daily portfolio with this simple engine.
    if horizon == 1 and d:
        wealth = peak = 1.0
        mdd = 0.0
        for r in d:
            wealth *= max(0.0, 1.0 + r)
            peak = max(peak, wealth)
            mdd = min(mdd, wealth / peak - 1.0)
        out["compounded_nonoverlap"] = wealth - 1.0
        out["max_drawdown_nonoverlap"] = mdd
    else:
        out["compounded_nonoverlap"] = None
        out["max_drawdown_nonoverlap"] = None
    return out


def run_walk_forward(obs: pd.DataFrame, n_days: int):
    first_test = TRAIN_DAYS + PURGE_DAYS
    fold_starts = list(range(first_test, n_days - 1, TEST_DAYS))
    names = list(BASELINES) + ["logistic"]
    trade_store = {n: {h: {c: [] for c in COSTS} for h in HORIZONS} for n in names}
    day_store = {n: {h: {c: [] for c in COSTS} for h in HORIZONS} for n in names}
    prob_store = {h: [] for h in HORIZONS}
    folds = []

    for fold_no, test_start in enumerate(fold_starts, 1):
        test_end = min(test_start + TEST_DAYS, n_days - 1)
        train_end = test_start - PURGE_DAYS
        train_start = max(0, train_end - TRAIN_DAYS)
        if train_end - train_start < int(TRAIN_DAYS * 0.9):
            continue
        train = obs[(obs.decision_idx >= train_start) & (obs.decision_idx < train_end)]
        test = obs[(obs.decision_idx >= test_start) & (obs.decision_idx < test_end)]
        models = {}
        for h in HORIZONS:
            tr = train.dropna(subset=FEATURES + [f"ret{h}"])
            if len(tr) < 5000:
                continue
            y = (tr[f"ret{h}"] - LABEL_COST > 0).astype(int)
            if y.nunique() < 2:
                continue
            m = _model()
            m.fit(tr[FEATURES], y)
            models[h] = m
        if not models:
            continue
        folds.append({
            "fold": fold_no, "train_idx": [train_start, train_end - 1],
            "test_idx": [test_start, test_end - 1], "train_rows": int(len(train)), "test_rows": int(len(test)),
        })

        for h, m in models.items():
            te = test.dropna(subset=FEATURES + [f"ret{h}"]).copy()
            if te.empty:
                continue
            te["logistic"] = m.predict_proba(te[FEATURES])[:, 1]
            te["y"] = (te[f"ret{h}"] - LABEL_COST > 0).astype(int)
            prob_store[h].extend(zip(te.logistic.astype(float), te.y.astype(int), te[f"ret{h}"].astype(float)))
            for decision_idx, day in te.groupby("decision_idx", sort=True):
                for name in names:
                    top = day.nlargest(TOP_K, name)
                    if len(top) < TOP_K:
                        continue
                    gross = top[f"ret{h}"].astype(float).tolist()
                    for cname, cost in COSTS.items():
                        vals = [v - cost for v in gross]
                        trade_store[name][h][cname].extend(vals)
                        day_store[name][h][cname].append(statistics.fmean(vals))

    report = {"folds": folds, "models": {}, "calibration": {}}
    for name in names:
        report["models"][name] = {"horizons": {}}
        for h in HORIZONS:
            report["models"][name]["horizons"][str(h)] = {
                cname: summarize(trade_store[name][h][cname], day_store[name][h][cname], h)
                for cname in COSTS
            }

    for h in HORIZONS:
        rows = prob_store[h]
        if not rows:
            continue
        p = np.array([r[0] for r in rows], dtype=float)
        y = np.array([r[1] for r in rows], dtype=float)
        gross = np.array([r[2] for r in rows], dtype=float)
        base_rate = float(y.mean())
        brier = float(np.mean((p - y) ** 2))
        base_brier = float(np.mean((base_rate - y) ** 2))
        diag = {
            "n": int(len(y)), "base_rate": base_rate, "brier": brier,
            "base_rate_brier": base_brier,
            "brier_skill_vs_constant": 1.0 - brier / base_brier if base_brier > 0 else None,
            "probability_tail": {},
        }
        for coverage in (0.01, 0.05, 0.10):
            cutoff = float(np.quantile(p, 1.0 - coverage))
            mask = p >= cutoff
            net = gross[mask] - LABEL_COST
            diag["probability_tail"][f"top_{int(coverage*100)}pct"] = {
                "n": int(mask.sum()), "cutoff": cutoff,
                "mean_net_25bp": float(net.mean()) if mask.any() else None,
                "precision_net_positive": float((net > 0).mean()) if mask.any() else None,
            }
        report["calibration"][str(h)] = diag
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--marcap-dir", required=True)
    ap.add_argument("--from-date", default="2018-01-02")
    ap.add_argument("--to-date", default="2026-09-25")
    ap.add_argument("--output", default="research_results/kospi_clean_v2.json")
    args = ap.parse_args()

    raw = load_data(args.marcap_dir, args.from_date, args.to_date)
    dates = sorted(raw.date.unique())
    obs = engineer(raw)
    report = run_walk_forward(obs, len(dates))
    payload = {
        "research_version": "indexalert-kospi-clean-v2",
        "model_version": MODEL_VERSION,
        "universe_version": UNIVERSE_VERSION,
        "data_source": "FinanceData/marcap; KRX official daily change ratio field",
        "from_date": args.from_date, "to_date": args.to_date,
        "trading_days": len(dates), "raw_filtered_rows": int(len(raw)), "observation_rows": int(len(obs)),
        "common_share_rule": "KOSPI; 6-digit code ending 0; excludes names containing SPAC/REIT/ETF/ETN/inverse/leverage terms",
        "cost_scenarios": COSTS,
        "walk_forward": report,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "research_status": "DEVELOPMENT_CONTAMINATED_NOT_SEALED",
        "profitability_validated": False,
        "limitations": [
            "Historical security type is proxied from code/name because marcap does not include a security-type field.",
            "Delisting cash recovery is not reconstructed; exact-next-session absence makes that observation unavailable.",
            "Costs are fixed stress scenarios, not broker-specific spread/impact estimates.",
            "The 2018-2026 period is development-contaminated after inspection and cannot serve as a fresh sealed holdout.",
            "Intraday +5/+15 entry policies require a separate historical intraday source.",
        ],
    }
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
