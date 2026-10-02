import json
from datetime import datetime, timezone
from pathlib import Path

from research_v1_krx_auth_preflight import DATA_MARKETPLACE_ROUTE
from research_v1_krx_authorization_evidence import validate_authorization_evidence


REF = "KRX_EMAIL_REPLY_2026-10-02_1440KST_C50A76BB"
DOC_SHA = "c50a76bb22d8e16b48b9b2eb56c78ab97f620068ed4fae4a65cd4bf6f4ae5f38"
EVAL = datetime(2026, 10, 2, 6, 30, tzinfo=timezone.utc)

CASES = [
    (
        Path("INDEXALERT_KRX_AUTH_EVIDENCE_SECURITY_STATUS.json"),
        "KRX_SECURITY_STATUS",
        "INTERNAL_RESEARCH_AND_FINAL_JUDGE_INPUT_PREPARATION",
    ),
    (
        Path("INDEXALERT_KRX_AUTH_EVIDENCE_INVESTOR_FLOW.json"),
        "KRX_INVESTOR_FLOW",
        "INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION",
    ),
]


def test_committed_krx_permission_records_are_valid_for_tiny_probe_preflight_only():
    for path, family, scope in CASES:
        data = json.loads(path.read_text(encoding="utf-8"))
        out = validate_authorization_evidence(
            data,
            expected_source_family=family,
            expected_access_route=DATA_MARKETPLACE_ROUTE,
            expected_intended_use_scope=scope,
            evaluation_time=EVAL,
            expected_reference=REF,
        )
        assert out["sufficient_for_tiny_probe_preflight"] is True
        assert out["reason_codes"] == []
        assert out["record"]["approval_state"] == "PERMITTED_NO_SEPARATE_APPROVAL"
        assert out["record"]["automated_collection_authorized"] is True
        assert out["record"]["evidence_document_sha256"] == DOC_SHA
        assert out["gate_a_status_ceiling"] == "PARTIAL"
        assert out["bulk_historical_acquisition_authorized"] is False
        assert out["feature_performance_testing_authorized"] is False
        assert out["sealed_holdout_authorized"] is False
        assert out["live_trading_authorized"] is False


def test_committed_records_contain_no_recipient_identity_or_secret_fields():
    forbidden_keys = {
        "recipient",
        "recipient_email",
        "password",
        "token",
        "cookie",
        "secret",
        "auth_key",
        "api_key",
    }
    for path, _, _ in CASES:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert forbidden_keys.isdisjoint(set(data))
        serialized = json.dumps(data, ensure_ascii=False).lower()
        assert "@gmail." not in serialized
        assert "ksyisgood" not in serialized
