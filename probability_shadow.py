"""Prospective-only shadow forecasts for probability challengers.

Shadow forecasts never change the probability served by IndexAlert.  They are
written before the target session opens and scored only after that target close
exists in completed price history.  This gives future-only evidence for model
promotion without repeatedly mining the same historical sample.
"""
import os
import sqlite3

DB_PATH = os.getenv("INDEXALERT_DB", "/tmp/indexalert.db")

# Pre-registered, low-risk calibration challengers.  These are intentionally
# simple and frozen: changing a formula gets a new model name so prospective
# histories remain comparable and immutable.
SHADOW_MODELS = {
    "shadow-fixed75-v1": lambda p, base: base + 0.75 * (p - base),
    "shadow-fixed50-v1": lambda p, base: base + 0.50 * (p - base),
    "shadow-half75-v1": lambda p, base: 50.0 + 0.75 * (p - 50.0),
}


def _probabilities(result):
    p = float(result["probability"])
    base = float(result["base_rate"])
    values = {}
    for name, transform in SHADOW_MODELS.items():
        value = float(transform(p, base))
        if not 0.0 <= value <= 100.0:
            raise ValueError(f"shadow probability out of range: {name}")
        values[name] = value / 100.0
    return values


def record_shadow_forecasts(symbol, result, rows, now, db_path=None):
    """Score old shadows and immutably record today's pre-open challengers.

    Returns aggregate prospective Brier scores by shadow model.  The function
    is deliberately independent of the served model's table so a shadow bug
    cannot modify production forecast records.
    """
    path = db_path or DB_PATH
    prices = dict(rows)
    with sqlite3.connect(path, timeout=10) as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS probability_shadow_forecasts(
                model TEXT NOT NULL,
                symbol TEXT NOT NULL,
                as_of TEXT NOT NULL,
                target TEXT NOT NULL,
                p REAL NOT NULL,
                created REAL NOT NULL,
                outcome INTEGER,
                scored_at REAL,
                PRIMARY KEY(model,symbol,as_of)
            )"""
        )

        pending = con.execute(
            "SELECT model,as_of,target FROM probability_shadow_forecasts "
            "WHERE symbol=? AND outcome IS NULL",
            (symbol,),
        ).fetchall()
        for model, as_of, target in pending:
            if as_of in prices and target in prices:
                con.execute(
                    "UPDATE probability_shadow_forecasts SET outcome=?,scored_at=? "
                    "WHERE model=? AND symbol=? AND as_of=? AND outcome IS NULL",
                    (int(prices[target] > prices[as_of]), now, model, symbol, as_of),
                )

        # Like the production ledger, only a forecast that existed before the
        # target open is eligible. INSERT OR IGNORE makes it immutable.
        if now < float(result["target_open"]):
            for model, probability in _probabilities(result).items():
                con.execute(
                    "INSERT OR IGNORE INTO probability_shadow_forecasts "
                    "VALUES(?,?,?,?,?,?,NULL,NULL)",
                    (
                        model,
                        symbol,
                        result["as_of"],
                        result["target_date"],
                        probability,
                        now,
                    ),
                )

        rows_scored = con.execute(
            "SELECT model,p,outcome FROM probability_shadow_forecasts "
            "WHERE symbol=? AND outcome IS NOT NULL",
            (symbol,),
        ).fetchall()

    grouped = {}
    for model, p, outcome in rows_scored:
        item = grouped.setdefault(model, {"count": 0, "sse": 0.0})
        item["count"] += 1
        item["sse"] += (float(p) - int(outcome)) ** 2
    return {
        model: {
            "count": values["count"],
            "brier": values["sse"] / values["count"],
        }
        for model, values in grouped.items()
    }
