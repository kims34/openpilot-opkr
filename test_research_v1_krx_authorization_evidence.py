from datetime import datetime, timezone

import pytest

from research_v1_krx_auth_preflight import DATA_MARKETPLACE_ROUTE
from research_v1_krx_authorization_evidence import (
    KRXAuthorizationEvidenceError,
    parse_and_validate_authorization_evidence_json,
    validate_authorization_evidence,
)


EVAL = datetime(2026, 10, 1, 4, 30, tzinfo=timezone.utc)
SCOPE = "INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION"


def _record(**overrides):
    base = {
        "schema_version": "1",
        "evidence_reference": "krx-approval-ref-2026-001",
        "issuer": "KRX",
        "source_family": "KRX_INVESTOR_FLOW",
        "access_route": DATA_MARKETPLACE_ROUTE,
        "intended_use_scope": SCOPE,
        "approval_state": "APPROVED",
        "scope_statement": "Non-secret approval metadata for the declared tiny Data Marketplace source probe.",
        "automated_collection_authorized": True,
        "evidence_document_sha256": "a" * 64,
        "captured_at": "2026-09-30T12:00:00+00:00",
        "valid_from": "2026-09-30T00:00:00+00:00",
        "valid_until": "2026-12-31T23:59:59+00:00",
    }
    base.update(overrides)
    return base


def _validate(record):
    return validate_authorization_evidence(
        record,
        expected_source_family="KRX_INVESTOR_FLOW",
        expected_access_route=DATA_MARKETPLACE_ROUTE,
        expected_intended_use_scope=SCOPE,
        evaluation_time=EVAL,
        expected_reference="krx-approval-ref-2026-001",
    )


def test_matching_approved_active_record_is_only_tiny_probe_metadata():
    out = _validate(_record())
    assert out["sufficient_for_tiny_probe_preflight"] is True
    assert out["reason_codes"] == []
    assert out["gate_a_status_ceiling"] == "PARTIAL"
    assert out["bulk_historical_acquisition_authorized"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["alpha_or_final_judge_promotion_authorized"] is False
    assert out["live_trading_authorized"] is False
    assert len(out["record_fingerprint_sha256"]) == 64


def test_reference_route_family_scope_and_issuer_mismatch_fail_closed():
    cases = [
        ("evidence_reference", "other-ref", "EVIDENCE_REFERENCE_MISMATCH"),
        ("access_route", "KRX_OPENAPI_APPROVED_SERVICE", "ACCESS_ROUTE_MISMATCH"),
        ("source_family", "KRX_SECURITY_STATUS", "SOURCE_FAMILY_MISMATCH"),
        ("intended_use_scope", "OTHER_SCOPE", "INTENDED_USE_SCOPE_MISMATCH"),
        ("issuer", "OTHER", "ISSUER_NOT_KRX"),
    ]
    for field, value, reason in cases:
        out = _validate(_record(**{field: value}))
        assert out["sufficient_for_tiny_probe_preflight"] is False
        assert reason in out["reason_codes"]
        assert out["gate_a_status_ceiling"] == "BLOCKED"


def test_pending_revoked_expired_and_not_yet_valid_are_blocked():
    pending = _validate(_record(approval_state="PENDING"))
    assert "APPROVAL_STATE_PENDING" in pending["reason_codes"]

    revoked = _validate(_record(approval_state="REVOKED"))
    assert "APPROVAL_STATE_REVOKED" in revoked["reason_codes"]

    expired = _validate(_record(valid_until="2026-09-30T23:59:59+00:00"))
    assert "EXPIRED" in expired["reason_codes"]

    not_yet = _validate(_record(valid_from="2026-10-02T00:00:00+00:00"))
    assert "NOT_YET_VALID" in not_yet["reason_codes"]


def test_unknown_fields_are_rejected_to_prevent_secret_stowaway_metadata():
    record = _record()
    record["password"] = "should-never-be-here"
    with pytest.raises(KRXAuthorizationEvidenceError, match="unsupported fields"):
        _validate(record)


def test_secret_like_values_are_rejected():
    with pytest.raises(KRXAuthorizationEvidenceError, match="secret-like"):
        _validate(_record(scope_statement="Authorization: Bearer hidden"))


def test_document_hash_and_time_contracts_are_strict():
    with pytest.raises(KRXAuthorizationEvidenceError, match="64-character"):
        _validate(_record(evidence_document_sha256="abc"))
    with pytest.raises(KRXAuthorizationEvidenceError, match="timezone-aware"):
        _validate(_record(captured_at="2026-09-30T12:00:00"))
    with pytest.raises(KRXAuthorizationEvidenceError, match="cannot be in the future"):
        _validate(_record(captured_at="2026-10-02T12:00:00+00:00"))
    with pytest.raises(KRXAuthorizationEvidenceError, match="cannot precede"):
        _validate(
            _record(
                valid_from="2026-12-01T00:00:00+00:00",
                valid_until="2026-11-01T00:00:00+00:00",
            )
        )


def test_json_parser_rejects_missing_or_non_object_and_accepts_valid_record():
    with pytest.raises(KRXAuthorizationEvidenceError, match="not configured"):
        parse_and_validate_authorization_evidence_json(
            "",
            expected_source_family="KRX_INVESTOR_FLOW",
            expected_access_route=DATA_MARKETPLACE_ROUTE,
            expected_intended_use_scope=SCOPE,
            evaluation_time=EVAL,
        )
    with pytest.raises(KRXAuthorizationEvidenceError, match="must be an object"):
        parse_and_validate_authorization_evidence_json(
            "[]",
            expected_source_family="KRX_INVESTOR_FLOW",
            expected_access_route=DATA_MARKETPLACE_ROUTE,
            expected_intended_use_scope=SCOPE,
            evaluation_time=EVAL,
        )

    import json
    out = parse_and_validate_authorization_evidence_json(
        json.dumps(_record()),
        expected_source_family="KRX_INVESTOR_FLOW",
        expected_access_route=DATA_MARKETPLACE_ROUTE,
        expected_intended_use_scope=SCOPE,
        evaluation_time=EVAL,
        expected_reference="krx-approval-ref-2026-001",
    )
    assert out["sufficient_for_tiny_probe_preflight"] is True


def test_data_marketplace_requires_explicit_automation_permission():
    missing = _record()
    missing.pop("automated_collection_authorized")
    out = _validate(missing)
    assert out["sufficient_for_tiny_probe_preflight"] is False
    assert "AUTOMATED_COLLECTION_NOT_EXPLICITLY_AUTHORIZED" in out["reason_codes"]

    denied = _validate(_record(automated_collection_authorized=False))
    assert denied["sufficient_for_tiny_probe_preflight"] is False
    assert "AUTOMATED_COLLECTION_NOT_EXPLICITLY_AUTHORIZED" in denied["reason_codes"]
