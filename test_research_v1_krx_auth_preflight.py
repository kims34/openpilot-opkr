import pytest

from research_v1_krx_auth_preflight import (
    DATA_MARKETPLACE_ROUTE,
    OPENAPI_ROUTE,
    PURCHASED_PRODUCT_ROUTE,
    KRXAuthPreflightError,
    evaluate_auth_preflight,
)


def test_data_marketplace_requires_both_credentials_and_auth_reference():
    out = evaluate_auth_preflight(
        source_family="KRX_INVESTOR_FLOW",
        access_route=DATA_MARKETPLACE_ROUTE,
        environment={"KRX_ID": "id", "KRX_PW": "pw"},
        authorization_evidence_reference="approval-ref-001",
    )
    assert out["request_attempt_authorized"] is True
    assert out["gate_a_status_hint"] == "PARTIAL"
    assert out["missing_requirements"] == []
    assert out["bulk_historical_acquisition_authorized"] is False
    assert out["alpha_or_final_judge_promotion_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_data_marketplace_does_not_accept_openapi_key_as_substitute():
    out = evaluate_auth_preflight(
        source_family="KRX_SECURITY_STATUS",
        access_route=DATA_MARKETPLACE_ROUTE,
        environment={"KRX_OPENAPI_AUTH_KEY": "key"},
        authorization_evidence_reference="approval-ref-001",
    )
    assert out["request_attempt_authorized"] is False
    assert out["gate_a_status_hint"] == "BLOCKED"
    assert "KRX_ID" in out["missing_requirements"]
    assert "KRX_PW" in out["missing_requirements"]


def test_auth_reference_is_required_even_when_credentials_exist():
    out = evaluate_auth_preflight(
        source_family="KRX_INVESTOR_FLOW",
        access_route=DATA_MARKETPLACE_ROUTE,
        environment={"KRX_ID": "id", "KRX_PW": "pw"},
        authorization_evidence_reference=None,
    )
    assert out["request_attempt_authorized"] is False
    assert "KRX_AUTH_EVIDENCE_REF" in out["missing_requirements"]


def test_openapi_requires_key_mapping_and_auth_reference():
    blocked = evaluate_auth_preflight(
        source_family="KRX_SECURITY_STATUS",
        access_route=OPENAPI_ROUTE,
        environment={"KRX_OPENAPI_AUTH_KEY": "key"},
        authorization_evidence_reference="approval-ref-002",
        exact_service_mapping_confirmed=False,
    )
    assert blocked["request_attempt_authorized"] is False
    assert "EXACT_APPROVED_OPENAPI_SERVICE_MAPPING" in blocked["missing_requirements"]

    allowed = evaluate_auth_preflight(
        source_family="KRX_SECURITY_STATUS",
        access_route=OPENAPI_ROUTE,
        environment={"KRX_OPENAPI_AUTH_KEY": "key"},
        authorization_evidence_reference="approval-ref-002",
        exact_service_mapping_confirmed=True,
    )
    assert allowed["request_attempt_authorized"] is True
    assert allowed["gate_a_status_hint"] == "PARTIAL"


def test_purchased_product_never_infers_access_from_online_credentials():
    out = evaluate_auth_preflight(
        source_family="KRX_SECURITY_STATUS",
        access_route=PURCHASED_PRODUCT_ROUTE,
        environment={
            "KRX_ID": "id",
            "KRX_PW": "pw",
            "KRX_OPENAPI_AUTH_KEY": "key",
        },
        authorization_evidence_reference="contract-ref-003",
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
            environment={"KRX_ID": "id", "KRX_PW": "pw"},
            authorization_evidence_reference=reference,
        )


def test_individual_credential_presence_is_reported_without_values():
    out = evaluate_auth_preflight(
        source_family="KRX_INVESTOR_FLOW",
        access_route=DATA_MARKETPLACE_ROUTE,
        environment={"KRX_ID": "id", "KRX_PW": None, "KRX_OPENAPI_AUTH_KEY": "key"},
        authorization_evidence_reference="approval-ref-004",
    )
    assert out["krx_id_present"] is True
    assert out["krx_pw_present"] is False
    assert out["openapi_auth_key_present"] is True
    assert "id" not in str(out)
    assert "key" not in str(out)


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
