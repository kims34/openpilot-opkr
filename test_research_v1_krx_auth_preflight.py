import pytest

from research_v1_krx_auth_preflight import (
    DATA_MARKETPLACE_ROUTE,
    EXPLICIT_PROBE_CONSENT_ENV,
    EXPLICIT_PROBE_CONSENT_SENTINEL,
    OPENAPI_ROUTE,
    PURCHASED_PRODUCT_ROUTE,
    KRXAuthPreflightError,
    evaluate_auth_preflight,
)


def _consented(**extra):
    env = {EXPLICIT_PROBE_CONSENT_ENV: EXPLICIT_PROBE_CONSENT_SENTINEL}
    env.update(extra)
    return env


def test_data_marketplace_requires_credentials_validated_evidence_and_explicit_consent():
    out = evaluate_auth_preflight(
        source_family="KRX_INVESTOR_FLOW",
        access_route=DATA_MARKETPLACE_ROUTE,
        environment=_consented(KRX_ID="id", KRX_PW="pw"),
        authorization_evidence_reference="approval-ref-001",
        authorization_evidence_record_validated=True,
        automated_collection_authorized=True,
    )
    assert out["request_attempt_authorized"] is True
    assert out["authorization_evidence_record_validated"] is True
    assert out["explicit_probe_consent_present"] is True
    assert out["gate_a_status_hint"] == "PARTIAL"
    assert out["missing_requirements"] == []
    assert out["bulk_historical_acquisition_authorized"] is False
    assert out["alpha_or_final_judge_promotion_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_reference_string_without_validated_record_never_authorizes_request():
    out = evaluate_auth_preflight(
        source_family="KRX_INVESTOR_FLOW",
        access_route=DATA_MARKETPLACE_ROUTE,
        environment=_consented(KRX_ID="id", KRX_PW="pw"),
        authorization_evidence_reference="approval-ref-001",
        authorization_evidence_record_validated=False,
    )
    assert out["request_attempt_authorized"] is False
    assert out["gate_a_status_hint"] == "BLOCKED"
    assert "VALIDATED_KRX_AUTHORIZATION_EVIDENCE_RECORD" in out["missing_requirements"]


def test_credentials_validated_evidence_without_explicit_consent_remain_dry_run():
    out = evaluate_auth_preflight(
        source_family="KRX_INVESTOR_FLOW",
        access_route=DATA_MARKETPLACE_ROUTE,
        environment={"KRX_ID": "id", "KRX_PW": "pw"},
        authorization_evidence_reference="approval-ref-001",
        authorization_evidence_record_validated=True,
        automated_collection_authorized=True,
    )
    assert out["request_attempt_authorized"] is False
    assert out["explicit_probe_consent_present"] is False
    assert out["gate_a_status_hint"] == "BLOCKED"
    assert out["missing_requirements"] == ["EXPLICIT_TINY_REQUEST_CONSENT"]


@pytest.mark.parametrize(
    "value",
    ["true", "TRUE", "1", "yes", "ALLOW_AUTHENTICATED_REQUEST", " allow_tiny_authenticated_request "],
)
def test_only_exact_explicit_consent_sentinel_is_accepted(value):
    out = evaluate_auth_preflight(
        source_family="KRX_INVESTOR_FLOW",
        access_route=DATA_MARKETPLACE_ROUTE,
        environment={
            "KRX_ID": "id",
            "KRX_PW": "pw",
            EXPLICIT_PROBE_CONSENT_ENV: value,
        },
        authorization_evidence_reference="approval-ref-001",
        authorization_evidence_record_validated=True,
        automated_collection_authorized=True,
    )
    assert out["request_attempt_authorized"] is False
    assert out["explicit_probe_consent_present"] is False
    assert "EXPLICIT_TINY_REQUEST_CONSENT" in out["missing_requirements"]


def test_data_marketplace_does_not_accept_openapi_key_as_substitute():
    out = evaluate_auth_preflight(
        source_family="KRX_SECURITY_STATUS",
        access_route=DATA_MARKETPLACE_ROUTE,
        environment=_consented(KRX_OPENAPI_AUTH_KEY="key"),
        authorization_evidence_reference="approval-ref-001",
        authorization_evidence_record_validated=True,
        automated_collection_authorized=True,
    )
    assert out["request_attempt_authorized"] is False
    assert out["gate_a_status_hint"] == "BLOCKED"
    assert "KRX_ID" in out["missing_requirements"]
    assert "KRX_PW" in out["missing_requirements"]


def test_auth_reference_is_required_even_when_credentials_evidence_and_consent_exist():
    out = evaluate_auth_preflight(
        source_family="KRX_INVESTOR_FLOW",
        access_route=DATA_MARKETPLACE_ROUTE,
        environment=_consented(KRX_ID="id", KRX_PW="pw"),
        authorization_evidence_reference=None,
        authorization_evidence_record_validated=True,
        automated_collection_authorized=True,
    )
    assert out["request_attempt_authorized"] is False
    assert "KRX_AUTH_EVIDENCE_REF" in out["missing_requirements"]


def test_openapi_requires_key_mapping_validated_evidence_and_explicit_consent():
    blocked = evaluate_auth_preflight(
        source_family="KRX_SECURITY_STATUS",
        access_route=OPENAPI_ROUTE,
        environment=_consented(KRX_OPENAPI_AUTH_KEY="key"),
        authorization_evidence_reference="approval-ref-002",
        authorization_evidence_record_validated=True,
        automated_collection_authorized=True,
        exact_service_mapping_confirmed=False,
    )
    assert blocked["request_attempt_authorized"] is False
    assert "EXACT_APPROVED_OPENAPI_SERVICE_MAPPING" in blocked["missing_requirements"]

    allowed = evaluate_auth_preflight(
        source_family="KRX_SECURITY_STATUS",
        access_route=OPENAPI_ROUTE,
        environment=_consented(KRX_OPENAPI_AUTH_KEY="key"),
        authorization_evidence_reference="approval-ref-002",
        authorization_evidence_record_validated=True,
        automated_collection_authorized=True,
        exact_service_mapping_confirmed=True,
    )
    assert allowed["request_attempt_authorized"] is True
    assert allowed["gate_a_status_hint"] == "PARTIAL"


def test_purchased_product_never_infers_access_from_online_credentials():
    out = evaluate_auth_preflight(
        source_family="KRX_SECURITY_STATUS",
        access_route=PURCHASED_PRODUCT_ROUTE,
        environment=_consented(
            KRX_ID="id",
            KRX_PW="pw",
            KRX_OPENAPI_AUTH_KEY="key",
        ),
        authorization_evidence_reference="contract-ref-003",
        authorization_evidence_record_validated=True,
        automated_collection_authorized=True,
    )
    assert out["request_attempt_authorized"] is False
    assert "PURCHASED_PRODUCT_ACCESS_VERIFICATION" in out["missing_requirements"]


@pytest.mark.parametrize(
    "reference",
    [
        "password=abc",
        "token=abc",
        "cookie=session",
        "Authorization: Bearer abc",
        "bearer abc",
    ],
)
def test_secret_like_authorization_reference_is_rejected(reference):
    with pytest.raises(KRXAuthPreflightError, match="opaque non-secret"):
        evaluate_auth_preflight(
            source_family="KRX_INVESTOR_FLOW",
            access_route=DATA_MARKETPLACE_ROUTE,
            environment=_consented(KRX_ID="id", KRX_PW="pw"),
            authorization_evidence_reference=reference,
            authorization_evidence_record_validated=True,
        automated_collection_authorized=True,
        )


def test_individual_credential_presence_is_reported_without_values():
    private_id = "PRIVATE_KRX_USER_7XQ9"
    private_openapi_key = "PRIVATE_KRX_OPENAPI_9YP4"
    out = evaluate_auth_preflight(
        source_family="KRX_INVESTOR_FLOW",
        access_route=DATA_MARKETPLACE_ROUTE,
        environment={
            "KRX_ID": private_id,
            "KRX_PW": None,
            "KRX_OPENAPI_AUTH_KEY": private_openapi_key,
            EXPLICIT_PROBE_CONSENT_ENV: EXPLICIT_PROBE_CONSENT_SENTINEL,
        },
        authorization_evidence_reference="approval-ref-004",
        authorization_evidence_record_validated=True,
        automated_collection_authorized=True,
    )
    assert out["krx_id_present"] is True
    assert out["krx_pw_present"] is False
    assert out["openapi_auth_key_present"] is True
    assert out["explicit_probe_consent_present"] is True
    rendered = str(out)
    assert private_id not in rendered
    assert private_openapi_key not in rendered


def test_unknown_family_or_route_fails_closed():
    with pytest.raises(KRXAuthPreflightError, match="unsupported source_family"):
        evaluate_auth_preflight(
            source_family="UNKNOWN",
            access_route=DATA_MARKETPLACE_ROUTE,
            environment={},
            authorization_evidence_reference="ref",
        )
    with pytest.raises(KRXAuthPreflightError, match="unsupported access_route"):
        evaluate_auth_preflight(
            source_family="KRX_INVESTOR_FLOW",
            access_route="UNOFFICIAL_PROXY",
            environment={},
            authorization_evidence_reference="ref",
        )


def test_data_marketplace_blocks_when_automation_permission_missing():
    out = evaluate_auth_preflight(
        source_family="KRX_INVESTOR_FLOW",
        access_route=DATA_MARKETPLACE_ROUTE,
        environment=_consented(KRX_ID="id", KRX_PW="pw"),
        authorization_evidence_reference="approval-ref-automation",
        authorization_evidence_record_validated=True,
        automated_collection_authorized=False,
    )
    assert out["request_attempt_authorized"] is False
    assert "EXPLICIT_KRX_AUTOMATED_COLLECTION_PERMISSION" in out["missing_requirements"]
