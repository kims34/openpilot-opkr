"""Original 2022 Q3 DART first-receipt financial-viewer cooccurrence ONLY.

A new source-only hypothesis: do operating-income rows, consolidated income
heading, literal three-month and full 2022/2021 July-September windows occur
*within the same original viewer subdocument*? Cooccurrence is NOT a statement
+ cell-period association. Do not save original HTML, values, identifiers,
subdocument names, raw dates, provider messages or any source secrets.
Exactly 2 fixed official registry/index calls + 1 first-receipt viewer
TOC call + at most 4 selected source-only public viewer subdocument calls.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re

from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT, _registry, _window
from research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import original_first_receipt
from research_v1_opendart_m20_2022_first_document_pilot import _has_q3_period_window
from research_v1_opendart_m20_2022_first_viewer_financial_sections import (
    SectionShape, SectionGap, SAFE, _choose_first_edition_sections,
    _bounded_public_get,
)
from research_v1_opendart_m20_2022_first_viewer_toc import _viewer_fetch

OUT = Path("research_results/opendart_m20_2022_viewer_section_cooccurrence/counts.json")
MAX_OFFICIAL = 2
MAX_PUBLIC_VIEWER = 5

class SectionCoflag(SectionShape):
    """In-memory original-viewer subdocument source hints; no values retained."""
    def result(self):
        source = super().result()
        body = re.sub(r"\s+", "", "".join(self.all_parts))
        has_profit = source["exact_operating_row_candidates"] > 0
        has_cfs = source["exact_cfs_income_heading_lexical_hint"]
        has_three_month = source["three_month_lexical_hint"]
        q3_2022 = _has_q3_period_window(body, 2022)
        q3_2021 = _has_q3_period_window(body, 2021)
        return {
            "operating_profit_row_candidates": source["exact_operating_row_candidates"],
            "profit_and_cfs_cooccur_in_viewer_subdocument": bool(has_profit and has_cfs),
            "profit_and_three_month_cooccur_in_viewer_subdocument": bool(
                has_profit and has_three_month
            ),
            "profit_and_2022_full_q3_window_cooccur": bool(has_profit and q3_2022),
            "profit_and_2021_full_q3_window_cooccur": bool(has_profit and q3_2021),
            "profit_and_both_full_q3_windows_cooccur": bool(
                has_profit and q3_2022 and q3_2021
            ),
            "profit_and_cfs_and_three_month_and_both_periods_cooccur": bool(
                has_profit and has_cfs and has_three_month and q3_2022 and q3_2021
            ),
            "viewer_subdocument_is_authoritative_original_profit_fact": False,
        }


def inspect_first_receipt_financial_sections(session, toc: str, original_receipt: str) -> dict:
    selected = _choose_first_edition_sections(toc, original_receipt)
    if len(selected) != 4:
        raise SectionGap("COOCCURRENCE_FOUR_FIRST_FINANCIAL_SECTIONS_REQUIRED")
    forms = []
    for section in selected:
        parser = SectionCoflag()
        parser.feed(_bounded_public_get(session, section, original_receipt))
        parser.close()
        forms.append(parser.result())
    if len(forms) != 4:
        raise SectionGap("COOCCURRENCE_SOURCE_CARDINALITY_DRIFT")
    result = {
        "source_status": "FIRST_ORIGINAL_VIEWER_SUBDOCUMENT_COOCCURRENCE_ONLY",
        "first_original_viewer_financial_sections": len(forms),
        "first_original_viewer_operating_candidates": sum(
            x["operating_profit_row_candidates"] for x in forms
        ),
        "operating_and_cfs_same_section_count": sum(
            x["profit_and_cfs_cooccur_in_viewer_subdocument"] for x in forms
        ),
        "operating_and_three_month_same_section_count": sum(
            x["profit_and_three_month_cooccur_in_viewer_subdocument"] for x in forms
        ),
        "operating_and_2022_complete_q3_window_same_section_count": sum(
            x["profit_and_2022_full_q3_window_cooccur"] for x in forms
        ),
        "operating_and_2021_complete_q3_window_same_section_count": sum(
            x["profit_and_2021_full_q3_window_cooccur"] for x in forms
        ),
        "operating_and_both_complete_q3_windows_same_section_count": sum(
            x["profit_and_both_full_q3_windows_cooccur"] for x in forms
        ),
        "operating_cfs_three_month_both_complete_periods_same_section_count": sum(
            x["profit_and_cfs_and_three_month_and_both_periods_cooccur"] for x in forms
        ),
        "viewer_cooccurrence_is_not_a_fact_period_or_edition_binding": True,
        "original_2022_2021_three_month_cfs_profit_values_verified": False,
    }
    for k,v in result.items():
        if k.endswith("_count") and not 0 <= v <= len(forms):
            raise SectionGap("COOCCURRENCE_COUNT_INVARIANT_FAILED")
    return result


def execute(session, key: str) -> dict:
    raw = _official_get(session, "corpCode.xml",
                        {"crtfc_key": key}, zip_response=True)
    issuer = _registry(raw).get(COHORT[5])
    if issuer is None:
        raise SectionGap("COOCCURRENCE_ISSUER_NOT_IN_REGISTRY")
    begin, end = _window(2022)
    official_index = _official_get(session, "list.json", {
        "crtfc_key": key, "corp_code": issuer, "bgn_de": begin, "end_de": end,
        "pblntf_ty": "A", "last_reprt_at": "N", "page_count": "100",
    })
    first_receipt = original_first_receipt(official_index, 2022)
    toc = _viewer_fetch(session, first_receipt)
    return inspect_first_receipt_financial_sections(session, toc, first_receipt)


def run(session=None) -> dict:
    key = os.environ.get("OPENDART_API_KEY", "").strip()
    answer = {
        "purpose": "FROZEN_M20_SLOT5_2022_Q3_ORIGINAL_VIEWER_SAME_SUBDOC_COOCCURRENCE",
        "fixed_cohort_slot": 5,
        "max_official_requests": MAX_OFFICIAL,
        "max_public_viewer_requests": MAX_PUBLIC_VIEWER,
        "credential_present": bool(key),
        "source_status": "PENDING" if key else "AUTH_NOT_CONFIGURED",
        **SAFE,
        "original_2022_2021_three_month_cfs_profit_values_verified": False,
    }
    if not key:
        return answer
    if session is None:
        import requests
        session = requests.Session()
    try:
        answer.update(execute(session, key))
    except Exception as err:
        allow = {
            "COOCCURRENCE_FOUR_FIRST_FINANCIAL_SECTIONS_REQUIRED",
            "COOCCURRENCE_SOURCE_CARDINALITY_DRIFT",
            "COOCCURRENCE_COUNT_INVARIANT_FAILED",
            "COOCCURRENCE_ISSUER_NOT_IN_REGISTRY",
            "ORIGINAL_VIEWER_INPUT_INVALID", "ORIGINAL_VIEWER_TOC_UNAVAILABLE",
            "FINANCIAL_SUBDOCUMENT_COUNT_UNVERIFIED",
            "FINANCIAL_SUBDOCUMENT_DUPLICATE_METADATA",
            "VIEWER_RECEIPT_EDITION_MISMATCH",
        }
        code = str(err) if type(err) is SectionGap else ""
        answer["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        answer["failure_code"] = code if code in allow else "FIRST_SOURCE_COOCCURRENCE_UNVERIFIED"
    return answer


if __name__ == "__main__":
    evidence = run()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(evidence, sort_keys=True, indent=2), encoding="utf-8")
    print("M20_ORIGINAL_VIEWER_COOCCURRENCE=" +
          json.dumps(evidence, sort_keys=True), flush=True)
