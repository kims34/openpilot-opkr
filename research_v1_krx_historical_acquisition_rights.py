"""Fail-closed KRX full-history/high-frequency rights validator.

This module validates the user-provided KRX permission evidence for acquisition
rights. It never performs a network request and it deliberately separates
"rights to acquire" from "authorization to start the project's bulk job now".
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from research_v1_krx_permission_reply_evidence import validate_permission_reply_evidence


PERMISSION_PATH = Path("INDEXALERT_KRX_PERMISSION_REPLY_EVIDENCE.json")


class KRXHistoricalRightsError(ValueError):
    pass


def validate_historical_rights(data: Mapping[str, Any]) -> dict[str, Any]:
    permission = validate_permission_reply_evidence(data)
    required = (
        permission["automated_collection_authorized"],
        permission["high_frequency_collection_authorized"],
        permission["full_historical_download_rights_authorized"],
        permission["bulk_historical_acquisition_rights_authorized"],
    )
    if not all(required):
        raise KRXHistoricalRightsError("KRX historical acquisition rights are incomplete")
    if permission["bulk_historical_network_execution_authorized_by_user"] is not False:
        raise KRXHistoricalRightsError("permission evidence must not self-authorize project execution")
    return {
        "valid": True,
        "rights_authorized": True,
        "high_frequency_collection_authorized": True,
        "full_historical_download_rights_authorized": True,
        "redistribution_authorized": False,
        "external_sale_authorized": False,
        "project_network_execution_authorized": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PERMISSION_PATH) -> dict[str, Any]:
    return validate_historical_rights(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
