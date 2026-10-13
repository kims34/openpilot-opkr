"""Offline preflight for local KRX KOSPI calendar export plus source bytes.

The official KRX site exposes a human-operated holiday table/export.
This does NOT fetch from that page. The caller supplies already-authorized
local source bytes and separately normalized calendar dates. Only dates and
counts are returned to the trusted caller; never log protected date-level
content in public CI. Raw binary SHA equality proves the supplied source
bytes are unchanged relative to its recorded digest, NOT that the supplied
normalization or source origin is independently truthful.

Every result is explicitly *not* an official PIT source admission.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
import re

DAY = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
SHA = re.compile(r"^[0-9a-f]{64}$")
SOURCE_PAGE = "https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp"
SAFETY = {
    "original_krx_source_independently_authenticated": False,
    "normalization_against_source_table_attested": False,
    "as_of_historical_publication_confirmed": False,
    "official_exchange_calendar_admitted": False,
    "original_security_status_pit_verified": False,
    "27_problem_securities_released": False,
    "performance_run_authorized": False,
    "holdout_authorized": False,
    "orders_authorized": False,
    "ordering": "DISABLED",
    "network_requests_attempted": False,
    "private_data_mutated": False,
}


def normalize_calendar_export_claim(
    source_bytes: bytes, calendar_claim: dict, expected_year: int,
) -> dict:
    """Return normalized claimed closure dates only within caller's private scope.

    Supply source_bytes as the original local KRX export (e.g. downloaded
    spreadsheet) and calendar_claim as an independently normalized
    *claim* from that exact file. This routine cannot itself parse/audit
    binary XLS source rows. No source bytes/secret keys leave this function.
    """
    failure = {"status": "FAIL_CLOSED_UNVERIFIED_CALENDAR_INPUT", "dates": [], **SAFETY}
    if (type(expected_year) is not int or not (2015 <= expected_year <= 2026)
            or type(source_bytes) is not bytes or not (16 <= len(source_bytes) <= 8_000_000)
            or not isinstance(calendar_claim, dict)):
        return failure
    source_digest = hashlib.sha256(source_bytes).hexdigest()
    if (calendar_claim.get("market") != "KOSPI_CASH_EQUITIES"
            or calendar_claim.get("source_page_url") != SOURCE_PAGE
            or calendar_claim.get("source_document_sha256") != source_digest
            or calendar_claim.get("year") != expected_year
            or type(calendar_claim.get("year")) is not int
            or calendar_claim.get("source_kind") != "KRX_HUMAN_EXPORTED_HOLIDAY_SCHEDULE"
            or not isinstance(calendar_claim.get("calendar_closed_days"), list)):
        return failure

    try:
        downloaded = calendar_claim.get("downloaded_at_utc")
        if not isinstance(downloaded, str):
            return failure
        t = datetime.fromisoformat(downloaded.replace("Z", "+00:00"))
        if t.tzinfo != timezone.utc or not (2015 <= t.year <= 2026):
            return failure
        dates = calendar_claim["calendar_closed_days"]
        if len(dates) > 50 or len(dates) != len(set(dates)):
            return failure
        parsed = []
        for item in dates:
            if type(item) is not str or not DAY.fullmatch(item):
                return failure
            d = date.fromisoformat(item)
            if (d.isoformat() != item or d.year != expected_year
                    or d.weekday() >= 5):
                return failure
            parsed.append(item)
    except (TypeError, ValueError):
        return failure

    if not parsed:
        return failure
    return {
        "status": "SOURCE_BYTES_HASH_BOUND_CALENDAR_CLAIM_ONLY_NOT_PIT",
        "year": expected_year,
        "closed_weekday_count": len(parsed),
        "dates": sorted(parsed),
        "source_document_sha256": source_digest,
        "source_page": SOURCE_PAGE,
        **SAFETY,
    }
