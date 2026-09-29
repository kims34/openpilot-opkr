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
RECENT_COMMON_OOS_SESSIONS = 504


def paired_moving_block_bootstrap_lcb(
    differences, *, block_length: int = BLOCK_LENGTH,
    samples: int = BOOTSTRAP_SAMPLES, seed: int = BOOTSTRAP_SEED,
) -> dict:
    """Return mean H10-H5 difference and fixed-length moving-block 95% CI."""
    values = np.asarray(list(differences), dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"n_days": 0, "mean_difference": 0.0, "lcb95": 0.0, "ucb95": 0.0}
    if block_length <= 0:
        raise ValueError("block_length must be positive")
    effective_block = min(int(block_length), int(values.size))
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(values.size / effective_block))
    # Standard moving blocks must all have identical length. Restrict starts
    # so an end-of-series draw cannot silently create a short block.
    starts = np.arange(values.size - effective_block + 1)
    means = np.empty(samples, dtype=float)
    for i in range(samples):
        picked = rng.choice(starts, size=n_blocks, replace=True)
        path = np.concatenate([
            values[s:s + effective_block] for s in picked
        ])[:values.size]
        if path.size != values.size:
            raise RuntimeError("moving-block bootstrap produced a short resample")
        means[i] = float(np.mean(path))
    return {
        "n_days": int(values.size),
        "mean_difference": float(np.mean(values)),
        "lcb95": float(np.quantile(means, 0.025)),
        "ucb95": float(np.quantile(means, 0.975)),
        "block_length": int(effective_block),
        "bootstrap_samples": int(samples),
        "seed": int(seed),
    }


def compare_common_oos_paths(h5_daily, h10_daily) -> dict:
    """Compare only the shared OOS span; internal cash/no-trade days are zero."""
    left = pd.Series(h5_daily, dtype=float).sort_index()
    right = pd.Series(h10_daily, dtype=float).sort_index()
    if left.empty or right.empty:
        return paired_moving_block_bootstrap_lcb([])

    common_start = max(left.index.min(), right.index.min())
    common_end = min(left.index.max(), right.index.max())
    if common_start > common_end:
        return paired_moving_block_bootstrap_lcb([])

    left = left.loc[(left.index >= common_start) & (left.index <= common_end)]
    right = right.loc[(right.index >= common_start) & (right.index <= common_end)]
    frame = pd.concat([left.rename("h5"), right.rename("h10")], axis=1).sort_index().fillna(0.0)
    diff = frame["h10"] - frame["h5"]
    result = paired_moving_block_bootstrap_lcb(diff.to_numpy())
    result.update({
        "common_start": str(common_start),
        "common_end": str(common_end),
        "h5_mean_daily_net_return": float(frame["h5"].mean()) if len(frame) else 0.0,
        "h10_mean_daily_net_return": float(frame["h10"].mean()) if len(frame) else 0.0,
    })
    return result


def _finite_metric(d: dict, key: str):
    if not isinstance(d, dict) or key not in d:
        return None
    try:
        value = float(d[key])
    except (TypeError, ValueError):
        return None
    return value if np.isfinite(value) else None


def frozen_short_swing_dominance_audit(
    h5_daily,
    h10_daily,
    *,
    h5_view: dict,
    h10_view: dict,
    h10_best5: dict,
    h10_cost2: dict,
    h10_recent: dict,
) -> dict:
    """Apply every frozen H5-vs-H10 dominance rule without tuning.

    Required views are deliberately explicit so missing evidence fails closed.
    ``h10_recent`` must describe the latest 504 *common OOS* sessions and expose
    ``sessions``, ``selected_records`` and ``cluster_bootstrap_95_low``.
    This function is an evidence audit only and can never promote a model.
    """
    paired = compare_common_oos_paths(h5_daily, h10_daily)

    h10_mean = _finite_metric(h10_view, "fixed_participation_cost_proxy_mean_net_return")
    h10_pf = _finite_metric(h10_view, "profit_factor")
    h10_lcb = _finite_metric(h10_view, "date_cluster_lcb95")
    h5_mdd = _finite_metric(h5_view, "mdd")
    h10_mdd = _finite_metric(h10_view, "mdd")
    h5_es95 = _finite_metric(h5_view, "daily_portfolio_es95")
    h10_es95 = _finite_metric(h10_view, "daily_portfolio_es95")
    h5_es99 = _finite_metric(h5_view, "daily_portfolio_es99")
    h10_es99 = _finite_metric(h10_view, "daily_portfolio_es99")

    best5_mean = _finite_metric(h10_best5, "mean_net_return")
    best5_pf = _finite_metric(h10_best5, "profit_factor")
    best5_lcb = _finite_metric(h10_best5, "cluster_bootstrap_95_low")
    cost2_mean = _finite_metric(h10_cost2, "mean_net_return")
    cost2_pf = _finite_metric(h10_cost2, "profit_factor")
    recent_lcb = _finite_metric(h10_recent, "cluster_bootstrap_95_low")
    try:
        recent_sessions = int(h10_recent.get("sessions", -1))
        recent_selected = int(h10_recent.get("selected_records", -1))
    except (TypeError, ValueError, AttributeError):
        recent_sessions = -1
        recent_selected = -1

    flags = {
        "common_oos_has_full_recent_window": int(paired.get("n_days", 0)) >= RECENT_COMMON_OOS_SESSIONS,
        "paired_h10_minus_h5_lcb95_gt_0": float(paired.get("lcb95", 0.0)) > 0.0,
        "h10_mean_net_return_gt_0": h10_mean is not None and h10_mean > 0.0,
        "h10_profit_factor_gt_1": h10_pf is not None and h10_pf > 1.0,
        "h10_date_cluster_lcb_gt_0": h10_lcb is not None and h10_lcb > 0.0,
        "h10_2x_cost_mean_gt_0": cost2_mean is not None and cost2_mean > 0.0,
        "h10_2x_cost_pf_gt_1": cost2_pf is not None and cost2_pf > 1.0,
        "h10_best5_removed_mean_gt_0": best5_mean is not None and best5_mean > 0.0,
        "h10_best5_removed_pf_gt_1": best5_pf is not None and best5_pf > 1.0,
        "h10_best5_removed_cluster_lcb_gt_0": best5_lcb is not None and best5_lcb > 0.0,
        "latest_504_common_oos_window_exact": recent_sessions == RECENT_COMMON_OOS_SESSIONS,
        "latest_504_has_admissions": recent_selected > 0,
        "latest_504_cluster_lcb_gt_0": recent_lcb is not None and recent_lcb > 0.0,
        # Drawdown and ES are returns: less negative / larger is no worse.
        "h10_mdd_not_worse_than_h5": (
            h5_mdd is not None and h10_mdd is not None and h10_mdd >= h5_mdd
        ),
        "h10_daily_es95_not_worse_than_h5": (
            h5_es95 is not None and h10_es95 is not None and h10_es95 >= h5_es95
        ),
        "h10_daily_es99_not_worse_than_h5": (
            h5_es99 is not None and h10_es99 is not None and h10_es99 >= h5_es99
        ),
    }
    all_pass = bool(all(flags.values()))
    failed = [name for name, ok in flags.items() if not ok]
    return {
        "evaluation_stage": "FROZEN_SHORT_SWING_DOMINANCE_AUDIT_NOT_HOLDOUT",
        "paired_common_oos": paired,
        "flags": flags,
        "failed_checks": failed,
        "all_frozen_dominance_checks_pass": all_pass,
        "verdict": (
            "SHORT_SWING_DOMINANCE_CONTRACT_PASS_NOT_PROMOTED"
            if all_pass
            else "SHORT_SWING_DOMINANCE_CONTRACT_FAIL"
        ),
        "promotion_allowed": False,
        "sealed_holdout_burned": False,
    }
