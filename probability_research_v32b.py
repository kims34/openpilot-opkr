"""Conservative model-3.2b research.

Model 3.1 is treated as the incumbent policy. Extra regime challengers may only
override it when their realised Brier loss beat the causal 3.1 policy in both
chronological halves of the trailing validation window. All comparisons use
only outcomes already known at forecast time.
"""
import json
import numpy as np

import probability_research_v32 as r


def build_v31_policy(y, preds):
    n = len(y)
    out = np.full(n, np.nan)
    names = np.empty(n, dtype=object)
    start = r.MIN_TRAIN + 120
    for t in range(start, n):
        name = r.causal_selector(y, preds, t, r.BASE_NAMES)
        out[t] = preds[name][t]
        names[t] = name
    return out, names


def conservative_overlay(y, preds, incumbent, t):
    if not np.isfinite(incumbent[t]):
        return "v31", float(incumbent[t])
    start = max(r.MIN_TRAIN + 120, t - r.LOOKBACK)
    mid = start + (t - start) // 2
    best_name = "v31"
    best_gain = 0.0
    for name in r.EXTRA_NAMES:
        p = preds[name]
        if not np.isfinite(p[t]):
            continue
        gains = []
        ok = True
        for a, b in ((start, mid), (mid, t)):
            idx = np.arange(a, b)
            valid = np.isfinite(p[idx]) & np.isfinite(incumbent[idx])
            idx = idx[valid]
            if len(idx) < 60:
                ok = False
                break
            gain = float(np.mean((incumbent[idx] - y[idx]) ** 2 - (p[idx] - y[idx]) ** 2))
            gains.append(gain)
        # Both halves must improve versus the deployed policy, not just fixed base.
        if ok and min(gains) > 0 and sum(gains) > best_gain:
            best_name = name
            best_gain = sum(gains)
    if best_name == "v31":
        return best_name, float(incumbent[t])
    return best_name, float(preds[best_name][t])


def score(p, y):
    return float(np.mean((p - y) ** 2))


def main():
    results = []
    for s in r.SYMBOLS:
        rows = r.fetch(s)
        dates = [d for d, _ in rows]
        prices = np.array([p for _, p in rows], float)
        y, preds = r.candidate_probs(prices, dates)
        n = len(prices)
        incumbent, incumbent_names = build_v31_policy(y, preds)
        start = n - 1 - r.EVAL

        p32 = np.full(n - 1, np.nan)
        choices = []
        for t in range(start, n - 1):
            name, prob = conservative_overlay(y, preds, incumbent, t)
            p32[t] = prob
            choices.append(name)

        idx = np.arange(start, n - 1)
        p31 = incumbent[idx]
        b32 = score(p32[idx], y[idx])
        b31 = score(p31, y[idx])
        mid = start + r.EVAL // 2
        h1_32 = score(p32[start:mid], y[start:mid])
        h1_31 = score(incumbent[start:mid], y[start:mid])
        h2_32 = score(p32[mid:n - 1], y[mid:n - 1])
        h2_31 = score(incumbent[mid:n - 1], y[mid:n - 1])
        counts = {k: choices.count(k) for k in ["v31"] + r.EXTRA_NAMES}
        results.append({
            "symbol": s,
            "brier_v32b": b32,
            "brier_v31": b31,
            "skill_vs_v31": (1 - b32 / b31) * 100,
            "first_half_skill_vs_v31": (1 - h1_32 / h1_31) * 100,
            "second_half_skill_vs_v31": (1 - h2_32 / h2_31) * 100,
            "choices": counts,
            "override_days": int(sum(counts[k] for k in r.EXTRA_NAMES)),
            "current_probability_v32b": float(p32[n - 2]) * 100,
            "current_probability_v31": float(incumbent[n - 2]) * 100,
            "current_v31_strategy": str(incumbent_names[n - 2]),
        })

    pooled32 = float(np.mean([x["brier_v32b"] for x in results]))
    pooled31 = float(np.mean([x["brier_v31"] for x in results]))
    overall = sum(x["skill_vs_v31"] > 0 for x in results)
    recent = sum(x["second_half_skill_vs_v31"] > 0 for x in results)
    # Require a real pooled gain, broad support, and no material recent regression.
    deploy = bool(
        pooled32 < pooled31
        and overall >= 2
        and recent >= 2
        and min(x["second_half_skill_vs_v31"] for x in results) > -0.03
    )
    final = {
        "results": results,
        "pooled_brier_v32b": pooled32,
        "pooled_brier_v31": pooled31,
        "pooled_skill_vs_v31": (1 - pooled32 / pooled31) * 100,
        "deploy": deploy,
        "promotion_rule": "beat v3.1 pooled; >=2 symbols overall/recent; worst recent-half regression > -0.03%",
    }
    print("FINAL", json.dumps(final, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
