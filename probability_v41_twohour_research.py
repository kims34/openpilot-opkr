"""Research-only v4.1 candidate: second-hour nowcast vs validated v4.0.

No production imports use this file.  The candidate is promoted only if it
beats the causally reconstructed v4.0 baseline on an untouched final 126
session holdout, both chronological halves, every 21-session block, and a
moving-block bootstrap lower confidence bound above zero.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np

import probability_v40_firsthour as v40

NY = ZoneInfo("America/New_York")
SYMBOLS = ("SPY", "QQQ", "SCHD")
HOLDOUT = 126
MIN_TRAIN = 126
GRID = [(w, r, c) for w in (126, 252, 378) for r in (10.0, 30.0, 100.0, 300.0) for c in (0.04, 0.06, 0.08, 0.10)]


def second_hour(symbol: str):
    result = v40._chart(symbol, "2y", "60m")
    quote = (result.get("indicators", {}).get("quote") or [{}])[0]
    per_day = {}
    for i, stamp in enumerate(result.get("timestamp") or []):
        local = datetime.fromtimestamp(int(stamp), timezone.utc).astimezone(NY)
        minute = local.hour * 60 + local.minute
        if not (9 * 60 + 30 <= minute < 11 * 60 + 30):
            continue
        day = local.date().isoformat()
        try:
            row = tuple(float((quote.get(k) or [])[i]) for k in ("open", "high", "low", "close", "volume"))
        except Exception:
            continue
        if all(np.isfinite(row)) and min(row[:4]) > 0 and row[4] >= 0:
            per_day.setdefault(day, []).append((minute, row))
    out = {}
    for day, rows in per_day.items():
        rows = sorted(rows)[:2]
        if len(rows) != 2:
            continue
        a, b = rows[0][1], rows[1][1]
        out[day] = (a[0], max(a[1], b[1]), min(a[2], b[2]), b[3], a[4] + b[4], a[3])
    return out


def twohour_features(dates, closes, positions, own, spy, qqq, vix):
    rows = []
    volumes = []
    for j, t0 in enumerate(positions):
        t = int(t0)
        if t + 1 >= len(dates):
            continue
        target = dates[t + 1]
        if any(target not in x for x in (own, spy, qqq, vix)):
            continue
        o, h, l, c, vol, c1 = own[target]
        so, sh, sl, sc, _, sc1 = spy[target]
        qo, qh, ql, qc, _, qc1 = qqq[target]
        vo, vh, vl, vc, _, vc1 = vix[target]
        prev = float(closes[t])
        if prev <= 0 or min(o, h, l, c, so, sc, qo, qc, vo, vc, c1, sc1, qc1, vc1) <= 0:
            continue
        prior_vol = [x for _, x in volumes[-20:] if x > 0]
        med_vol = float(np.median(prior_vol)) if len(prior_vol) >= 10 else float("nan")
        volume_ratio = np.log(max(vol / med_vol, 1e-6)) if np.isfinite(med_vol) and med_vol > 0 else float("nan")
        close_loc = (c - l) / max(h - l, 1e-12)
        feat = np.asarray([
            o / prev - 1.0,
            c1 / o - 1.0,
            c / c1 - 1.0,
            c / prev - 1.0,
            (h - l) / prev,
            close_loc,
            volume_ratio,
            sc1 / so - 1.0,
            sc / sc1 - 1.0,
            qc1 / qo - 1.0,
            qc / qc1 - 1.0,
            np.log(vc),
            vc1 / vo - 1.0,
            vc / vc1 - 1.0,
        ], float)
        volumes.append((target, vol))
        if np.all(np.isfinite(feat)):
            rows.append((j, t, target, feat))
    return rows


def causal_predictions(rows, outcomes, baseline, config, min_train=MIN_TRAIN):
    window, ridge, cap = config
    pred = {}
    for k, row in enumerate(rows):
        j = int(row[0])
        history = rows[max(0, k - window):k]
        if len(history) < min_train:
            continue
        idx = np.asarray([int(x[0]) for x in history], int)
        X = np.vstack([x[3] for x in history])
        y = outcomes[idx]
        b = baseline[idx]
        if not (np.all(np.isfinite(X)) and np.all(np.isfinite(y)) and np.all(np.isfinite(b))):
            continue
        mean = X.mean(axis=0)
        sd = np.maximum(X.std(axis=0, ddof=1), 1e-6)
        Z = (X - mean) / sd
        beta = np.linalg.solve(Z.T @ Z + ridge * np.eye(Z.shape[1]), Z.T @ (y - b))
        adj = float(np.clip(((row[3] - mean) / sd) @ beta, -cap, cap))
        pred[j] = float(np.clip(baseline[j] + adj, 0.05, 0.95))
    return pred


def gains(base_p, cand_p, y):
    d = (base_p - y) ** 2 - (cand_p - y) ** 2
    n = len(d)
    h = n // 2
    return float(d.mean()), float(d[:h].mean()), float(d[h:].mean()), d


def bootstrap_lower(diff, seed=20260928, reps=3000, block=5):
    rng = np.random.default_rng(seed)
    n = len(diff)
    vals = []
    for _ in range(reps):
        parts = []
        while sum(len(x) for x in parts) < n:
            start = int(rng.integers(0, max(1, n - block + 1)))
            parts.append(diff[start:start + block])
        vals.append(float(np.concatenate(parts)[:n].mean()))
    return float(np.quantile(vals, 0.025))


def build_v40(symbol, dates, closes, positions, outcomes, p39, first_shared):
    rows = v40.hour_features(dates, closes, positions, first_shared[symbol], first_shared["SPY"], first_shared["QQQ"], first_shared["^VIX"])
    preds = causal_predictions(rows, outcomes, p39, v40.FROZEN_CONFIG[symbol])
    return rows, preds


def evaluate_symbol(symbol, daily, first_shared, two_shared):
    # Use completed daily rows as the common causal backbone.
    dates_all = sorted(set(daily[symbol]).intersection(daily["SPY"], daily["QQQ"], daily["SCHD"]))
    completed = [(d, daily[symbol][d][3]) for d in dates_all]
    # v39_series needs a future target label only to build its historical trace.
    meta = {"target_date": "2999-12-31"}
    dates, closes, positions, outcomes, p39 = v40.v39_series(symbol, completed, meta, daily[symbol])

    first_rows, p40_map = build_v40(symbol, dates, closes, positions, outcomes, p39, first_shared)
    two_rows = twohour_features(dates, closes, positions, two_shared[symbol], two_shared["SPY"], two_shared["QQQ"], two_shared["^VIX"])
    available = sorted(set(int(r[0]) for r in two_rows).intersection(p40_map))
    if len(available) < HOLDOUT + 160:
        raise RuntimeError(f"insufficient aligned samples {symbol}: {len(available)}")

    p40 = np.full(len(outcomes), np.nan)
    for j, p in p40_map.items():
        p40[j] = p
    # Restrict row list to samples where validated v4.0 baseline exists.
    two_rows = [r for r in two_rows if int(r[0]) in p40_map]
    hold_idx = set(available[-HOLDOUT:])
    dev_idx = set(available[:-HOLDOUT])

    best = None
    for cfg in GRID:
        cmap = causal_predictions(two_rows, outcomes, p40, cfg)
        idx = np.asarray(sorted(dev_idx.intersection(cmap)), int)
        if len(idx) < 126:
            continue
        g = gains(p40[idx], np.asarray([cmap[i] for i in idx]), outcomes[idx])
        if min(g[:3]) <= 0:
            continue
        score = g[0]
        if best is None or score > best[0]:
            best = (score, cfg, cmap, len(idx), g[:3])
    if best is None:
        return {"symbol": symbol, "promote": False, "reason": "no stable development winner", "aligned": len(available)}

    _, cfg, cmap, dev_n, dev_g = best
    hidx = np.asarray(sorted(hold_idx.intersection(cmap)), int)
    if len(hidx) != HOLDOUT:
        return {"symbol": symbol, "promote": False, "reason": f"holdout coverage {len(hidx)}/{HOLDOUT}", "config": cfg}
    cand = np.asarray([cmap[i] for i in hidx])
    base = p40[hidx]
    y = outcomes[hidx]
    overall, half1, half2, diff = gains(base, cand, y)
    blocks = [float(diff[i:i+21].mean()) for i in range(0, HOLDOUT, 21)]
    ci_low = bootstrap_lower(diff)
    promote = overall > 0 and half1 > 0 and half2 > 0 and all(x > 0 for x in blocks) and ci_low > 0
    return {
        "symbol": symbol,
        "promote": promote,
        "config": {"window": cfg[0], "ridge": cfg[1], "cap": cfg[2]},
        "development_n": dev_n,
        "development_gain": [round(x, 8) for x in dev_g],
        "holdout_n": len(hidx),
        "v40_brier": round(float(np.mean((base-y)**2)), 8),
        "v41_brier": round(float(np.mean((cand-y)**2)), 8),
        "holdout_gain": round(overall, 8),
        "half_gains": [round(half1, 8), round(half2, 8)],
        "block_gains": [round(x, 8) for x in blocks],
        "bootstrap95_gain_lower": round(ci_low, 8),
    }


def main():
    daily = {s: v40.daily_ohlcv(s) for s in ("SPY", "QQQ", "SCHD")}
    first_shared = {s: v40.first_hour(s) for s in ("SPY", "QQQ", "SCHD", "^VIX")}
    two_shared = {s: second_hour(s) for s in ("SPY", "QQQ", "SCHD", "^VIX")}
    results = [evaluate_symbol(s, daily, first_shared, two_shared) for s in SYMBOLS]
    print(json.dumps({"model": "v4.1-two-hour-research", "results": results}, ensure_ascii=False, indent=2))
    print("ALL_PROMOTE=", all(r.get("promote") for r in results))


if __name__ == "__main__":
    main()
