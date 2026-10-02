"""Fail-closed validator for user-provided KRX permission-reply evidence."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping


PATH = Path("INDEXALERT_KRX_PERMISSION_REPLY_EVIDENCE.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class KRXPermissionReplyEvidenceError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXPermissionReplyEvidenceError(msg)


def validate_permission_reply_evidence(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "evidence must be an object")
    _require(data.get("schema_version") == "3", "unsupported schema_version")
    _require(
        data.get("evidence_class")
        == "USER_PROVIDED_KRX_EMAIL_REPLY_FULL_HISTORY_HIGH_FREQUENCY_EXPLICIT_OFFICIAL_DOMAIN_ATTESTED",
        "unexpected evidence_class",
    )
    for key in ("original_screenshot_sha256", "latest_redacted_email_record_sha256"):
        _require(bool(SHA256_RE.fullmatch(str(data.get(key) or ""))), f"{key} invalid")
    _require(
        data.get("latest_redacted_email_record_sha256")
        == "3fa82170250320e4b406ae343e6a5872ca4945119cd4df4c17115754ddc301c1",
        "latest normalized email-record hash drift",
    )
    _require(data.get("image_stored_in_repository") is False, "image must not be stored in repository")

    meta = data.get("email_metadata") or {}
    _require(meta.get("subject") == "[KRX Data Marketplace] 데이터 이용 문의에 대한 답변의 건", "subject drift")
    _require(meta.get("sender_address") == "krxdata@krx.co.kr", "sender address drift")
    _require(meta.get("sender_domain") == "krx.co.kr", "sender domain drift")
    _require(meta.get("reply_at") == "2026-10-02T14:40:00+09:00", "reply timestamp drift")
    _require(meta.get("recipient_redacted") is True, "recipient must stay redacted")
    _require(meta.get("metadata_source") == "USER_PROVIDED_EMAIL_HEADER_TEXT", "metadata-source drift")

    scope = data.get("supported_scope") or {}
    for key in (
        "personal_research",
        "noncommercial_use",
        "full_historical_period_download",
        "complete_historical_data_download_and_query",
        "programmatic_querying",
        "automated_querying",
        "low_frequency_collection",
        "high_frequency_collection",
    ):
        _require(scope.get(key) is True, f"{key} must remain true")
    _require(scope.get("separate_prior_approval_required") is False, "approval wording drift")

    prohibited = data.get("prohibited_scope") or {}
    for key in ("external_leakage", "external_sale", "third_party_distribution"):
        _require(prohibited.get(key) is True, f"{key} prohibition weakened")

    unproven = data.get("still_not_proven_by_permission_text") or {}
    for key in (
        "exact_bld_schema_equivalence",
        "actual_source_availability_for_every_required_date",
        "stable_security_mapping_across_all_history",
        "record_level_pit_lineage",
        "completeness_of_status_economics",
        "model_performance_validity",
    ):
        _require(unproven.get(key) is True, f"{key} evidence boundary weakened")

    cls = data.get("project_classification") or {}
    _require(cls.get("issuer_domain_matches_official_krx_domain") is True, "official-domain match lost")
    _require(cls.get("issuer_metadata_user_attested") is True, "user-attested origin lost")
    _require(cls.get("issuer_independently_verified") is False, "origin must not be overstated")
    _require(cls.get("automated_collection_authorized") is True, "automation permission lost")
    _require(cls.get("high_frequency_collection_authorized") is True, "high-frequency permission lost")
    _require(cls.get("full_historical_download_rights_authorized") is True, "full-history permission lost")
    _require(cls.get("permission_state") == "PERMITTED_NO_SEPARATE_APPROVAL", "permission-state drift")
    _require(cls.get("gate_f_status_for_personal_research") == "PASS", "Gate F scope status drift")
    _require(cls.get("gate_a_status_ceiling_from_permission_alone") == "PARTIAL", "Gate A ceiling drift")
    _require(cls.get("bulk_historical_acquisition_rights_authorized") is True, "historical acquisition rights lost")
    _require(cls.get("bulk_historical_network_execution_authorized_by_user") is False, "bulk network execution illegally pre-authorized")
    for key in (
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(cls.get(key) is False, f"{key} illegally true")

    return {
        "valid": True,
        "automated_collection_authorized": True,
        "high_frequency_collection_authorized": True,
        "full_historical_download_rights_authorized": True,
        "bulk_historical_acquisition_rights_authorized": True,
        "bulk_historical_network_execution_authorized_by_user": False,
        "permission_state": "PERMITTED_NO_SEPARATE_APPROVAL",
        "gate_f_status_for_personal_research": "PASS",
        "gate_a_status_ceiling_from_permission_alone": "PARTIAL",
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_permission_reply_evidence(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
