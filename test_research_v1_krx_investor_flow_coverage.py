import pandas as pd
import pytest

from research_v1_krx_investor_flow_coverage import (
    KRXInvestorFlowCoverageError,
    audit_investor_flow_coverage,
    normalise_expected_investor_flow_scope,
)
from research_v1_krx_investor_flow_lineage import normalise_investor_flow_lineage
from research_v1_krx_public_evidence import public_evidence_fingerprint_sha256


SOURCE_FP = "a" * 64
SCOPE_FP = "c" * 64


def _lineage_row(symbol="005930", isu_cd="KR7005930003", event_date="2026-09-23"):
    return {
        "symbol": symbol,
        "isu_cd": isu_cd,
        "event_time": f"{event_date}T15:30:00+09:00",
        "published_at": f"{event_date}T20:00:00+09:00",
        "available_at": f"{event_date}T20:05:00+09:00",
        "ingested_at": f"{event_date}T20:10:00+09:00",
        "source_contract_fingerprint_sha256": SOURCE_FP,
        "public_contract_evidence_fingerprint_sha256": public_evidence_fingerprint_sha256(),
    }


def _scope_row(symbol="005930", isu_cd="KR7005930003", event_date="2026-09-23", **overrides):
    row = {
        "event_date": event_date,
        "symbol": symbol,
        "isu_cd": isu_cd,
        "common_stock_identity_official": True,
        "scope_contract_fingerprint_sha256": SCOPE_FP,
    }
    row.update(overrides)
    return row


def test_exact_attested_key_coverage_is_structurally_complete_only():
    scope = pd.DataFrame([
        _scope_row(),
        _scope_row("000660", "KR7000660001"),
    ])
    lineage = normalise_investor_flow_lineage(pd.DataFrame([
        _lineage_row(),
        _lineage_row("000660", "KR7000660001"),
    ]))

    out = audit_investor_flow_coverage(scope, lineage)
    assert out["exact_key_coverage"] is True
    assert out["coverage_structurally_complete"] is True
    assert out["missing_key_count"] == 0
    assert out["extra_key_count"] == 0
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False


def test_missing_expected_key_does_not_become_implicit_zero():
    scope = pd.DataFrame([
        _scope_row(),
        _scope_row("000660", "KR7000660001"),
    ])
    lineage = normalise_investor_flow_lineage(pd.DataFrame([_lineage_row()]))

    out = audit_investor_flow_coverage(scope, lineage)
    assert out["coverage_structurally_complete"] is False
    assert out["missing_key_count"] == 1
    assert out["extra_key_count"] == 0
    assert out["feature_performance_testing_authorized"] is False


def test_observed_key_outside_attested_scope_is_not_silently_accepted():
    scope = pd.DataFrame([_scope_row()])
    lineage = normalise_investor_flow_lineage(pd.DataFrame([
        _lineage_row(),
        _lineage_row("000660", "KR7000660001"),
    ]))

    out = audit_investor_flow_coverage(scope, lineage)
    assert out["coverage_structurally_complete"] is False
    assert out["missing_key_count"] == 0
    assert out["extra_key_count"] == 1


def test_duplicate_observed_event_security_key_is_rejected():
    scope = pd.DataFrame([_scope_row()])
    lineage = normalise_investor_flow_lineage(pd.DataFrame([
        _lineage_row(),
        _lineage_row(),
    ]))
    with pytest.raises(KRXInvestorFlowCoverageError, match="duplicate event/security"):
        audit_investor_flow_coverage(scope, lineage)


def test_duplicate_expected_scope_key_is_rejected():
    with pytest.raises(KRXInvestorFlowCoverageError, match="duplicate keys"):
        normalise_expected_investor_flow_scope(
            pd.DataFrame([_scope_row(), _scope_row()])
        )


def test_non_common_or_unattested_security_is_rejected_from_expected_scope():
    with pytest.raises(KRXInvestorFlowCoverageError, match="non-common/unattested"):
        normalise_expected_investor_flow_scope(
            pd.DataFrame([_scope_row(common_stock_identity_official=False)])
        )


def test_expected_scope_requires_boolean_common_stock_attestation():
    with pytest.raises(KRXInvestorFlowCoverageError, match="must be bool"):
        normalise_expected_investor_flow_scope(
            pd.DataFrame([_scope_row(common_stock_identity_official="True")])
        )


def test_expected_scope_cannot_mix_scope_contract_fingerprints():
    with pytest.raises(KRXInvestorFlowCoverageError, match="mixes multiple"):
        normalise_expected_investor_flow_scope(
            pd.DataFrame([
                _scope_row(),
                _scope_row(
                    "000660",
                    "KR7000660001",
                    scope_contract_fingerprint_sha256="d" * 64,
                ),
            ])
        )


def test_expected_event_date_with_intraday_time_is_rejected_not_truncated():
    with pytest.raises(KRXInvestorFlowCoverageError, match="date/midnight"):
        normalise_expected_investor_flow_scope(
            pd.DataFrame([_scope_row(event_date="2026-09-23T09:00:00")])
        )


def test_symbol_issue_mapping_mismatch_appears_as_missing_and_extra():
    scope = pd.DataFrame([_scope_row("005930", "KR7005930003")])
    lineage = normalise_investor_flow_lineage(
        pd.DataFrame([_lineage_row("005930", "KR7000660001")])
    )
    out = audit_investor_flow_coverage(scope, lineage)
    assert out["coverage_structurally_complete"] is False
    assert out["missing_key_count"] == 1
    assert out["extra_key_count"] == 1
