from pathlib import Path


ROOT = Path(__file__).parent


def _read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_master_spec_records_frozen_project_execution_protocol():
    text = _read("INDEXALERT_MASTER_SPEC.md")
    assert "Frozen empirical execution-sufficiency protocol" in text
    assert "INDEXALERT_EXECUTION_SUFFICIENCY_PROTOCOL.md" in text
    assert "INDEXALERT_EXECUTION_SUFFICIENCY_PROTOCOL.json" in text
    assert "600" in text
    assert "200 distinct decision dates" in text
    assert "0.0005" in text
    assert "sealed_holdout_authorized=false" in text
    assert "live_trading_authorized=false" in text


def test_status_snapshot_contract_and_ledger_do_not_reopen_frozen_protocol():
    status = _read("INDEXALERT_RESEARCH_STATUS.md")
    snapshot = _read("INDEXALERT_CONTINUITY_SNAPSHOT.md")
    contract = _read("INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md")
    ledger = _read("INDEXALERT_RESEARCH_LEDGER.md")

    assert "project v1 frozen, genuine LIVE not yet observed" in status
    assert "project thresholds not yet frozen" not in status

    assert "project v1 FROZEN, genuine LIVE not yet observed" in snapshot
    assert "project criteria NOT FROZEN" not in snapshot
    assert "DONE — frozen project execution-sufficiency protocol" in snapshot

    assert "canonical IndexAlert project thresholds are frozen" in contract
    assert "no genuine staged LIVE evidence window and no independent broker-native provenance admission exist yet" in contract

    assert "Execution-sufficiency project protocol v1" in ledger
    assert "600 LIVE observations" in ledger
    assert "genuine LIVE execution evidence" in ledger


def test_docs_preserve_holdout_and_live_order_guardrails():
    for name in [
        "INDEXALERT_MASTER_SPEC.md",
        "INDEXALERT_RESEARCH_STATUS.md",
        "INDEXALERT_CONTINUITY_SNAPSHOT.md",
        "INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md",
    ]:
        text = _read(name)
        assert "sealed holdout" in text.lower()
        assert "live" in text.lower()

    master = _read("INDEXALERT_MASTER_SPEC.md")
    snapshot = _read("INDEXALERT_CONTINUITY_SNAPSHOT.md")
    assert "one-shot" in master.lower()
    assert "untouched" in snapshot.lower()
    assert "LIVE ORDERING — disabled" in snapshot


def test_live_execution_provenance_is_required_before_project_blocker_closure():
    master = _read("INDEXALERT_MASTER_SPEC.md")
    status = _read("INDEXALERT_RESEARCH_STATUS.md")
    snapshot = _read("INDEXALERT_CONTINUITY_SNAPSHOT.md")
    contract = _read("INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md")
    provenance = _read("INDEXALERT_LIVE_EXECUTION_PROVENANCE_CONTRACT.md")

    assert "execution_metric_gates_passed" in master
    assert "execution_metric_sufficiency_assessed=true" in master
    assert "empirical_execution_sufficiency_assessed=false" in provenance
    assert "INDEXALERT_LIVE_EXECUTION_PROVENANCE_CONTRACT.md" in master
    assert "genuine_live_provenance_verified=false" in status
    assert "broker-native provenance admission" in snapshot
    assert "self-authored or unit-test rows" in contract
    assert "A file hash proves byte identity only" in provenance
    assert "empirical_execution_blocker_closed=false" in provenance
    assert "Current automated real-account ordering remains disabled" in provenance
