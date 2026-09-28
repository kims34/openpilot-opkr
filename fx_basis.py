"""USD/KRW basis helpers.

Historical daily points and the day-change reference use Bank of Korea ECOS
731Y003 / 0000003, the Seoul FX market 15:30 USD/KRW close.  The current card
value may come from a live market feed; this module only owns the official
15:30 close series and the rule that today's live quote is compared with the
last completed *prior* Seoul business-day close.
"""
from __future__ import annotations

import math
import os
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

SEOUL = ZoneInfo("Asia/Seoul")
ECOS_STAT_CODE = "731Y003"
ECOS_ITEM_CODE = "0000003"
ECOS_API_KEY = os.getenv("ECOS_API_KEY", "sample").strip() or "sample"
ECOS_URL = (
    "https://ecos.bok.or.kr/api/StatisticSearch/"
    "{key}/json/kr/1/10/{stat}/D/{start}/{end}/{item}"
)


def parse_ecos_close_rows(payload: dict) -> list[tuple[date, float]]:
    block = payload.get("StatisticSearch") if isinstance(payload, dict) else None
    rows = (block or {}).get("row") or []
    out: dict[date, float] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        raw_day = str(row.get("TIME") or "").strip()
        try:
            day = datetime.strptime(raw_day[:8], "%Y%m%d").date()
            value = float(str(row.get("DATA_VALUE") or "").replace(",", "").strip())
        except Exception:
            continue
        if math.isfinite(value) and value > 0:
            out[day] = value
    return sorted(out.items(), key=lambda x: x[0])


def prior_business_close(
    closes: list[tuple[date, float]],
    current_day: date,
) -> tuple[float | None, str | None]:
    eligible = [(d, v) for d, v in closes if d < current_day and math.isfinite(v) and v > 0]
    if not eligible:
        return None, None
    day, value = max(eligible, key=lambda x: x[0])
    return float(value), day.isoformat()


def fetch_usdkrw_1530_closes(
    requests_module,
    *,
    now: datetime | None = None,
    lookback_days: int = 42,
    headers: dict | None = None,
) -> list[tuple[date, float]]:
    """Fetch recent official 15:30 closes from ECOS.

    The public ``sample`` key is limited to 10 rows per request.  We therefore
    request small calendar chunks (9 days), merge them, and de-duplicate by day.
    A real ECOS_API_KEY can be supplied through the environment without changing
    this code.
    """
    now = now.astimezone(SEOUL) if now is not None else datetime.now(SEOUL)
    end_day = now.date()
    start_day = end_day - timedelta(days=max(14, int(lookback_days)))
    cursor = start_day
    merged: dict[date, float] = {}
    last_error: Exception | None = None

    while cursor <= end_day:
        chunk_end = min(end_day, cursor + timedelta(days=8))
        url = ECOS_URL.format(
            key=ECOS_API_KEY,
            stat=ECOS_STAT_CODE,
            start=cursor.strftime("%Y%m%d"),
            end=chunk_end.strftime("%Y%m%d"),
            item=ECOS_ITEM_CODE,
        )
        try:
            response = requests_module.get(url, headers=headers or {}, timeout=15)
            response.raise_for_status()
            parsed = parse_ecos_close_rows(response.json())
            for day, value in parsed:
                merged[day] = value
        except Exception as exc:
            last_error = exc
        cursor = chunk_end + timedelta(days=1)

    rows = sorted(merged.items(), key=lambda x: x[0])
    if not rows and last_error is not None:
        raise last_error
    if not rows:
        raise RuntimeError("ECOS USD/KRW 15:30 close unavailable")
    return rows
