from datetime import datetime, timezone
import json

import pytest

from research_v1_krx_auth_preflight import (
    EXPLICIT_PROBE_CONSENT_ENV,
    EXPLICIT_PROBE_CONSENT_SENTINEL,
    KRXAuthPreflightError,
)
from research_v1_krx_auth_readiness import build_readiness_report


EVAL = datetime(2026, 10, 1, 4, 40, tzinfo=timezone.utc)
REF = "approval-ref-ready-001"


def _evidence_json(*, reference=REF, state="APPROVED"):
    return json.dumps(
        {
            "schema_version": "1",
            "evidence_reference": reference,
            "issuer": "KRX",
            "source_family": "KRX_INVESTOR_FLOW",
            "access_route": "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
            "intended_use_scope": "INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION",
            "approval_state": state,
            "scope_statement": "Non-secret approval metadata for the declared tiny probe.",
            "evidence_document_sha256": "b" * 64,
            "captured_at": "2026-09-30T12:00:00+00:00",
            "valid_from": "2026-09-30T00:00:00+00:00",
            "valid_until": "2026-12-31T23:59:59+00:00",
        }
    )


def test_ready_configuration_never_authorizes_or_attempts_network_request():
    out = build_readiness_report(
        environment={
            "KRX_ID": "PRIVATE_USER",
            "KRX_PW": "PRIVATE_PASSWORD",
        },
        authorization_evidence_reference=REF,
        authorization_evidence_json=_evidence_json(),
        evaluation_time=EVAL,
    )
    assert out["configuration_ready_for_manual_authenticated_probe"] is True
    assert out["authorization_evidence"]["valid_for_declared_tiny_probe"] is True
    assert out["explicit_probe_consent_forced_off"] is True
    assert out["request_attempt_authorized"] is False
    assert out["authenticated_request_attempted"] is False
    assert out["network_request_attempted"] is False
    assert out["remaining_requirements_before_manual_probe"] == [
        "EXPLICIT_TINY_REQUEST_CONSENT"
    ]
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False
    assert len(out["readiness_fingerprint_sha256"]) == 64


def test_readiness_forcibly_ignores_even_exact_request_consent_from_caller():
    out = build_readiness_report(
        environment={
            "KRX_ID": "PRIVATE_USER",
            "KRX_PW": "PRIVATE_PASSWORD",
            EXPLICIT_PROBE_CONSENT_ENV: EXPLICIT_PROBE_CONSENT_SENTINEL,
        },
        authorization_evidence_reference=REF,
        authorization_evidence_json=_evidence_json(),
        evaluation_time=EVAL,
    )
    assert out["configuration_ready_for_manual_authenticated_probe"] is True
    assert out["request_attempt_authorized"] is False
    assert out["network_request_attempted"] is False


def test_reference_without_structured_record_is_not_ready():
    out = build_readiness_report(
        environment={"KRX_ID": "PRIVATE_USER", "KRX_PW": "PRIVATE_PASSWORD"},
        authorization_evidence_reference=REF,
        authorization_evidence_json=None,
        evaluation_time=EVAL,
    )
    assert out["configuration_ready_for_manual_authenticated_probe"] is False
    assert "VALIDATED_KRX_AUTHORIZATION_EVIDENCE_RECORD" in out[
        "remaining_requirements_before_manual_probe"
    ]
    assert out["authorization_evidence"]["configured"] is False


def test_pending_or_mismatched_record_is_not_ready():
    pending = build_readiness_report(
        environment={"KRX_ID": "PRIVATE_USER", "KRX_PW": "PRIVATE_PASSWORD"},
        authorization_evidence_reference=REF,
        authorization_evidence_json=_evidence_json(state="PENDING"),
        evaluation_time=EVAL,
    )
    assert pending["configuration_ready_for_manual_authenticated_probe"] is False
    assert "APPROVAL_STATE_PENDING" in pending["authorization_evidence"]["reason_codes"]

    mismatch = build_readiness_report(
        environment={"KRX_ID": "PRIVATE_USER", "KRX_PW": "PRIVATE_PASSWORD"},
        authorization_evidence_reference="different-ref",
        authorization_evidence_json=_evidence_json(),
        evaluation_time=EVAL,
    )
    assert mismatch["configuration_ready_for_manual_authenticated_probe"] is False
    assert "EVIDENCE_REFERENCE_MISMATCH" in mismatch["authorization_evidence"]["reason_codes"]


def test_missing_password_keeps_configuration_not_ready():
    out = build_readiness_report(
        environment={"KRX_ID": "PRIVATE_USER", "KRX_PW": None},
        authorization_evidence_reference=REF,
        authorization_evidence_json=_evidence_json(),
        evaluation_time=EVAL,
    )
    assert out["configuration_ready_for_manual_authenticated_probe"] is False
    assert "KRX_PW" in out["remaining_requirements_before_manual_probe"]
    assert "EXPLICIT_TINY_REQUEST_CONSENT" in out[
        "remaining_requirements_before_manual_probe"
    ]
    assert out["network_request_attempted"] is False


def test_missing_authorization_reference_keeps_configuration_not_ready():
    out = build_readiness_report(
        environment={"KRX_ID": "PRIVATE_USER", "KRX_PW": "PRIVATE_PASSWORD"},
        authorization_evidence_reference=None,
        authorization_evidence_json=_evidence_json(),
        evaluation_time=EVAL,
    )
    assert out["configuration_ready_for_manual_authenticated_probe"] is False
    assert "KRX_AUTH_EVIDENCE_REF" in out[
        "remaining_requirements_before_manual_probe"
    ]
    assert out["network_request_attempted"] is False


def test_secret_values_and_raw_evidence_json_are_not_rendered_in_readiness_report():
    private_id = "PRIVATE_KRX_ID_ABC123"
    private_pw = "PRIVATE_KRX_PW_XYZ987"
    private_key = "PRIVATE_OPENAPI_KEY_QWE456"
    raw = _evidence_json()
    out = build_readiness_report(
        environment={
            "KRX_ID": private_id,
            "KRX_PW": private_pw,
            "KRX_OPENAPI_AUTH_KEY": private_key,
        },
        authorization_evidence_reference=REF,
        authorization_evidence_json=raw,
        evaluation_time=EVAL,
    )
    rendered = str(out)
    assert private_id not in rendered
    assert private_pw not in rendered
    assert private_key not in rendered
    assert raw not in rendered


def test_secret_like_authorization_reference_is_rejected():
    with pytest.raises(KRXAuthPreflightError, match="opaque non-secret"):
        build_readiness_report(
            environment={"KRX_ID": "id", "KRX_PW": "pw"},
            authorization_evidence_reference="token=do-not-store-this",
            authorization_evidence_json=_evidence_json(),
            evaluation_time=EVAL,
        )
