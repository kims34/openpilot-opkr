"""Prospective-only reliability diagnostics for IndexAlert probability forecasts.

This module never changes the served probability. It summarizes immutable live
forecasts after their target sessions complete, so historical backtests cannot
silently substitute for real-world evidence.
"""
import sqlite3

WINDOWS = (20, 40, 60)


def _metrics(rows):
    """Rows are (p, baseline_p, outcome), ordered oldest -> newest."""
    if not rows:
        return None
    n = len(rows)
    model_brier = sum((float(p) - int(y)) ** 2 for p, _, y in rows) / n
    baseline_brier = sum((float(b) - int(y)) ** 2 for _, b, y in rows) / n
    skill = (1.0 - model_brier / baseline_brier) * 100.0 if baseline_brier > 0 else None
    direction_accuracy = (
        sum(int((float(p) >= 0.5) == bool(int(y))) for p, _, y in rows) / n * 100.0
    )
    mean_probability = sum(float(p) for p, _, _ in rows) / n * 100.0
    observed_rise_rate = sum(int(y) for _, _, y in rows) / n * 100.0
    return {
        "count": n,
        "brier": model_brier,
        "baseline_brier": baseline_brier,
        "skill": skill,
        "direction_accuracy": direction_accuracy,
        "mean_probability": mean_probability,
        "observed_rise_rate": observed_rise_rate,
        "calibration_gap_pp": mean_probability - observed_rise_rate,
        "beats_baseline": bool(model_brier < baseline_brier),
    }


def summarize(db_path, model_version, symbol):
    """Return rolling live diagnostics for one symbol/model.

    Guardrail states are intentionally conservative and informational only:
      collecting: fewer than 20 scored forecasts
      normal: no persistent evidence of recent underperformance
      watch: both available 20- and 40-session windows trail the baseline
      review: 20-, 40-, and 60-session windows all trail the baseline

    No state changes the forecast served to the app.
    """
    try:
        with sqlite3.connect(db_path, timeout=10) as con:
            table = con.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='probability_forecasts'"
            ).fetchone()
            if not table:
                return {
                    "state": "collecting",
                    "scored_count": 0,
                    "windows": {},
                    "served_probability_unchanged": True,
                }
            rows = con.execute(
                """SELECT p,base,outcome
                   FROM probability_forecasts
                   WHERE model=? AND symbol=? AND outcome IS NOT NULL
                   ORDER BY target""",
                (model_version, symbol),
            ).fetchall()
    except Exception as exc:
        return {
            "state": "unavailable",
            "scored_count": 0,
            "windows": {},
            "served_probability_unchanged": True,
            "error": type(exc).__name__,
        }

    scored = len(rows)
    windows = {}
    for size in WINDOWS:
        if scored >= size:
            windows[str(size)] = _metrics(rows[-size:])

    if scored < 20:
        state = "collecting"
    else:
        trailing = {
            int(k): bool(v and not v["beats_baseline"])
            for k, v in windows.items()
        }
        if all(trailing.get(size, False) for size in WINDOWS):
            state = "review"
        elif trailing.get(20, False) and trailing.get(40, False):
            state = "watch"
        else:
            state = "normal"

    return {
        "state": state,
        "scored_count": scored,
        "windows": windows,
        "served_probability_unchanged": True,
    }
