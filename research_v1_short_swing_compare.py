"""Frozen H5-vs-H10 common-OOS paired portfolio comparison.

This is a reporting utility only. It does not tune either engine or redefine
the existing execution, cost, PIT, or validation contracts.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

BLOCK_LENGTH = 10
BOOTSTRAP_SAMPLES = 2000
BOOTSTRAP_SEED = 20260929


def paired_moving_block_bootstrap_lcb(
    differences, *, block_length: int = BLOCK_LENGTH,
    samples: int = BOOTSTRAP_SAMPLES, seed: int = BOOTSTRAP_SEED,
) -> dict:
    """Return mean H10-H5 difference and fixed 10-session block 95% LCB."""
    values = np.asarray(list(differences), dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"n_days": 0, "mean_difference": 0.0, "lcb95": 0.0, "ucb95": 0.0}
    if block_length <= 0:
        raise ValueError("block_length must be positive")
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(values.size / block_length))
    starts = np.arange(values.size)
    means = np.empty(samples, dtype=float)
    for i in range(samples):
        picked = rng.choice(starts, size=n_blocks, replace=True)
        path = np.concatenate([values[s:s + block_length] for s in picked])[:values.size]
        means[i] = float(np.mean(path))
    return {
        "n_days": int(values.size),
        "mean_difference": float(np.mean(values)),
        "lcb95": float(np.quantile(means, 0.025)),
        "ucb95": float(np.quantile(means, 0.975)),
        "block_length": int(block_length),
        "bootstrap_samples": int(samples),
        "seed": int(seed),
    }


def compare_common_oos_paths(h5_daily, h10_daily) -> dict:
    """Compare aligned daily portfolio paths, assigning cash/no-trade as zero."""
    left = pd.Series(h5_daily, dtype=float)
    right = pd.Series(h10_daily, dtype=float)
    frame = pd.concat([left.rename("h5"), right.rename("h10")], axis=1).sort_index().fillna(0.0)
    diff = frame["h10"] - frame["h5"]
    result = paired_moving_block_bootstrap_lcb(diff.to_numpy())
    result.update({
        "common_start": str(frame.index.min()) if len(frame) else None,
        "common_end": str(frame.index.max()) if len(frame) else None,
        "h5_mean_daily_net_return": float(frame["h5"].mean()) if len(frame) else 0.0,
        "h10_mean_daily_net_return": float(frame["h10"].mean()) if len(frame) else 0.0,
    })
    return result

