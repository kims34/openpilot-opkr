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
    _require(data.get("schema_version") == "2", "unsupported schema_version")
    _require(
        data.get("evidence_class")
        == "USER_PROVIDED_KRX_EMAIL_REPLY_AUTOMATION_EXPLICIT_OFFICIAL_DOMAIN_ATTESTED",
        "unexpected evidence_class",
    )
    for key in ("original_screenshot_sha256", "redacted_email_record_sha256"):
        _require(bool(SHA256_RE.fullmatch(str(data.get(key) or ""))), f"{key} invalid")
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
        "personal_user",
        "noncommercial_internal_research",
        "low_frequency_querying",
        "programmatic_querying",
        "automated_querying",
        "use_available_without_stated_limit_within_visible_scope",
    ):
        _require(scope.get(key) is True, f"{key} must remain true")
    _require(scope.get("separate_approval_procedure_required") is False, "separate approval wording drift")

    limits = data.get("not_authorized_or_not_proven") or {}
    for key in (
        "bulk_or_high_frequency_collection",
        "unrestricted_full_historical_download",
        "redistribution",
        "commercial_use",
        "exact_bld_schema_equivalence",
        "full_history_coverage",
        "pit_lineage",
    ):
        _require(limits.get(key) is True, f"{key} limit weakened")

    cls = data.get("project_classification") or {}
    _require(cls.get("issuer_domain_matches_official_krx_domain") is True, "official-domain match lost")
    _require(cls.get("issuer_metadata_user_attested") is True, "user-attested origin lost")
    _require(cls.get("issuer_independently_verified") is False, "origin must not be overstated")
    _require(cls.get("automated_collection_authorized") is True, "explicit automation permission lost")
    _require(cls.get("permission_state") == "PERMITTED_NO_SEPARATE_APPROVAL", "permission-state drift")
    _require(cls.get("sufficient_for_data_marketplace_tiny_probe_preflight") is True, "tiny-probe evidence readiness lost")
    _require(cls.get("gate_a_status_ceiling_before_authenticated_probe") == "BLOCKED", "pre-probe Gate A drift")
    _require(cls.get("gate_a_status_ceiling_after_successful_tiny_probe") == "PARTIAL", "post-probe Gate A ceiling drift")
    _require(cls.get("gate_f_evidence_strengthened") is True, "Gate F strengthening lost")
    for key in (
        "bulk_historical_acquisition_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(cls.get(key) is False, f"{key} illegally true")

    return {
        "valid": True,
        "automated_collection_authorized": True,
        "permission_state": "PERMITTED_NO_SEPARATE_APPROVAL",
        "sufficient_for_data_marketplace_tiny_probe_preflight": True,
        "gate_a_status_ceiling_before_authenticated_probe": "BLOCKED",
        "gate_a_status_ceiling_after_successful_tiny_probe": "PARTIAL",
        "gate_f_evidence_strengthened": True,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_permission_reply_evidence(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
