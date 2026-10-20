"""Fail-closed historical exchange holiday NOTICE venue + as-of classifier.

A press report of KRX or an original notice can be a calendar research hint,
never source-PIT or a trading authorization. Source metadata is untrusted:
this checks consistency only, and never authenticates publisher bytes/time.
No network, private KRX, secrets, instrument data, order or storage I/O.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
import re

VALID_MARKETS = frozenset(("KOSPI", "KOSDAQ", "DERIVATIVES", "ALL_EQUITIES",
                            "GENERAL_PUBLIC"))
VALID_SOURCES = frozenset(("KRX_PRIMARY_MARKET_NOTICE", "REPORTED_KRX_MARKET_NOTICE",
                            "GOVERNMENT_PUBLIC_HOLIDAY", "ISSUER_PRODUCT_DISCLOSURE"))
DATE_RE = re.compile(r"[0-9]{8}\Z")
TIMESTAMP_RE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}(?::[0-9]{2})?\+09:00\Z"
)
DENIED = {
    "official_original_market_calendar_authenticated": False,
    "independently_authenticated_publication_instant": False,
    "original_exchange_market_status_pit_verified": False,
    "individual_security_tradability_verified": False,
    "source_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "permissions_change_authorized": False,
    "storage_mutated": False,
    "network_request_attempted": False,
    "ordering": "DISABLED",
}


class CalendarNoticeGap(ValueError):
    """Constant failure codes only; never echo original notice text."""


def _parse_kst(value: str) -> datetime:
    if type(value) is not str or not TIMESTAMP_RE.fullmatch(value):
        raise CalendarNoticeGap("CALENDAR_NOTICE_KST_TIMESTAMP_UNVERIFIED")
    try:
        result = datetime.fromisoformat(value)
    except ValueError:
        raise CalendarNoticeGap("CALENDAR_NOTICE_KST_TIMESTAMP_UNVERIFIED") from None
    if result.utcoffset() != timedelta(hours=9):
        raise CalendarNoticeGap("CALENDAR_NOTICE_TIMEZONE_CONFLICT")
    return result


def classify_notice(
    *, session_day: str, required_market: str, source_kind: str,
    notice_market: str, public_report_at_kst: str, signal_asof_kst: str,
) -> dict:
    """Return source consistency hints, never an authenticated PIT entitlement.

    The caller labels the claimed source-kind/venue/time. Nothing here can
    cryptographically establish that claim; this is only a negative gate.
    """
    if (type(session_day) is not str or not DATE_RE.fullmatch(session_day)
            or type(required_market) is not str
            or required_market not in ("KOSPI", "KOSDAQ")
            or type(notice_market) is not str
            or notice_market not in VALID_MARKETS
            or type(source_kind) is not str
            or source_kind not in VALID_SOURCES):
        raise CalendarNoticeGap("CALENDAR_NOTICE_VENUE_OR_SOURCE_SHAPE_INVALID")
    try:
        target_day = date.fromisoformat(
            f"{session_day[:4]}-{session_day[4:6]}-{session_day[6:]}"
        )
    except ValueError:
        raise CalendarNoticeGap("CALENDAR_NOTICE_DATE_INVALID") from None
    published = _parse_kst(public_report_at_kst)
    signal = _parse_kst(signal_asof_kst)
    if signal.date() > target_day:
        raise CalendarNoticeGap("CALENDAR_SIGNAL_AFTER_TARGET_SESSION")
    # An ordinary government holiday is not an exchange notice; an issuer
    # disclosure has no market-calendar rulemaking power.
    source_scope_valid = source_kind in (
        "KRX_PRIMARY_MARKET_NOTICE", "REPORTED_KRX_MARKET_NOTICE"
    )
    venue_scope_valid = notice_market in (required_market, "ALL_EQUITIES")
    # Evidence of an announcement after the signal is FUTURE information.
    # An article's publication can NOT establish any earlier original release.
    reported_available_by_signal = published <= signal
    possible = bool(source_scope_valid and venue_scope_valid
                    and reported_available_by_signal
                    and published.date() <= target_day)
    reason = ("CANDIDATE_ONLY_NOT_AUTHENTICATED"
              if possible else
              "NON_EXCHANGE_SOURCE" if not source_scope_valid else
              "WRONG_MARKET_SCOPE" if not venue_scope_valid else
              "REPORT_NOT_AVAILABLE_BY_SIGNAL" if not reported_available_by_signal
              else "REPORT_AFTER_TARGET_SESSION")
    return {
        "purpose": "HISTORICAL_KRX_MARKET_NOTICE_ASOF_VENUE_SCOPE_REVIEW",
        "status": reason,
        "required_equity_venue": required_market,
        "notice_venue_label": notice_market,
        "source_kind_label": source_kind,
        "candidate_market_scope_consistent": venue_scope_valid and source_scope_valid,
        "reported_evidence_available_by_signal": reported_available_by_signal,
        "candidate_notice_may_be_considered_not_pit": possible,
        "self_supplied_publication_metadata_is_not_authenticated": True,
        **DENIED,
    }
