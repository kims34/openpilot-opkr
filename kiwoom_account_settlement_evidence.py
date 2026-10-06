"""Offline fail-closed normalization of Kiwoom account settlement snapshots.

No network/authentication/order capability. This parser only prepares exact broker
fields for later independently authenticated provenance and settlement admission.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re

OFFICIAL_SCHEMA_COMMIT = "953e5dbff123f437ab4d11a78a95191a685eb51f"


class SettlementEvidenceError(ValueError):
    pass


def _require(condition):
    if not condition:
        raise SettlementEvidenceError("ACCOUNT_SETTLEMENT_EVIDENCE_BLOCKED")


def _decimal_text(value):
    _require(type(value) is str and value.strip() == value and value != "")
    # Do not reinterpret Python-only separators or Unicode digit aliases as
    # native cash bytes. Existing ASCII Decimal notation stays supported.
    _require(value.isascii() and '_' not in value)
    # Commas must represent complete thousands groups, never arbitrary
    # characters to discard. Preserve the existing comma-free Decimal path.
    _require(',' not in value or re.fullmatch(r'[+-]?[0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]+)?', value))
    try:
        parsed = Decimal(value.replace(",", ""))
    except (InvalidOperation, ValueError):
        raise SettlementEvidenceError("ACCOUNT_SETTLEMENT_EVIDENCE_BLOCKED") from None
    _require(parsed.is_finite())
    return parsed


@dataclass(frozen=True)
class AccountSettlementSnapshot:
    account_fingerprint: str
    captured_at: str
    deposit_cash_krw: Decimal
    withdrawable_cash_krw: Decimal
    d2_estimated_cash_krw: Decimal
    orderable_amount_krw: Decimal

    def report(self):
        return {
            "mode": "OFFLINE_ACCOUNT_SETTLEMENT_NORMALIZATION",
            "account_fingerprint": self.account_fingerprint,
            "captured_at": self.captured_at,
            "deposit_cash_krw": str(self.deposit_cash_krw),
            "withdrawable_cash_krw": str(self.withdrawable_cash_krw),
            "d2_estimated_cash_krw": str(self.d2_estimated_cash_krw),
            "orderable_amount_krw": str(self.orderable_amount_krw),
            "source_api": "kt00001",
            "official_schema_commit": OFFICIAL_SCHEMA_COMMIT,
            "buying_power_verified": False,
            "source_account_origin_authenticated": False,
            "snapshot_freshness_attested": False,
            "trading_date_origin_attested": False,
            "account_settlement_admitted": False,
            "genuine_live_provenance_verified": False,
            "real_orders_authorized": False,
        }


def normalize_kt00001_settlement(row, *, account_fingerprint, captured_at):
    """Normalize reviewed kt00001 cash/settlement fields without admitting origin."""
    _require(type(row) is dict)
    _require(type(account_fingerprint) is str and
             re.fullmatch(r'(?:sha256:)?[0-9a-f]{64}', account_fingerprint) is not None)
    _require(type(captured_at) is str and captured_at.strip() == captured_at)
    try:
        captured = datetime.fromisoformat(captured_at.replace('Z', '+00:00'))
        _require(captured.tzinfo is not None and captured.utcoffset() is not None)
    except ValueError:
        raise SettlementEvidenceError("ACCOUNT_SETTLEMENT_EVIDENCE_BLOCKED") from None

    # Reviewed Kiwoom schema names. Absence is fail-closed rather than inferred.
    # entr is deposit balance, NOT orderable funds. D+2 is estimated,
    # NOT settled cash. ord_alow_amt is a separate broker-reported amount;
    # this normalization never attests usable cash, margin or buying power.
    required = ("entr", "pymn_alow_amt", "d2_entra", "ord_alow_amt")
    _require(all(k in row for k in required))
    deposit = _decimal_text(row["entr"])
    withdrawable = _decimal_text(row["pymn_alow_amt"])
    d2 = _decimal_text(row["d2_entra"])
    orderable = _decimal_text(row["ord_alow_amt"])
    _require(deposit >= 0 and withdrawable >= 0 and d2 >= 0 and orderable >= 0)

    return AccountSettlementSnapshot(
        account_fingerprint=account_fingerprint,
        captured_at=captured_at,
        deposit_cash_krw=deposit,
        withdrawable_cash_krw=withdrawable,
        d2_estimated_cash_krw=d2,
        orderable_amount_krw=orderable,
    )
