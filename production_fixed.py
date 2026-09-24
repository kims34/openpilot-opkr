import math
from datetime import datetime, timezone
from urllib.parse import quote
from zoneinfo import ZoneInfo

import monitor
import production

# Preserve the hardened production app/routes and only replace KOSPI100 ATH logic.
app = production.app
_original_init_db = monitor.init_db


def _init_db_with_kospi_ath_fix():
    _original_init_db()
    with monitor.db() as con:
        if not con.execute("SELECT 1 FROM migrations WHERE name='kospi100-ath-crosscheck-v2'").fetchone():
            con.execute("DELETE FROM index_state WHERE id='kospi100'")
            con.execute("DELETE FROM fired WHERE index_id='kospi100'")
            con.execute("DELETE FROM deliveries WHERE index_id='kospi100'")
            con.execute("INSERT INTO migrations(name) VALUES('kospi100-ath-crosscheck-v2')")


monitor.init_db = _init_db_with_kospi_ath_fix
_original_evaluate = monitor.evaluate


def _history_candidates(symbol: str):
    candidates = []
    for range_ in ("max", "1y"):
        try:
            result = monitor.yahoo_result(symbol, range_, "1d", False)
            timestamps = result.get("timestamp") or []
            highs = result.get("indicators", {}).get("quote", [{}])[0].get("high", []) or []
            best = 0.0
            best_ts = 0
            for ts, high in zip(timestamps, highs):
                if high is None:
                    continue
                h = float(high)
                if math.isfinite(h) and h > 0 and h >= best:
                    best = h
                    best_ts = int(ts)
            if best > 0:
                candidates.append((best, best_ts, range_))

            meta = result.get("meta", {})
            for key in ("fiftyTwoWeekHigh", "fiftyTwoWeekRange"):
                raw = meta.get(key)
                if key == "fiftyTwoWeekHigh":
                    try:
                        value = float(raw or 0)
                    except Exception:
                        value = 0.0
                    if math.isfinite(value) and value > 0:
                        candidates.append((value, 0, "52w-meta"))
        except Exception as exc:
            print("kospi100 ATH candidate failed", range_, type(exc).__name__, flush=True)
    if not candidates:
        raise RuntimeError("KOSPI100 ATH unavailable")
    return candidates


def _kospi100_ath():
    candidates = _history_candidates("KOSPI100.KS")
    best_value, best_ts, source = max(candidates, key=lambda x: x[0])

    # If metadata supplies the winning 52-week high but no timestamp, locate
    # the matching daily high in the 1-year series so ATH date/days remain useful.
    if not best_ts:
        try:
            result = monitor.yahoo_result("KOSPI100.KS", "1y", "1d", False)
            timestamps = result.get("timestamp") or []
            highs = result.get("indicators", {}).get("quote", [{}])[0].get("high", []) or []
            closest = None
            for ts, high in zip(timestamps, highs):
                if high is None:
                    continue
                h = float(high)
                if not math.isfinite(h) or h <= 0:
                    continue
                delta = abs(h - best_value)
                if closest is None or delta < closest[0]:
                    closest = (delta, int(ts), h)
            if closest and closest[0] / best_value < 0.005:
                best_ts = closest[1]
        except Exception:
            pass

    print("kospi100 ATH crosscheck", {"ath": best_value, "ts": best_ts, "source": source, "candidates": candidates}, flush=True)
    return best_value, best_ts


def _evaluate(index_id: str):
    if index_id != "kospi100":
        return _original_evaluate(index_id)

    rule = monitor.RULES[index_id]
    cash_result = monitor.yahoo_result(rule["cash"], prepost=False)
    points = monitor.series(cash_result)
    if not points:
        raise RuntimeError("no KOSPI100 prices")

    cash_ts, value = points[-1]
    meta = cash_result.get("meta", {})
    previous_close = production._previous_close(meta, value)
    ath, ath_ts = _kospi100_ath()

    if not math.isfinite(ath) or ath <= 0 or not math.isfinite(value) or value <= 0:
        raise RuntimeError("invalid KOSPI100 data")
    # An ATH can never be below the current index value.
    ath = max(ath, value)
    if ath == value and not ath_ts:
        ath_ts = cash_ts

    drawdown = (value / ath - 1.0) * 100.0
    day_change = value - previous_close
    day_change_percent = (value / previous_close - 1.0) * 100.0 if previous_close > 0 else 0.0
    tz = ZoneInfo("Asia/Seoul")
    ath_date = datetime.fromtimestamp(ath_ts, tz=timezone.utc).astimezone(tz).date().isoformat() if ath_ts else None

    monitor.save_state(index_id, ath, value, value, rule["regular_label"])
    production.EXTRA_STATE[index_id] = {
        "previous_close": previous_close,
        "day_change": day_change,
        "day_change_percent": day_change_percent,
        "ath_date": ath_date,
        "ath_days": production._days_since(ath_ts, "Asia/Seoul"),
        "drawdown": drawdown,
        "market_state": monitor.session_state(meta),
        "value_ts": cash_ts,
    }
    return {
        "id": index_id,
        "name": rule["name"],
        "value": value,
        "cash": value,
        "ath": ath,
        "drawdown": drawdown,
        "source": rule["regular_label"],
        "market_state": monitor.session_state(meta),
        "cash_ts": cash_ts,
        "value_ts": cash_ts,
        **production.EXTRA_STATE[index_id],
    }


monitor.evaluate = _evaluate
