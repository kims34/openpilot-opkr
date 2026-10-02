"""Fail-closed validator for the official KRX Data Marketplace terms constraint."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


PATH = Path("INDEXALERT_KRX_DATA_MARKETPLACE_TERMS_AUDIT.json")


class KRXTermsAuditError(ValueError):
    pass


def _require(cond: bool, message: str) -> None:
    if not cond:
        raise KRXTermsAuditError(message)


def validate_terms_audit(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "terms audit must be an object")
    _require(data.get("schema_version") == "1", "unsupported schema_version")
    _require(
        data.get("evidence_class") == "OFFICIAL_KRX_TERMS_CONSTRAINT",
        "unexpected evidence_class",
    )
    _require(
        data.get("official_url")
        == "https://data.krx.co.kr/contents/MDC/INFO/informationController/MDCINFO003.cmd",
        "official terms URL drift",
    )
    _require(data.get("terms_effective_date") == "2026-08-29", "terms effective date drift")

    clauses = data.get("clauses") or {}
    required_true = {
        "membership_contract_requires_signup_and_terms_agreement",
        "ordinary_service_includes_data_lookup_search_guidance",
        "unauthorized_automated_collection_reproduction_distribution_prohibited",
        "copying_reproduction_distribution_transmission_public_transmission_without_prior_krx_permission_prohibited",
        "purchased_market_data_subject_to_separate_terms",
    }
    _require(required_true.issubset(set(clauses)), "required terms clauses missing")
    for key in required_true:
        _require(clauses.get(key) is True, f"{key} must remain true")

    interp = data.get("project_interpretation") or {}
    for key in (
        "account_credentials_are_not_automation_permission",
        "authenticated_web_session_probe_requires_explicit_krx_automation_permission",
        "absence_of_permission_keeps_request_authorized_false",
        "openapi_route_is_separate",
        "purchased_or_distributed_product_route_is_separate",
    ):
        _require(interp.get(key) is True, f"{key} must remain true")

    authority = data.get("authority") or {}
    for key in (
        "data_marketplace_authenticated_probe_authorized",
        "bulk_historical_acquisition_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(authority.get(key) is False, f"{key} illegally true")

    return {
        "valid": True,
        "data_marketplace_authenticated_probe_authorized": False,
        "bulk_historical_acquisition_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_terms_audit(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
