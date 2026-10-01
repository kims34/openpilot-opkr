import pandas as pd
import pytest

from research_v1_krx_official_status import normalise_basic_info
from research_v1_krx_status_coverage import (
    KRXStatusCoverageError,
    audit_status_identity_coverage,
    normalise_expected_status_scope,
)


SCOPE_FP = "c" * 64


def _scope(symbol="005930", isu_cd="KR7005930003", snapshot_date="2026-09-29", **overrides):
    row = {
        "snapshot_date": snapshot_date,
        "symbol": symbol,
        "isu_cd": isu_cd,
        "scope_contract_fingerprint_sha256": SCOPE_FP,
    }
    row.update(overrides)
    return row


def _observed(symbol="005930", isu_cd="KR7005930003", snapshot_date="2026-09-29", common=True):
    return {
        "decision_date": snapshot_date,
        "symbol": symbol,
        "isu_cd": isu_cd,
        "common_stock_identity_official": common,
        "security_scope_identity_validated": True,
        "available_at": f"{snapshot_date}T20:00:00+09:00",
    }


def test_exact_stable_identity_coverage_is_structural_only():
    scope = pd.DataFrame([
        _scope(),
        _scope("000660", "KR7000660001"),
    ])
    observed = pd.DataFrame([
        _observed(),
        _observed("000660", "KR7000660001"),
    ])
    out = audit_status_identity_coverage(scope, observed)
    assert out["stable_issue_id_present_in_observed"] is True
    assert out["exact_key_coverage"] is True
    assert out["coverage_structurally_complete"] is True
    assert out["judge_security_status_ready"] is False
    assert out["sealed_holdout_authorized"] is False


def test_current_basic_info_shape_without_stable_issue_id_cannot_close_gate_c():
    raw = pd.DataFrame([
        {
            "ISU_SRT_CD": "005930",
            "ISU_NM": "삼성전자",
            "MKT_TP_NM": "KOSPI",
            "SECUGRP_NM": "주권",
            "KIND_STKCERT_TP_NM": "보통주",
            "LIST_DD": "1975/06/11",
        }
    ])
    identity = normalise_basic_info(
        raw,
        asof_date="2026-09-29",
        available_at="2026-09-29T20:00:00+09:00",
    )
    out = audit_status_identity_coverage(pd.DataFrame([_scope()]), identity)
    assert out["stable_issue_id_present_in_observed"] is False
    assert out["exact_key_coverage"] is False
    assert out["coverage_structurally_complete"] is False
    assert out["judge_security_status_ready"] is False


def test_missing_expected_identity_key_remains_incomplete():
    scope = pd.DataFrame([
        _scope(),
        _scope("000660", "KR7000660001"),
    ])
    observed = pd.DataFrame([_observed()])
    out = audit_status_identity_coverage(scope, observed)
    assert out["missing_key_count"] == 1
    assert out["extra_key_count"] == 0
    assert out["coverage_structurally_complete"] is False


def test_symbol_issue_mapping_mismatch_is_missing_plus_extra():
    scope = pd.DataFrame([_scope("005930", "KR7005930003")])
    observed = pd.DataFrame([_observed("005930", "KR7000660001")])
    out = audit_status_identity_coverage(scope, observed)
    assert out["missing_key_count"] == 1
    assert out["extra_key_count"] == 1
    assert out["coverage_structurally_complete"] is False


def test_non_common_observed_security_does_not_fill_common_stock_scope():
    scope = pd.DataFrame([_scope()])
    observed = pd.DataFrame([_observed(common=False)])
    out = audit_status_identity_coverage(scope, observed)
    assert out["observed_common_stock_records"] == 0
    assert out["coverage_structurally_complete"] is False


def test_unvalidated_identity_row_is_rejected():
    observed = pd.DataFrame([_observed()])
    observed.loc[0, "security_scope_identity_validated"] = False
    with pytest.raises(KRXStatusCoverageError, match="unvalidated identity"):
        audit_status_identity_coverage(pd.DataFrame([_scope()]), observed)


def test_naive_availability_timestamp_is_rejected():
    observed = pd.DataFrame([_observed()])
    observed.loc[0, "available_at"] = "2026-09-29T20:00:00"
    with pytest.raises(KRXStatusCoverageError, match="timezone-aware"):
        audit_status_identity_coverage(pd.DataFrame([_scope()]), observed)


def test_duplicate_observed_stable_identity_key_is_rejected():
    observed = pd.DataFrame([_observed(), _observed()])
    with pytest.raises(KRXStatusCoverageError, match="duplicate snapshot/security"):
        audit_status_identity_coverage(pd.DataFrame([_scope()]), observed)


def test_expected_scope_mixed_contract_fingerprints_are_rejected():
    with pytest.raises(KRXStatusCoverageError, match="mixes multiple"):
        normalise_expected_status_scope(
            pd.DataFrame([
                _scope(),
                _scope(
                    "000660",
                    "KR7000660001",
                    scope_contract_fingerprint_sha256="d" * 64,
                ),
            ])
        )


def test_expected_snapshot_intraday_time_is_rejected_not_truncated():
    with pytest.raises(KRXStatusCoverageError, match="date/midnight"):
        normalise_expected_status_scope(
            pd.DataFrame([_scope(snapshot_date="2026-09-29T09:00:00")])
        )
