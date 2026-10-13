"""Metadata-only fail-closed gate for an isolated Kiwoom ka10059 investor-flow probe.

No networking, credentials, data persistence, backtests or orders. A broker API
response, even when valid, cannot prove point-in-time reproducible historical
availability, universe coverage, usage rights or source admission.
"""
from __future__ import annotations

from datetime import datetime
import re
from typing import Mapping, Any

API_ID = "ka10059"
API_PATH = "/api/dostk/stkinfo"
MAX_PAGES = 3
REQUEST = {
    "dt": "20261008",
    "stk_cd": "005930",
    "amt_qty_tp": "1",
    "trde_tp": "0",
    "unit_tp": "1",
}
REQUIRED_NUMERIC_FIELDS = ("frgnr_invsr", "orgn", "acc_trde_prica")
REQUIRED_DATE_FIELD = "dt"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
DATE8 = re.compile(r"^[0-9]{8}$")
SENSITIVE_KEYS = frozenset({
    "token", "access_token", "appkey", "app_key", "secretkey",
    "app_secret", "authorization", "kiwoom_app_key", "kiwoom_app_secret",
})

PENDING_EVIDENCE = (
    "authenticated bounded response with source identity and exchange scope",
    "exact monetary units and net-buy sign validated against issuer/day official source",
    "start-to-end historical depth, continuation and full panel coverage",
    "official historical security identities, delistings, halts and corporate actions",
    "as-published vintage, historical corrections and verified publication timestamps",
    "per-record event_time, published_at, available_at, ingested_at",
    "licence/terms for this exact source and research use",
    "independent expected universe including missing and zero-activity rows",
    "precommitted experiment protocol and untouched independent evaluation sample",
)


def _valid_day(value: Any) -> bool:
    if not isinstance(value, str) or DATE8.fullmatch(value) is None:
        return False
    try:
        datetime.strptime(value, "%Y%m%d")
        return True
    except ValueError:
        return False


def audit_kiwoom_probe(report: Mapping[str, Any] | None) -> dict[str, Any]:
    """Inspect metadata, never infer admission from status or fabricated flags.

    This is deliberately a one-way gate: there is NO user-supplied boolean that
    turns source/admission/performance/holdout or trading authority on.
    """
    failures: list[str] = []
    if not isinstance(report, Mapping):
        return _result(["missing_or_invalid_report"], False, 0, False)
    if any(str(k).lower() in SENSITIVE_KEYS for k in report):
        failures.append("sensitive_key_in_metadata")
    for k in ("ordering", "performance_admitted", "raw_rows_persisted"):
        if report.get(k) is not False:
            failures.append("unsafe_" + k)
    if report.get("purpose") != "SOURCE_FEASIBILITY_NOT_PROFITABILITY":
        failures.append("purpose_drift")
    if report.get("requested_body") != REQUEST:
        failures.append("request_scope_drift")
    if report.get("status") not in (
        "SOURCE_REACHABLE_METADATA_ONLY", "SOURCE_REACHABLE_EMPTY",
    ):
        failures.append("source_not_reachable")
    pages = report.get("pages")
    if not isinstance(pages, list) or not 1 <= len(pages) <= MAX_PAGES:
        failures.append("page_count_invalid")
        pages = []
    count = 0
    earliest: str | None = None
    latest: str | None = None
    for index, page in enumerate(pages):
        if not isinstance(page, Mapping):
            failures.append("page_not_object")
            continue
        rows = page.get("rows")
        if type(rows) is not int or rows < 0:
            failures.append("row_count_invalid")
            continue
        count += rows
        for field in ("invalid_dates", "missing_required_rows", "invalid_numeric_rows"):
            if type(page.get(field)) is not int or page[field] != 0:
                failures.append(field + "_present")
        if not isinstance(page.get("raw_sha256"), str) or HEX64.fullmatch(page["raw_sha256"]) is None:
            failures.append("response_digest_missing")
        low, high = page.get("min_date"), page.get("max_date")
        if rows:
            if not (_valid_day(low) and _valid_day(high) and low <= high <= REQUEST["dt"]):
                failures.append("invalid_date_bounds")
            else:
                if latest is not None and high >= earliest:
                    # Normal reverse-date pagination must not overlap an earlier page.
                    failures.append("overlapping_or_unsorted_pages")
                earliest, latest = low, high
        elif low is not None or high is not None:
            failures.append("empty_page_with_dates")
        more = page.get("more")
        if type(more) is not bool:
            failures.append("continuation_flag_missing")
        elif index < len(pages) - 1 and more is not True:
            failures.append("pagination_ended_early")
    duplicate_days = report.get("duplicate_dates")
    if type(duplicate_days) is not int or duplicate_days != 0:
        failures.append("duplicate_or_unverified_dates")
    if pages and isinstance(pages[-1], Mapping) and pages[-1].get("more") is True and report.get("history_exhausted") is True:
        failures.append("pagination_exhaustion_conflict")
    if report.get("history_exhausted") is not True:
        # This covers incomplete (truncated) pagination, NOT full-history
        # coverage: ka10059 may impose its own undocumented retention window.
        failures.append("pagination_not_exhausted")
    if count == 0:
        failures.append("zero_observations")
    if report.get("status") == "SOURCE_REACHABLE_EMPTY" and count != 0:
        failures.append("empty_status_conflict")
    if report.get("status") == "SOURCE_REACHABLE_METADATA_ONLY" and count == 0:
        failures.append("nonempty_status_conflict")
    reachable = report.get("status") == "SOURCE_REACHABLE_METADATA_ONLY"
    return _result(failures, reachable, count, True)


def _result(failures: list[str], reachable: bool, rows: int, presented: bool) -> dict[str, Any]:
    return {
        "source": "KIWOOM_REST_KA10059",
        "api_id": API_ID,
        "api_path": API_PATH,
        "probe_report_present": presented,
        "metadata_validation_pass": not failures,
        "metadata_failures": list(dict.fromkeys(failures)),
        "observed_rows_metadata_only": rows,
        "bounded_route_reachability": reachable and not failures,
        "authenticated_route_evidence_verified": False,
        "full_universe_coverage_verified": False,
        "broker_historical_vintage_pit_verified": False,
        "licence_and_publication_verified": False,
        "source_admitted": False,
        "new_strategy_preregistered": False,
        "performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "champion_change_authorized": False,
        "ordering_enabled": False,
        "live_trading_authorized": False,
        "required_independent_evidence": list(PENDING_EVIDENCE),
        "interpretation": (
            "A metadata-only ka10059 response cannot prove retrospective PIT "
            "availability, original vintages, full-universe coverage, trading rights "
            "or post-cost profitability. Missing evidence remains missing."
        ),
    }
