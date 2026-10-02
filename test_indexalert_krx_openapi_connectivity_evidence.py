import json
from pathlib import Path


EVIDENCE_JSON = Path("INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.json")
EVIDENCE_MD = Path("INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.md")


def _load():
    return json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))


def test_krx_openapi_evidence_is_exact_revision_and_sanitized():
    data = _load()
    assert data["schema_version"] == "1"
    assert data["evidence_id"] == "INDEXALERT-KRX-OPENAPI-CONNECTIVITY-2026-10-02-v1"
    assert data["evidence_class"] == "AUTHENTICATED_CONNECTIVITY_AND_SCHEMA_ONLY"
    assert data["production_server_commit"] == "62cb089131ca519815434616dd7f217315fbe346"
    assert data["railway_deployment_id"] == "3cc6ffb2-4f11-4582-a5ba-aeca7fb1b681"
    assert data["github_action_run_id"] == 36952309738
    assert data["github_action_job_id"] == 110667696519
    assert data["request_date"] == "20261001"
    assert data["authentication"]["route"] == "KRX_OPENAPI"
    assert data["authentication"]["header_name"] == "AUTH_KEY"
    assert data["authentication"]["secret_value_recorded"] is False


def test_exact_observed_service_schemas_are_frozen():
    data = _load()
    master = data["services"]["security_master"]
    daily = data["services"]["daily_trade"]

    assert master["endpoint"].endswith("/stk_isu_base_info")
    assert daily["endpoint"].endswith("/stk_bydd_trd")
    for row in (master, daily):
        assert row["method"] == "GET"
        assert row["http_status"] == 200
        assert row["json_parsed"] is True
        assert row["row_count"] == 942
        assert row["schema_ok"] is True

    assert set(master["fields"]) == {
        "ISU_ABBRV", "ISU_CD", "ISU_ENG_NM", "ISU_NM", "ISU_SRT_CD",
        "KIND_STKCERT_TP_NM", "LIST_DD", "LIST_SHRS", "MKT_TP_NM",
        "PARVAL", "SECT_TP_NM", "SECUGRP_NM",
    }
    assert set(daily["fields"]) == {
        "ACC_TRDVAL", "ACC_TRDVOL", "BAS_DD", "CMPPREVDD_PRC", "FLUC_RT",
        "ISU_CD", "ISU_NM", "LIST_SHRS", "MKTCAP", "MKT_NM", "SECT_TP_NM",
        "TDD_CLSPRC", "TDD_HGPRC", "TDD_LWPRC", "TDD_OPNPRC",
    }


def test_connectivity_evidence_cannot_grant_source_promotion_holdout_or_live_authority():
    data = _load()
    authority = data["authority"]
    assert authority == {
        "krx_source_contract_closed": False,
        "judge_security_status_ready": False,
        "investor_flow_feature_testing_authorized": False,
        "alpha_or_final_judge_promotion_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }

    missing = set(data["not_proven"])
    assert "trading-halt history" in missing
    assert "actual delisting history" in missing
    assert "investor-by-security flow access" in missing
    assert "record-level point-in-time availability lineage" in missing


def test_human_evidence_doc_keeps_a_f_fail_closed_boundaries():
    text = EVIDENCE_MD.read_text(encoding="utf-8")
    assert "Gate A `AUTHORIZED_OFFICIAL_ROUTE`: remains **BLOCKED**" in text
    assert "Gate B `EXACT_DATASET_SCHEMA_MAPPING`: remains **PARTIAL**" in text
    assert "Gate C `HISTORICAL_COVERAGE_SECURITY_MAPPING`: remains **BLOCKED**" in text
    assert "Gate D `PIT_AVAILABILITY_LINEAGE`: remains **BLOCKED**" in text
    assert "Gate E `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`: remains **PARTIAL**" in text
    assert "Gate F `INTENDED_USE_RIGHTS`: remains **PARTIAL**" in text
    assert "`judge_security_status_ready=false`" in text
    assert "`sealed_holdout_authorized=false`" in text
    assert "`live_trading_authorized=false`" in text
    assert "Neither observed service is investor-by-security flow" in text
