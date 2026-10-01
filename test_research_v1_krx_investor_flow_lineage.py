import pandas as pd
import pytest

from research_v1_krx_investor_flow_lineage import (
    KRXInvestorFlowLineageError,
    attach_decision_eligibility,
    audit_investor_flow_lineage,
    normalise_investor_flow_lineage,
)
from research_v1_krx_public_evidence import public_evidence_fingerprint_sha256


SOURCE_FP = "a" * 64


def _valid_row(**overrides):
    row = {
        "symbol": "005930",
        "isu_cd": "KR7005930003",
        "event_time": "2026-09-23T15:30:00+09:00",
        "published_at": "2026-09-23T20:00:00+09:00",
        "available_at": "2026-09-23T20:05:00+09:00",
        "ingested_at": "2026-09-23T20:10:00+09:00",
        "source_contract_fingerprint_sha256": SOURCE_FP,
        "public_contract_evidence_fingerprint_sha256": public_evidence_fingerprint_sha256(),
    }
    row.update(overrides)
    return row


def test_valid_lineage_is_structurally_valid_but_not_performance_authority():
    lineage = normalise_investor_flow_lineage(pd.DataFrame([_valid_row()]))
    assert lineage["lineage_validated"].tolist() == [True]
    assert lineage.loc[0, "publication_floor_kst"].isoformat() == "2026-09-23T20:00:00+09:00"

    audit = audit_investor_flow_lineage(lineage)
    assert audit["lineage_structurally_valid"] is True
    assert audit["chronology_valid"] is True
    assert audit["publication_floor_valid"] is True
    assert audit["public_contract_evidence_matches_current"] is True
    assert audit["feature_performance_testing_authorized"] is False
    assert audit["sealed_holdout_authorized"] is False


def test_naive_timestamp_is_rejected():
    with pytest.raises(KRXInvestorFlowLineageError, match="timezone-aware"):
        normalise_investor_flow_lineage(
            pd.DataFrame([_valid_row(published_at="2026-09-23T20:00:00")])
        )


def test_publication_before_20_kst_is_rejected():
    with pytest.raises(KRXInvestorFlowLineageError, match="publication.*floor|published_at violates"):
        normalise_investor_flow_lineage(
            pd.DataFrame([_valid_row(published_at="2026-09-23T19:59:59+09:00")])
        )


def test_later_day_publication_is_allowed():
    lineage = normalise_investor_flow_lineage(
        pd.DataFrame([
            _valid_row(
                published_at="2026-09-24T08:00:00+09:00",
                available_at="2026-09-24T08:01:00+09:00",
                ingested_at="2026-09-24T08:02:00+09:00",
            )
        ])
    )
    assert bool(lineage.loc[0, "lineage_validated"])


def test_available_before_publication_is_rejected():
    with pytest.raises(KRXInvestorFlowLineageError, match="chronology violation"):
        normalise_investor_flow_lineage(
            pd.DataFrame([
                _valid_row(
                    published_at="2026-09-23T20:10:00+09:00",
                    available_at="2026-09-23T20:09:59+09:00",
                )
            ])
        )


def test_ingested_before_available_is_rejected():
    with pytest.raises(KRXInvestorFlowLineageError, match="chronology violation"):
        normalise_investor_flow_lineage(
            pd.DataFrame([
                _valid_row(
                    available_at="2026-09-23T20:10:00+09:00",
                    ingested_at="2026-09-23T20:09:59+09:00",
                )
            ])
        )


def test_decision_before_availability_is_ineligible_and_after_is_eligible():
    lineage = normalise_investor_flow_lineage(pd.DataFrame([_valid_row()]))

    before = attach_decision_eligibility(
        lineage, "2026-09-23T20:04:59+09:00"
    )
    after = attach_decision_eligibility(
        lineage, "2026-09-23T20:05:00+09:00"
    )
    assert before["eligible_at_decision"].tolist() == [False]
    assert after["eligible_at_decision"].tolist() == [True]


def test_decision_timestamp_must_be_timezone_aware():
    lineage = normalise_investor_flow_lineage(pd.DataFrame([_valid_row()]))
    with pytest.raises(KRXInvestorFlowLineageError, match="timezone-aware"):
        attach_decision_eligibility(lineage, "2026-09-24T09:00:00")


def test_missing_stable_issue_mapping_is_rejected():
    with pytest.raises(KRXInvestorFlowLineageError, match="isu_cd is missing"):
        normalise_investor_flow_lineage(pd.DataFrame([_valid_row(isu_cd="")]))


def test_mixed_source_contract_fingerprints_are_rejected():
    with pytest.raises(KRXInvestorFlowLineageError, match="mixes multiple source-contract"):
        normalise_investor_flow_lineage(
            pd.DataFrame([
                _valid_row(symbol="005930", isu_cd="KR7005930003"),
                _valid_row(
                    symbol="000660",
                    isu_cd="KR7000660001",
                    source_contract_fingerprint_sha256="b" * 64,
                ),
            ])
        )


def test_stale_public_contract_evidence_fingerprint_is_rejected():
    with pytest.raises(KRXInvestorFlowLineageError, match="does not match the current"):
        normalise_investor_flow_lineage(
            pd.DataFrame([
                _valid_row(public_contract_evidence_fingerprint_sha256="f" * 64)
            ])
        )


def test_missing_required_lineage_column_is_rejected():
    row = _valid_row()
    del row["available_at"]
    with pytest.raises(KRXInvestorFlowLineageError, match="missing required columns"):
        normalise_investor_flow_lineage(pd.DataFrame([row]))
