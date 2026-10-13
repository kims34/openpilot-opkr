"""Read-only locally captured KRX holiday CSV row validator.

No site requests. No broker, order, model, holdout, filesystem modifications.
Extracts weekday closures DIRECTLY from the supplied original CSV bytes and
refuses if the external manually-normalized list differs. This is *not*
independent authentication that a given file actually originated at KRX,
nor original historical disclosure/PIT source-admission certification.
XLS/XLSX/HTML files are intentionally UNSUPPORTED: do not convert them
silently or pass through self-attested manual date claims.
"""
from __future__ import annotations

import csv
from datetime import date
import io
from research_v1_krx_official_calendar_input_preflight import (
    normalize_calendar_export_claim, SAFETY,
)

DAYS_KR = "월화수목금토일"
HEADERS = ("일자", "요일", "비고")


def extract_and_reconcile_csv(source_bytes: bytes, claim: dict, year: int) -> dict:
    refusal = {
        "status": "FAIL_CLOSED_UNPARSED_OR_UNMATCHED_SOURCE_ROWS",
        "dates": [],
        "source_table_rows_verified_against_claim": False,
        "original_source_independently_authenticated": False,
        "original_historical_publication_verified": False,
        "actual_krx_trading_calendar_pit_admitted": False,
        "source_openapi_requests": 0,
        "ordering": "DISABLED",
        "real_orders_authorized": False,
        "performance_run_authorized": False,
    }
    baseline = normalize_calendar_export_claim(source_bytes, claim, year)
    if baseline["status"] != "SOURCE_BYTES_HASH_BOUND_CALENDAR_CLAIM_ONLY_NOT_PIT":
        return refusal
    # csv only: genuine binary XLS/OLE/Zip/HTML requires its own independently
    # verified parser, never treat a claimed sidecar as parsed source facts.
    if source_bytes[:4] in (b"PK\x03\x04", b"\xd0\xcf\x11\xe0", b"<htm"):
        return refusal
    try:
        try:
            decoded = source_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            decoded = source_bytes.decode("cp949")
        if any(c in decoded for c in ("\x00", "\x1b")):
            return refusal
        reader = csv.reader(io.StringIO(decoded, newline=""), strict=True)
        rows = list(reader)
        if not (2 <= len(rows) <= 400):
            return refusal
        header = [v.strip() for v in rows[0]]
        if header != list(HEADERS):
            return refusal
        seen = set()
        weekdays = []
        for row in rows[1:]:
            if len(row) != 3:
                return refusal
            literal, weekday, note = [v.strip() for v in row]
            # No silent lexical date coercion; explicit KRX CSV export form.
            if len(literal) != 10 or literal[4] != "-" or literal[7] != "-":
                return refusal
            d = date.fromisoformat(literal)
            if d.isoformat() != literal or d.year != year or literal in seen:
                return refusal
            if weekday not in (DAYS_KR[d.weekday()], DAYS_KR[d.weekday()] + "요일"):
                return refusal
            if len(note) > 300:
                return refusal
            seen.add(literal)
            if d.weekday() < 5:
                weekdays.append(literal)
        if not weekdays or sorted(weekdays) != baseline["dates"]:
            return refusal
        return {
            **baseline,
            "status": "SOURCE_CSV_ROWS_EXACT_MATCH_CLAIM_ONLY_NOT_PIT",
            "source_table_rows_verified_against_claim": True,
            "original_source_independently_authenticated": False,
            "original_historical_publication_verified": False,
            "actual_krx_trading_calendar_pit_admitted": False,
            "parsed_source_total_rows": len(rows)-1,
            "parsed_source_weekday_closures": len(weekdays),
            "source_openapi_requests": 0,
            "ordering": "DISABLED",
            "real_orders_authorized": False,
            "performance_run_authorized": False,
        }
    except (ValueError, UnicodeError, csv.Error, TypeError, IndexError):
        return refusal
