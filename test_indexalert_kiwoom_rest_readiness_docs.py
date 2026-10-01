from pathlib import Path


ROOT = Path(__file__).resolve().parent
READINESS = (ROOT / "INDEXALERT_KIWOOM_REST_READINESS_CONTRACT.md").read_text(encoding="utf-8")
BROKER = (ROOT / "INDEXALERT_BROKER_EXECUTION_CONTRACT.md").read_text(encoding="utf-8")
PROVENANCE = (ROOT / "INDEXALERT_LIVE_EXECUTION_PROVENANCE_CONTRACT.md").read_text(encoding="utf-8")


def test_kiwoom_readiness_is_explicitly_non_ordering_and_fail_closed():
    required = (
        "READ-ONLY / DEMO PREPARATION ONLY — REAL-ACCOUNT ORDERING DISABLED",
        "genuine_live_provenance_verified=false",
        "empirical_execution_sufficiency_assessed=false",
        "sealed_holdout_authorized=false",
        "live_trading_authorized=false",
        "demo/paper observations must never be relabelled `PROSPECTIVE_LIVE_EXECUTION_LOG`",
        "possession of REAL credentials alone does not authorize a REAL request or any order submission",
        "Real-account order submission remains disabled",
        "The sealed holdout remains untouched",
    )
    for marker in required:
        assert marker in READINESS


def test_kiwoom_official_schema_snapshot_contains_provenance_identifiers():
    required = (
        "Kiwoom-Securities/Kiwoom-REST-API",
        "953e5dbff123f437ab4d11a78a95191a685eb51f",
        "`ka00001`",
        "`kt00007`",
        "`ka10076`",
        "execution/fill number (`909`)",
        "`ord_no`",
        "`cntr_qty`",
        "`tdy_trde_cmsn`",
        "`tdy_trde_tax`",
    )
    for marker in required:
        assert marker in READINESS


def test_demo_and_historical_real_data_cannot_bypass_prospective_live_admission():
    assert "demo/paper observations cannot satisfy the frozen execution-sufficiency sample or metric gates" in READINESS
    assert "They do **not** automatically count toward the frozen prospective execution-sufficiency window" in READINESS
    assert "Only observations generated under the frozen decision/execution policies and admitted by the provenance contract may enter that window" in READINESS


def test_existing_broker_and_provenance_contracts_remain_authoritative():
    assert "Default is `MASTER_OFF`" in BROKER
    assert "Do not start real-order implementation now." in BROKER
    assert "source label" in PROVENANCE.lower()
    assert "broker-native" in PROVENANCE.lower()
