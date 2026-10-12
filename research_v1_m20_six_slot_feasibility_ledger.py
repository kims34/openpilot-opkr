"""M20 six-slot original-Q3 source feasibility ledger (evidence, NOT alpha).

Use ONLY public-safe official workflow JSON reports. Never read raw XBRL,
issuer identities, returns, source financial amounts or historical Holdout.
The fixed six predeclared issuers are a source-shape sample, not the full
trade universe. Neither six success statuses nor amount parity authorize PIT,
performance evaluation, model promotion, broker orders or capital.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

FROZEN_SLOTS = tuple(range(6))
DIAGNOSTIC = "ORIGINAL_2022_2023_TO_CFS_3MONTH_PARITY_DIAGNOSTIC_ONLY"
SOURCE_GAP = "SOURCE_GAP_FAIL_CLOSED"
REQUIRED_FALSE = (
    "historical_xbrl_qname_equivalence_verified",
    "initial_xbrl_statement_table_binding_verified",
    "historical_security_corp_mapping_verified",
    "historical_intraday_publication_pit_verified",
    "historical_correction_lineage_complete",
    "market_status_and_true_cost_return_path_verified",
    "full_universe_history_verified",
    "m20_feature_pit_admitted",
    "m20_performance_run_authorized",
    "independent_holdout_authorized",
    "champion_change_authorized",
    "real_orders_authorized",
    "funds_movement_authorized",
    "permissions_change_authorized",
    "data_values_issuer_ids_and_source_rows_saved",
)
PARITY_FLAGS = (
    "api_2022_comparative_3month_equals_2022_first_original",
    "api_2023_3month_equals_2023_first_original",
    "api_2023_receipt_is_first_submitted",
    "initial_qnames_same",
    "initial_local_concept_name_same",
    "initial_source_namespace_same",
    "initial_reporter_identity_same",
    "initial_declared_precision_same",
    "origins_versus_current_2023_CFS_both_values_match",
)
PUBLIC_REASON_CATEGORIES = {
    "OFFICIAL_XBRL_FILE_NOT_FOUND": "ORIGINAL_XBRL_FILE_MISSING",
    "OFFICIAL_XBRL_NO_DATA": "ORIGINAL_XBRL_NO_DATA",
    "OFFICIAL_XBRL_REQUEST_LIMIT": "OFFICIAL_RATE_LIMIT",
    "UNCLASSIFIED": "UNCLASSIFIED_SOURCE_ERROR",
}


class LedgerError(ValueError):
    """No source text or identifiers may occur in any error."""


def _bool(row: dict, field: str) -> bool:
    if type(row.get(field)) is not bool:
        raise LedgerError("INVALID_BOUNDED_DIAGNOSTIC_FLAGS")
    return row[field]


def summarize_six_slot_sources(reports: list[dict]) -> dict:
    if type(reports) is not list or len(reports) != len(FROZEN_SLOTS):
        raise LedgerError("EXACT_SIX_FIXED_SOURCE_SLOTS_REQUIRED")
    slot_map = {}
    for row in reports:
        if type(row) is not dict or type(row.get("cohort_slot")) is not int:
            raise LedgerError("INVALID_FIXED_SOURCE_SLOT")
        slot = row["cohort_slot"]
        if slot not in FROZEN_SLOTS or slot in slot_map:
            raise LedgerError("DUPLICATE_OR_UNKNOWN_FIXED_SOURCE_SLOT")
        if row.get("ordering") != "DISABLED" or row.get("max_approved_official_requests") != 6:
            raise LedgerError("FORBIDDEN_ORDERING_OR_SOURCE_SCOPE")
        for flag in REQUIRED_FALSE:
            if _bool(row, flag):
                raise LedgerError("FORBIDDEN_ADMISSION_FLAG")
        status = row.get("source_status")
        if status not in (DIAGNOSTIC, SOURCE_GAP):
            raise LedgerError("UNKNOWN_SOURCE_DIAGNOSTIC_STATUS")
        if status == DIAGNOSTIC:
            if _bool(row, "two_initial_original_Q3_XBRL_financial_facts_found") is not True:
                raise LedgerError("COMPARATIVE_WITHOUT_BOTH_ORIGINAL_FACTS")
            for flag in PARITY_FLAGS:
                _bool(row, flag)
            expected = (row["api_2022_comparative_3month_equals_2022_first_original"]
                        and row["api_2023_3month_equals_2023_first_original"]
                        and row["api_2023_receipt_is_first_submitted"])
            if row["origins_versus_current_2023_CFS_both_values_match"] != expected:
                raise LedgerError("PARITY_INTERNAL_CONTRADICTION")
        else:
            if _bool(row, "two_initial_original_Q3_XBRL_financial_facts_found"):
                raise LedgerError("SOURCE_GAP_WITH_COMPLETE_PAIR")
            # Do not copy provider/exception strings into a public report.
            if type(row.get("failure_stage")) is not str or type(row.get("failure_code")) is not str:
                raise LedgerError("SOURCE_GAP_REASON_FIELDS_INVALID")
        slot_map[slot] = row

    factual = [slot_map[s] for s in FROZEN_SLOTS if slot_map[s]["source_status"] == DIAGNOSTIC]
    missing = [slot_map[s] for s in FROZEN_SLOTS if slot_map[s]["source_status"] == SOURCE_GAP]
    amount_both = sum(x["origins_versus_current_2023_CFS_both_values_match"] for x in factual)
    mismatch_22 = sum(not x["api_2022_comparative_3month_equals_2022_first_original"] for x in factual)
    mismatch_23 = sum(not x["api_2023_3month_equals_2023_first_original"] for x in factual)
    qname_drift = sum(not x["initial_qnames_same"] for x in factual)
    missing_files = sum(x.get("failure_code") == "OFFICIAL_XBRL_FILE_NOT_FOUND" for x in missing)

    categories = {}
    for row in missing:
        category = PUBLIC_REASON_CATEGORIES.get(row["failure_code"], "OTHER_SOURCE_GAP")
        categories[category] = categories.get(category, 0) + 1
    reason_codes = ["FULL_UNIVERSE_HISTORICAL_PIT_NOT_ADMITTED",
                    "HISTORICAL_MARKET_STATUS_AND_EXECUTION_NOT_ADMITTED",
                    "FIRST_FILED_XBRL_CONCEPT_EQUIVALENCE_UNVERIFIED"]
    if missing:
        reason_codes.append("ORIGINAL_2022_2023_SOURCE_GAPS")
    if mismatch_22 or mismatch_23:
        reason_codes.append("CURRENT_COMPARATIVE_RESTATEMENT_OR_SEMANTIC_DRIFT")
    if qname_drift:
        reason_codes.append("ORIGINAL_XBRL_QNAME_DRIFT")
    return {
        "purpose": "M20_FROZEN_SIX_ISSUER_2022_2023_SOURCE_FEASIBILITY_ONLY",
        "diagnostic_status": "NEW_EVIDENCE_REQUIRED_NOT_PERFORMANCE",
        "fixed_sample_slots": 6,
        "complete_original_pairs": len(factual),
        "missing_or_failed_original_pairs": len(missing),
        "current_api_both_three_month_amounts_match_originals": amount_both,
        "current_api_2022_comparative_mismatch_slots": mismatch_22,
        "current_api_2023_amount_mismatch_slots": mismatch_23,
        "original_qname_drift_slots": qname_drift,
        "official_original_xbrl_file_not_found_slots": missing_files,
        "source_gap_categories": dict(sorted(categories.items())),
        "reason_codes": reason_codes,
        "six_issuer_sample_is_full_strategy_universe": False,
        "historical_publication_pit_verified": False,
        "semantic_statement_binding_verified": False,
        "historical_corporate_action_and_tradability_verified": False,
        "m20_performance_run_authorized": False,
        "independent_holdout_authorized": False,
        "champion_change_authorized": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "permissions_change_authorized": False,
        "ordering": "DISABLED",
        "raw_original_filing_identifiers_values_and_rows_published": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output-file", required=True, type=Path)
    args = parser.parse_args()
    try:
        report_files = sorted(args.input_dir.glob("slot_*.json"))
        # Never allow extra candidate slots or partially downloaded artifacts.
        if {p.name for p in report_files} != {f"slot_{s}.json" for s in FROZEN_SLOTS}:
            raise LedgerError("EXACT_SIX_FIXED_SOURCE_SLOTS_REQUIRED")
        rows = []
        for f in report_files:
            if f.stat().st_size > 16_384:
                raise LedgerError("OVERSIZED_SOURCE_DIAGNOSTIC_FILE")
            row = json.loads(f.read_text(encoding="utf-8"))
            if type(row) is not dict or f.name != f"slot_{row.get('cohort_slot')}.json":
                raise LedgerError("SOURCE_DIAGNOSTIC_FILE_SLOT_BINDING")
            rows.append(row)
        summary = summarize_six_slot_sources(rows)
    except (LedgerError, ValueError, OSError, UnicodeError, TypeError):
        # Do not echo raw source report fields, path, XML or credential messages.
        raise SystemExit("M20_SIX_SLOT_LEDGER_FAIL_CLOSED") from None
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(json.dumps(summary, sort_keys=True, indent=2), encoding="utf-8")
    print("M20_SIX_SLOT_FEASIBILITY=" + json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
