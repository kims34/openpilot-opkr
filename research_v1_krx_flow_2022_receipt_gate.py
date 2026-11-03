"""KRX MDCSTAT02303 2022 source-*receipt* boundary, no raw market data.

This prepares the handoff for one privately archived, user-authorized
historical investor-flow sample. It is not a KRX client, an authentication
attestation, a normalization algorithm, or a historical PIT verifier.

An ordinary 2026 retrieval of 2022 results CANNOT attest the version
visible to an investor at the original 2022 decision time. The official
20:00 KST final-result rule is a publication floor, not proof of the
original vintage or of correction/revision history.
"""
from __future__ import annotations

from datetime import date, datetime, time
import re
from typing import Any, Mapping

SOURCE = "KRX_DATA_MARKETPLACE_MDCSTAT02303"
ROUTE = "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION"
BLD = "dbms/MDC/STAT/standard/MDCSTAT02303"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ISIN = re.compile(r"^KR[0-9A-Z]{10}$")
SYMBOL = re.compile(r"^[0-9]{6}$")
COLUMNS = frozenset((
    "일자", "금융투자", "보험", "투신", "사모", "은행", "기타금융",
    "연기금 등", "기타법인", "개인", "외국인", "기타외국인", "전체",
))
INSTITUTION_COMPONENTS = (
    "금융투자", "보험", "투신", "사모", "은행", "기타금융", "연기금 등",
)
ALLOWED = frozenset((
    "source", "access_route", "api_bld", "market_scope",
    "symbol", "isu_cd", "year", "request_start_date", "request_end_date",
    "ask_bid", "trade_volume_value", "observed_first_date",
    "observed_last_date", "observed_row_count", "columns",
    "raw_response_sha256", "schema_sha256", "retrieved_at",
    "capture_mode",
))


class KRXFlow2022ReceiptError(ValueError):
    """Fail closed: reject unscoped source metadata or raw/secret values."""


def _day(value: Any, label: str) -> date:
    if type(value) is not str or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise KRXFlow2022ReceiptError(label + ": YYYY-MM-DD required")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise KRXFlow2022ReceiptError(label + ": invalid date") from exc


def _stamp(value: Any) -> datetime:
    if type(value) is not str:
        raise KRXFlow2022ReceiptError("retrieved_at: timezone-aware string required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise KRXFlow2022ReceiptError("retrieved_at: invalid datetime") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise KRXFlow2022ReceiptError("retrieved_at: timezone offset required")
    return parsed


def audit_krx_2022_flow_receipt(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Structural compatibility only, never an authenticated/raw PIT pass.

    Caller-supplied digests, observed dates and counts are untrusted claims.
    Source-byte verification must happen independently inside the protected
    KRX worker, not from this isolated GitHub metadata validator.
    """
    if not isinstance(candidate, Mapping):
        raise KRXFlow2022ReceiptError("candidate metadata mapping required")
    if set(candidate) != ALLOWED:
        raise KRXFlow2022ReceiptError("metadata keys differ from allowlist")
    if (
        candidate["source"] != SOURCE or candidate["access_route"] != ROUTE
        or candidate["api_bld"] != BLD or candidate["market_scope"] != "KOSPI"
    ):
        raise KRXFlow2022ReceiptError("KRX source route or market scope drift")
    if (
        type(candidate["symbol"]) is not str
        or SYMBOL.fullmatch(candidate["symbol"]) is None
        or type(candidate["isu_cd"]) is not str
        or ISIN.fullmatch(candidate["isu_cd"]) is None
    ):
        raise KRXFlow2022ReceiptError("historical issue identity format invalid")
    if type(candidate["year"]) is not int or candidate["year"] != 2022:
        raise KRXFlow2022ReceiptError("receipt requires exact 2022 historical year")
    if candidate["capture_mode"] != "HISTORICAL_RECONSTRUCTION":
        raise KRXFlow2022ReceiptError("historic capture mode required")
    if candidate["ask_bid"] != "3" or candidate["trade_volume_value"] != "2":
        raise KRXFlow2022ReceiptError("net-buy value mode mismatch")
    start = _day(candidate["request_start_date"], "request_start_date")
    end = _day(candidate["request_end_date"], "request_end_date")
    first = _day(candidate["observed_first_date"], "observed_first_date")
    last = _day(candidate["observed_last_date"], "observed_last_date")
    if not (
        start <= first <= last <= end
        and start.year == end.year == first.year == last.year == 2022
    ):
        raise KRXFlow2022ReceiptError("historical request and observed date bounds mismatch")
    row_count = candidate["observed_row_count"]
    if type(row_count) is not int or not 1 <= row_count <= 365:
        raise KRXFlow2022ReceiptError("bounded historical response row count invalid")
    cols = candidate["columns"]
    if (
        not isinstance(cols, (list, tuple))
        or len(cols) != len(COLUMNS)
        or any(type(x) is not str for x in cols)
        or set(cols) != COLUMNS
    ):
        raise KRXFlow2022ReceiptError("investor category schema mismatch")
    for name in ("raw_response_sha256", "schema_sha256"):
        value = candidate[name]
        if type(value) is not str or SHA256.fullmatch(value) is None:
            raise KRXFlow2022ReceiptError(name + ": fingerprint invalid")
    retrieved = _stamp(candidate["retrieved_at"])
    first_eligible_capture = datetime.combine(end, time.min, tzinfo=retrieved.tzinfo)
    if retrieved < first_eligible_capture:
        raise KRXFlow2022ReceiptError("retrieval before request end date")

    return {
        "source_family": "KRX_INVESTOR_FLOW",
        "source_receipt_shape_compatible": True,
        "requested_year": 2022,
        "declared_response_rows": row_count,
        "declared_institution_component_categories": list(INSTITUTION_COMPONENTS),
        "foreign_vs_other_foreign_are_distinct": True,
        "institution_aggregate_mapping_independently_verified": False,
        "foreign_aggregate_mapping_independently_verified": False,
        "exact_krw_units_independently_verified": False,
        "raw_response_bytes_independently_verified": False,
        "authenticated_2022_acquisition_independently_verified": False,
        "original_as_published_2022_vintage_verified": False,
        "original_publication_time_independently_verified": False,
        "historical_revision_lineage_verified": False,
        "historical_identity_episode_verified": False,
        "full_universe_coverage_verified": False,
        "source_admitted": False,
        "performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
        "ordering_enabled": False,
        "interpretation": (
            "Only caller-asserted metadata matches a pinned 2026 tiny-probe schema. "
            "The separately authenticated 2026 three-day route does not prove a "
            "2022 historical source response, original vintage, foreign/institution "
            "aggregate semantics, or proper trading-day availability."
        ),
    }
