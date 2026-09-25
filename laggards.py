import math
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 IndexAlert/1.0"}
SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
NASDAQ100_URLS = [
    "https://indexes.nasdaq.com/Index/Weighting/NDX",
    "https://en.wikipedia.org/wiki/List_of_NASDAQ-100_companies",
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
        trs = table.find_all("tr")
        if not trs:
            continue
        for header_row_index in range(min(4, len(trs))):
            header_cells = trs[header_row_index].find_all(["th", "td"])
            headers = [c.get_text(" ", strip=True).lower() for c in header_cells]
            if not headers:
                continue
            rows = []
            for tr in trs[header_row_index + 1:]:
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
        for row in rows:
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
                matches = [x for x in ("security symbol", "symbol", "ticker", "ticker symbol") if x in headers]
                if not matches:
                    continue
                sym_i = headers.index(matches[0])
                out = set()
                for row in rows:
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
            for row in rows:
                if len(row) <= sym_i:
                    continue
                sym = _clean_symbol(row[sym_i])
                if re.fullmatch(r"[A-Z.\-]{1,8}", sym):
                    out.add(sym)
            if len(out) >= 80:
                return out
    except Exception:
        pass
    return set()


def init_db(monitor):
    with monitor.db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS universe_mover_cache(
            universe TEXT NOT NULL,
            rank INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            current REAL NOT NULL,
            previous_close REAL NOT NULL,
            day_change REAL NOT NULL,
            day_change_pct REAL NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY(universe, rank)
        );
        CREATE TABLE IF NOT EXISTS app_meta(
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """)


def _market_quote(monitor, symbol: str):
    result = monitor.yahoo_result(_yahoo_symbol(symbol), "5d", "5m", True)
    points = monitor.series(result)
    if not points:
        raise RuntimeError("quote unavailable")
    _, current = points[-1]
    meta = result.get("meta", {})
    previous_close = current
    for key in ("regularMarketPreviousClose", "previousClose", "chartPreviousClose"):
        try:
            value = float(meta.get(key) or 0)
            if math.isfinite(value) and value > 0:
                previous_close = value
                break
        except Exception:
            pass
    if current <= 0 or previous_close <= 0:
        raise RuntimeError("invalid quote")
    name = str(meta.get("longName") or meta.get("shortName") or symbol).strip()
    day_change = current - previous_close
    day_change_pct = (current / previous_close - 1.0) * 100.0
    return {
        "symbol": symbol,
        "name": name,
        "current": current,
        "previous_close": previous_close,
        "day_change": day_change,
        "day_change_pct": day_change_pct,
    }


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
        sp_list = sp500_constituents()
        sp_names = {s: n for s, n in sp_list}
        sp500 = set(sp_names)
        ndx = nasdaq100_symbols()
        schd = schd_symbols()
        universes = {"sp500": sp500, "nasdaq100": ndx, "schd": schd}
        etf_symbols = {"sp500": "SPY", "nasdaq100": "QQQ", "schd": "SCHD"}
        all_symbols = sorted(sp500 | ndx | schd)

        def work(symbol):
            row = _market_quote(monitor, symbol)
            if symbol in sp_names:
                row["name"] = sp_names[symbol]
            return row

        result_map = {}
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(work, symbol): symbol for symbol in all_symbols}
            for future in as_completed(futures):
                try:
                    row = future.result()
                    result_map[row["symbol"]] = row
                except Exception:
                    pass

        etf_moves = {}
        for universe, etf_symbol in etf_symbols.items():
            try:
                etf_moves[universe] = _market_quote(monitor, etf_symbol)["day_change_pct"]
            except Exception:
                etf_moves[universe] = 0.0

        now = datetime.now(timezone.utc).isoformat()
        summaries = {}
        with monitor.db() as con:
            con.execute("DELETE FROM universe_mover_cache")
            for universe, members in universes.items():
                rows = [result_map[s] for s in members if s in result_map]
                coverage = len(rows)
                total = len(members)
                status = "ready" if total > 0 and coverage >= max(10, int(total * 0.80)) else "building"
                direction_pct = etf_moves.get(universe, 0.0)
                direction = "up" if direction_pct >= 0 else "down"
                ranked = []
                if status == "ready":
                    ranked = sorted(rows, key=lambda x: x["day_change_pct"], reverse=(direction == "up"))[:3]
                    con.executemany(
                        """INSERT INTO universe_mover_cache(
                               universe,rank,symbol,name,current,previous_close,day_change,day_change_pct,updated_at)
                           VALUES(?,?,?,?,?,?,?,?,?)""",
                        [
                            (universe, i, r["symbol"], r["name"], r["current"], r["previous_close"],
                             r["day_change"], r["day_change_pct"], now)
                            for i, r in enumerate(ranked, 1)
                        ],
                    )
                con.execute(
                    "INSERT INTO app_meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (f"laggard_{universe}_coverage", f"{coverage}/{total}"),
                )
                con.execute(
                    "INSERT INTO app_meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (f"laggard_{universe}_status", status),
                )
                con.execute(
                    "INSERT INTO app_meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (f"laggard_{universe}_direction", direction),
                )
                con.execute(
                    "INSERT INTO app_meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (f"laggard_{universe}_etf_change_pct", str(direction_pct)),
                )
                summaries[universe] = {
                    "coverage": f"{coverage}/{total}",
                    "status": status,
                    "direction": direction,
                    "etf_change_pct": direction_pct,
                    "items": len(ranked),
                }

        _set_meta(monitor, "laggard_source_time", now)
        _set_meta(monitor, "laggard_status", "ready")
        print("mover refresh complete", summaries, flush=True)
    except Exception as exc:
        _set_meta(monitor, "laggard_status", "error")
        _set_meta(monitor, "laggard_error", type(exc).__name__)
        print("mover refresh failed:", type(exc).__name__, flush=True)
    finally:
        REFRESH_LOCK.release()


def get(monitor):
    init_db(monitor)
    with monitor.db() as con:
        meta = dict(con.execute("SELECT key,value FROM app_meta WHERE key LIKE 'laggard_%'").fetchall())
        sections = {}
        for universe in ("sp500", "nasdaq100", "schd"):
            rows = con.execute(
                """SELECT rank,symbol,name,current,previous_close,day_change,day_change_pct,updated_at
                   FROM universe_mover_cache WHERE universe=? ORDER BY rank""",
                (universe,),
            ).fetchall()
            sections[universe] = {
                "status": meta.get(f"laggard_{universe}_status", "building"),
                "coverage": meta.get(f"laggard_{universe}_coverage", "0/0"),
                "direction": meta.get(f"laggard_{universe}_direction", "up"),
                "etf_change_percent": float(meta.get(f"laggard_{universe}_etf_change_pct", "0") or 0),
                "items": [
                    {
                        "rank": r[0],
                        "symbol": r[1],
                        "name": r[2],
                        "current": r[3],
                        "previous_close": r[4],
                        "day_change": r[5],
                        "day_change_percent": r[6],
                        "updated_at": r[7],
                    }
                    for r in rows
                ],
            }

    sp = sections["sp500"]
    return {
        "status": meta.get("laggard_status", "building"),
        "coverage": sp["coverage"],
        "updated_at": meta.get("laggard_source_time"),
        "items": sp["items"],
        "sections": sections,
    }
