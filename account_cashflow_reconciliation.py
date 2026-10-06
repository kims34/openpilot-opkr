"""Broker-neutral offline settlement ledger comparison; no origin admission.

Only independently mapped, net SETTLED cash movements belong here. Unsettled
fills, expected sale proceeds and D+2 estimates are never credited. Net deltas
already include fees/tax; recorded costs are not subtracted a second time.
Completeness and mapping semantics require external attestation. Exact local
arithmetic is a necessary consistency check, never independent account proof.
"""
from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from fractions import Fraction
import re

from account_settlement_binding import bind_journal_settlement_to_early_live
from kiwoom_account_settlement_evidence import AccountSettlementSnapshot


class CashflowReconciliationError(ValueError):
    pass


def require(value):
    if not value:
        raise CashflowReconciliationError('CASHFLOW_RECONCILIATION_BLOCKED')


def instant(value):
    require(type(value) is str)
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise CashflowReconciliationError('CASHFLOW_RECONCILIATION_BLOCKED') from None
    require(result.tzinfo is not None and result.utcoffset() is not None)
    return result


def account(value):
    require(type(value) is str and re.fullmatch(r'(?:sha256:)?[0-9a-f]{64}', value))
    return value.removeprefix('sha256:')


def money(value):
    require(type(value) is Decimal and value.is_finite())
    # Fraction(Decimal) preserves every digit regardless of Decimal context.
    return Fraction(value)


@dataclass(frozen=True)
class SettledCashMovement:
    transaction_id: str
    account_fingerprint: str
    settled_at: str
    net_cash_delta_krw: Decimal
    fees_tax_krw: Decimal


@dataclass(frozen=True)
class CashflowReconciliation:
    closing_snapshot: AccountSettlementSnapshot
    cash_balance_matched: bool
    complete_settlement_scope_attested: bool
    signed_net_mapping_attested: bool
    fees_tax_completeness_attested: bool
    unique_movement_count: int
    duplicate_delivery_count: int

    @property
    def fields_consistent(self):
        return (self.cash_balance_matched and self.complete_settlement_scope_attested
                and self.signed_net_mapping_attested and self.fees_tax_completeness_attested)

    def report(self):
        return dict(mode='OFFLINE_ACCOUNT_CASHFLOW_RECONCILIATION',
                    cash_balance_matched=self.cash_balance_matched,
                    settlement_fields_consistent=self.fields_consistent,
                    unique_movement_count=self.unique_movement_count,
                    duplicate_delivery_count=self.duplicate_delivery_count,
                    source_account_origin_authenticated=False,
                    account_settlement_admitted=False,
                    genuine_live_provenance_verified=False,
                    real_orders_authorized=False, broker_request_sent=False,
                    funds_movement_attempted=False)


def reconcile_settled_cashflow(opening, closing, movements, *,
                              complete_settlement_scope_attested=False,
                              signed_net_mapping_attested=False,
                              fees_tax_completeness_attested=False):
    require(type(opening) is AccountSettlementSnapshot and type(closing) is AccountSettlementSnapshot)
    flags = (complete_settlement_scope_attested, signed_net_mapping_attested,
             fees_tax_completeness_attested)
    require(all(type(flag) is bool for flag in flags))
    require(type(movements) in (list, tuple))
    scope = account(opening.account_fingerprint)
    require(account(closing.account_fingerprint) == scope)
    start, end = instant(opening.captured_at), instant(closing.captured_at)
    require(start < end)
    require(money(opening.deposit_cash_krw) >= 0 and money(closing.deposit_cash_krw) >= 0)
    seen, duplicates = {}, 0
    for item in movements:
        require(type(item) is SettledCashMovement)
        require(type(item.transaction_id) is str and bool(item.transaction_id.strip())
                and item.transaction_id.strip() == item.transaction_id)
        require(account(item.account_fingerprint) == scope)
        timestamp = instant(item.settled_at)
        require(start < timestamp <= end)
        delta, fees = money(item.net_cash_delta_krw), money(item.fees_tax_krw)
        require(fees >= 0)
        payload = (timestamp, delta, fees)
        if item.transaction_id in seen:
            require(seen[item.transaction_id] == payload)
            duplicates += 1
        else:
            seen[item.transaction_id] = payload
    total = sum((row[1] for row in seen.values()), Fraction(0))
    matched = money(closing.deposit_cash_krw) - money(opening.deposit_cash_krw) == total
    return CashflowReconciliation(closing, matched, *flags, len(seen), duplicates)


def bind_reconciled_cashflow_to_early_live(base, settlement, snapshot, journal, cashflow, **scope):
    """Cashflow mismatch may only veto external admission; never create it."""
    require(type(cashflow) is CashflowReconciliation)
    # A matching report for another account/time/balance cannot be replayed
    # into this journal-backed settlement view.
    require(cashflow.closing_snapshot == snapshot)
    require(all(type(v) is bool for v in (cashflow.cash_balance_matched,
                cashflow.complete_settlement_scope_attested, cashflow.signed_net_mapping_attested,
                cashflow.fees_tax_completeness_attested)))
    effective = replace(settlement,
                        settlement_fields_verified=settlement.settlement_fields_verified and cashflow.fields_consistent)
    return bind_journal_settlement_to_early_live(base, effective, snapshot, journal, **scope)
