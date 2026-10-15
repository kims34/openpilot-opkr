"""Fixed 2022 first-filing DART viewer subdocument TOC feasibility (source-only).

This is an independent public DART viewer index route for the exact original
receipt selected by official OpenDART list. It is NOT an official time API,
verified DART XSD, stable public API, original accounting fact or trading
authorization. Only safe counts and booleans leave the process. No raw
receipt, document ID, title, URL, source or amounts are persisted.

Two bounded authenticated official reads (corpCode/list), then exactly one
public first-edition DART viewer main.do GET, with no key in the public call.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re

from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT, _registry, _window
from research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import original_first_receipt

OUTPUT = Path("research_results/opendart_m20_2022_first_viewer_toc/counts.json")
VIEWER_URL = "https://dart.fss.or.kr/dsaf001/main.do"
MAX_BYTES = 3 * 1024 * 1024
MAX_ITEMS = 1000
MAX_OFFICIAL_API_CALLS = 2
MAX_DART_VIEWER_CALLS = 1
RECEIPT = re.compile(r"[0-9]{14}\Z")
# Multidocument TOC records in existing DART viewer JavaScript, as observed
# in public client examples. Only fixed metadata categories are retained.
NODE = re.compile(
    r"""(?P<node>node[12])\['text'\]\s*=\s*["'](?P<title>[^"'<>]{0,300})["']\s*;"""
    r"""(?:(?!node[12]\['text'\]).){0,1000}?(?P=node)\['id'\]\s*=\s*["'](?P<id>[0-9]{1,12})["']\s*;"""
    r"""(?:(?!node[12]\['text'\]).){0,1000}?(?P=node)\['rcpNo'\]\s*=\s*["'](?P<receipt>[0-9]{14})["']\s*;"""
    r"""(?:(?!node[12]\['text'\]).){0,1000}?(?P=node)\['dcmNo'\]\s*=\s*["'](?P<document>[0-9]{1,12})["']\s*;"""
    r"""(?:(?!node[12]\['text'\]).){0,1000}?(?P=node)\['eleId'\]\s*=\s*["'](?P<element>[0-9]{1,12})["']\s*;"""
    r"""(?:(?!node[12]\['text'\]).){0,1000}?(?P=node)\['offset'\]\s*=\s*["'](?P<offset>[0-9]{1,12})["']\s*;"""
    r"""(?:(?!node[12]\['text'\]).){0,1000}?(?P=node)\['length'\]\s*=\s*["'](?P<length>[0-9]{1,12})["']\s*;"""
    r"""(?:(?!node[12]\['text'\]).){0,1000}?(?P=node)\['dtd'\]\s*=\s*["'](?P<dtd>[A-Za-z0-9._-]{1,30})["']\s*;""",
    re.DOTALL,
)
# Independent receipt assignments must not be hidden by a malformed JS node.
# They are metadata evidence only; rejecting ambiguous editions never admits PIT.
RECEIPT_ASSIGN = re.compile(
    r"""node[12]\['rcpNo'\]\s*=\s*["'](?P<receipt>[0-9]{14})["']"""
)


SINGLE = re.compile(
    r"""viewDoc\(\s*["'](?P<receipt>[0-9]{14})["']\s*,\s*"""
    r"""["'](?P<document>[0-9]{1,12})["']\s*,\s*"""
    r"""["'](?P<element>[0-9]{1,12})["']\s*,\s*"""
    r"""["'](?P<offset>[0-9]{1,12})["']\s*,\s*"""
    r"""["'](?P<length>[0-9]{1,12})["']\s*,\s*"""
    r"""["'](?P<dtd>[A-Za-z0-9._-]{1,30})["']""",
)
GUARDS = {
    "viewer_is_original_vintage_financial_proof": False,
    "viewer_toc_is_official_sgml_xsd_schema_proof": False,
    "viewer_toc_is_first_publication_instant_proof": False,
    "verified_original_2022_q3_cfs_profit": False,
    "verified_original_2021_q3_3month_comparator": False,
    "historical_issuer_security_pit_verified": False,
    "complete_original_to_correction_cell_lineage": False,
    "m20_feature_pit_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "provider_response_html_titles_urls_ids_saved": False,
    "ordering": "DISABLED",
}


class ViewerGap(ValueError):
    """Public-safe, fixed codes only."""


def _safe_counts(html: str, first_receipt: str) -> dict:
    if not RECEIPT.fullmatch(first_receipt) or len(html) > MAX_BYTES:
        raise ViewerGap("VIEWER_INPUT_INVALID")
    if "<html" not in html.lower() and "<!doctype" not in html.lower():
        raise ViewerGap("VIEWER_NOT_HTML")
    raw_receipt_assignments = {
        match.group("receipt") for match in RECEIPT_ASSIGN.finditer(html)
    }
    if raw_receipt_assignments - {first_receipt}:
        raise ViewerGap("VIEWER_MULTIPLE_RECEIPT_EDITIONS")
    nodes = list(NODE.finditer(html))
    if len(nodes) > MAX_ITEMS:
        raise ViewerGap("VIEWER_TOC_ITEMS_BUDGET")
    first_only = [x for x in nodes if x.group("receipt") == first_receipt]
    other_receipt_count = sum(x.group("receipt") != first_receipt for x in nodes)
    # Competing receipts could mean a newer edition/related filing is mixed in.
    if other_receipt_count:
        raise ViewerGap("VIEWER_MULTIPLE_RECEIPT_EDITIONS")
    if not first_only:
        singles = list(SINGLE.finditer(html))
        if len(singles) > MAX_ITEMS or any(
            x.group("receipt") != first_receipt for x in singles
        ):
            raise ViewerGap("VIEWER_UNLINKED_SUBDOCUMENT")
        if not singles:
            raise ViewerGap("VIEWER_TOC_NOT_STRUCTURED")
        return {
            "source_status": "FIRST_RECEIPT_VIEWER_SINGLE_DOC_METADATA_ONLY",
            "matched_first_receipt_toc_entries": 0,
            "matched_first_receipt_single_viewdoc_entries": len(singles),
            "toc_exact_cfs_income_heading_entries": 0,
            "toc_generic_financial_statement_heading_entries": 0,
            "toc_notes_heading_entries": 0,
            "toc_has_dart3_xsd_query_marker": any(
                x.group("dtd") == "dart3.xsd" for x in singles
            ),
            "toc_structured_first_original_cfs_section_proven": False,
        }
    titles = [x.group("title") for x in first_only]
    return {
        "source_status": "FIRST_RECEIPT_VIEWER_TOC_METADATA_ONLY",
        "matched_first_receipt_toc_entries": len(first_only),
        "matched_first_receipt_single_viewdoc_entries": 0,
        "toc_exact_cfs_income_heading_entries": sum(
            ("연결포괄손익계산서" in title or "연결손익계산서" in title)
            for title in titles
        ),
        "toc_generic_financial_statement_heading_entries": sum(
            "재무제표" in title for title in titles
        ),
        "toc_notes_heading_entries": sum("주석" in title for title in titles),
        "toc_has_dart3_xsd_query_marker": any(
            x.group("dtd") == "dart3.xsd" for x in first_only
        ),
        "toc_structured_first_original_cfs_section_proven": False,
    }


def _viewer_fetch(session, first_receipt: str) -> str:
    if not RECEIPT.fullmatch(first_receipt):
        raise ViewerGap("VIEWER_RECEIPT_SHAPE_INVALID")
    try:
        response = session.get(
            VIEWER_URL, params={"rcpNo": first_receipt},
            timeout=20, allow_redirects=False, stream=True,
            headers={"User-Agent": "IndexAlert-ReadOnlyResearch/1.0"},
        )
    except Exception:
        raise ViewerGap("VIEWER_NETWORK_UNAVAILABLE") from None
    try:
        if response.status_code != 200:
            raise ViewerGap("VIEWER_HTTP_UNAVAILABLE")
        if "text/html" not in response.headers.get("Content-Type", "").lower():
            raise ViewerGap("VIEWER_RESPONSE_NOT_HTML")
        buffer = bytearray()
        for part in response.iter_content(chunk_size=65536):
            buffer.extend(part)
            if len(buffer) > MAX_BYTES:
                raise ViewerGap("VIEWER_HTML_BUDGET_EXCEEDED")
        for enc in ("utf-8", "cp949", "euc-kr"):
            try:
                return bytes(buffer).decode(enc, errors="strict")
            except UnicodeError:
                pass
        raise ViewerGap("VIEWER_TEXT_DECODING_INVALID")
    finally:
        response.close()


def execute(session, key: str) -> dict:
    registry = _official_get(session, "corpCode.xml",
                             {"crtfc_key": key}, zip_response=True)
    issuer = _registry(registry).get(COHORT[5])
    if issuer is None:
        raise ViewerGap("ORIGINAL_FIXED_CORP_REGISTRY_MISSING")
    begin, end = _window(2022)
    filing_index = _official_get(session, "list.json", {
        "crtfc_key": key, "corp_code": issuer, "bgn_de": begin, "end_de": end,
        "pblntf_ty": "A", "last_reprt_at": "N", "page_count": "100",
    })
    first = original_first_receipt(filing_index, 2022)
    return _safe_counts(_viewer_fetch(session, first), first)


def run(session=None) -> dict:
    key = os.environ.get("OPENDART_API_KEY", "").strip()
    output = {
        "purpose": "FROZEN_M20_FIRST_2022_Q3_DART_VIEWER_TOC_ONLY",
        "fixed_cohort_slot": 5,
        "max_official_api_calls": MAX_OFFICIAL_API_CALLS,
        "max_public_viewer_calls": MAX_DART_VIEWER_CALLS,
        "credential_present": bool(key),
        "source_status": "PENDING" if key else "AUTH_NOT_CONFIGURED",
        **GUARDS,
    }
    if not key:
        return output
    if session is None:
        import requests
        session = requests.Session()
    try:
        output.update(execute(session, key))
    except Exception as exc:
        known = {
            "VIEWER_INPUT_INVALID", "VIEWER_NOT_HTML", "VIEWER_TOC_ITEMS_BUDGET",
            "VIEWER_MULTIPLE_RECEIPT_EDITIONS", "VIEWER_UNLINKED_SUBDOCUMENT",
            "VIEWER_TOC_NOT_STRUCTURED", "VIEWER_RECEIPT_SHAPE_INVALID",
            "VIEWER_NETWORK_UNAVAILABLE", "VIEWER_HTTP_UNAVAILABLE",
            "VIEWER_RESPONSE_NOT_HTML", "VIEWER_HTML_BUDGET_EXCEEDED",
            "VIEWER_TEXT_DECODING_INVALID", "ORIGINAL_FIXED_CORP_REGISTRY_MISSING",
        }
        label = str(exc) if type(exc) is ViewerGap else ""
        output["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        output["failure_code"] = label if label in known else "VIEWER_OR_SOURCE_UNVERIFIED"
    return output


if __name__ == "__main__":
    report = run()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, sort_keys=True, indent=2), encoding="utf-8")
    print("M20_FIRST_DART_VIEWER_TOC=" + json.dumps(report, sort_keys=True), flush=True)
