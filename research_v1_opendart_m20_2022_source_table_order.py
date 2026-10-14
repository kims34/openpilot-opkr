"""M20 2022 original/correction source-table ORDER census, not financial facts.

Strictly read-only five official OpenDART requests, frozen cohort slot 5 and
previously pinned archive SHA256 values. Old/new in-document table-text hashes
and their positions are ephemeral. Output only bounded aggregate counts.
Even a unique insertion proves neither accounting-statement identity nor PIT.
"""
from __future__ import annotations

from bisect import bisect_left
from collections import Counter, defaultdict
from html.parser import HTMLParser
import hashlib
import io
import json
import os
from pathlib import Path
import zipfile

from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT, _registry, _window
from research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import original_first_receipt
from research_v1_opendart_m20_2022_correction_source_pair import _source_pair
from research_v1_opendart_m20_2022_later_edition_census import LATER_BEGIN, AS_OF
from research_v1_opendart_m20_2022_source_proof import EXPECTED_ORIGINAL_DOCUMENT_SHA256
from research_v1_opendart_m20_2022_correction_row_diff import (
    CORRECTED_ZIP_SHA256, _norm, MAX_HTML_NODES, MAX_TABLE_COUNT,
    MAX_TABLE_TEXT_CHARS, MAX_TOTAL_TABLE_INPUT_CHARS,
)
from research_v1_opendart_m20_2022_first_document_pilot import (
    _fetch_first_document, _decode_disclosure_markup,
    inspect_official_original_document,
)

OUTPUT = Path("research_results/opendart_m20_2022_order_census/summary.json")
REQUEST_LIMIT = 5
EXPECTED_ORIGINAL_TABLES = 1570
EXPECTED_CORRECTED_TABLES = 1576
EXPECTED_SHARED_TABLES = 1570
SOURCE_GAP = "SOURCE_GAP_FAIL_CLOSED"
SAFE_FALSE = (
    "original_q3_cfs_three_month_earnings_verified",
    "amended_q3_cfs_three_month_earnings_verified",
    "original_cfs_2021_q3_comparator_verified",
    "financial_cell_editions_semantically_bound",
    "complete_historical_correction_lineage_verified",
    "historical_publication_instant_pit_verified",
    "historical_issuer_security_pit_verified",
    "m20_feature_pit_admitted", "m20_performance_run_authorized",
    "independent_holdout_authorized", "champion_change_authorized",
    "real_orders_authorized", "funds_movement_authorized",
    "permissions_change_authorized",
    "raw_source_tables_hashes_positions_or_values_persisted",
)


class OrderGap(ValueError):
    """Internal source-only bounded error class, never provider messages."""


class _OrderedTableScanner(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.frames = []
        self.digests = []
        self.contexts = []
        self.nodes = 0
        self.text_size = 0
        self.preceding = ""

    def handle_starttag(self, tag, attrs):
        self.nodes += 1
        if self.nodes > MAX_HTML_NODES:
            raise OrderGap("HTML_NODES_BUDGET_EXCEEDED")
        if tag == "table":
            if len(self.frames) >= 50 or len(self.digests) + len(self.frames) >= MAX_TABLE_COUNT:
                raise OrderGap("TABLE_SCAN_BUDGET_EXCEEDED")
            self.frames.append({"parts": [], "nested": bool(self.frames),
                                "prefix": _norm(self.preceding[-400:])})

    def handle_data(self, text):
        if self.frames:
            self.text_size += len(text)
            if self.text_size > MAX_TOTAL_TABLE_INPUT_CHARS:
                raise OrderGap("TABLE_INPUT_BUDGET_EXCEEDED")
            for frame in self.frames:
                frame["parts"].append(text)
        else:
            self.preceding = (self.preceding + text)[-400:]

    def handle_endtag(self, tag):
        if tag != "table":
            return
        if not self.frames:
            raise OrderGap("TABLE_NESTING_UNVERIFIED")
        frame = self.frames.pop()
        raw = "".join(frame["parts"])
        if len(raw) > MAX_TABLE_TEXT_CHARS:
            raise OrderGap("TABLE_TEXT_BUDGET_EXCEEDED")
        content = _norm(raw)
        self.digests.append(hashlib.sha256(content.encode("utf-8")).hexdigest())
        # No text or digests leave this scanner.
        self.contexts.append({
            "nested": frame["nested"],
            "nearby_exact_cfs": any(s in frame["prefix"] for s in
                                    ("연결손익계산서", "연결포괄손익계산서")),
            "nearby_notes": "주석" in frame["prefix"],
            "mentions_operating_income": "영업이익" in content or "영업손실" in content,
        })
        if len(self.digests) > MAX_TABLE_COUNT:
            raise OrderGap("TABLE_SCAN_BUDGET_EXCEEDED")

    def finish(self):
        if self.frames or not self.digests or len(self.digests) != len(self.contexts):
            raise OrderGap("TABLE_NESTING_UNVERIFIED")
        return self.digests, self.contexts


def _lcs_length_bounded(original: list[str], corrected: list[str]) -> int:
    """Source-only order similarity: bounded dynamic programming, no values."""
    if len(original) * len(corrected) > 3000000:
        raise OrderGap("TABLE_ORDER_LCS_BUDGET_EXCEEDED")
    dp = [0] * (len(corrected) + 1)
    for old in original:
        diagonal = 0
        for index, value in enumerate(corrected, 1):
            old_cell = dp[index]
            if old == value:
                dp[index] = diagonal + 1
            elif dp[index-1] > dp[index]:
                dp[index] = dp[index-1]
            diagonal = old_cell
    return dp[-1]


def _non_subsequence_diagnostic(original: list[str], corrected: list[str]) -> dict:
    n, m = len(original), len(corrected)
    lcs = _lcs_length_bounded(original, corrected)
    if lcs >= n:
        raise OrderGap("ORDER_DIAGNOSTIC_INVARIANT_INVALID")
    return {
        "original_order_preserved_as_subsequence": False,
        "original_ordered_table_count": n,
        "corrected_ordered_table_count": m,
        "order_lcs_shared_table_members": lcs,
        "minimum_table_removals_for_sequence_alignment": n-lcs,
        "minimum_table_insertions_for_sequence_alignment": m-lcs,
        "additional_table_multiset_members_not_uniquely_positioned": m-n,
        "source_edition_table_positions_semantically_linked": False,
        "correction_financial_cell_changes_verified": False,
        "source_only_order_change_unresolved": True,
    }


def assess_order(original: list[str], corrected: list[str], contexts: list[dict]) -> dict:
    """An updated position is forced-new iff it cannot match ANY embedding.

    For every corrected position use greedy maximal old-prefix and old-suffix
    matching plus a bisect test of possible old source indices. This avoids the
    false conclusion that duplicated old text was definitely added.
    """
    if (not original or not corrected or len(contexts) != len(corrected)
            or len(original) > MAX_TABLE_COUNT or len(corrected) > MAX_TABLE_COUNT):
        raise OrderGap("ORDER_INPUT_CARDINALITY_INVALID")
    n, m = len(original), len(corrected)
    old_positions = defaultdict(list)
    for index, value in enumerate(original):
        old_positions[value].append(index)
    prefix, suffix = [0] * (m + 1), [0] * (m + 1)
    match = 0
    for index, value in enumerate(corrected):
        prefix[index] = match
        if match < n and value == original[match]:
            match += 1
    prefix[m] = match
    if match != n:
        return _non_subsequence_diagnostic(original, corrected)
    match = 0
    for index in range(m - 1, -1, -1):
        value = corrected[index]
        if match < n and value == original[n - 1 - match]:
            match += 1
        suffix[index] = match
    if match != n:
        raise OrderGap("ORIGINAL_TABLE_REVERSE_MATCH_INCONSISTENT")
    forced = []
    possible = []
    for index, value in enumerate(corrected):
        lowest = max(0, n - suffix[index+1] - 1)
        highest = min(n - 1, prefix[index])
        ids = old_positions.get(value, [])
        where = bisect_left(ids, lowest)
        could_be_old = lowest <= highest and where < len(ids) and ids[where] <= highest
        (possible if could_be_old else forced).append(index)
    insertion_count = m - n
    if not 0 <= len(forced) <= insertion_count or len(forced) + len(possible) != m:
        raise OrderGap("UNIQUE_INSERTION_COUNTER_INCONSISTENT")
    unique_contexts = [contexts[i] for i in forced]
    return {
        "original_order_preserved_as_subsequence": True,
        "order_lcs_shared_table_members": n,
        "minimum_table_removals_for_sequence_alignment": 0,
        "minimum_table_insertions_for_sequence_alignment": m-n,
        "source_edition_table_positions_semantically_linked": False,
        "original_ordered_table_count": n,
        "corrected_ordered_table_count": m,
        "minimum_insertions_if_subsequence": insertion_count,
        "forced_new_table_positions": len(forced),
        "insertions_not_position_uniquely_attributable": insertion_count - len(forced),
        "forced_new_nested_context_hints": sum(x["nested"] for x in unique_contexts),
        "forced_new_nearby_exact_cfs_hints": sum(x["nearby_exact_cfs"] for x in unique_contexts),
        "forced_new_nearby_notes_hints": sum(x["nearby_notes"] for x in unique_contexts),
        "forced_new_operating_income_mentions": sum(x["mentions_operating_income"]
                                                     for x in unique_contexts),
        "forced_new_table_is_authoritative_cfs_earnings": False,
        "unclassified_insertions_remain_source_gap": True,
    }


def _scan_official_document(raw: bytes, digest: str) -> tuple[list[str], list[dict]]:
    if hashlib.sha256(raw).hexdigest() != digest:
        raise OrderGap("OFFICIAL_DOCUMENT_SHA_DRIFT")
    if inspect_official_original_document(raw).get("official_original_document_zip_received") is not True:
        raise OrderGap("OFFICIAL_DOCUMENT_ZIP_UNVERIFIED")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        items = [x for x in archive.infolist()
                 if not x.is_dir() and x.filename.lower().endswith(
                     (".xml", ".htm", ".html", ".xhtml"))]
        if len(items) != 1 or items[0].file_size > 32 * 1024 * 1024:
            raise OrderGap("OFFICIAL_DOCUMENT_MEMBER_UNVERIFIED")
        decoded = _decode_disclosure_markup(archive.read(items[0]))
    scanner = _OrderedTableScanner()
    scanner.feed(decoded)
    scanner.close()
    return scanner.finish()


def compare_source_archives(first: bytes, amended: bytes) -> dict:
    original, _ = _scan_official_document(first, EXPECTED_ORIGINAL_DOCUMENT_SHA256)
    corrected, contexts = _scan_official_document(amended, CORRECTED_ZIP_SHA256)
    if (len(original) != EXPECTED_ORIGINAL_TABLES
            or len(corrected) != EXPECTED_CORRECTED_TABLES
            or sum((Counter(original) & Counter(corrected)).values()) != EXPECTED_SHARED_TABLES):
        raise OrderGap("OFFICIAL_SOURCE_TABLE_COUNTS_DRIFTED")
    return {
        **(lambda audit: {
            "source_status": (
                "OFFICIAL_SOURCE_TABLE_ORDER_DIAGNOSTIC_ONLY"
                if audit["original_order_preserved_as_subsequence"]
                else "OFFICIAL_SOURCE_TABLE_ORDER_NON_SUBSEQUENCE_DIAGNOSTIC_ONLY"
            ),
            **audit,
        })(assess_order(original, corrected, contexts)),
        "period_statement_and_financial_cells_unverified": True,
    }


def execute(session, key: str) -> dict:
    registry = _official_get(session, "corpCode.xml", {"crtfc_key": key}, zip_response=True)
    company = _registry(registry).get(COHORT[5])
    if company is None:
        raise OrderGap("FIXED_ISSUER_NOT_IN_REGISTRY")
    begin, end = _window(2022)
    original_index = _official_get(session, "list.json", {
        "crtfc_key": key, "corp_code": company, "bgn_de": begin, "end_de": end,
        "pblntf_ty": "A", "last_reprt_at": "N", "page_count": "100",
    })
    original_receipt = original_first_receipt(original_index, 2022)
    amended_index = _official_get(session, "list.json", {
        "crtfc_key": key, "corp_code": company, "bgn_de": LATER_BEGIN, "end_de": AS_OF,
        "pblntf_ty": "A", "last_reprt_at": "N", "page_no": "1", "page_count": "100",
    })
    amended_receipt = _source_pair(original_index, amended_index, original_receipt)
    return compare_source_archives(
        _fetch_first_document(session, key, original_receipt),
        _fetch_first_document(session, key, amended_receipt),
    )


def run(session=None) -> dict:
    key = os.getenv("OPENDART_API_KEY", "").strip()
    result = {
        "purpose": "FROZEN_M20_SLOT5_ORIGINAL_AMENDED_2022_Q3_TABLE_ORDER",
        "fixed_cohort_slot": 5,
        "credential_present": bool(key),
        "max_official_requests": REQUEST_LIMIT,
        "source_status": "PENDING" if key else "AUTH_NOT_CONFIGURED",
        "ordering": "DISABLED",
        **{k: False for k in SAFE_FALSE},
    }
    if not key:
        return result
    if session is None:
        import requests
        session = requests.Session()
    try:
        result.update(execute(session, key))
    except Exception as exc:
        safe = {
            "HTML_NODES_BUDGET_EXCEEDED", "TABLE_SCAN_BUDGET_EXCEEDED",
            "TABLE_INPUT_BUDGET_EXCEEDED", "TABLE_TEXT_BUDGET_EXCEEDED",
            "TABLE_NESTING_UNVERIFIED", "ORDER_INPUT_CARDINALITY_INVALID",
            "ORIGINAL_TABLE_REVERSE_MATCH_INCONSISTENT",
            "TABLE_ORDER_LCS_BUDGET_EXCEEDED",
            "ORDER_DIAGNOSTIC_INVARIANT_INVALID",
            "UNIQUE_INSERTION_COUNTER_INCONSISTENT",
            "OFFICIAL_DOCUMENT_SHA_DRIFT", "OFFICIAL_DOCUMENT_ZIP_UNVERIFIED",
            "OFFICIAL_DOCUMENT_MEMBER_UNVERIFIED",
            "OFFICIAL_SOURCE_TABLE_COUNTS_DRIFTED", "FIXED_ISSUER_NOT_IN_REGISTRY",
        }
        label = str(exc) if type(exc) is OrderGap else ""
        result["source_status"] = SOURCE_GAP
        result["failure_code"] = label if label in safe else "OFFICIAL_SOURCE_OR_LAYOUT_UNVERIFIED"
    return result


if __name__ == "__main__":
    answer = run()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(answer, indent=2, sort_keys=True), encoding="utf-8")
    print("M20_2022_SOURCE_ORDER=" + json.dumps(answer, sort_keys=True), flush=True)
