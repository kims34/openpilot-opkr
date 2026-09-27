"""Attach prospective Brier safety gates without changing frozen model math."""
from __future__ import annotations

import sqlite3
import time

import next_day_probability as base
import preopen_futures_v312_live
import open_nowcast_v39
import firsthour_nowcast_v40
import probability_live_gate as gate

_PATCHED = False


def _scores(table: str, model: str, symbol: str, previous_column: str):
    allowed = {
        "preopen_futures_forecasts": "baseline_probability",
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


def _score_preopen(symbol, item, result, now):
    """Freeze v3.12 raw candidate and score it against its frozen baseline."""
    now = time.time() if now is None else float(now)
    completed_rows, _ = base.fetch_history(symbol, now)
    prices = dict(completed_rows)
    with sqlite3.connect(base.DB_PATH, timeout=10) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS preopen_futures_forecasts(
            model TEXT, symbol TEXT, as_of TEXT, target TEXT,
            probability REAL, baseline_probability REAL, created REAL,
            outcome INTEGER, scored_at REAL,
            PRIMARY KEY(model,symbol,target))''')
        pending = con.execute(
            "SELECT target,as_of FROM preopen_futures_forecasts WHERE model=? AND symbol=? AND outcome IS NULL",
            (preopen_futures_v312_live.MODEL_VERSION, symbol),
        ).fetchall()
        for target, as_of in pending:
            if target in prices and as_of in prices:
                con.execute(
                    "UPDATE preopen_futures_forecasts SET outcome=?,scored_at=? "
                    "WHERE model=? AND symbol=? AND target=? AND outcome IS NULL",
                    (
                        int(prices[target] > prices[as_of]),
                        now,
                        preopen_futures_v312_live.MODEL_VERSION,
                        symbol,
                        target,
                    ),
                )
        con.execute(
            "INSERT OR IGNORE INTO preopen_futures_forecasts VALUES(?,?,?,?,?,?,?,NULL,NULL)",
            (
                preopen_futures_v312_live.MODEL_VERSION,
                symbol,
                item.get("as_of"),
                item.get("target_date"),
                float(result["probability"]) / 100.0,
                float(result["baseline_probability"]) / 100.0,
                now,
            ),
        )
        rows = con.execute(
            "SELECT probability,baseline_probability,outcome FROM preopen_futures_forecasts "
            "WHERE model=? AND symbol=? AND outcome IS NOT NULL ORDER BY target",
            (preopen_futures_v312_live.MODEL_VERSION, symbol),
        ).fetchall()
    return gate.apply(result, gate.evaluate(rows), "baseline_probability")


def install():
    global _PATCHED
    if _PATCHED:
        return

    original_preopen = preopen_futures_v312_live.estimate
    original_open = open_nowcast_v39._score_and_record
    original_hour = firsthour_nowcast_v40._score_and_record

    def gated_preopen(symbol, item, now=None):
        # The frozen v3.12 model runs first. Only its served probability can be
        # switched; its raw candidate remains frozen in the prospective ledger.
        out = original_preopen(symbol, item, now)
        if not out.get("available") or out.get("probability") is None or out.get("baseline_probability") is None:
            return out
        try:
            return _score_preopen(symbol, item, out, now)
        except Exception as exc:
            out["prospective_error"] = "장전 선물모델 실시간 검증 기록 일시 중단"
            print("preopen live gate unavailable", symbol, type(exc).__name__, flush=True)
            return out

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

    preopen_futures_v312_live.estimate = gated_preopen
    open_nowcast_v39._score_and_record = gated_open
    firsthour_nowcast_v40._score_and_record = gated_hour
    _PATCHED = True


install()
