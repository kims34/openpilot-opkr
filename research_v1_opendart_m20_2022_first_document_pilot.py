"""Fixed-slot M20 *first-filed 2022 Q3 original document* availability probe.

Why: the prior official first-filing financial-XBRL route for fixed slot 5
returned OpenDART 014. The separately documented official "document.xml"
endpoint may provide the exact SAME originally filed report document ZIP.
This probe checks only source existence/integrity; it does not assume a
document HTML/XML table equals a standardized original XBRL Q3 CFS fact.

One frozen issuer/filing and at most THREE official OpenDART calls:
corpCode.xml, list.json, document.xml. No altered original edition, fallback
year, later revision, numerical earnings, KRX/market/broker data, training,
holdout or permission changes. No receipt, corp code, original content,
filing date, amounts, credentials, or provider message is persisted/logged.
"""
from __future__ import annotations

import argparse
import io
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import stat
import unicodedata
import zipfile

from defusedxml.ElementTree import fromstring
from defusedxml.common import DefusedXmlException
from xml.etree.ElementTree import ParseError

from research_v1_opendart_lineage_pilot import BASE, _official_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import (
    COHORT, _registry, _window,
)
from research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import (
    original_first_receipt,
)

FROZEN_SLOT = 5
ORIGINAL_YEAR = 2022
MAX_OFFICIAL_CALLS = 3
MAX_ARCHIVE_BYTES = 32 * 1024 * 1024
MAX_FILES = 120
MAX_EXPANDED_BYTES = 80 * 1024 * 1024
MAX_ONE_FILE_BYTES = 32 * 1024 * 1024
MAX_ERROR_XML_BYTES = 4096
RECEIPT = re.compile(r"[0-9]{14}\Z")
OUTPUT = Path("research_results/opendart_m20_first_2022_document/summary.json")
DOCUMENT_ERROR_CODES = {
    "010": "DOCUMENT_KEY_UNREGISTERED",
    "011": "DOCUMENT_KEY_DISABLED",
    "012": "DOCUMENT_IP_FORBIDDEN",
    "013": "DOCUMENT_NO_DATA",
    "014": "DOCUMENT_FILE_NOT_FOUND",
    "020": "DOCUMENT_REQUEST_LIMIT",
    "100": "DOCUMENT_BAD_REQUEST",
    "101": "DOCUMENT_ACCESS_FORBIDDEN",
    "800": "DOCUMENT_PROVIDER_MAINTENANCE",
    "900": "DOCUMENT_PROVIDER_ERROR",
    "901": "DOCUMENT_ACCOUNT_EXPIRED",
}
SAFETY = {
    "fixed_slot_unchanged": True,
    "original_edition_only": True,
    "archive_is_standardized_financial_xbrl": False,
    "original_2022_standalone_cfs_earnings_value_verified": False,
    "original_statement_binding_verified": False,
    "original_q3_vs_prior_year_comparability_verified": False,
    "historical_security_corp_mapping_verified": False,
    "historical_publication_instant_pit_verified": False,
    "historical_correction_lineage_complete": False,
    "historical_market_cap_and_tradability_verified": False,
    "complete_universe_original_filing_panel_verified": False,
    "m20_feature_pit_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "source_bytes_financial_values_and_identifiers_saved": False,
    "ordering": "DISABLED",
}


class OriginalDocumentGap(ValueError):
    """Known fixed reason codes; never expose provider payloads."""


def inspect_official_original_document(source: bytes) -> dict:
    if type(source) is not bytes or not 4 <= len(source) <= MAX_ARCHIVE_BYTES:
        raise OriginalDocumentGap("DOCUMENT_RESPONSE_BYTES_INVALID")
    if source[:4] != bytes((80, 75, 3, 4)):
        if not 8 <= len(source) <= MAX_ERROR_XML_BYTES:
            raise OriginalDocumentGap("DOCUMENT_RESPONSE_NOT_VERIFIABLE_ZIP")
        try:
            root = fromstring(source, forbid_dtd=True, forbid_entities=True,
                              forbid_external=True)
        except (DefusedXmlException, ParseError, ValueError):
            raise OriginalDocumentGap("DOCUMENT_RESPONSE_NOT_VERIFIABLE_ZIP") from None
        if root.tag != "result" or len(root) > 4:
            raise OriginalDocumentGap("DOCUMENT_RESPONSE_NOT_VERIFIABLE_ZIP")
        statuses = [child.text for child in root if child.tag == "status"
                    and len(child) == 0]
        if len(statuses) != 1 or statuses[0] not in DOCUMENT_ERROR_CODES:
            raise OriginalDocumentGap("DOCUMENT_RESPONSE_NOT_VERIFIABLE_ZIP")
        raise OriginalDocumentGap(DOCUMENT_ERROR_CODES[statuses[0]])

    try:
        with zipfile.ZipFile(io.BytesIO(source)) as z:
            entries = z.infolist()
            files = [e for e in entries if not e.is_dir()]
            if not files or len(files) > MAX_FILES or len(entries) != len(files):
                raise OriginalDocumentGap("DOCUMENT_ARCHIVE_FILE_COUNT_INVALID")
            if sum(e.file_size for e in files) > MAX_EXPANDED_BYTES:
                raise OriginalDocumentGap("DOCUMENT_ARCHIVE_EXPANSION_LIMIT")
            names = set()
            count = 0
            for e in files:
                name = e.filename.replace("\\", "/")
                parts = name.split("/")
                if (name.startswith("/") or any(t in ("", ".", "..") for t in parts)
                        or name.casefold() in names or e.flag_bits & 1
                        or e.file_size <= 0 or e.file_size > MAX_ONE_FILE_BYTES
                        or stat.S_IFMT(e.external_attr >> 16) not in (0, stat.S_IFREG)):
                    raise OriginalDocumentGap("DOCUMENT_ARCHIVE_ENTRY_UNSAFE")
                names.add(name.casefold())
                if name.lower().endswith((".xml", ".htm", ".html", ".xhtml")):
                    count += 1
                size = 0
                with z.open(e) as f:
                    while True:
                        block = f.read(65536)
                        if not block:
                            break
                        size += len(block)
                        if size > e.file_size or size > MAX_ONE_FILE_BYTES:
                            raise OriginalDocumentGap("DOCUMENT_ARCHIVE_ENTRY_UNSAFE")
                if size != e.file_size:
                    raise OriginalDocumentGap("DOCUMENT_ARCHIVE_ENTRY_UNSAFE")
            if count == 0:
                raise OriginalDocumentGap("DOCUMENT_STRUCTURED_SOURCE_ABSENT")
            return {
                "official_original_document_zip_received": True,
                "original_document_file_count": len(files),
                "structured_document_entry_count": count,
                "zip_crc_and_bounded_read_completed": True,
                "original_document_financial_semantics_validated": False,
            }
    except (zipfile.BadZipFile, RuntimeError, EOFError, UnicodeError, OSError):
        raise OriginalDocumentGap("DOCUMENT_ZIP_INTEGRITY_INVALID") from None



LAYOUT_MAX_NODES = 500_000
LAYOUT_MAX_TEXT_CHARS = 36 * 1024 * 1024



class _BoundedDisclosureHTML(HTMLParser):
    """HTML/SGML layout flags only. Never extract financial observations."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.chars = 0
        self.nodes = 0
        self.in_cell = 0
        self.table_found = False
        self.profit_cell = False

    def handle_starttag(self, tag, attrs):
        self.nodes += 1
        if self.nodes > LAYOUT_MAX_NODES:
            raise OriginalDocumentGap("DOCUMENT_LAYOUT_NODES_LIMIT")
        if tag in ("table", "tr", "td", "th"):
            self.table_found = True
        if tag in ("td", "th"):
            self.in_cell += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag in ("td", "th"):
            self.in_cell = max(0, self.in_cell - 1)

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self.in_cell = max(0, self.in_cell - 1)

    def handle_data(self, data):
        self.chars += len(data)
        if self.chars > LAYOUT_MAX_TEXT_CHARS:
            raise OriginalDocumentGap("DOCUMENT_LAYOUT_TEXT_LIMIT")
        self.parts.append(data)
        if self.in_cell and any(
            token in unicodedata.normalize("NFKC", data).replace(" ", "")
            for token in ("영업이익", "영업손실")
        ):
            self.profit_cell = True


def _decode_disclosure_markup(raw: bytes) -> str:
    """Decode bytes for a *layout-only* fallback; never substitute in factual data."""
    header = raw[:2048].lower()
    if b"<!entity" in header or re.search(rb"<!\s*entity\b", raw, re.I):
        raise OriginalDocumentGap("DOCUMENT_LAYOUT_ENTITY_DECLARATION")
    encodings = ("utf-8-sig", "cp949") if (
        b"euc-kr" not in header and b"cp949" not in header
    ) else ("cp949", "utf-8-sig")
    for enc in encodings:
        try:
            return raw.decode(enc, errors="strict")
        except UnicodeError:
            pass
    raise OriginalDocumentGap("DOCUMENT_LAYOUT_TEXT_ENCODING_INVALID")


def inspect_original_document_layout(source: bytes) -> dict:
    """Coarse XML layout flags only, NOT a bindable Q3 CFS financial fact.

    Financial terms may occur in footnotes or narrative; no actual amount,
    period, current/prior value, share identity, or PIT validity is asserted.
    Entire original ZIP is CRC and bounded-read verified first.
    """
    checked = inspect_official_original_document(source)
    contents = []
    parsed = 0
    nodes = 0
    table_tag = False
    profit_cell = False
    non_xml_count = 0
    try:
        with zipfile.ZipFile(io.BytesIO(source)) as archive:
            for entry in archive.infolist():
                if not entry.filename.lower().endswith((".xml", ".htm", ".html", ".xhtml")):
                    continue
                raw = archive.read(entry)
                try:
                    root = fromstring(raw, forbid_dtd=False,
                                      forbid_entities=True, forbid_external=True)
                except (DefusedXmlException, ParseError, ValueError, UnicodeError):
                    # DART document.xml ZIP entries may contain legacy SGML/
                    # HTML, which is not well-formed XBRL/XML. This alternate
                    # path is strictly a non-binding layout diagnostic.
                    # Never interpret its text/cells as financial facts.
                    text = _decode_disclosure_markup(raw)
                    if not any(mark in text.lower() for mark in
                               ("<html", "<table", "<tr", "<td", "<th", "<body", "<p")):
                        raise OriginalDocumentGap("DOCUMENT_LAYOUT_XML_UNSAFE")
                    try:
                        scanner = _BoundedDisclosureHTML()
                        scanner.feed(text)
                        scanner.close()
                    except (ValueError, AssertionError, UnicodeError) as ex:
                        if isinstance(ex, OriginalDocumentGap):
                            raise
                        raise OriginalDocumentGap("DOCUMENT_LAYOUT_HTML_UNSAFE") from None
                    parsed += 1
                    non_xml_count += 1
                    nodes += scanner.nodes
                    if nodes > LAYOUT_MAX_NODES:
                        raise OriginalDocumentGap("DOCUMENT_LAYOUT_NODES_LIMIT")
                    contents.extend(scanner.parts)
                    table_tag |= scanner.table_found
                    profit_cell |= scanner.profit_cell
                    continue
                parsed += 1
                for node in root.iter():
                    nodes += 1
                    if nodes > LAYOUT_MAX_NODES:
                        raise OriginalDocumentGap("DOCUMENT_LAYOUT_NODES_LIMIT")
                    tag = node.tag.rsplit("}", 1)[-1].upper() if type(node.tag) is str else ""
                    if tag in ("TABLE", "TR", "TD", "TH"):
                        table_tag = True
                    if node.text:
                        contents.append(node.text)
                        if tag in ("TD", "TH"):
                            cell = unicodedata.normalize("NFKC", node.text)
                            if any(word in cell.replace(" ", "") for word in ("영업이익", "영업손실")):
                                profit_cell = True
    except (zipfile.BadZipFile, RuntimeError, EOFError, OSError, UnicodeError):
        raise OriginalDocumentGap("DOCUMENT_LAYOUT_ZIP_UNREADABLE") from None
    if parsed == 0:
        raise OriginalDocumentGap("DOCUMENT_LAYOUT_XML_ABSENT")
    if sum(map(len, contents)) > LAYOUT_MAX_TEXT_CHARS:
        raise OriginalDocumentGap("DOCUMENT_LAYOUT_TEXT_LIMIT")
    text = re.sub(r"\s+", "", unicodedata.normalize("NFKC", "".join(contents)))
    return {
        **checked,
        "structured_markup_entries_inspected": parsed,
        "non_xml_sgml_html_layout_entries": non_xml_count,
        "safely_parsed_strict_xml_count": parsed - non_xml_count,
        "document_contains_table_tags": table_tag,
        "document_contains_consolidated_term": any(w in text for w in
            ("연결재무제표", "연결포괄손익계산서", "연결손익계산서")),
        "document_contains_income_statement_term": any(w in text for w in
            ("손익계산서", "포괄손익계산서")),
        "document_contains_operating_profit_term": any(w in text for w in
            ("영업이익", "영업손실")),
        "document_contains_operating_profit_cell_text": profit_cell,
        "original_q3_cfs_three_month_profit_bound": False,
        "raw_source_text_or_financial_values_persisted": False,
        "original_document_financial_semantics_validated": False,
    }


def _fetch_first_document(session, key: str, receipt: str) -> bytes:
    if type(receipt) is not str or not RECEIPT.fullmatch(receipt):
        raise OriginalDocumentGap("DOCUMENT_RECEIPT_INVALID")
    try:
        response = session.get(
            BASE + "document.xml",
            params={"crtfc_key": key, "rcept_no": receipt},
            timeout=35, allow_redirects=False, stream=True,
        )
    except Exception:
        raise OriginalDocumentGap("DOCUMENT_NETWORK_ERROR") from None
    try:
        if response.status_code != 200:
            raise OriginalDocumentGap("DOCUMENT_HTTP_FAILURE")
        chunks = bytearray()
        for chunk in response.iter_content(chunk_size=65536):
            chunks.extend(chunk)
            if len(chunks) > MAX_ARCHIVE_BYTES:
                raise OriginalDocumentGap("DOCUMENT_RESPONSE_BYTES_INVALID")
        return bytes(chunks)
    except OriginalDocumentGap:
        raise
    except Exception:
        raise OriginalDocumentGap("DOCUMENT_NETWORK_ERROR") from None
    finally:
        response.close()


def run(session=None) -> dict:
    key = os.getenv("OPENDART_API_KEY", "").strip()
    result = {
        "purpose": "FROZEN_M20_SLOT5_FIRST_SUBMITTED_2022_Q3_DOCUMENT_SOURCE_PILOT",
        "source_status": "PENDING" if key else "AUTH_NOT_CONFIGURED",
        "credential_present": bool(key),
        "fixed_cohort_slot": FROZEN_SLOT,
        "original_report_year": ORIGINAL_YEAR,
        "max_official_requests": MAX_OFFICIAL_CALLS,
        "official_original_document_zip_received": False,
        **SAFETY,
    }
    if not key:
        return result
    if session is None:
        import requests
        session = requests.Session()
    stage = "OFFICIAL_CORP_REGISTRY"
    try:
        registry = _official_get(session, "corpCode.xml",
                                 {"crtfc_key": key}, zip_response=True)
        corp = _registry(registry).get(COHORT[FROZEN_SLOT])
        if corp is None:
            raise OriginalDocumentGap("FROZEN_CORP_MAPPING_ABSENT")
        stage = "ORIGINAL_2022_Q3_FILING_INDEX"
        start, end = _window(ORIGINAL_YEAR)
        listing = _official_get(session, "list.json", {
            "crtfc_key": key, "corp_code": corp,
            "bgn_de": start, "end_de": end,
            "pblntf_ty": "A", "page_count": "100",
        })
        receipt = original_first_receipt(listing, ORIGINAL_YEAR)
        stage = "EXACT_FIRST_SUBMITTED_2022_DOCUMENT_ZIP"
        source = _fetch_first_document(session, key, receipt)
        # A layout/DTD parse failure must not hide already verified ZIP receipt.
        result.update(inspect_official_original_document(source))
        result.update(inspect_original_document_layout(source))
        result["source_status"] = "ORIGINAL_2022_DOCUMENT_LAYOUT_DIAGNOSTIC_ONLY"
    except Exception as ex:
        result["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        result["failure_stage"] = stage
        allowed = {
            "DOCUMENT_RESPONSE_BYTES_INVALID",
            "DOCUMENT_RESPONSE_NOT_VERIFIABLE_ZIP",
            "DOCUMENT_LAYOUT_XML_UNSAFE", "DOCUMENT_LAYOUT_HTML_UNSAFE",
            "DOCUMENT_LAYOUT_ENTITY_DECLARATION", "DOCUMENT_LAYOUT_TEXT_ENCODING_INVALID",
            "DOCUMENT_LAYOUT_NODES_LIMIT",
            "DOCUMENT_LAYOUT_ZIP_UNREADABLE", "DOCUMENT_LAYOUT_XML_ABSENT",
            "DOCUMENT_LAYOUT_TEXT_LIMIT",
            "DOCUMENT_ARCHIVE_FILE_COUNT_INVALID",
            "DOCUMENT_ARCHIVE_EXPANSION_LIMIT",
            "DOCUMENT_ARCHIVE_ENTRY_UNSAFE",
            "DOCUMENT_STRUCTURED_SOURCE_ABSENT",
            "DOCUMENT_ZIP_INTEGRITY_INVALID",
            "DOCUMENT_RECEIPT_INVALID",
            "DOCUMENT_NETWORK_ERROR",
            "DOCUMENT_HTTP_FAILURE",
            "FROZEN_CORP_MAPPING_ABSENT",
            *DOCUMENT_ERROR_CODES.values(),
        }
        reason = str(ex) if type(ex) is OriginalDocumentGap else ""
        result["failure_code"] = reason if reason in allowed else "UNCLASSIFIED"
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--fixed-slot", type=int, required=True, choices=[FROZEN_SLOT])
    a = p.parse_args()
    r = run()
    if a.fixed_slot != FROZEN_SLOT:
        raise SystemExit("FROZEN_SLOT_MISMATCH")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(r, sort_keys=True, indent=2), encoding="utf-8")
    print("OPENDART_M20_ORIGINAL_DOCUMENT_2022=" + json.dumps(r, sort_keys=True))
