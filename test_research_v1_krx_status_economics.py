import pandas as pd
import pytest

from research_v1_krx_status_economics import (
    KRXStatusEconomicsError,
    audit_exact_status_economics,
)


CONTRACT = "c" * 64


def _expected(rows=None):
    rows = rows or [
        {
            "position_id": "P1",
            "symbol": "005930",
            "event_type": "DELISTING",
            "affected_qty": 10,
            "entry_cost_basis_total": 1000,
            "source_contract_fingerprint": CONTRACT,
        }
    ]
    return pd.DataFrame(rows)


def _evidence(**overrides):
    row = {
        "position_id": "P1",
        "symbol": "005930",
        "event_type": "DELISTING",
        "affected_qty": 10,
        "verified_exit_fill_qty": 0,
        "verified_exit_avg_price": 0,
        "exit_fill_evidence_type": "",
        "exit_fill_evidence_ref": "",
        "verified_recovery_qty": 10,
        "verified_recovery_cash_per_share": 30,
        "recovery_evidence_type": "OFFICIAL_KRX_RECOVERY_RECORD",
        "recovery_evidence_ref": "krx-recovery-record-1",
        "explicit_fees_taxes_total": 0,
        "economic_available_at": "2026-01-03T09:00:00+09:00",
        "source_contract_fingerprint": CONTRACT,
    }
    row.update(overrides)
    return pd.DataFrame([row])


def test_verified_official_recovery_fully_closes_position_economics_only():
    out = audit_exact_status_economics(
        expected_positions=_expected(),
        economics_evidence=_evidence(),
        expected_scope_attested=True,
    )
    assert out["exact_status_economics_ready"] is True
    assert out["unresolved_positions"] == 0
    assert out["unsupported_recovery_evidence_positions"] == 0
    assert out["resolved_position_economics"][0]["verified_recovery_cash"] == "300"
    assert out["resolved_position_economics"][0]["exact_net_return"] == "-0.7"
    assert out["judge_security_status_ready"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["alpha_or_final_judge_promotion_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_live_fill_plus_official_recovery_can_close_split_quantity():
    out = audit_exact_status_economics(
        expected_positions=_expected(),
        economics_evidence=_evidence(
            verified_exit_fill_qty=4,
            verified_exit_avg_price=50,
            exit_fill_evidence_type="PROSPECTIVE_LIVE_EXECUTION_LOG",
            exit_fill_evidence_ref="broker-fill-123",
            verified_recovery_qty=6,
            verified_recovery_cash_per_share=20,
            explicit_fees_taxes_total=5,
        ),
        expected_scope_attested=True,
    )
    assert out["exact_status_economics_ready"] is True
    row = out["resolved_position_economics"][0]
    assert row["verified_fill_cash"] == "200"
    assert row["verified_recovery_cash"] == "120"
    assert row["verified_net_exit_cash"] == "315"


@pytest.mark.parametrize(
    "evidence_type",
    [
        "BACKTEST_GENERATED_FILL",
        "SYNTHETIC_FILL",
        "MODELLED_FILL",
        "MARKET_OPEN_ASSUMPTION",
        "PROSPECTIVE_SHADOW_DECISION_LOG",
        "PROSPECTIVE_PAPER_EXECUTION_LOG",
        "DAILY_OHLC",
        "MDCSTAT239_DAILY_PRICE_ONLY",
    ],
)
def test_non_live_or_synthetic_fill_sources_cannot_close_exact_economics(evidence_type):
    out = audit_exact_status_economics(
        expected_positions=_expected(),
        economics_evidence=_evidence(
            verified_exit_fill_qty=10,
            verified_exit_avg_price=50,
            exit_fill_evidence_type=evidence_type,
            exit_fill_evidence_ref="not-exact-fill",
            verified_recovery_qty=0,
            verified_recovery_cash_per_share=0,
            recovery_evidence_type="",
            recovery_evidence_ref="",
        ),
        expected_scope_attested=True,
    )
    assert out["exact_status_economics_ready"] is False
    assert out["unsupported_fill_evidence_positions"] == 1


def test_unresolved_quantity_blocks_exact_economics():
    out = audit_exact_status_economics(
        expected_positions=_expected(),
        economics_evidence=_evidence(
            verified_recovery_qty=9,
            verified_recovery_cash_per_share=30,
        ),
        expected_scope_attested=True,
    )
    assert out["exact_status_economics_ready"] is False
    assert out["accounting_mismatch_positions"] == 1
    assert out["unresolved_positions"] == 1


def test_over_resolved_quantity_is_accounting_mismatch():
    out = audit_exact_status_economics(
        expected_positions=_expected(),
        economics_evidence=_evidence(
            verified_exit_fill_qty=5,
            verified_exit_avg_price=40,
            exit_fill_evidence_type="PROSPECTIVE_LIVE_EXECUTION_LOG",
            exit_fill_evidence_ref="fill",
            verified_recovery_qty=6,
        ),
        expected_scope_attested=True,
    )
    assert out["exact_status_economics_ready"] is False
    assert out["accounting_mismatch_positions"] == 1


def test_missing_or_extra_position_evidence_blocks_exact_scope():
    missing = audit_exact_status_economics(
        expected_positions=_expected(),
        economics_evidence=pd.DataFrame(columns=_evidence().columns),
        expected_scope_attested=True,
    )
    assert missing["exact_status_economics_ready"] is False
    assert missing["missing_position_evidence"] == 1

    extra_df = pd.concat(
        [
            _evidence(),
            _evidence(
                position_id="P2",
                symbol="000660",
            ),
        ],
        ignore_index=True,
    )
    extra = audit_exact_status_economics(
        expected_positions=_expected(),
        economics_evidence=extra_df,
        expected_scope_attested=True,
    )
    assert extra["exact_status_economics_ready"] is False
    assert extra["extra_position_evidence"] == 1


def test_expected_scope_must_be_independently_attested_even_when_rows_match():
    out = audit_exact_status_economics(
        expected_positions=_expected(),
        economics_evidence=_evidence(),
        expected_scope_attested=False,
    )
    assert out["exact_status_economics_ready"] is False
    assert out["expected_scope_attested"] is False


def test_empty_attested_expected_scope_can_pass_without_inventing_rows():
    expected = pd.DataFrame(
        columns=[
            "position_id",
            "symbol",
            "event_type",
            "affected_qty",
            "entry_cost_basis_total",
            "source_contract_fingerprint",
        ]
    )
    evidence = pd.DataFrame(columns=_evidence().columns)
    out = audit_exact_status_economics(
        expected_positions=expected,
        economics_evidence=evidence,
        expected_scope_attested=True,
    )
    assert out["exact_status_economics_ready"] is True
    assert out["expected_affected_positions"] == 0
    assert out["observed_positions"] == 0


def test_zero_recovery_value_is_allowed_only_with_verified_recovery_record():
    out = audit_exact_status_economics(
        expected_positions=_expected(),
        economics_evidence=_evidence(verified_recovery_cash_per_share=0),
        expected_scope_attested=True,
    )
    assert out["exact_status_economics_ready"] is True
    assert out["resolved_position_economics"][0]["verified_recovery_cash"] == "0"


def test_wrong_contract_or_naive_pit_timestamp_blocks_exact_economics():
    wrong_contract = audit_exact_status_economics(
        expected_positions=_expected(),
        economics_evidence=_evidence(source_contract_fingerprint="d" * 64),
        expected_scope_attested=True,
    )
    assert wrong_contract["exact_status_economics_ready"] is False
    assert wrong_contract["source_contract_mismatch_positions"] == 1

    naive = audit_exact_status_economics(
        expected_positions=_expected(),
        economics_evidence=_evidence(economic_available_at="2026-01-03T09:00:00"),
        expected_scope_attested=True,
    )
    assert naive["exact_status_economics_ready"] is False
    assert naive["pit_lineage_invalid_positions"] == 1


def test_duplicate_position_ids_fail_closed():
    dup_expected = pd.concat([_expected(), _expected()], ignore_index=True)
    with pytest.raises(KRXStatusEconomicsError, match="duplicate expected"):
        audit_exact_status_economics(
            expected_positions=dup_expected,
            economics_evidence=_evidence(),
            expected_scope_attested=True,
        )

    dup_evidence = pd.concat([_evidence(), _evidence()], ignore_index=True)
    with pytest.raises(KRXStatusEconomicsError, match="duplicate economics"):
        audit_exact_status_economics(
            expected_positions=_expected(),
            economics_evidence=dup_evidence,
            expected_scope_attested=True,
        )
