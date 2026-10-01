import pytest

from research_v1_krx_auth_preflight import (
    EXPLICIT_PROBE_CONSENT_ENV,
    EXPLICIT_PROBE_CONSENT_SENTINEL,
    KRXAuthPreflightError,
)
from research_v1_krx_auth_readiness import build_readiness_report


def test_ready_configuration_never_authorizes_or_attempts_network_request():
    out = build_readiness_report(
        environment={
            "KRX_ID": "PRIVATE_USER",
            "KRX_PW": "PRIVATE_PASSWORD",
        },
        authorization_evidence_reference="approval-ref-ready-001",
    )
    assert out["configuration_ready_for_manual_authenticated_probe"] is True
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
        authorization_evidence_reference="approval-ref-ready-002",
    )
    assert out["configuration_ready_for_manual_authenticated_probe"] is True
    assert out["request_attempt_authorized"] is False
    assert out["network_request_attempted"] is False


def test_missing_password_keeps_configuration_not_ready():
    out = build_readiness_report(
        environment={"KRX_ID": "PRIVATE_USER", "KRX_PW": None},
        authorization_evidence_reference="approval-ref-ready-003",
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
    )
    assert out["configuration_ready_for_manual_authenticated_probe"] is False
    assert "KRX_AUTH_EVIDENCE_REF" in out[
        "remaining_requirements_before_manual_probe"
    ]
    assert out["network_request_attempted"] is False


def test_secret_values_are_not_rendered_in_readiness_report():
    private_id = "PRIVATE_KRX_ID_ABC123"
    private_pw = "PRIVATE_KRX_PW_XYZ987"
    private_key = "PRIVATE_OPENAPI_KEY_QWE456"
    out = build_readiness_report(
        environment={
            "KRX_ID": private_id,
            "KRX_PW": private_pw,
            "KRX_OPENAPI_AUTH_KEY": private_key,
        },
        authorization_evidence_reference="approval-ref-ready-004",
    )
    rendered = str(out)
    assert private_id not in rendered
    assert private_pw not in rendered
    assert private_key not in rendered


def test_secret_like_authorization_reference_is_rejected():
    with pytest.raises(KRXAuthPreflightError, match="opaque non-secret"):
        build_readiness_report(
            environment={"KRX_ID": "id", "KRX_PW": "pw"},
            authorization_evidence_reference="token=do-not-store-this",
        )
