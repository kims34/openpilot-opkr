"""Machine-readable public KRX contract evidence frozen by audit date.

This file contains only facts verified from public official KRX pages. It is
source-governance metadata, not market data, Alpha evidence, legal advice or an
authorization token. It deliberately records unknown mappings as unknown rather
than inferring them from similar names or public-search absence.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


PUBLIC_EVIDENCE_VERSION = "2026-10-01.v1"
PUBLIC_EVIDENCE_AUDIT_DATE = "2026-10-01"

OPENAPI_ACCESS_MODEL = {
    "authentication_key_required": True,
    "authentication_key_admin_approval_required": True,
    "per_api_service_application_required": True,
    "per_api_service_approval_required": True,
    "auth_header_name": "AUTH_KEY",
    "auth_key_implies_all_services": False,
    "official_guide_url": "https://openapi.krx.co.kr/contents/OPP/INFO/OPPINFO003.jsp",
}

OPENAPI_TERMS = {
    "effective_date": "2025-12-26",
    "noncommercial_only": True,
    "may_charge_third_parties_for_api_results": False,
    "may_provide_krx_received_information_to_third_parties": False,
    "max_requests_per_key_per_day": 10000,
    "screen_attribution_required": True,
    "required_screen_attribution_text": "한국거래소 통계정보",
    "may_continue_using_received_information_after_contract_end": False,
    "official_terms_url": "https://openapi.krx.co.kr/contents/OPP/INFO/OPPINFO002.jsp",
}

OPENAPI_MISSING_DATA_NOTICE = {
    "title": "KRX Open API 미제공 데이터에 대한 안내",
    "listed_on_public_homepage": True,
    "notice_month": "2026-06",
    "dataset_list_reliably_retrieved_in_audit": False,
    "inference_rule": (
        "The notice proves only that Data Marketplace and OpenAPI coverage must not be assumed equivalent. "
        "It does not prove availability or non-availability of a specific IndexAlert-required dataset."
    ),
    "official_home_url": "https://openapi.krx.co.kr/contents/OPP/MAIN/main/index.cmd",
}

PUBLIC_SCREEN_CONTRACTS = {
    "MDCSTAT237": {
        "name": "정리매매종목 현황",
        "fields_verified": [
            "종목코드",
            "종목명",
            "시장구분",
            "증권구분",
            "정리매매기간_시작일",
            "정리매매기간_종료일",
            "상장폐지예정일",
            "상장폐지사유",
        ],
        "current_price_context": "same-day regular-session context when displayed",
        "official_url": "https://data.krx.co.kr/contents/MDC/STAT/issue/MDCSTAT237.jsp",
    },
    "MDCSTAT238": {
        "name": "상장폐지종목 현황",
        "fields_verified": [
            "종목코드",
            "종목명",
            "시장구분",
            "증권구분",
            "주식종류",
            "상장일",
            "폐지일",
            "폐지사유",
        ],
        "event_semantics": "information is based on the last trading day immediately before delisting",
        "official_url": "https://data.krx.co.kr/contents/MDC/STAT/issue/MDCSTAT238.jsp",
    },
    "MDCSTAT239": {
        "name": "상장폐지종목 시세 추이",
        "fields_verified": [
            "일자",
            "종목코드",
            "종목명",
            "시장구분",
            "증권구분",
            "종가",
            "대비",
            "등락률",
            "시가",
            "고가",
            "저가",
            "거래량",
            "거래대금",
            "시가총액",
        ],
        "price_session": "regular session 09:00-15:30",
        "official_url": "https://data.krx.co.kr/contents/MDC/STAT/issue/MDCSTAT239.jsp",
    },
    "STOCK_INVESTOR_TRADING": {
        "name": "투자자별 거래실적 / 투자자별 거래실적(개별종목)",
        "per_security_screen_publicly_listed": True,
        "same_day_final_results_available_after": "20:00 Asia/Seoul",
        "decision_eligibility_rule": "day-D final results may enter only a later eligible decision after publication",
        "official_market_page_url": "https://data.krx.co.kr/contents/MDC/MDI/outerLoader/index.cmd?screenId=MDCSTAT022",
    },
}

EXACT_MAPPING_STATE = {
    "security_status_complete_public_openapi_mapping_established": False,
    "investor_flow_per_security_public_openapi_mapping_established": False,
    "mdcstat213_low_level_transport_promoted_to_exact_contract": False,
    "mdcstat237_low_level_transport_promoted_to_exact_contract": False,
    "public_search_absence_is_nonavailability_evidence": False,
}


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def public_evidence_manifest() -> dict[str, Any]:
    manifest = {
        "version": PUBLIC_EVIDENCE_VERSION,
        "audit_date": PUBLIC_EVIDENCE_AUDIT_DATE,
        "openapi_access_model": OPENAPI_ACCESS_MODEL,
        "openapi_terms": OPENAPI_TERMS,
        "openapi_missing_data_notice": OPENAPI_MISSING_DATA_NOTICE,
        "public_screen_contracts": PUBLIC_SCREEN_CONTRACTS,
        "exact_mapping_state": EXACT_MAPPING_STATE,
        "promotion_boundary": {
            "source_evidence_only": True,
            "alpha_promotion_authorized": False,
            "sealed_holdout_authorized": False,
            "live_trading_authorized": False,
        },
    }
    return manifest


def public_evidence_fingerprint_sha256() -> str:
    return _canonical_sha256(public_evidence_manifest())
