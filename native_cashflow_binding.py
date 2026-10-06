"""Offline coverage binding for externally reviewed native settlement rows.

This does not decode undocumented direction/currency/time codes. A review
supplies independently established settled KRW net movements or an exclusion.
Local coverage and arithmetic cannot authenticate that review or its origin.
"""
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from account_cashflow_reconciliation import (
    account, instant, require, reconcile_settled_cashflow, SettledCashMovement)
from kiwoom_account_settlement_evidence import AccountSettlementSnapshot
from kiwoom_settlement_history import SettlementHistoryBatch, NativeSettlementTransaction, native_day


@dataclass(frozen=True)
class ReviewedNativeCashflow:
    native_record: NativeSettlementTransaction
    disposition: str
    movement: SettledCashMovement | None = None


def reconcile_reviewed_native_history(batch, opening, closing, reviews, *,
        complete_settlement_scope_attested=False, signed_net_mapping_attested=False,
        fees_tax_completeness_attested=False, exclusions_attested=False):
    """One exact review per native row; unreviewed rows cannot disappear.

    NON_CASH and OUTSIDE_WINDOW are externally reviewed classifications, not
    inferred from broker names, codes, trade dates or processing timestamps.
    Missing exclusion evidence vetoes consistency even when balances match.
    """
    require(type(batch) is SettlementHistoryBatch)
    require(type(opening) is AccountSettlementSnapshot and type(closing) is AccountSettlementSnapshot)
    require(type(reviews) in (list, tuple))
    require(all(type(flag) is bool for flag in (complete_settlement_scope_attested,
        signed_net_mapping_attested, fees_tax_completeness_attested, exclusions_attested)))
    require(account(batch.account_fingerprint) == account(opening.account_fingerprint))
    require(account(batch.account_fingerprint) == account(closing.account_fingerprint))
    start, end = instant(opening.captured_at), instant(closing.captured_at)
    require(start < end <= instant(batch.captured_at))
    query = dict(batch.request_fields)
    korea = ZoneInfo('Asia/Seoul')
    try:
        start_day, end_day = start.astimezone(korea).date(), end.astimezone(korea).date()
    except OverflowError:
        # A parseable timestamp can exceed datetime's range on conversion.
        require(False)
    require(native_day(query['strt_dt']) <= start_day)
    require(native_day(query['end_dt']) >= end_day)
    require(query['tp'] == '0' and query['gds_tp'] == '0' and query['dmst_stex_tp'] == '%')
    require(all(query[field] == '' for field in ('stk_cd', 'crnc_cd', 'frgn_stex_code')))
    require(type(batch.records) is tuple and all(type(row) is NativeSettlementTransaction for row in batch.records))
    require(len(set(batch.records)) == len(batch.records))
    expected, reviewed, movements, movement_ids = set(batch.records), set(), [], set()
    exclusions = 0
    for review in reviews:
        require(type(review) is ReviewedNativeCashflow)
        require(type(review.native_record) is NativeSettlementTransaction)
        require(review.native_record in expected and review.native_record not in reviewed)
        reviewed.add(review.native_record)
        require(review.disposition in ('SETTLED_KRW_NET', 'NON_CASH', 'OUTSIDE_WINDOW'))
        if review.disposition == 'SETTLED_KRW_NET':
            require(type(review.movement) is SettledCashMovement)
            # Distinct native rows cannot silently collapse under one local ID.
            require(review.movement.transaction_id not in movement_ids)
            movement_ids.add(review.movement.transaction_id)
            movements.append(review.movement)
        else:
            require(review.movement is None)
            exclusions += 1
    require(reviewed == expected)
    return reconcile_settled_cashflow(opening, closing, movements,
        complete_settlement_scope_attested=(complete_settlement_scope_attested
            and (not exclusions or exclusions_attested)),
        signed_net_mapping_attested=signed_net_mapping_attested,
        fees_tax_completeness_attested=fees_tax_completeness_attested)
