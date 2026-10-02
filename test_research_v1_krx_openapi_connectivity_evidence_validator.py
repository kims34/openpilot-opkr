import copy
import json
from pathlib import Path

import pytest

from research_v1_krx_openapi_connectivity_evidence import (
    KRXOpenAPIEvidenceError,
    validate_evidence,
    validate_file,
)


EVIDENCE = Path("INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.json")


def _data():
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_committed_evidence_validates_fail_closed():
    out = validate_file()
    assert out["valid"] is True
    assert out["source_contract_closed"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False
    assert len(out["evidence_fingerprint_sha256"]) == 64


def test_authority_escalation_is_rejected():
    data = _data()
    data["authority"]["sealed_holdout_authorized"] = True
    with pytest.raises(KRXOpenAPIEvidenceError, match="sealed_holdout_authorized illegally true"):
        validate_evidence(data)


def test_missing_unproven_boundary_is_rejected():
    data = _data()
    data["not_proven"] = [
        x for x in data["not_proven"]
        if x != "investor-by-security flow access"
    ]
    with pytest.raises(KRXOpenAPIEvidenceError, match="not_proven boundary weakened"):
        validate_evidence(data)


def test_service_schema_or_endpoint_drift_is_rejected():
    data = _data()
    data["services"]["security_master"]["endpoint"] = "https://example.invalid/wrong"
    with pytest.raises(KRXOpenAPIEvidenceError, match="security_master endpoint mismatch"):
        validate_evidence(data)

    data = _data()
    data["services"]["daily_trade"]["fields"] = ["BAS_DD"]
    with pytest.raises(KRXOpenAPIEvidenceError, match="daily_trade required fields missing"):
        validate_evidence(data)


def test_schema_v2_requires_provenance_hashes_and_timestamp():
    data = _data()
    for row in data["services"].values():
        row.pop("response_schema_sha256", None)
        row.pop("response_payload_sha256", None)
        row.pop("observed_at", None)
    with pytest.raises(KRXOpenAPIEvidenceError, match="response_schema_sha256 invalid"):
        validate_evidence(data)

    data = _data()
    out = validate_evidence(data)
    assert out["valid"] is True
    assert out["schema_version"] == "2"


def test_secret_like_material_is_rejected():
    data = _data()
    data["note"] = "token=should-never-be-here"
    with pytest.raises(KRXOpenAPIEvidenceError, match="secret-like material"):
        validate_evidence(data)
