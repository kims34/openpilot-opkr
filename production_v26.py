"""IndexAlert production v2.8: Naver realtime KPI100 polling API."""
from __future__ import annotations

import math
from datetime import datetime, timezone

import monitor
import production
import production_v25

app = production_v25.app
SEOUL = production_v25.SEOUL

POLLING_URL = "https://polling.finance.naver.com/api/realtime"
POLLING_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36",
    "Referer": "https://stock.naver.com/",
    "Accept": "application/json,text/plain,*/*",
}


def _scaled_index_value(value):
    if value is None:
        return None
    try:
        x = float(str(value).replace(",", ""))
    except Exception:
        return None
    # Naver realtime SERVICE_INDEX fields are integer hundredths for index
    # levels/changes (e.g. 527730 => 5277.30). Already-decimal values are kept.
    if abs(x) >= 100000:
        x /= 100.0
    return x


def _plain_float(value):
    if value is None:
        return None
    try:
        return float(str(value).replace(",", ""))
    except Exception:
        return None


def _polling_data(code: str):
    r = monitor.requests.get(
        POLLING_URL,
        params={"query": f"SERVICE_INDEX:{code}"},
        headers=POLLING_HEADERS,
        timeout=10,
    )
    r.raise_for_status()
    root = r.json()
    areas = ((root.get("result") or {}).get("areas") or [])
    for area in areas:
        for data in (area.get("datas") or []):
            if not isinstance(data, dict):
                continue
            cd = str(data.get("cd") or data.get("code") or "").upper()
            if cd and cd not in {code.upper(), f"{code.upper()}.KS"}:
                continue
            nv = _scaled_index_value(data.get("nv"))
            if nv is not None and nv > 0:
                return data, r.url
    return None, r.url


def _naver_kpi100_polling():
    errors = []
    chosen = None
    chosen_code = None
    chosen_url = None
    # KPI100 is Naver's legacy/public code for KOSPI100. Alternate aliases are
    # tried only if the primary code is temporarily unsupported.
    for code in ("KPI100", "KOSPI100", "KS100"):
        try:
            data, url = _polling_data(code)
            if data:
                chosen, chosen_code, chosen_url = data, code, url
                break
            errors.append(f"{code}:empty")
        except Exception as exc:
            errors.append(f"{code}:{type(exc).__name__}")

    if not chosen:
        print("KPI100 polling unavailable", errors, flush=True)
        # Last-resort Naver legacy parser from v25; never silently switch to
        # the KOSPI composite.
        return production_v25._naver_kpi100_robust()

    current = _scaled_index_value(chosen.get("nv"))
    change = _scaled_index_value(chosen.get("cv"))
    rate = _plain_float(chosen.get("cr"))
    previous = _scaled_index_value(chosen.get("sv"))
    day_high = _scaled_index_value(chosen.get("hv"))

    if current is None or current <= 0:
        raise RuntimeError("Naver KPI100 polling current unavailable")

    # rf 2=rise, 5=fall on Naver polling. Some responses already sign cv/cr;
    # normalize sign from rf when present.
    rf = str(chosen.get("rf") or "")
    change = float(change or 0.0)
    rate = float(rate or 0.0)
    if rf == "5":
        change, rate = -abs(change), -abs(rate)
    elif rf == "2":
        change, rate = abs(change), abs(rate)

    if previous is None or previous <= 0:
        previous = current - change
    if previous <= 0:
        previous = current / (1.0 + rate / 100.0) if abs(rate) < 99 else current
        change = current - previous
    if day_high is None or day_high <= 0:
        day_high = current

    market_status = str(chosen.get("ms") or "").upper()
    state = "REGULAR" if market_status in {"OPEN", "OPENED", "REGULAR"} else "CLOSED"

    # Polling payloads may expose a timestamp in several fields. If absent,
    # current request time is used for freshness only, not for ATH dating.
    now = datetime.now(SEOUL)
    ts = int(now.timestamp())

    print(
        "KPI100 naver realtime",
        {
            "code": chosen_code,
            "current": current,
            "previous": previous,
            "change": change,
            "rate": rate,
            "day_high": day_high,
            "market_status": market_status,
            "rf": rf,
            "url": chosen_url,
        },
        flush=True,
    )
    # Polling does not consistently provide 52w high, so leave it None; v24's
    # persisted ATH + Yahoo historical cross-check logic handles the peak.
    return current, previous, change, rate, day_high, None, ts, state


# Reuse all v24 state/ATH logic, replacing only its Naver current-quote source.
production_v24 = production_v25.production_v24
production_v24._naver_kpi100 = _naver_kpi100_polling
