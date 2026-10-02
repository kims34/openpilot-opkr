"""Fail-closed validator for Railway historical-worker readiness evidence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_HISTORICAL_RAILWAY_READINESS_EVIDENCE.json")


class KRXHistoricalRailwayReadinessError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXHistoricalRailwayReadinessError(msg)


def validate_readiness(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "evidence must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(
        data.get("evidence_class") == "RAILWAY_READ_ONLY_INFRASTRUCTURE_GAP_AUDIT",
        "evidence_class drift",
    )

    req = data.get("required_worker") or {}
    _require(req.get("service_name") == "indexalert-krx-historical-worker", "worker service drift")
    _require(req.get("branch") == "index-alert-research-v1", "branch drift")
    _require(req.get("dockerfile") == "Dockerfile.krx-historical-worker", "Dockerfile drift")
    _require(req.get("dedicated_volume_mount") == "/data", "volume mount drift")
    _require(req.get("private_raw_root") == "/data/indexalert/krx-historical-v3", "raw root drift")
    _require(req.get("public_domain_forbidden") is True, "public-domain guard lost")
    _require(req.get("restart_policy") == "NEVER", "restart-policy drift")

    services = {str(x.get("name")): x for x in (data.get("observed_services") or [])}
    _require("indexalert-runtime" in services, "runtime observation missing")
    _require(services["indexalert-runtime"].get("has_volume") is True, "runtime volume observation drift")
    _require(services["indexalert-runtime"].get("volume_mount") == "/data", "runtime volume mount drift")
    _require(services["indexalert-runtime"].get("must_not_be_reused") is True, "runtime-volume isolation guard lost")

    _require(data.get("worker_service_exists") is False, "worker service cannot be claimed present")
    _require(data.get("dedicated_worker_volume_exists") is False, "worker volume cannot be claimed present")
    _require(data.get("production_runtime_volume_reuse_allowed") is False, "production volume reuse illegally allowed")
    _require(data.get("infrastructure_ready_for_bulk_execution") is False, "infrastructure cannot be pre-authorized")

    auth = data.get("authority") or {}
    for key in (
        "service_creation_authorized",
        "volume_creation_or_attachment_authorized",
        "bulk_network_execution_authorized_by_user",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(auth.get(key) is False, f"{key} illegally true")

    return {
        "valid": True,
        "worker_service_exists": False,
        "dedicated_worker_volume_exists": False,
        "infrastructure_ready_for_bulk_execution": False,
        "service_creation_authorized": False,
        "volume_creation_or_attachment_authorized": False,
        "bulk_network_execution_authorized_by_user": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_readiness(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
