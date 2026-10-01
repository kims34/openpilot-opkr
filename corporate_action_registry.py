"""Source-backed corporate-action exclusions for operational mover display.

This registry is deliberately narrow. It does not estimate an adjusted price,
manufacture a total return, or alter research/backtest evidence. It only marks a
symbol/date as non-comparable when a documented corporate action makes the raw
prior close economically incompatible with the post-action share price.

A registered event causes the operational mover feed to fail closed for that
symbol on the effective local market date until a separately verified adjusted
basis exists.
"""
from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo


KNOWN_NONCOMPARABLE_EVENTS: dict[tuple[str, str], dict[str, object]] = {
    ("CTVA", "2026-10-01"): {
        "kind": "SPIN_OFF_DISTRIBUTION",
        "basis_status": "RAW_PREVIOUS_CLOSE_NONCOMPARABLE",
        "description": "Corteva distributed Vylor shares 1-for-1 on the separation date.",
        "sources": [
            "https://www.corteva.com/resources/media-center/corteva-board-approves-vylor-distribution.html",
            "https://www.sec.gov/Archives/edgar/data/2128626/000119312526402928/ck0002128626-ex99_1.htm",
        ],
    },
}


def active_noncomparable_event(
    symbol: str,
    current_ts: int,
    tz_name: str = "America/New_York",
) -> dict[str, object] | None:
    """Return documented event metadata for the symbol's local market date."""
    try:
        clean_symbol = str(symbol or "").strip().upper()
        ts = int(current_ts)
        if not clean_symbol or ts <= 0:
            return None
        local_date = datetime.fromtimestamp(ts, timezone.utc).astimezone(ZoneInfo(tz_name)).date().isoformat()
    except Exception:
        return None
    event = KNOWN_NONCOMPARABLE_EVENTS.get((clean_symbol, local_date))
    return dict(event) if event is not None else None
