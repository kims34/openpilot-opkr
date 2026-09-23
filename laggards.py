import math
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 IndexAlert/1.0"}
SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
NASDAQ100_URLS = [
    "https://indexes.nasdaq.com/Index/Weighting/NDX",
    "https://en.wikipedia.org/wiki/Nasdaq-100",
]
SCHD_URL = "https://www.schwabassetmanagement.com/allholdings/schd"
REFRESH_LOCK = threading.Lock()


def _clean_symbol(symbol: str) -> str:
    return symbol.strip().upper().replace("\u00a0", "")


def _yahoo_symbol(symbol: str) -> str:
    return _clean_symbol(symbol).replace(".", "-")


def _table_rows(url: str):
    r = requests.get(url, headers=UA, timeout=25)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for table in soup.find_all("table"):
        headers = [th.get_text(" ", strip=True).lower() for th in table.find_all("th")]
        if not headers:
            continue
        rows = []
        for tr in table.find_all("tr"):
            cells = [x.get_text(" ", strip=True) for x in tr.find_all(["td", "th"])]
            if cells:
                rows.append(cells)
        yield headers, rows


def sp500_constituents():
    for headers, rows in _table_rows(SP500_URL):
        if "symbol" not in headers or not any(x in headers for x in ("security", "company", "company name")):
            continue
        sym_i = headers.index("symbol")
        name_i = next(headers.index(x) for x in ("security", "company", "company name") if x in headers)
        out = []
        for row in rows[1:]:
            if len(row) <= max(sym_i, name_i):
                continue
            sym = _clean_symbol(row[sym_i])
            name = row[name_i].strip()
            if re.fullmatch(r"[A-Z.\-]{1,8}", sym):
                out.append((sym, name))
        if len(out) >= 450:
            return out
    raise RuntimeError("S&P500 constituent list unavailable")


def nasdaq100_symbols():
    for url in NASDAQ100_URLS:
        try:
            for headers, rows in _table_rows(url):
                symbol_headers = ("security symbol", "symbol", "ticker")
                matches = [x for x in symbol_headers if x in headers]
                if not matches:
                    continue
                sym_i = headers.index(matches[0])
                out = set()
                for row in rows[1:]:
                    if len(row) <= sym_i:
                        continue
                    sym = _clean_symbol(row[sym_i])
                    if re.fullmatch(r"[A-Z.\-]{1,8}", sym):
                        out.add(sym)
                if len(out) >= 90:
                    return out
        except Exception:
            continue
    return set()


def schd_symbols():
    try:
        for headers, rows in _table_rows(SCHD_URL):
            if "symbol" not in headers:
                continue
            sym_i = headers.index("symbol")
            out = set()
            for row in rows[1:]:
                if len(row) <= sym_i:
                    continue
                sym = _clean_symbol(row[sym_i])
                if re.fullmatch(r"[A-Z.\-]{1,8}", sym):
                    out.add(sym)
            if len(out) >= 80:
                return out

        r = requests.get(SCHD_URL, headers=UA, timeout=25)
        r.raise_for_status()
        lines = [x.strip() for x in BeautifulSoup(r.text, "html.parser").stripped_strings]
        out = set()
        for i, line in enumerate(lines[:-1]):
            if line.lower() == "symbol":
                sym = _clean_symbol(lines[i + 1])
                if re.fullmatch(r"[A-Z.\-]{1,8}", sym):
                    out.add(sym)
        return out if len(out) >= 80 else set()
    except Exception:
        return set()


def init_db(monitor):
    with monitor.db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS stock_ath(
            symbol TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            ath REAL NOT NULL,
            ath_ts INTEGER NOT NULL,
            current REAL NOT NULL,
            drawdown REAL NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS laggard_cache(
            rank INTEGER PRIMARY KEY,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            current REAL NOT NULL,
            ath REAL NOT NULL,
            drawdown REAL NOT NULL,
            in_nasdaq100 INTEGER NOT NULL,
            in_schd INTEGER NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS app_meta(
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """)


def _history_ath(monitor, symbol: str):
    ys = _yahoo_symbol(symbol)
    url = monitor.YAHOO.format(symbol=quote(ys, safe=""))
    r = requests.get(
        url,
        params={"range": "max", "interval": "1mo", "includePrePost": "false", "events": "splits"},
        headers=UA,
        timeout=20,
    )
    r.raise_for_status()
    result = (r.json().get("chart", {}).get("result") or [None])[0]
    if not result:
        raise RuntimeError("history unavailable")
    timestamps = result.get("timestamp") or []
    highs = result.get("indicators", {}).get("quote", [{}])[0].get("high", []) or []
    split_events = (result.get("events") or {}).get("splits") or {}
    splits = []
    for ev in split_events.values():
        try:
            ts = int(ev.get("date") or 0)
            num = float(ev.get("numerator") or 0)
            den = float(ev.get("denominator") or 0)
            if num > 0 and den > 0:
                ratio = num / den
            else:
                raw = str(ev.get("splitRatio") or "")
                if ":" in raw:
                    a, b = raw.split(":", 1)
                    ratio = float(a) / float(b)
                else:
                    ratio = float(raw)
            if ts > 0 and ratio > 0:
                splits.append((ts, ratio))
        except Exception:
            continue
    best = 0.0
    best_ts = 0
    for ts, high in zip(timestamps, highs):
        if high is None:
            continue
        h = float(high)
        if not math.isfinite(h) or h <= 0:
            continue
        factor = 1.0
        for split_ts, ratio in splits:
            if split_ts > int(ts):
                factor *= ratio
        adjusted = h / factor
        if adjusted >= best:
            best = adjusted
            best_ts = int(ts)
    if best <= 0:
        raise RuntimeError("ATH unavailable")
    return best, best_ts


def _daily_quote(monitor, symbol: str):
    result = monitor.yahoo_result(_yahoo_symbol(symbol), "5d", "1d", False)
    points = monitor.series(result)
    if not points:
        raise RuntimeError("quote unavailable")
    ts, current = points[-1]
    highs = result.get("indicators", {}).get("quote", [{}])[0].get("high", []) or []
    timestamps = result.get("timestamp") or []
    recent_high = current
    recent_high_ts = ts
    for hts, high in zip(timestamps, highs):
        if high is None:
            continue
        h = float(high)
        if math.isfinite(h) and h >= recent_high:
            recent_high = h
            recent_high_ts = int(hts)
    return current, recent_high, recent_high_ts


def _set_meta(monitor, key: str, value: str):
    with monitor.db() as con:
        con.execute(
            "INSERT INTO app_meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )


def refresh(monitor):
    if not REFRESH_LOCK.acquire(blocking=False):
        return
    try:
        init_db(monitor)
        constituents = sp500_constituents()
        ndx = nasdaq100_symbols()
        schd = schd_symbols()
        with monitor.db() as con:
            existing = {
                row[0]: (float(row[1]), int(row[2]))
                for row in con.execute("SELECT symbol,ath,ath_ts FROM stock_ath").fetchall()
            }

        def work(item):
            symbol, name = item
            current, recent_high, recent_high_ts = _daily_quote(monitor, symbol)
            if symbol in existing:
                ath, ath_ts = existing[symbol]
            else:
                ath, ath_ts = _history_ath(monitor, symbol)
            if recent_high >= ath:
                ath, ath_ts = recent_high, recent_high_ts
            if ath <= 0 or current <= 0:
                raise RuntimeError("invalid values")
            dd = (current / ath - 1.0) * 100.0
            return symbol, name, current, ath, ath_ts, dd

        results = []
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(work, item) for item in constituents]
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception:
                    pass

        now = datetime.now(timezone.utc).isoformat()
        with monitor.db() as con:
            con.executemany(
                """INSERT INTO stock_ath(symbol,name,ath,ath_ts,current,drawdown,updated_at)
                   VALUES(?,?,?,?,?,?,?)
                   ON CONFLICT(symbol) DO UPDATE SET name=excluded.name,ath=excluded.ath,ath_ts=excluded.ath_ts,
                   current=excluded.current,drawdown=excluded.drawdown,updated_at=excluded.updated_at""",
                [(s,n,a,ts,c,dd,now) for s,n,c,a,ts,dd in results],
            )

        coverage = len(results)
        total = len(constituents)
        _set_meta(monitor, "laggard_coverage", f"{coverage}/{total}")
        _set_meta(monitor, "laggard_source_time", now)
        if coverage < max(400, int(total * 0.85)):
            _set_meta(monitor, "laggard_status", "building")
            return

        ranked = sorted(results, key=lambda x: x[5])[:10]
        with monitor.db() as con:
            con.execute("DELETE FROM laggard_cache")
            con.executemany(
                """INSERT INTO laggard_cache(rank,symbol,name,current,ath,drawdown,in_nasdaq100,in_schd,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?)""",
                [
                    (i, s, n, c, a, dd, int(s in ndx), int(s in schd), now)
                    for i, (s,n,c,a,ts,dd) in enumerate(ranked, 1)
                ],
            )
        _set_meta(monitor, "laggard_status", "ready")
    except Exception as exc:
        _set_meta(monitor, "laggard_status", "error")
        _set_meta(monitor, "laggard_error", type(exc).__name__)
        print("laggard refresh failed:", type(exc).__name__, flush=True)
    finally:
        REFRESH_LOCK.release()


def get(monitor):
    init_db(monitor)
    with monitor.db() as con:
        rows = con.execute(
            """SELECT rank,symbol,name,current,ath,drawdown,in_nasdaq100,in_schd,updated_at
               FROM laggard_cache ORDER BY rank"""
        ).fetchall()
        meta = dict(con.execute("SELECT key,value FROM app_meta WHERE key LIKE 'laggard_%'").fetchall())
    return {
        "status": meta.get("laggard_status", "building"),
        "coverage": meta.get("laggard_coverage", "0/0"),
        "updated_at": meta.get("laggard_source_time"),
        "items": [
            {
                "rank": r[0], "symbol": r[1], "name": r[2], "current": r[3], "ath": r[4],
                "drawdown": r[5], "sp500": True, "nasdaq100": bool(r[6]), "schd": bool(r[7]),
                "updated_at": r[8],
            }
            for r in rows
        ],
    }
