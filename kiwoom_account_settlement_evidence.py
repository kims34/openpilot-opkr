"""Offline fail-closed normalization of Kiwoom account settlement snapshots.

No network/authentication/order capability. This parser only prepares exact broker
fields for later independently authenticated provenance and settlement admission.
"""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


class SettlementEvidenceError(ValueError):
    pass


def _require(condition):
    if not condition:
        raise SettlementEvidenceError("ACCOUNT_SETTLEMENT_EVIDENCE_BLOCKED")


def _decimal_text(value):
    _require(type(value) is str and value.strip() == value and value != "")
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
    available_cash_krw: Decimal
    withdrawable_cash_krw: Decimal
    d2_estimated_cash_krw: Decimal

    def report(self):
        return {
            "mode": "OFFLINE_ACCOUNT_SETTLEMENT_NORMALIZATION",
            "account_fingerprint": self.account_fingerprint,
            "captured_at": self.captured_at,
            "available_cash_krw": str(self.available_cash_krw),
            "withdrawable_cash_krw": str(self.withdrawable_cash_krw),
            "d2_estimated_cash_krw": str(self.d2_estimated_cash_krw),
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
    _require(type(account_fingerprint) is str and 16 <= len(account_fingerprint) <= 128)
    _require(account_fingerprint.strip() == account_fingerprint)
    _require(type(captured_at) is str and captured_at.endswith(("+09:00", "Z")))

    # Reviewed Kiwoom schema names. Absence is fail-closed rather than inferred.
    required = ("entr", "pymn_alow_amt", "d2_entra")
    _require(all(k in row for k in required))
    available = _decimal_text(row["entr"])
    withdrawable = _decimal_text(row["pymn_alow_amt"])
    d2 = _decimal_text(row["d2_entra"])
    _require(available >= 0 and withdrawable >= 0 and d2 >= 0)

    return AccountSettlementSnapshot(
        account_fingerprint=account_fingerprint,
        captured_at=captured_at,
        available_cash_krw=available,
        withdrawable_cash_krw=withdrawable,
        d2_estimated_cash_krw=d2,
    )
