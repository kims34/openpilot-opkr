from research_v1_krx_public_evidence import (
    PUBLIC_EVIDENCE_AUDIT_DATE,
    PUBLIC_EVIDENCE_VERSION,
    EXACT_MAPPING_STATE,
    OPENAPI_ACCESS_MODEL,
    OPENAPI_MISSING_DATA_NOTICE,
    OPENAPI_PUBLIC_SERVICE_CATALOG,
    OPENAPI_TERMS,
    PUBLIC_SCREEN_CONTRACTS,
    public_evidence_fingerprint_sha256,
    public_evidence_manifest,
)


def test_openapi_access_model_keeps_key_and_service_approval_separate():
    assert OPENAPI_ACCESS_MODEL["authentication_key_required"] is True
    assert OPENAPI_ACCESS_MODEL["authentication_key_admin_approval_required"] is True
    assert OPENAPI_ACCESS_MODEL["per_api_service_application_required"] is True
    assert OPENAPI_ACCESS_MODEL["per_api_service_approval_required"] is True
    assert OPENAPI_ACCESS_MODEL["auth_key_implies_all_services"] is False
    assert OPENAPI_ACCESS_MODEL["auth_header_name"] == "AUTH_KEY"


def test_current_openapi_terms_do_not_authorize_commercial_redistribution():
    assert OPENAPI_TERMS["effective_date"] == "2025-12-26"
    assert OPENAPI_TERMS["noncommercial_only"] is True
    assert OPENAPI_TERMS["may_charge_third_parties_for_api_results"] is False
    assert OPENAPI_TERMS["may_provide_krx_received_information_to_third_parties"] is False
    assert OPENAPI_TERMS["max_requests_per_key_per_day"] == 10000
    assert OPENAPI_TERMS["screen_attribution_required"] is True
    assert OPENAPI_TERMS["may_continue_using_received_information_after_contract_end"] is False


def test_missing_data_notice_does_not_identify_specific_dataset_availability():
    assert OPENAPI_MISSING_DATA_NOTICE["listed_on_public_homepage"] is True
    assert OPENAPI_MISSING_DATA_NOTICE["dataset_list_reliably_retrieved_in_audit"] is False


def test_status_screen_contracts_preserve_verified_economic_semantics():
    assert "정리매매기간_시작일" in PUBLIC_SCREEN_CONTRACTS["MDCSTAT237"]["fields_verified"]
    assert "주식종류" in PUBLIC_SCREEN_CONTRACTS["MDCSTAT238"]["fields_verified"]
    assert "폐지일" in PUBLIC_SCREEN_CONTRACTS["MDCSTAT238"]["fields_verified"]
    assert PUBLIC_SCREEN_CONTRACTS["MDCSTAT239"]["price_session"] == "regular session 09:00-15:30"


def test_investor_publication_rule_is_next_decision_only():
    investor = PUBLIC_SCREEN_CONTRACTS["STOCK_INVESTOR_TRADING"]
    assert investor["per_security_screen_publicly_listed"] is True
    assert investor["same_day_final_results_available_after"] == "20:00 Asia/Seoul"
    assert "later eligible decision" in investor["decision_eligibility_rule"]


def test_unknown_exact_mappings_remain_false_and_manifest_has_no_promotion_power():
    assert all(value is False for value in EXACT_MAPPING_STATE.values())
    manifest = public_evidence_manifest()
    assert manifest["promotion_boundary"]["source_evidence_only"] is True
    assert manifest["promotion_boundary"]["alpha_promotion_authorized"] is False
    assert manifest["promotion_boundary"]["sealed_holdout_authorized"] is False
    assert manifest["promotion_boundary"]["live_trading_authorized"] is False
    assert len(public_evidence_fingerprint_sha256()) == 64


def test_current_public_openapi_catalog_does_not_list_required_status_or_investor_services():
    catalog = OPENAPI_PUBLIC_SERVICE_CATALOG
    assert catalog["audit_date"] == "2026-10-02"
    assert catalog["data_target_period_note"] == "2010년 이후 데이터"
    assert "유가증권 일별매매정보" in catalog["public_stock_service_names"]
    assert "유가증권 종목기본정보" in catalog["public_stock_service_names"]
    assert catalog["status_or_delisting_service_publicly_listed"] is False
    assert catalog["investor_flow_service_publicly_listed"] is False
    assert {"거래정지", "정리매매", "상장폐지", "투자자"}.issubset(
        set(catalog["catalog_search_terms_not_present"])
    )
    assert "must not be upgraded into proof" in catalog["inference_rule"]


def test_trading_halt_public_screen_contract_is_frozen_without_openapi_inference():
    halt = PUBLIC_SCREEN_CONTRACTS["MDCSTAT213"]
    assert halt["name"] == "매매거래정지 내역(개별종목)"
    assert {"종목코드", "정지일", "재개일"}.issubset(set(halt["fields_verified"]))
    assert "immediately before suspension" in halt["price_context"]


def test_public_evidence_version_and_fingerprint_are_frozen():
    assert PUBLIC_EVIDENCE_VERSION == "2026-10-02.v2"
    assert PUBLIC_EVIDENCE_AUDIT_DATE == "2026-10-02"
    assert public_evidence_fingerprint_sha256() == (
        "39f357fda6eec5bb994f1dcba1ba44ed913714df256ec6b542b5aeadf14a0380"
    )
