"""One-year *read-only* private KRX calendar reconciliation runner.

Default dry-run; --audit requires existing Railway KRX historical-worker
environment and files already present on the dedicated /data mount.
No authenticated KRX calls, no model/backtest/holdout/orders, no writes.
The original holiday export and normalization claim MUST remain private.
Even a date-set match is only source consistency, NOT PIT source admission.

Example (AFTER authorized original KRX export and independent SHA are staged):
  python -B research_v1_krx_private_calendar_year_runner.py \
    --year 2025 --document /data/krx-calendar/2025-source-export.csv \
    --claim /data/krx-calendar/2025-claimed-dates.json \
    --expected-document-sha256 <independently pinned source sha256> --audit

Output is aggregate JSON with no day-level observations or security IDs.
The original CSV or XLSX date rows must match the claim exactly, or this runner
refuses. Original KRX file origin and historical publication remain unverified;
binary legacy XLS/HTML and unsupported spreadsheets are always rejected.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
import hashlib
import json
import os
from pathlib import Path
import re

from research_v1_krx_calendar_csv_source_validator import extract_and_reconcile_csv
from research_v1_krx_calendar_xlsx_source_validator import read_holiday_source_xlsx
from research_v1_krx_private_date_set_comparator import audit_private_scope

SHA = re.compile(r"^[a-f0-9]{64}$")
MANIFEST = Path(__file__).resolve().parent / "evidence/krx/2026-10-13-krx-market-source-pit-boundaries.json"
EXPECTED_WORKER = "indexalert-krx-historical-worker"
STORE = "openapi_kospi_history_v1"

LOCKS = {
    "official_session_schedule_attested": False,
    "source_admitted_for_pit": False,
    "performance_authorized": False,
    "holdout_authorized": False,
    "27_quarantined_securities_released": False,
    "live_orders_authorized": False,
    "ordering": "DISABLED",
    "network_requests_attempted": False,
    "storage_mutated": False,
    "original_market_rows_emitted": False,
}


def _in_private_mount(path: Path) -> bool:
    if not isinstance(path, Path) or not path.is_absolute():
        return False
    if not path.is_relative_to("/data") or path.is_symlink():
        return False
    try:
        return path.resolve(strict=True).is_relative_to("/data") and path.is_file()
    except (OSError, ValueError):
        return False


def run_year(
    *, year: int, document: Path, claim: Path,
    expected_document_sha256: str, execute: bool = False,
) -> dict:
    report = {
        "status": "DRY_RUN_NO_PRIVATE_FILES_READ" if not execute else "FAIL_CLOSED_NO_AUTHORIZED_SOURCE",
        "year": year if type(year) is int else None,
        "yearly_expected_weekday_pairs": None,
        "yearly_expected_empty_responses": None,
        "calendar_claim_closed_weekdays_in_range": None,
        "source_comparison": None,
        "original_document_sha256": None,
        **LOCKS,
    }
    if not execute:
        return report
    if type(year) is not int or not (2015 <= year <= 2026):
        return report
    if type(expected_document_sha256) is not str or not SHA.fullmatch(expected_document_sha256):
        return report
    if os.getenv("RAILWAY_SERVICE_NAME") != EXPECTED_WORKER:
        return report
    # Mirrors the already deployed integrity audit's default /data mount.
    # A missing variable must not incorrectly refuse a valid existing
    # Railway mount; relative, symlinked or off-volume bases still fail.
    base = Path(os.getenv("KRX_PRIVATE_RAW_DIR") or "/data")
    if (not base.is_absolute() or not base.is_relative_to("/data")
            or base.is_symlink()):
        return report
    root = base / STORE
    if (not _in_private_mount(Path(document))
            or not _in_private_mount(Path(claim))
            or not root.exists() or root.is_symlink()):
        return report
    try:
        if document.stat().st_size > 8_000_000 or claim.stat().st_size > 40_000:
            return report
        original_blob = document.read_bytes()
        claim_data = json.loads(claim.read_text(encoding="utf-8"))
        if hashlib.sha256(original_blob).hexdigest() != expected_document_sha256:
            report["status"] = "FAIL_CLOSED_PINNED_DOCUMENT_SHA_MISMATCH"
            return report
        if original_blob.startswith(b"PK\x03\x04"):
            ref = read_holiday_source_xlsx(original_blob, claim_data, year)
            accepted = "SOURCE_XLSX_ROWS_EXACT_MATCH_CLAIM_ONLY_NOT_PIT"
        else:
            ref = extract_and_reconcile_csv(original_blob, claim_data, year)
            accepted = "SOURCE_CSV_ROWS_EXACT_MATCH_CLAIM_ONLY_NOT_PIT"
        if ref["status"] != accepted:
            return report
        inventory = json.loads(MANIFEST.read_text(encoding="utf-8"))
        matches = [
            x for x in inventory["offline_verification"]["per_year"]
            if x["year"] == year
        ]
        if len(matches) != 1:
            return report
        record = matches[0]
        begin = f"{year}-01-01"
        end = f"{year}-12-31" if year < 2026 else "2026-10-08"
        lo, hi = date.fromisoformat(begin), date.fromisoformat(end)
        expected_weekdays = sum(
            (lo + timedelta(days=i)).weekday() < 5
            for i in range((hi-lo).days + 1)
        )
        # Pin exact annual metadata shape, coverage and the SHA derived by
        # the original worker's official private-source integrity auditor.
        # A malformed or stale manifest must never drive a volume read.
        expected_empties = record.get("unverified_exchange_calendar_or_source_gap_days")
        expected_snapshot = record.get("reported_metadata_snapshot_sha256")
        if (type(record.get("year")) is not int or record["year"] != year
                or record.get("integrity_class") != "STORAGE_ONLY_NOT_PIT"
                or type(record.get("verified_weekday_pairs")) is not int
                or record["verified_weekday_pairs"] != expected_weekdays
                or type(expected_empties) is not int or not (0 <= expected_empties <= expected_weekdays)
                or type(expected_snapshot) is not str or not SHA.fullmatch(expected_snapshot)):
            report["status"] = "FAIL_CLOSED_UNPINNED_YEAR_SOURCE_MANIFEST"
            return report
        reference = [d for d in ref["dates"] if begin <= d <= end]
        if not reference:
            return report
        out = audit_private_scope(
            private_root=root, start=begin, end=end,
            reference_closed_iso_days=reference,
            expected_empty_count=expected_empties,
            expected_original_audit_snapshot_sha256=expected_snapshot,
        )
        # Matching SHA + exact original annual scope is a prerequisite for
        # treating even the *comparison* result as credible. Older mocked or
        # incomplete payloads must fail closed, not surface 'exact match'.
        if out.get("status") in (
            "EXACT_DATE_SET_AGREES_REFERENCE_ONLY_NOT_PIT",
            "EXACT_DATE_SET_MISMATCH_SOURCE_ADMISSION_BLOCKED",
        ):
            if (out.get("weekday_scope_count") != expected_weekdays
                    or out.get("verified_original_pairs") != expected_weekdays
                    or out.get("original_empty_day_count") != expected_empties
                    or out.get("reference_closed_day_count") != len(reference)
                    or out.get("original_audit_compatible_snapshot_sha256") != expected_snapshot
                    or out.get("original_official_calendar_attested") is not False
                    or out.get("source_contract_gates_C_D_open") is not False
                    or out.get("real_orders_authorized") is not False):
                report["status"] = "FAIL_CLOSED_INCOMPLETE_PRIVATE_SOURCE_COMPARISON_RECEIPT"
                return report
        report.update({
            "status": out["status"],
            "yearly_expected_weekday_pairs": record["verified_weekday_pairs"],
            "yearly_expected_empty_responses": record["unverified_exchange_calendar_or_source_gap_days"],
            "calendar_claim_closed_weekdays_in_range": len(reference),
            "original_document_sha256": expected_document_sha256,
            "source_comparison": {
                k:out.get(k) for k in (
                    "weekday_scope_count", "verified_original_pairs",
                    "original_empty_day_count", "reference_closed_day_count",
                    "empty_on_reference_closed", "empty_on_reference_open",
                    "nonempty_on_reference_closed",
                    "original_audit_compatible_snapshot_sha256",
                    "comparison_metadata_sha256"
                )
            } if out.get("verified_original_pairs") else None,
        })
        return report
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return report


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--year", type=int, required=True)
    cli.add_argument("--document", type=Path, required=True)
    cli.add_argument("--claim", type=Path, required=True)
    cli.add_argument("--expected-document-sha256", required=True)
    cli.add_argument("--audit", action="store_true")
    args = cli.parse_args()
    result = run_year(
        year=args.year, document=args.document, claim=args.claim,
        expected_document_sha256=args.expected_document_sha256,
        execute=args.audit,
    )
    print("INDEXALERT_KRX_PRIVATE_CALENDAR_YEAR_RECONCILIATION=" + json.dumps(
        result, sort_keys=True, separators=(",", ":")
    ), flush=True)
    # A mismatch is diagnostic evidence, NOT a successful audit run.
    # Exit nonzero so cron/CI cannot inadvertently treat a mismatch as pass.
    if args.audit and result["status"] != "EXACT_DATE_SET_AGREES_REFERENCE_ONLY_NOT_PIT":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
