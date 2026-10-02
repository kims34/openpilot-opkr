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
    _require(data.get("schema_version") == "1", "unsupported schema_version")
    _require(
        data.get("evidence_class")
        == "USER_PROVIDED_KRX_REPLY_SCREENSHOT_SCOPE_EVIDENCE_AUTOMATION_AMBIGUOUS",
        "unexpected evidence_class",
    )
    _require(bool(SHA256_RE.fullmatch(str(data.get("image_sha256") or ""))), "image_sha256 invalid")
    _require(data.get("image_stored_in_repository") is False, "image must not be stored in repository")
    _require(data.get("visible_sender_identity") is False, "sender visibility must remain false for this record")
    _require(data.get("visible_original_question") is False, "original-question visibility must remain false for this record")

    scope = data.get("supported_scope") or {}
    for key in (
        "personal_user",
        "noncommercial_internal_research",
        "low_frequency_querying",
        "use_available_without_stated_limit_within_visible_scope",
    ):
        _require(scope.get(key) is True, f"{key} must remain true")
    _require(scope.get("separate_approval_procedure_required") is False, "separate approval wording drift")

    not_supported = data.get("not_explicitly_supported_by_visible_text") or {}
    for key in (
        "automated_or_programmatic_querying",
        "authenticated_web_session_automation",
        "bulk_or_high_frequency_collection",
        "specific_bld_routes",
        "full_historical_download",
        "redistribution",
        "commercial_use",
    ):
        _require(not_supported.get(key) is True, f"{key} ambiguity boundary weakened")

    cls = data.get("project_classification") or {}
    _require(cls.get("issuer_independently_verified") is False, "issuer cannot be treated as independently verified")
    _require(cls.get("automated_collection_authorized") is False, "automation authority illegally true")
    _require(cls.get("sufficient_for_data_marketplace_tiny_probe_preflight") is False, "tiny-probe preflight illegally authorized")
    _require(cls.get("gate_a_status_ceiling") == "BLOCKED", "Gate A ceiling drift")
    _require(cls.get("gate_f_evidence_strengthened") is True, "Gate F strengthening lost")
    for key in (
        "bulk_historical_acquisition_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(cls.get(key) is False, f"{key} illegally true")

    upgrades = set(data.get("required_upgrade_evidence") or [])
    _require(len(upgrades) >= 2, "upgrade evidence requirements missing")

    return {
        "valid": True,
        "automated_collection_authorized": False,
        "sufficient_for_data_marketplace_tiny_probe_preflight": False,
        "gate_a_status_ceiling": "BLOCKED",
        "gate_f_evidence_strengthened": True,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_permission_reply_evidence(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
