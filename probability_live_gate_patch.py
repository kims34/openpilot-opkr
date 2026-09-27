"""Attach prospective Brier safety gates without changing frozen model math."""
from __future__ import annotations

import sqlite3

import next_day_probability as base
import open_nowcast_v39
import firsthour_nowcast_v40
import probability_live_gate as gate

_PATCHED = False


def _scores(table: str, model: str, symbol: str, previous_column: str):
    allowed = {
        "open_nowcast_forecasts": "preopen_probability",
        "firsthour_nowcast_forecasts": "previous_probability",
    }
    if allowed.get(table) != previous_column:
        raise ValueError("unsupported probability ledger")
    with sqlite3.connect(base.DB_PATH, timeout=10) as con:
        return con.execute(
            f"SELECT probability,{previous_column},outcome FROM {table} "
            "WHERE model=? AND symbol=? AND outcome IS NOT NULL ORDER BY target",
            (model, symbol),
        ).fetchall()


def install():
    global _PATCHED
    if _PATCHED:
        return

    original_open = open_nowcast_v39._score_and_record
    original_hour = firsthour_nowcast_v40._score_and_record

    def gated_open(symbol, item, result, completed_rows, now):
        # Original function freezes/scores the RAW candidate first.
        out = original_open(symbol, item, result, completed_rows, now)
        rows = _scores(
            "open_nowcast_forecasts",
            open_nowcast_v39.MODEL_VERSION,
            symbol,
            "preopen_probability",
        )
        verdict = gate.evaluate(rows)
        return gate.apply(out, verdict, "preopen_probability")

    def gated_hour(symbol, item, result, completed_rows, now):
        # Original function freezes/scores the RAW candidate first.
        out = original_hour(symbol, item, result, completed_rows, now)
        rows = _scores(
            "firsthour_nowcast_forecasts",
            firsthour_nowcast_v40.MODEL_VERSION,
            symbol,
            "previous_probability",
        )
        verdict = gate.evaluate(rows)
        return gate.apply(out, verdict, "previous_probability")

    open_nowcast_v39._score_and_record = gated_open
    firsthour_nowcast_v40._score_and_record = gated_hour
    _PATCHED = True


install()
