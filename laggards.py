import json
import math
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

import corporate_action_registry
import market_basis

UA = {"User-Agent": "Mozilla/5.0 IndexAlert/1.0"}
SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
NASDAQ100_URLS = [
    "https://indexes.nasdaq.com/Index/Weighting/NDX",
    "https://en.wikipedia.org/wiki/List_of_NASDAQ-100_companies",
]
SCHD_URL = "https://www.schwabassetmanagement.com/allholdings/schd"
REFRESH_LOCK = threading.Lock()
NY = ZoneInfo("America/New_York")


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


def _regular_session_points(points):
    """Keep only U.S. regular-session samples so pre/post prices never become a close basis."""
    out = []
    for ts, value in points or []:
        try:
            t = int(ts)
            v = float(value)
            local = datetime.fromtimestamp(t, timezone.utc).astimezone(NY)
        except Exception:
            continue
        minute = local.hour * 60 + local.minute
        if local.weekday() < 5 and 570 <= minute < 960 and math.isfinite(v) and v > 0:
            out.append((t, v))
    return out


def _market_state(meta, current_ts: int) -> str:
    state = str((meta or {}).get("marketState") or "").upper()
    if state in {"PRE", "REGULAR", "POST", "CLOSED"}:
        return state
    local = datetime.fromtimestamp(int(current_ts), timezone.utc).astimezone(NY)
    if local.weekday() >= 5:
        return "CLOSED"
    minute = local.hour * 60 + local.minute
    if minute < 570:
        return "PRE"
    if minute < 960:
        return "REGULAR"
    return "POST"


def _market_quote(monitor, symbol: str, *, require_equity: bool = False):
    result = monitor.yahoo_result(_yahoo_symbol(symbol), "5d", "5m", True)
    points = monitor.series(result)
    if not points:
        raise RuntimeError("quote unavailable")
    current_ts, current = points[-1]
    current_ts = int(current_ts)
    current = float(current)
    meta = result.get("meta", {})
    instrument_type = str(meta.get("instrumentType") or meta.get("quoteType") or "").strip().upper()
    if require_equity and instrument_type != "EQUITY":
        # Constituent universes represent company equities. Holdings-source or
        # page-parser contamination must never allow an ETF/fund/index/currency
        # ticker to masquerade as an S&P500/NASDAQ100/SCHD stock constituent.
        raise RuntimeError(f"non-equity constituent: {instrument_type or 'UNKNOWN'}")
    if require_equity:
        event = corporate_action_registry.active_noncomparable_event(symbol, current_ts)
        if event is not None:
            # Do not turn a documented spin-off/distribution discontinuity into
            # a fake one-day mover. Until an independently verified adjusted
            # basis is available, omit this row rather than inventing a return.
            raise RuntimeError(f"non-comparable corporate action: {event.get('kind')}")
    state = _market_state(meta, current_ts)
    regular_points = _regular_session_points(points)
    previous_close, previous_close_date = market_basis.regular_close_basis(
        regular_points,
        current_ts,
        state,
        "America/New_York",
    )
    if (
        current <= 0
        or not math.isfinite(current)
        or previous_close is None
        or previous_close <= 0
        or not math.isfinite(previous_close)
    ):
        raise RuntimeError("invalid quote basis")
    name = str(meta.get("longName") or meta.get("shortName") or symbol).strip()
    day_change = current - previous_close
    day_change_pct = (current / previous_close - 1.0) * 100.0
    return {
        "symbol": symbol,
        "name": name,
        "current": current,
        "previous_close": previous_close,
        "previous_close_date": previous_close_date,
        "day_change": day_change,
        "day_change_pct": day_change_pct,
        "market_state": state,
        "instrument_type": instrument_type,
    }


def _rank_directional(rows, direction: str, limit: int = 3):
    """Return only movers whose sign matches the requested direction."""
    valid = []
    for row in rows or []:
        try:
            pct = float(row.get("day_change_pct"))
        except Exception:
            continue
        if not math.isfinite(pct):
            continue
        if direction == "down" and pct < 0:
            valid.append(row)
        elif direction == "up" and pct > 0:
            valid.append(row)
    valid.sort(key=lambda x: float(x["day_change_pct"]), reverse=(direction == "up"))
    return valid[:limit]


def _classify_constituent_exclusion(exc) -> str | None:
    """Return only deliberate, auditable fail-closed exclusion categories."""
    message = str(exc or "")
    if message.startswith("non-equity constituent:"):
        return "non_equity"
    if message.startswith("non-comparable corporate action:"):
        return "corporate_action"
    return None


def _meta_symbol_list(raw) -> list[str]:
    """Decode a persisted symbol list without leaking malformed metadata."""
    try:
        values = json.loads(raw or "[]")
    except Exception:
        return []
    if not isinstance(values, list):
        return []
    symbols = set()
    for value in values:
        symbol = _clean_symbol(str(value))
        if re.fullmatch(r"[A-Z.\-]{1,8}", symbol):
            symbols.add(symbol)
    return sorted(symbols)


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
            row = _market_quote(monitor, symbol, require_equity=True)
            if symbol in sp_names:
                row["name"] = sp_names[symbol]
            return row

        result_map = {}
        exclusions = {"non_equity": set(), "corporate_action": set()}
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(work, symbol): symbol for symbol in all_symbols}
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    row = future.result()
                    result_map[row["symbol"]] = row
                except Exception as exc:
                    category = _classify_constituent_exclusion(exc)
                    if category is not None:
                        exclusions[category].add(symbol)

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
                excluded_non_equity = sorted(members & exclusions["non_equity"])
                excluded_corporate_action = sorted(members & exclusions["corporate_action"])
                status = "ready" if total > 0 and coverage >= max(10, int(total * 0.80)) else "building"
                direction_pct = etf_moves.get(universe, 0.0)
                direction = "down" if direction_pct < 0 else "up"
                decliners = []
                gainers = []
                if status == "ready":
                    decliners = _rank_directional(rows, "down", 3)
                    gainers = _rank_directional(rows, "up", 3)
                    encoded = []
                    encoded.extend((i, r) for i, r in enumerate(decliners, 1))
                    encoded.extend((100 + i, r) for i, r in enumerate(gainers, 1))
                    con.executemany(
                        """INSERT INTO universe_mover_cache(
                               universe,rank,symbol,name,current,previous_close,day_change,day_change_pct,updated_at)
                           VALUES(?,?,?,?,?,?,?,?,?)""",
                        [
                            (universe, stored_rank, r["symbol"], r["name"], r["current"], r["previous_close"],
                             r["day_change"], r["day_change_pct"], now)
                            for stored_rank, r in encoded
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
                con.execute(
                    "INSERT INTO app_meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (f"laggard_{universe}_excluded_non_equity", json.dumps(excluded_non_equity, separators=(",", ":"))),
                )
                con.execute(
                    "INSERT INTO app_meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (f"laggard_{universe}_excluded_corporate_action", json.dumps(excluded_corporate_action, separators=(",", ":"))),
                )
                summaries[universe] = {
                    "coverage": f"{coverage}/{total}",
                    "status": status,
                    "direction": direction,
                    "etf_change_pct": direction_pct,
                    "decliners": len(decliners),
                    "gainers": len(gainers),
                    "excluded_non_equity": excluded_non_equity,
                    "excluded_corporate_action": excluded_corporate_action,
                    "sign_check": all(r["day_change_pct"] < 0 for r in decliners)
                    and all(r["day_change_pct"] > 0 for r in gainers),
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


def _item_from_row(r, display_rank: int):
    return {
        "rank": display_rank,
        "symbol": r[1],
        "name": r[2],
        "current": r[3],
        "previous_close": r[4],
        "day_change": r[5],
        "day_change_percent": r[6],
        "updated_at": r[7],
    }


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
            direction = meta.get(f"laggard_{universe}_direction", "up")
            has_dual_cache = any(int(r[0]) >= 100 for r in rows)
            if has_dual_cache:
                decliners = [_item_from_row(r, int(r[0])) for r in rows if 1 <= int(r[0]) <= 3 and float(r[6]) < 0]
                gainers = [_item_from_row(r, int(r[0]) - 100) for r in rows if 101 <= int(r[0]) <= 103 and float(r[6]) > 0]
            else:
                # Backward-compatible read during the first refresh after deploy.
                legacy = [_item_from_row(r, int(r[0])) for r in rows[:3]]
                decliners = [x for x in legacy if float(x["day_change_percent"]) < 0] if direction == "down" else []
                gainers = [x for x in legacy if float(x["day_change_percent"]) > 0] if direction == "up" else []
            selected = decliners if direction == "down" else gainers
            sections[universe] = {
                "status": meta.get(f"laggard_{universe}_status", "building"),
                "coverage": meta.get(f"laggard_{universe}_coverage", "0/0"),
                "direction": direction,
                "etf_change_percent": float(meta.get(f"laggard_{universe}_etf_change_pct", "0") or 0),
                "excluded_non_equity_symbols": _meta_symbol_list(meta.get(f"laggard_{universe}_excluded_non_equity")),
                "excluded_corporate_action_symbols": _meta_symbol_list(meta.get(f"laggard_{universe}_excluded_corporate_action")),
                "items": selected[:3],
                "decliners": decliners[:3],
                "gainers": gainers[:3],
            }

    sp = sections["sp500"]
    return {
        "status": meta.get("laggard_status", "building"),
        "coverage": sp["coverage"],
        "updated_at": meta.get("laggard_source_time"),
        "items": sp["items"],
        "sections": sections,
    }