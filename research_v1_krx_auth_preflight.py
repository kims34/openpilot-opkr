"""Fail-closed authorization preflight for KRX source probes/acquisition.

Credential presence is not authorization, an opaque approval reference is not
validated evidence, and authorization metadata is not runtime consent. This
module requires all three layers before any tiny authenticated online probe may
be attempted:

1. route-specific credentials;
2. a non-secret approval/evidence reference backed by a separately validated
   structured authorization-evidence record;
3. the exact explicit per-run consent sentinel.

The preflight never prints or persists credential values. A positive preflight
may authorize only the explicitly declared tiny source request. It cannot make
Gate A PASS, close any other A-F gate, authorize bulk historical acquisition,
feature testing, sealed holdout, promotion or live trading.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping


DATA_MARKETPLACE_ROUTE = "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION"
OPENAPI_ROUTE = "KRX_OPENAPI_APPROVED_SERVICE"
PURCHASED_PRODUCT_ROUTE = "KRX_PURCHASED_OR_DISTRIBUTED_PRODUCT"
ALLOWED_ROUTES = {DATA_MARKETPLACE_ROUTE, OPENAPI_ROUTE, PURCHASED_PRODUCT_ROUTE}
ALLOWED_FAMILIES = {"KRX_SECURITY_STATUS", "KRX_INVESTOR_FLOW"}
EXPLICIT_PROBE_CONSENT_ENV = "KRX_EXPLICIT_PROBE_CONSENT"
EXPLICIT_PROBE_CONSENT_SENTINEL = "ALLOW_TINY_AUTHENTICATED_REQUEST"


class KRXAuthPreflightError(ValueError):
    """Raised for malformed or unsafe authorization metadata."""


@dataclass(frozen=True)
class KRXAuthPreflight:
    source_family: str
    access_route: str
    krx_id_present: bool
    krx_pw_present: bool
    openapi_auth_key_present: bool
    route_credentials_complete: bool
    authorization_evidence_reference_present: bool
    authorization_evidence_record_validated: bool
    automated_collection_authorized: bool
    exact_service_mapping_confirmed: bool
    explicit_probe_consent_present: bool
    request_attempt_authorized: bool
    gate_a_status_hint: str
    missing_requirements: tuple[str, ...]
    alpha_or_final_judge_promotion_authorized: bool
    bulk_historical_acquisition_authorized: bool
    sealed_holdout_authorized: bool
    live_trading_authorized: bool


def _text(value, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise KRXAuthPreflightError(f"{field} must be non-empty")
    return text


def _opaque_auth_reference(value: str | None) -> tuple[str, bool]:
    text = str(value or "").strip()
    if not text:
        return "", False
    lowered = text.lower()
    forbidden = (
        "password=", "passwd=", "pwd=", "token=", "cookie=", "secret=",
        "auth_key=", "api_key=", "authorization:", "bearer ",
    )
    if any(marker in lowered for marker in forbidden):
        raise KRXAuthPreflightError(
            "authorization evidence reference must be an opaque non-secret reference"
        )
    if len(text) > 200:
        raise KRXAuthPreflightError("authorization evidence reference is unexpectedly long")
    return text, True


def evaluate_auth_preflight(
    *,
    source_family: str,
    access_route: str,
    environment: Mapping[str, str | None],
    authorization_evidence_reference: str | None,
    authorization_evidence_record_validated: bool = False,
    automated_collection_authorized: bool = False,
    exact_service_mapping_confirmed: bool = False,
) -> dict:
    """Evaluate whether one declared tiny authenticated request may be attempted.

    `authorization_evidence_record_validated` must come from the separate
    structured validator in `research_v1_krx_authorization_evidence.py`. Merely
    supplying a reference string is not sufficient.

    `exact_service_mapping_confirmed` is additionally required for the OpenAPI
    route because an AUTH_KEY by itself does not identify or approve the
    dataset service.

    The exact non-secret sentinel
    `KRX_EXPLICIT_PROBE_CONSENT=ALLOW_TINY_AUTHENTICATED_REQUEST` is required for
    every online tiny probe. Merely setting credentials and authorization
    metadata therefore remains dry-run safe on push, local execution and CI.
    """
    family = _text(source_family, "source_family")
    if family not in ALLOWED_FAMILIES:
        raise KRXAuthPreflightError(f"unsupported source_family: {family}")
    route = _text(access_route, "access_route")
    if route not in ALLOWED_ROUTES:
        raise KRXAuthPreflightError(f"unsupported access_route: {route}")

    krx_id = bool(str(environment.get("KRX_ID") or "").strip())
    krx_pw = bool(str(environment.get("KRX_PW") or "").strip())
    openapi_key = bool(str(environment.get("KRX_OPENAPI_AUTH_KEY") or "").strip())
    explicit_consent = (
        str(environment.get(EXPLICIT_PROBE_CONSENT_ENV) or "").strip()
        == EXPLICIT_PROBE_CONSENT_SENTINEL
    )
    _, auth_ref_present = _opaque_auth_reference(authorization_evidence_reference)
    auth_record_validated = bool(authorization_evidence_record_validated)

    missing: list[str] = []
    if route == DATA_MARKETPLACE_ROUTE:
        route_credentials_complete = krx_id and krx_pw
        if not krx_id:
            missing.append("KRX_ID")
        if not krx_pw:
            missing.append("KRX_PW")
    elif route == OPENAPI_ROUTE:
        route_credentials_complete = openapi_key
        if not openapi_key:
            missing.append("KRX_OPENAPI_AUTH_KEY")
        if not exact_service_mapping_confirmed:
            missing.append("EXACT_APPROVED_OPENAPI_SERVICE_MAPPING")
    else:
        route_credentials_complete = False
        missing.append("PURCHASED_PRODUCT_ACCESS_VERIFICATION")

    if not auth_ref_present:
        missing.append("KRX_AUTH_EVIDENCE_REF")
    if not auth_record_validated:
        missing.append("VALIDATED_KRX_AUTHORIZATION_EVIDENCE_RECORD")
    if route == DATA_MARKETPLACE_ROUTE and not automated_collection_authorized:
        missing.append("EXPLICIT_KRX_AUTOMATED_COLLECTION_PERMISSION")
    if route != PURCHASED_PRODUCT_ROUTE and not explicit_consent:
        missing.append("EXPLICIT_TINY_REQUEST_CONSENT")

    request_authorized = bool(
        route_credentials_complete
        and auth_ref_present
        and auth_record_validated
        and (route != DATA_MARKETPLACE_ROUTE or automated_collection_authorized)
        and explicit_consent
        and (route != OPENAPI_ROUTE or exact_service_mapping_confirmed)
        and route != PURCHASED_PRODUCT_ROUTE
    )

    result = KRXAuthPreflight(
        source_family=family,
        access_route=route,
        krx_id_present=krx_id,
        krx_pw_present=krx_pw,
        openapi_auth_key_present=openapi_key,
        route_credentials_complete=bool(route_credentials_complete),
        authorization_evidence_reference_present=auth_ref_present,
        authorization_evidence_record_validated=auth_record_validated,
        automated_collection_authorized=bool(automated_collection_authorized),
        exact_service_mapping_confirmed=bool(exact_service_mapping_confirmed),
        explicit_probe_consent_present=explicit_consent,
        request_attempt_authorized=request_authorized,
        gate_a_status_hint="PARTIAL" if request_authorized else "BLOCKED",
        missing_requirements=tuple(missing),
        alpha_or_final_judge_promotion_authorized=False,
        bulk_historical_acquisition_authorized=False,
        sealed_holdout_authorized=False,
        live_trading_authorized=False,
    )
    out = asdict(result)
    out["missing_requirements"] = list(result.missing_requirements)
    out["guardrail"] = (
        "Credentials are not authorization, an opaque reference is not validated evidence, and authorization metadata is not runtime consent. For the Data Marketplace web-session route, ordinary account access is insufficient: explicit KRX permission for automated collection must also be present in the validated evidence. "
        "A separately validated structured evidence record plus the exact explicit-consent sentinel are required before one declared tiny request. "
        "Gate A remains at most PARTIAL and all bulk/performance/holdout/promotion/live authorities remain false."
    )
    return out
