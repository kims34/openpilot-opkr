from pathlib import Path


AUDIT = Path("INDEXALERT_PHYSICAL_E2E_AUDIT.md")
STATUS = Path("INDEXALERT_RESEARCH_STATUS.md")
SNAPSHOT = Path("INDEXALERT_CONTINUITY_SNAPSHOT.md")

EXPECTED_BUILD = "4.7-47"
EXPECTED_SERVER_REVISION = "d8523810b1c2c092a9ffc8f6245586e3bb719645"
EXPECTED_CONTRACTS = (
    "register-client-build-v1",
    "android-register-direct-v1",
    "registered-device-build-receipt-v1",
    "physical-e2e-blocker-v1",
)


def _read(path: Path) -> str:
    assert path.exists(), f"missing canonical Physical E2E document: {path}"
    return path.read_text(encoding="utf-8")


def test_physical_e2e_canonical_documents_agree_on_confirmed_build_and_revision():
    docs = {
        "audit": _read(AUDIT),
        "status": _read(STATUS),
        "snapshot": _read(SNAPSHOT),
    }
    for name, text in docs.items():
        assert EXPECTED_BUILD in text, f"{name} lost audited Android build"
        assert EXPECTED_SERVER_REVISION in text, f"{name} lost audited production revision"
        assert "CONFIRMED" in text, f"{name} lost confirmed Physical E2E state"
        for contract in EXPECTED_CONTRACTS:
            assert contract in text, f"{name} lost frozen contract {contract}"


def test_physical_e2e_audit_preserves_real_handset_not_provider_send_boundary():
    text = _read(AUDIT)
    assert "POST /register" in text
    assert "POST /push-self-test" in text
    assert "POST /push-ack" in text
    assert "registration_device_matches_self_test = true" in text
    assert "registration_build_matches_self_test = true" in text
    assert "current_build_physical_e2e_confirmed = true" in text
    assert "Provider-send success alone was not used as delivery proof" in text
    assert "Raw FCM tokens and event IDs remain private" in text


def test_status_and_snapshot_do_not_reopen_completed_handset_blocker():
    status = _read(STATUS)
    snapshot = _read(SNAPSHOT)

    assert "Physical E2E state — CONFIRMED" in status
    assert "Physical notification E2E: **DONE" in status
    assert "Physical E2E — DONE for audited v4.7-47" in snapshot
    assert "DONE — PHYSICAL E2E for audited Android v4.7-47" in snapshot

    # These were the superseded pre-handset states. They may be named in
    # explanatory guardrails elsewhere, but cannot remain the declared current
    # production state after the audited handset ACK.
    assert "Current production observation — Physical E2E still OPEN" not in status
    assert "Current Physical E2E evidence — still OPEN" not in snapshot
    assert "PHYSICAL E2E EXTERNAL HANDSET BLOCKER" not in snapshot


def test_physical_e2e_completion_does_not_grant_research_or_trading_authority():
    audit = _read(AUDIT)
    status = _read(STATUS)
    snapshot = _read(SNAPSHOT)

    assert "It is not Alpha evidence" in audit
    assert "does not authorize live orders" in audit
    assert "sealed one-shot holdout" in audit
    assert "Real-account ordering remains disabled" in status
    assert "Real-account ordering remains disabled" in snapshot
    assert "SEALED HOLDOUT — untouched" in snapshot
