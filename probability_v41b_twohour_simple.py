"""Research-only simple second-hour challengers against validated v4.0.

Small feature families are tested separately to reduce overfit. Production is
untouched. A symbol passes only if the selected development winner improves the
untouched final 126 sessions overall, in both halves, in all six 21-session
blocks, and has a positive moving-block bootstrap 95% lower bound.
"""
from __future__ import annotations

import json
import numpy as np

import probability_v40_firsthour as v40
import probability_v41_twohour_research as core

SYMBOLS = ("SPY", "QQQ", "SCHD")
HOLDOUT = 126
GROUPS = {
    "position": (0,),
    "position_secondhour": (0, 1),
    "position_shape": (0, 1, 2, 3),
    "position_crossmarket": (0, 1, 4, 5),
}
GRID = [(w, r, c) for w in (126, 252) for r in (10.0, 30.0, 100.0, 300.0) for c in (0.03, 0.05, 0.08)]


def simple_rows(dates, closes, positions, own, spy, qqq):
    rows = []
    for j, t0 in enumerate(positions):
        t = int(t0)
        if t + 1 >= len(dates):
            continue
        target = dates[t + 1]
        if target not in own or target not in spy or target not in qqq:
            continue
        o, h, l, c, _, c1 = own[target]
        so, _, _, sc, _, _ = spy[target]
        qo, _, _, qc, _, _ = qqq[target]
        prev = float(closes[t])
        if min(prev, o, h, l, c, c1, so, sc, qo, qc) <= 0:
            continue
        close_loc = (c - l) / max(h - l, 1e-12)
        feat = np.asarray([
            c / prev - 1.0,       # 2h position vs prior close
            c / c1 - 1.0,         # second-hour return
            (h - l) / prev,        # first-2h range
            close_loc,             # close location in first-2h range
            sc / so - 1.0,         # SPY first-2h return
            qc / qo - 1.0,         # QQQ first-2h return
        ], float)
        if np.all(np.isfinite(feat)):
            rows.append((j, t, target, feat))
    return rows


def choose_and_test(symbol, daily, first_shared, two_shared):
    dates_all = sorted(set(daily[symbol]).intersection(daily["SPY"], daily["QQQ"], daily["SCHD"]))
    completed = [(d, daily[symbol][d][3]) for d in dates_all]
    dates, closes, positions, outcomes, p39 = v40.v39_series(
        symbol, completed, {"target_date": "2999-12-31"}, daily[symbol]
    )
    first_rows = v40.hour_features(
        dates, closes, positions,
        first_shared[symbol], first_shared["SPY"], first_shared["QQQ"], first_shared["^VIX"],
    )
    p40_map = core.causal_predictions(first_rows, outcomes, p39, v40.FROZEN_CONFIG[symbol])
    p40 = np.full(len(outcomes), np.nan)
    for j, p in p40_map.items():
        p40[j] = p

    raw = simple_rows(dates, closes, positions, two_shared[symbol], two_shared["SPY"], two_shared["QQQ"])
    raw = [r for r in raw if int(r[0]) in p40_map]
    available = sorted(int(r[0]) for r in raw)
    if len(available) < HOLDOUT + 126:
        return {"symbol": symbol, "promote": False, "reason": f"insufficient aligned {len(available)}"}
    hold = set(available[-HOLDOUT:])
    dev = set(available[:-HOLDOUT])

    best = None
    trials = []
    for group, cols in GROUPS.items():
        rows = [(j, t, d, x[list(cols)]) for j, t, d, x in raw]
        for cfg in GRID:
            cmap = core.causal_predictions(rows, outcomes, p40, cfg)
            idx = np.asarray(sorted(dev.intersection(cmap)), int)
            if len(idx) < 126:
                continue
            cand = np.asarray([cmap[i] for i in idx])
            g = core.gains(p40[idx], cand, outcomes[idx])
            trials.append((float(g[0]), group, cfg, g[:3], cmap, len(idx)))
            if min(g[:3]) > 0 and (best is None or g[0] > best[0]):
                best = (float(g[0]), group, cfg, g[:3], cmap, len(idx))
    if best is None:
        top = sorted(trials, reverse=True, key=lambda x: x[0])[:3]
        return {
            "symbol": symbol,
            "promote": False,
            "reason": "no stable development winner",
            "aligned": len(available),
            "best_development": [
                {"gain": round(x[0], 8), "group": x[1], "config": list(x[2]), "halves": [round(float(z), 8) for z in x[3][1:]]}
                for x in top
            ],
        }

    _, group, cfg, dev_g, cmap, dev_n = best
    hidx = np.asarray(sorted(hold.intersection(cmap)), int)
    if len(hidx) != HOLDOUT:
        return {"symbol": symbol, "promote": False, "reason": f"holdout coverage {len(hidx)}/{HOLDOUT}"}
    cand = np.asarray([cmap[i] for i in hidx])
    base = p40[hidx]
    y = outcomes[hidx]
    overall, half1, half2, diff = core.gains(base, cand, y)
    blocks = [float(diff[i:i+21].mean()) for i in range(0, HOLDOUT, 21)]
    ci_low = core.bootstrap_lower(diff)
    promote = overall > 0 and half1 > 0 and half2 > 0 and all(x > 0 for x in blocks) and ci_low > 0
    return {
        "symbol": symbol,
        "promote": bool(promote),
        "group": group,
        "config": {"window": cfg[0], "ridge": cfg[1], "cap": cfg[2]},
        "development_n": dev_n,
        "development_gain": [round(float(x), 8) for x in dev_g],
        "holdout_n": len(hidx),
        "v40_brier": round(float(np.mean((base-y)**2)), 8),
        "candidate_brier": round(float(np.mean((cand-y)**2)), 8),
        "holdout_gain": round(float(overall), 8),
        "half_gains": [round(float(half1), 8), round(float(half2), 8)],
        "block_gains": [round(float(x), 8) for x in blocks],
        "bootstrap95_gain_lower": round(float(ci_low), 8),
    }


def main():
    daily = {s: v40.daily_ohlcv(s) for s in SYMBOLS}
    first_shared = {s: v40.first_hour(s) for s in ("SPY", "QQQ", "SCHD", "^VIX")}
    two_shared = {s: core.second_hour(s) for s in ("SPY", "QQQ", "SCHD", "^VIX")}
    results = [choose_and_test(s, daily, first_shared, two_shared) for s in SYMBOLS]
    print(json.dumps({"model": "v4.1b-two-hour-simple", "results": results}, ensure_ascii=False, indent=2))
    print("ANY_PROMOTE=", any(r.get("promote") for r in results))


if __name__ == "__main__":
    main()
