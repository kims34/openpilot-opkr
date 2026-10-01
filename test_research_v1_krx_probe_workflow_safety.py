from pathlib import Path

import pytest


WORKFLOWS = [
    (
        Path(".github/workflows/indexalert-research-v1-krx-status-source-probe.yml"),
        "Run push-safe dry-run status diagnostic",
        "Run explicitly consented authenticated status probe",
    ),
    (
        Path(".github/workflows/indexalert-research-v1-krx-investor-flow-probe.yml"),
        "Run push-safe dry-run investor-flow diagnostic",
        "Run explicitly consented authenticated investor-flow probe",
    ),
]


@pytest.mark.parametrize("path,dry_name,auth_name", WORKFLOWS)
def test_probe_workflow_keeps_push_dry_and_authenticated_probe_manual_only(path, dry_name, auth_name):
    text = path.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in text
    assert "allow_authenticated_request:" in text
    assert "default: false" in text
    assert "authorization_evidence_reference:" in text

    dry_marker = f"- name: {dry_name}"
    auth_marker = f"- name: {auth_name}"
    upload_marker = "- name: Upload metadata-only"
    assert dry_marker in text
    assert auth_marker in text
    assert upload_marker in text

    dry = text.split(dry_marker, 1)[1].split(auth_marker, 1)[0]
    auth = text.split(auth_marker, 1)[1].split(upload_marker, 1)[0]

    assert "github.event_name != 'workflow_dispatch' || inputs.allow_authenticated_request != true" in dry
    assert "KRX_ID: ''" in dry
    assert "KRX_PW: ''" in dry
    assert "KRX_OPENAPI_AUTH_KEY: ''" in dry
    assert "KRX_AUTH_EVIDENCE_REF: ''" in dry
    assert "KRX_EXPLICIT_PROBE_CONSENT: ''" in dry
    assert "secrets.KRX_ID" not in dry
    assert "secrets.KRX_PW" not in dry

    assert "github.event_name == 'workflow_dispatch' && inputs.allow_authenticated_request == true" in auth
    assert "KRX_ID: ${{ secrets.KRX_ID }}" in auth
    assert "KRX_PW: ${{ secrets.KRX_PW }}" in auth
    assert "KRX_OPENAPI_AUTH_KEY: ''" in auth
    assert "inputs.authorization_evidence_reference || vars.KRX_AUTH_EVIDENCE_REF" in auth
    assert "KRX_EXPLICIT_PROBE_CONSENT: 'ALLOW_TINY_AUTHENTICATED_REQUEST'" in auth

    # Data Marketplace probe workflows must never consume the OpenAPI secret.
    assert "secrets.KRX_OPENAPI_AUTH_KEY" not in text


def test_probe_workflows_do_not_define_job_level_krx_secret_environment():
    for path, _, _ in WORKFLOWS:
        text = path.read_text(encoding="utf-8")
        prefix = text.split("steps:", 1)[0]
        assert "secrets.KRX_ID" not in prefix
        assert "secrets.KRX_PW" not in prefix
        assert "secrets.KRX_OPENAPI_AUTH_KEY" not in prefix
