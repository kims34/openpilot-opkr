"""Compose four prior OFFICIAL original-DART viewer *counts-only* artifacts.

No new issuer, OpenDART, KRX or market request; the runner only downloads
four exactly pinned, previously completed GitHub Actions artifacts and verifies
run SHA, run conclusion, artifact ID/name/digest, 2022 Q3 cohort identity,
source-shape count consistency and mandatory NO-GO. No financial values,
original HTML, receipts, issuers, prices, returns or holdout data allowed.

Cross-checking counts does not certify first-edition CFS fiscal cell/PIT.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

EXPECTED = {
    "financial_sections": (38706084440, "595743780a11b203fa37e29dbb3a83e5c4ba31d4",
        11958577751, "m20-2022-original-viewer-financial-section-counts-only",
        "sha256:6968c8d31404b8fc87f2c08d0bb92e00c7fd72c564d20f46f2994cb0a808d106",
        "FIRST_SUBMITTED_VIEWER_FINANCIAL_SUBDOC_LEXICAL_DIAGNOSTIC_ONLY"),
    "same_subdocument": (38708786002, "8703a83d5430b064b3e67d2091c912d034c6c60e",
        11958909398, "m20-first-source-q3-subdocument-cooccurrence-counts-only",
        "sha256:d615ae2888883df0fe1cb7ce093cc4ed4faa84ef8b8ebca39785ef74b83f8aa3",
        "FIRST_ORIGINAL_VIEWER_SUBDOCUMENT_COOCCURRENCE_ONLY"),
    "same_table": (38731230183, "af048d8d202d63a6fb41527e622658588cb1f339",
        11971011193, "m20-first-original-viewer-same-table-q3-counts-only",
        "sha256:145cbca42fd9336f9a375aa8a9475f3f11464ca08795a0ba1b65935dc0a3a153",
        "FIRST_ORIGINAL_VIEWER_SAME_TABLE_Q3_SHAPE_ONLY"),
    "header_rows": (38822004271, "bb61dc5da281c1a0388575de3e13e9cc30caa5a0",
        12013358036, "m20-2022-original-viewer-header-shape-counts-only",
        "sha256:9c6aa171cf30902a502b611096587389d5ba5d8d99aadec5300d92fba1ebef66",
        "FIRST_RECEIPT_VIEWER_HEADER_ROW_SHAPES_ONLY"),
}
ALLOWED_STR = frozenset(("purpose", "source_status", "ordering"))
BLOCKED_SUFFIXES = ("_authorized", "_admitted", "_verified", "_saved")
OUT = Path("research_results/opendart_m20_original_evidence_gate/verdict.json")
# Exact observed first-receipt viewer diagnostics, not candidate factual values.
OBSERVED = {
    "financial_sections": {
        "first_receipt_financial_toc_sections_selected": 4,
        "viewer_financial_sections_returned_html": 4,
        "viewer_financial_total_table_tags": 329,
        "viewer_financial_total_operating_row_text_candidates": 2,
        "viewer_sections_exact_cfs_income_heading_hints": 2,
        "viewer_sections_three_month_hints": 2,
    },
    "same_subdocument": {
        "first_original_viewer_financial_sections": 4,
        "first_original_viewer_operating_candidates": 2,
        "operating_and_cfs_same_section_count": 1,
        "operating_and_three_month_same_section_count": 1,
        "operating_and_2022_complete_q3_window_same_section_count": 0,
        "operating_and_2021_complete_q3_window_same_section_count": 0,
        "operating_cfs_three_month_both_complete_periods_same_section_count": 0,
    },
    "same_table": {
        "first_original_financial_viewer_sections": 4,
        "total_viewer_tables_in_financial_sections": 329,
        "profit_candidate_tables": 2,
        "profit_rows_with_four_numeric_peer_cells": 2,
        "profit_tables_with_current_and_prior_quarter_headers": 1,
        "profit_tables_with_three_month_header": 0,
        "profit_tables_with_complete_2022_q3_date_window": 0,
        "profit_tables_with_complete_2021_q3_date_window": 0,
        "profit_tables_with_explicit_cfs_income_heading": 0,
    },
    "header_rows": {
        "fixed_first_filing_financial_subdocuments": 4,
        "source_table_tags": 329,
        "operating_candidate_tables": 2,
        "operating_candidate_rows": 2,
        "operating_with_four_numeric_peers": 2,
        "operating_with_preceding_th_cell": 2,
        "operating_with_preceding_current_and_prior_quarter_words": 0,
        "operating_with_preceding_three_month_word": 0,
        "operating_candidate_tables_with_unsupported_span": 0,
        "unsupported_span_attributes_encountered": 2,
    },
}
REQUIRED_BLOCKS = (
    "m20_feature_pit_admitted", "m20_performance_run_authorized",
    "independent_holdout_authorized", "champion_change_authorized",
    "real_orders_authorized", "funds_movement_authorized",
    "permissions_change_authorized",
)
PUB_SAFE_ERROR = "M20_PINNED_ORIGINAL_SOURCE_EVIDENCE_FAIL_CLOSED"


class EvidenceGap(ValueError):
    """No upstream private/provider contents or source strings in errors."""


def _unique_pairs(pairs):
    output = {}
    for key, value in pairs:
        if key in output:
            raise EvidenceGap("DUPLICATE_JSON_KEY")
        output[key] = value
    return output


def _safe_object(v):
    if type(v) is not dict:
        raise EvidenceGap("INVALID_JSON_OBJECT")
    return v


def validate_contract(manifest: dict) -> None:
    _safe_object(manifest)
    if (manifest.get("schema_version") != "M20_FIRST_Q3_ORIGINAL_VIEWER_EVIDENCE_1"
            or type(manifest.get("fixed_cohort_slot")) is not int
            or manifest["fixed_cohort_slot"] != 5
            or manifest.get("year") != 2022 or manifest.get("report") != "Q3"
            or manifest.get("ordering") != "DISABLED"
            or manifest.get("performance_authorization") is not False
            or manifest.get("order_authorization") is not False):
        raise EvidenceGap("SOURCE_MANIFEST_SCOPE_INVALID")
    records = manifest.get("source_records")
    if type(records) is not list or len(records) != 4:
        raise EvidenceGap("SOURCE_MANIFEST_COMPLETENESS_INVALID")
    if set(x.get("key") for x in records if type(x) is dict) != set(EXPECTED):
        raise EvidenceGap("SOURCE_MANIFEST_KEYS_INVALID")
    for x in records:
        if type(x) is not dict:
            raise EvidenceGap("SOURCE_MANIFEST_RECORD_INVALID")
        key = x["key"]
        actual = (x.get("run_id"), x.get("head_sha"), x.get("artifact_id"),
                  x.get("artifact_name"), x.get("artifact_digest"))
        expected = EXPECTED[key][:5]
        if actual != expected or any(type(value) is not type(ref) for value, ref in zip(actual, expected)):
            raise EvidenceGap("PINNED_SOURCE_REFERENCE_MISMATCH")


def validate_metadata(manifest: dict, metadata: dict) -> None:
    _safe_object(metadata)
    if set(metadata) != set(EXPECTED):
        raise EvidenceGap("PINNED_METADATA_MISSING")
    for x in manifest["source_records"]:
        key = x["key"]
        pair = _safe_object(metadata[key])
        run = _safe_object(pair.get("run"))
        artifact = _safe_object(pair.get("artifact"))
        if (run.get("id") != x["run_id"]
                or run.get("head_sha") != x["head_sha"]
                or run.get("status") != "completed"
                or run.get("conclusion") != "success"
                or type(run.get("id")) is not int):
            raise EvidenceGap("SOURCE_RUN_IDENTITY_OR_SUCCESS_MISMATCH")
        if (artifact.get("id") != x["artifact_id"]
                or artifact.get("name") != x["artifact_name"]
                or artifact.get("digest") != x["artifact_digest"]
                or artifact.get("expired") is not False
                or type(artifact.get("id")) is not int):
            raise EvidenceGap("PINNED_ARTIFACT_INTEGRITY_OR_EXPIRED")


def validate_source_counts(records: dict) -> dict:
    _safe_object(records)
    if set(records) != set(EXPECTED):
        raise EvidenceGap("EXACT_FOUR_ORIGINAL_REPORTS_REQUIRED")
    for key in EXPECTED:
        r = _safe_object(records[key])
        if (r.get("fixed_cohort_slot") != 5
                or type(r["fixed_cohort_slot"]) is not int
                or r.get("source_status") != EXPECTED[key][5]
                or r.get("ordering") != "DISABLED"
                or r.get("credential_present") is not True):
            raise EvidenceGap("ORIGINAL_SOURCE_STATUS_OR_SCOPE_MISMATCH")
        for flag in REQUIRED_BLOCKS:
            if r.get(flag) is not False:
                raise EvidenceGap("FORBIDDEN_OR_MISSING_FINANCIAL_OR_TRADE_FLAG")
        # Refuse accidental identifier/amount fields and silently promoted
        # financial/PIT status, even when the headline counts happen to match.
        for field, value in r.items():
            if field in ALLOWED_STR:
                if type(value) is not str:
                    raise EvidenceGap("SOURCE_STRING_FIELD_TYPE_INVALID")
            elif type(value) is str:
                raise EvidenceGap("UNEXPECTED_SOURCE_STRING_OR_PRIVATE_DATA")
            elif type(value) not in (int, bool):
                raise EvidenceGap("UNSAFE_SOURCE_REPORT_DATATYPE")
            if field.endswith(BLOCKED_SUFFIXES) and value is not False:
                raise EvidenceGap("UNAUTHORIZED_PIT_OR_PERFORMANCE_PROMOTION")
        for field, wanted in OBSERVED[key].items():
            if type(r.get(field)) is not int or r[field] != wanted:
                raise EvidenceGap("PINNED_SOURCE_CROSS_REPORT_DRIFT")
    # 4 financial sections, 329 table tags and 2 source row candidates
    # reconcile across four independent official source-only workflow runs.
    return {
        "purpose": "M20_FIXED_SLOT5_2022_FIRST_SOURCE_COUNT_RECONCILIATION",
        "status": "FOUR_OFFICIAL_SOURCE_DIAGNOSTICS_AGREE_NO_PIT",
        "verified_pinned_source_artifact_count": 4,
        "first_original_financial_viewer_subdocuments": 4,
        "financial_viewer_table_tags": 329,
        "first_original_operating_label_table_candidates": 2,
        "candidates_with_both_quarter_words_in_preceding_header_rows": 0,
        "candidates_with_full_2022_q3_window_in_same_table": 0,
        "candidates_with_full_2021_q3_window_in_same_table": 0,
        "actual_original_cfs_operating_profit_cell_period_lineage_verified": False,
        "historical_first_publication_instant_verified": False,
        "historical_issuer_security_pit_verified": False,
        "frozen_strategy_source_data_admitted": False,
        "m20_feature_pit_admitted": False,
        "m20_performance_run_authorized": False,
        "independent_holdout_authorized": False,
        "champion_change_authorized": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "permissions_change_authorized": False,
        "ordering": "DISABLED",
        "raw_source_values_or_proprietary_ids_persisted": False,
    }


def _read(path: Path, size=32_768) -> dict:
    if not path.is_file() or path.is_symlink() or path.stat().st_size > size:
        raise EvidenceGap("MISSING_OR_OVERSIZED_SOURCE_DIAGNOSTIC")
    return _safe_object(json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs))


def run(manifest_path: Path, input_dir: Path, metadata_dir: Path, output_path: Path) -> dict:
    manifest = _read(manifest_path, 16_384)
    validate_contract(manifest)
    reports = {}
    metadata = {}
    for key in EXPECTED:
        reports[key] = _read(input_dir / key / "counts.json", 16_384)
        metadata[key] = {
            "run": _read(metadata_dir / (key + ".run.json"), 256_000),
            "artifact": _read(metadata_dir / (key + ".artifact.json"), 64_000),
        }
    validate_metadata(manifest, metadata)
    verdict = validate_source_counts(reports)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(verdict, sort_keys=True, indent=2), encoding="utf-8")
    print("M20_SOURCE_EVIDENCE_GATE=" + json.dumps(verdict, sort_keys=True), flush=True)
    return verdict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--metadata-dir", required=True, type=Path)
    parser.add_argument("--output", default=OUT, type=Path)
    args = parser.parse_args()
    try:
        run(args.manifest, args.input_dir, args.metadata_dir, args.output)
    except (EvidenceGap, KeyError, ValueError, TypeError, OSError, UnicodeError):
        raise SystemExit(PUB_SAFE_ERROR) from None


if __name__ == "__main__":
    main()
