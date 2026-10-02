"""Fail-closed validator for KRX per-security preparation evidence."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_PER_SECURITY_HISTORY_PREPARATION_EVIDENCE.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class KRXPerSecurityPreparationEvidenceError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXPerSecurityPreparationEvidenceError(msg)


def _sha(v: Any, field: str) -> str:
    s = str(v or "").strip().lower()
    _require(bool(SHA256_RE.fullmatch(s)), f"{field} must be SHA-256")
    return s


def validate_evidence(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "evidence must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(
        data.get("evidence_id")
        == "INDEXALERT-KRX-PER-SECURITY-HISTORY-PREP-2026-10-03-v1",
        "evidence_id drift",
    )
    _require(data.get("stage") == "PER_SECURITY_HISTORY", "stage drift")
    _require(
        data.get("status") == "PREPARED_NETWORK_FREE_EXECUTION_NOT_AUTHORIZED",
        "status drift",
    )

    prep = data.get("preparation") or {}
    _require(prep.get("railway_service") == "indexalert-krx-historical-worker", "worker drift")
    _require(prep.get("mode") == "PREPARE_PER_SECURITY_HISTORY", "mode drift")
    _require(int(prep.get("task_count", -1)) == 14296, "task count drift")
    _require(
        prep.get("task_count_by_kind")
        == {
            "investor_trading_individual_daily": 9485,
            "trading_halt": 4811,
        },
        "task-kind counts drift",
    )
    _require(
        _sha(prep.get("task_set_fingerprint_sha256"), "task_set_fingerprint_sha256")
        == "fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38",
        "task-set fingerprint drift",
    )
    _require(
        _sha(prep.get("private_task_manifest_metadata_sha256"), "private_task_manifest_metadata_sha256")
        == "0d98f45168cedeecc013e95c71abe661ca1fac9df0403ba477d2f5653572c116",
        "private manifest hash drift",
    )
    _require(
        prep.get("private_task_manifest_relpath")
        == "task_manifests/per-security-history-v3.json",
        "private manifest relpath drift",
    )
    _require(prep.get("phase_status") == "PENDING", "phase status drift")
    _require(prep.get("phase_complete") is False, "phase cannot be complete at preparation")
    _require(prep.get("network_request_attempted") is False, "preparation attempted network")
    _require(prep.get("security_identifiers_emitted") is False, "identifiers leaked")
    _require(prep.get("raw_rows_emitted") is False, "raw rows leaked")

    identity = data.get("identity_boundary") or {}
    for key in (
        "preserves_official_six_character_alphanumeric_short_codes",
        "same_day_official_noncommon_new_listings_excluded",
        "official_noncommon_prestart_delisted_excluded_at_start",
        "missing_or_ambiguous_identity_fail_closed",
    ):
        _require(identity.get(key) is True, f"{key} guard lost")
    _require(identity.get("lookahead_backfill_used") is False, "lookahead/backfill illegally used")

    authority = data.get("authority") or {}
    for key in (
        "per_security_history_execution_authorized",
        "status_economics_execution_authorized",
        "expected_scope_network_execution_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    ):
        _require(authority.get(key) is False, f"{key} illegally true")

    return {
        "valid": True,
        "task_count": 14296,
        "investor_task_count": 9485,
        "halt_task_count": 4811,
        "network_request_attempted": False,
        "execution_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_evidence(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
