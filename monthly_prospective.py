"""Append-only *prospective* IndexAlert 21-session barrier forecasts and scores.

This observes the already served monthly probabilities; it NEVER changes
the probabilities, places orders, performs backfills, or promotes a model.
Only forecasts generated before the next exchange session opens are frozen.
Completed 21-day labels are scored from independently strict daily OHLC.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sqlite3
import time
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import requests

HORIZON = 21
DB_PATH = os.getenv("INDEXALERT_DB", "/tmp/indexalert.db")
ALLOWED_SYMBOLS = frozenset(("SPY", "QQQ"))
NY = ZoneInfo("America/New_York")
MODEL_FAMILY = "served-1m-analog-blended-v1"
SCHEMA_VERSION = 1


def _finite(value, minimum=None, maximum=None):
    if isinstance(value, bool):
        raise ValueError("boolean not numeric")
    x = float(value)
    if not math.isfinite(x):
        raise ValueError("nonfinite number")
    if minimum is not None and x < minimum:
        raise ValueError("number too small")
    if maximum is not None and x > maximum:
        raise ValueError("number too large")
    return x


def _connect(path=None):
    con = sqlite3.connect(path or DB_PATH, timeout=20)
    con.execute("PRAGMA busy_timeout=20000")
    con.execute("""
        CREATE TABLE IF NOT EXISTS monthly_prospective_v1(
          symbol TEXT NOT NULL, model TEXT NOT NULL, as_of TEXT NOT NULL,
          maturity_session TEXT NOT NULL, anchor REAL NOT NULL,
          up_p REAL NOT NULL, down_p REAL NOT NULL,
          baseline_up REAL NOT NULL, baseline_down REAL NOT NULL,
          issued_at REAL NOT NULL, price_basis TEXT NOT NULL,
          source_digest TEXT NOT NULL,
          up_hit INTEGER, down_hit INTEGER, scored_at REAL,
          PRIMARY KEY(symbol,model,as_of)
        )
    """)
    return con


def _maturity(target_first_session, now):
    # Trade-day calendar, NOT calendar-day addition.
    import next_day_probability as market
    first = date.fromisoformat(str(target_first_session))
    cal = market.calendar(datetime.fromtimestamp(now, timezone.utc).year)
    seq = list(cal.sessions_in_range(first.isoformat(),
                  (first + timedelta(days=46)).isoformat()))
    if len(seq) < HORIZON or seq[0].date() != first:
        raise ValueError("incomplete next-21-session calendar")
    return seq[HORIZON-1].date().isoformat()


def _strict_future_ohlc(symbol):
    """No substitution of close for missing daily high/low, even one day."""
    if symbol not in ALLOWED_SYMBOLS:
        raise ValueError("unsupported symbol")
    response = requests.get(
        "https://query1.finance.yahoo.com/v8/finance/chart/" + symbol,
        params={"range": "10y", "interval": "1d", "includePrePost": "false",
                "events": "div,splits"},
        headers={"User-Agent": "Mozilla/5.0 IndexAlert-prospective/1"},
        timeout=25)
    response.raise_for_status()
    results = (response.json().get("chart") or {}).get("result") or []
    if len(results) != 1:
        raise ValueError("missing unique OHLC source")
    raw = results[0]
    if raw.get("meta", {}).get("symbol") != symbol:
        raise ValueError("OHLC symbol mismatch")
    ts = raw.get("timestamp") or []
    q = ((raw.get("indicators") or {}).get("quote") or [{}])[0]
    high, low, closes = (q.get("high") or []), (q.get("low") or []), (q.get("close") or [])
    if not len(ts) == len(high) == len(low) == len(closes):
        raise ValueError("OHLC length mismatch")
    out = {}
    invalid_days = set()
    for stamp, h, l, c in zip(ts, high, low, closes):
        d = datetime.fromtimestamp(int(stamp), timezone.utc).astimezone(NY).date().isoformat()
        if d in out or d in invalid_days:
            raise ValueError("duplicated daily OHLC")
        if h is None or l is None or c is None:
            invalid_days.add(d)
            continue
        try:
            hh, ll, cc = [_finite(v, minimum=1e-12) for v in (h, l, c)]
        except (ValueError, TypeError):
            invalid_days.add(d)
            continue
        if ll > cc + 1e-6 or hh + 1e-6 < cc or hh < ll:
            invalid_days.add(d)
            continue
        out[d] = (hh, ll, cc)
    return out


def _validate_rows(rows):
    if not rows or len(rows) < HORIZON+1:
        raise ValueError("insufficient completed close history")
    last = None
    for day, close in rows:
        d = date.fromisoformat(str(day))
        _finite(close, minimum=1e-12)
        if last is not None and d <= last:
            raise ValueError("unordered or duplicated sessions")
        last = d


def _score_pending(con, symbol, rows, now, vendor):
    prices = {str(d): _finite(v, minimum=1e-12) for d, v in rows}
    by_pos = {str(d): i for i, (d, _) in enumerate(rows)}
    pending = con.execute(
        "SELECT model,as_of,maturity_session,anchor FROM monthly_prospective_v1 "
        "WHERE symbol=? AND up_hit IS NULL", (symbol,)).fetchall()
    scored = 0
    for model, as_of, maturity, anchor in pending:
        if as_of not in by_pos or maturity not in by_pos:
            continue
        idx = by_pos[as_of]
        future = rows[idx+1:idx+1+HORIZON]
        if len(future) != HORIZON or str(future[-1][0]) != maturity:
            continue
        if abs(prices[as_of]/anchor - 1) > 0.001:
            # A split/rebase or historical vendor revision makes the original
            # issued anchor incomparable to today's revised history.
            continue
        touched_hi = False
        touched_lo = False
        complete = True
        for day, close in future:
            d = str(day)
            bar = vendor.get(d)
            if bar is None:
                complete = False
                break
            hi, lo, vendor_close = bar
            if abs(vendor_close/_finite(close, minimum=1e-12) - 1) > 0.001:
                complete = False
                break
            touched_hi |= hi >= anchor*1.10
            touched_lo |= lo <= anchor*0.90
        if not complete:
            continue
        con.execute(
            "UPDATE monthly_prospective_v1 SET up_hit=?,down_hit=?,scored_at=? "
            "WHERE symbol=? AND model=? AND as_of=? AND up_hit IS NULL",
            (int(touched_hi),int(touched_lo),now,symbol,model,as_of))
        scored += 1
    return scored


def observe(symbol, month, rows, meta, now=None, db_path=None, strict_supplier=None):
    """Score previously issued predictions; freeze today's unmodified app output.

    The same (symbol,model,as_of) is never overwritten. A source failure does
    not invent a score. Eventual scores require 21 *complete* future sessions.
    """
    if symbol not in ALLOWED_SYMBOLS:
        return {"status": "symbol_not_tracked"}
    now = time.time() if now is None else float(now)
    _validate_rows(rows)
    with _connect(db_path) as con:
        pending_ready = con.execute(
            "SELECT as_of,maturity_session FROM monthly_prospective_v1 "
            "WHERE symbol=? AND up_hit IS NULL",(symbol,)).fetchall()
        ready_dates = {str(d) for d,_ in rows}
        ready = any(a in ready_dates and m in ready_dates for a,m in pending_ready)
        n_scored = 0
        if ready:
            vendor = (strict_supplier or _strict_future_ohlc)(symbol)
            n_scored = _score_pending(con, symbol, rows, now, vendor)

        inserted = False
        if (isinstance(month, dict) and not month.get("error")
                and month.get("price_basis") == "daily_high_low"
                and str(meta.get("as_of")) == str(rows[-1][0])
                and str(month.get("as_of")) == str(rows[-1][0])
                and now < float(meta.get("target_open") or 0)):
            a = _finite(rows[-1][1], minimum=1e-12)
            up = _finite(month.get("up_10_probability"),0,100)/100
            down = _finite(month.get("down_10_probability"),0,100)/100
            bup = _finite(month.get("baseline_up_10_probability"),0,100)/100
            bdown = _finite(month.get("baseline_down_10_probability"),0,100)/100
            maturity = _maturity(meta["target_date"], now)
            original = con.total_changes
            digest = hashlib.sha256(json.dumps(rows, separators=(",",":")).encode()).hexdigest()
            con.execute("""
                INSERT OR IGNORE INTO monthly_prospective_v1
                (symbol,model,as_of,maturity_session,anchor,up_p,down_p,
                 baseline_up,baseline_down,issued_at,price_basis,source_digest)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                """,(symbol,MODEL_FAMILY,str(rows[-1][0]),maturity,a,up,down,
                      bup,bdown,now,"daily_high_low",digest))
            inserted = con.total_changes > original
        return {"status":"ok", "inserted":inserted, "scored":n_scored}


def summary(db_path=None):
    """Only aggregate anonymised, read-only counts/Brier; no trade authority."""
    with _connect(db_path) as con:
        out = {}
        for symbol in sorted(ALLOWED_SYMBOLS):
            n, pending, last_asof = con.execute(
                "SELECT COUNT(*),SUM(CASE WHEN up_hit IS NULL THEN 1 ELSE 0 END),"
                "MAX(as_of) FROM monthly_prospective_v1 WHERE symbol=?",
                (symbol,)).fetchone()
            rows = con.execute(
                "SELECT up_p,down_p,baseline_up,baseline_down,up_hit,down_hit "
                "FROM monthly_prospective_v1 WHERE symbol=? AND up_hit IS NOT NULL",
                (symbol,)).fetchall()
            scored = len(rows)
            report = {"stored_count":n,"pending_count":int(pending or 0),
                      "scored_count":scored,"last_forecast_date":last_asof,
                      "independent_event_count_approx":scored//HORIZON,
                      "status":"INSUFFICIENT_PROSPECTIVE_EVIDENCE"}
            if scored:
                mean = lambda index, outcome: sum((r[index]-r[outcome])**2 for r in rows)/scored
                report["brier_up"] = mean(0,4)
                report["brier_down"] = mean(1,5)
                report["historical_rate_baseline_brier_up"] = mean(2,4)
                report["historical_rate_baseline_brier_down"] = mean(3,5)
                report["up_event_count"] = sum(int(r[4]) for r in rows)
                report["down_event_count"] = sum(int(r[5]) for r in rows)
            out[symbol] = report
        import monthly_touch_shadow
        import quarterly_touch
        import historical_touch
        return {"model":MODEL_FAMILY,"horizon_sessions":HORIZON,
                "source":"independent prospectively issued predictions, public subsequently checked OHLC",
                "probabilities_altered":False,"orders_enabled":False,
                "symbols":out,"candidates":monthly_touch_shadow.summary(db_path),
                "quarterly_forecasts":quarterly_touch.summary(db_path),
                "historical_forecasts":historical_touch.summary(db_path)}
