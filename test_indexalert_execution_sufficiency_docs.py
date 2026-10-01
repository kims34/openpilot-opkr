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

    assert "canonical IndexAlert project thresholds are now frozen" in contract
    assert "genuine staged LIVE evidence has not been collected or assessed" in contract

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
