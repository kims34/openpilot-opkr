"""Direct historical benchmark against the EXACT existing blended 21-day model.

No prod deployment, no secret, no orders. FastBaseline is an algorithmic
memoization of one_month_calibrated.estimate_probability: all its per-target
analog calculations, K grid, split gates, training label cutoffs, and prior
are preserved. A parity unit test checks against the unmodified app code.
Public historical VIX/VXN and highs/lows are NOT authenticated PIT snapshots.
"""
from __future__ import annotations

import math
import statistics
from collections import defaultdict

import numpy as np

import one_month_probability as barrier
import one_month_calibrated as served
import research_monthly_touch_v1 as monthly

K_VALUES = tuple(barrier.K_CANDIDATES)
W_VALUES = tuple(served.BLEND_WEIGHTS)
H = barrier.HORIZON
MIN_I = barrier.MIN_FEATURE_INDEX


def _one_ranked_prediction(rank, outcomes, prior, k):
    subset = rank[:k]
    if not subset:
        return prior
    bandwidth = max(statistics.median(d for d, idx in subset), 0.35)
    weights = [math.exp(-0.5*(d/bandwidth)**2) for d, idx in subset]
    sw = sum(weights)
    return (sum(w*outcomes[idx] for w, (_,idx) in zip(weights, subset))
            + barrier.PRIOR_STRENGTH * prior) / (sw + barrier.PRIOR_STRENGTH)


class FastServedReplay:
    """Identical arithmetic and cutoff semantics, but caches historical targets."""
    def __init__(self, close_rows, ohlc_rows):
        dates, prices, highs, lows = monthly.validate_ohlc(close_rows, ohlc_rows)
        self.dates, self.p, self.h, self.l = dates, prices, highs, lows
        self.prices = prices.tolist()
        self.records = barrier._records(self.prices, highs.tolist(), lows.tolist())
        self.features = {r[0]: r[1] for r in self.records}
        # Current forecast target t may not itself yet have completed 21-day label,
        # but its features require only prices already observed at time t.
        self.score_cache = {}
        self.current_cache = {}
        self.calls = 0

    def _predict_pair(self, t, *, current):
        cache = self.current_cache if current else self.score_cache
        if t in cache:
            return cache[t]
        if t < MIN_I:
            raise ValueError("insufficient feature history")
        cutoff = t - H if current else t - H - 1
        count = cutoff - MIN_I + 1
        if count < 300:
            raise ValueError("insufficient fully matured analog training")
        training = self.records[:count]
        # All training labels end at or before t (strictly before t for
        # historical validation rows, reproducing the old model's +1 gap).
        up = [r[2] for r in training]
        down = [r[3] for r in training]
        base = (sum(up) / count, sum(down) / count)
        f = (barrier._features(self.prices, t) if current else self.features[t])
        # Once ranked, de-overlapping neighbor selection is identical for
        # all K. Never rank a future observation.
        ranked = sorted((barrier._distance(f, r[1]), r[0]) for r in training)
        selected = []
        selected_indices = []
        for distance, idx in ranked:
            if any(abs(idx-old) < 3 for old in selected_indices):
                continue
            selected.append((distance, idx))
            selected_indices.append(idx)
            if len(selected) >= max(K_VALUES):
                break
        u = {r[0]:r[2] for r in training}
        d = {r[0]:r[3] for r in training}
        output = {"base": np.asarray(base, dtype=float),
                  "analog": {k: np.asarray((
                      _one_ranked_prediction(selected, u, base[0], k),
                      _one_ranked_prediction(selected, d, base[1], k)),
                      dtype=float) for k in K_VALUES}}
        cache[t] = output
        self.calls += 1
        return output

    def prep(self, targets):
        if not targets:
            raise ValueError("no historical evaluation targets")
        lo = min(targets)
        hi = max(targets)
        # Original history scoring window: last 504 mature target windows.
        for q in range(max(MIN_I+300+H, lo-504-H), hi-H+1):
            self._predict_pair(q, current=False)
        for t in targets:
            self._predict_pair(t, current=True)

    def _score_grid(self, indices, side, k):
        q = [self._predict_pair(int(i), current=False) for i in indices]
        b = np.asarray([x["base"][side] for x in q])
        a = np.asarray([x["analog"][k][side] for x in q])
        y = np.asarray([self.records[int(i)-MIN_I][side+2] for i in indices],
                       dtype=float)
        baseline = float(np.mean((b-y)**2))
        return {w: {
            "count": len(y),
            "model_brier": float(np.mean((b+w*(a-b)-y)**2)),
            "baseline_brier": baseline,
            "skill": 100.0*(1.0 - float(np.mean((b+w*(a-b)-y)**2))/baseline)
                     if baseline > 0 else 0.0,
        } for w in W_VALUES}

    def _choose(self, t, side):
        # Same policy as _validation_targets, _choose_binary, _half_guardrail.
        last_mature = t-H
        start = max(MIN_I+300+H, (t+1)-barrier.VALIDATION_DAYS-H)
        eligible = list(range(start, last_mature+1))
        if len(eligible) < 120:
            return K_VALUES[1], 0.0, False
        split = max(60, int(len(eligible)*barrier.TUNE_FRACTION))
        tune, test = eligible[:split], eligible[split:]
        candidates = []
        for k in K_VALUES:
            for w, val in self._score_grid(tune, side, k).items():
                candidates.append((val["model_brier"], w, k))
        _, weight, chosen_k = min(candidates, key=lambda x: (x[0], x[1], x[2]))
        whole = self._score_grid(test, side, chosen_k).get(weight)
        mid = len(test)//2
        first = self._score_grid(test[:mid], side, chosen_k).get(weight)
        second = self._score_grid(test[mid:], side, chosen_k).get(weight)
        passed = bool(
            weight > 0
            and whole and whole["count"] >= served.MIN_TEST_COUNT
            and whole["skill"] > 0
            and first and second
            and first["count"] >= served.MIN_HALF_COUNT
            and second["count"] >= served.MIN_HALF_COUNT
            and first["skill"] > 0 and second["skill"] > 0
        )
        return chosen_k, float(weight if passed else 0.0), passed

    def estimate(self, t):
        if t < MIN_I + H + 300:
            raise ValueError("not enough causal lookback for served monthly model")
        state = self._predict_pair(t, current=True)
        answer = {}
        for side, field in enumerate(("up", "down")):
            k, w, selected = self._choose(t, side)
            prob = float(state["base"][side]+w*(state["analog"][k][side]-state["base"][side]))
            answer[field] = round(prob*100.0, 1)/100.0
            answer[field+"_selected_k"] = k
            answer[field+"_blend_weight"] = w
            answer[field+"_analog_enabled"] = selected
        return answer

    def exact_app_estimate(self, t):
        """Slow original code for audit parity; use sparingly."""
        rows = list(zip(self.dates[:t+1], self.prices[:t+1]))
        ohlc = [(self.dates[i], float(self.h[i]), float(self.l[i]), float(self.p[i]))
                for i in range(t+1)]
        result = served.estimate_probability(rows, ohlc)
        return {"up": result["up_10_probability"]/100.0,
                "down": result["down_10_probability"]/100.0,
                "up_selected_k": result["selected_k_up"],
                "down_selected_k": result["selected_k_down"],
                "up_blend_weight": result["blend_weight_up"],
                "down_blend_weight": result["blend_weight_down"]}


def metric(a, b, outcomes, *, block_size=H):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    y = np.asarray(outcomes, dtype=float)
    if len(y) < 2 or a.shape != b.shape or a.shape != y.shape:
        raise ValueError("misaligned direct comparison")
    l0, l1 = (a-y)**2, (b-y)**2
    gain = l0-l1
    actual_event = y.sum(axis=0)
    rng = np.random.default_rng(20261116)
    block = min(int(block_size), len(y))
    simulations = []
    for _ in range(600):
        start = rng.integers(0, len(y)-block+1,
                             size=math.ceil(len(y)/block))
        ids = (start[:,None] + np.arange(block)).ravel()[:len(y)]
        simulations.append(float(gain[ids].mean()))
    lo, hi = np.quantile(simulations, (0.025,0.975))
    buckets = []
    for side in range(2):
        bins = []
        for left, right in ((0,0.1),(0.1,0.2),(0.2,0.4),(0.4,1.00001)):
            mask = (a[:,side] >= left)&(a[:,side] < right)
            if int(mask.sum())>0:
                bins.append({"band":f"{left:.1f}-{min(right,1):.1f}",
                    "n":int(mask.sum()),"mean_probability":float(a[mask,side].mean()),
                    "actual_rate":float(y[mask,side].mean())})
        buckets.append(bins)
    return {
        "n":len(y), "event_count_up":int(actual_event[0]),
        "event_count_down":int(actual_event[1]),
        "baseline_brier_up":float(l0[:,0].mean()),
        "baseline_brier_down":float(l0[:,1].mean()),
        "challenger_brier_up":float(l1[:,0].mean()),
        "challenger_brier_down":float(l1[:,1].mean()),
        "gain_up":float(gain[:,0].mean()),
        "gain_down":float(gain[:,1].mean()),
        "gain_combined":float(gain.mean()),
        "block_bootstrap_ci95_combined":[float(lo),float(hi)],
        "baseline_calibration_bins":[{"side":"up","bins":buckets[0]},
                                     {"side":"down","bins":buckets[1]}],
    }


def compare(prices, highs, lows, baseline, rival, *, dates=None, block=H):
    outcomes = []
    for t in range(len(baseline)):
        outcomes.append(monthly.touch_label(prices,highs,lows,t))
    return metric(baseline,rival,outcomes,block_size=block)
