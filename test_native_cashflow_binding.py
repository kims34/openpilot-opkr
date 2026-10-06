"""Synthetic externally reviewed mapping fixtures; no native proof claims."""
import unittest
from dataclasses import replace
from decimal import Decimal
import test_kiwoom_settlement_history as history_fixtures
from native_cashflow_binding import *
from account_cashflow_reconciliation import CashflowReconciliationError
from kiwoom_account_settlement_evidence import normalize_kt00001_settlement


class NativeBindingTests(unittest.TestCase):
    def setUp(self):
        self.batch = history_fixtures.HistoryTests().normalize()
        def snapshot(value, hour):
            return normalize_kt00001_settlement(dict(entr=value, pymn_alow_amt='0',
                d2_entra='99999', ord_alow_amt='0'), account_fingerprint='a'*64,
                captured_at=f'2026-10-06T{hour}:00:00+09:00')
        self.opening, self.closing = snapshot('10000','08'), snapshot('8999','10')
        self.movement = SettledCashMovement('synthetic-review-1', 'a'*64,
            '2026-10-06T09:00:00+09:00', Decimal('-1001'), Decimal('1'))
        self.review = ReviewedNativeCashflow(self.batch.records[0], 'SETTLED_KRW_NET', self.movement)

    def run_binding(self, reviews=None, batch=None, **flags):
        return reconcile_reviewed_native_history(batch or self.batch, self.opening, self.closing,
            [self.review] if reviews is None else reviews, **flags)

    def test_exact_coverage_still_needs_external_attestations(self):
        result = self.run_binding()
        self.assertTrue(result.cash_balance_matched)
        self.assertFalse(result.fields_consistent)
        result = self.run_binding(complete_settlement_scope_attested=True,
            signed_net_mapping_attested=True, fees_tax_completeness_attested=True)
        self.assertTrue(result.fields_consistent)
        self.assertFalse(result.report()['account_settlement_admitted'])
        self.assertFalse(result.report()['real_orders_authorized'])

    def test_missing_duplicate_and_foreign_reviews_block(self):
        changed = replace(self.review.native_record, native_fields=tuple(sorted(
            {**dict(self.review.native_record.native_fields), 'cmsn':'2'}.items())))
        for reviews in ([], [self.review,self.review], [replace(self.review,native_record=changed)]):
            with self.assertRaises(CashflowReconciliationError): self.run_binding(reviews)

    def test_wrong_account_incomplete_period_and_stale_capture_block(self):
        query = dict(self.batch.request_fields)
        query['strt_dt'] = '20261007'
        for batch in (replace(self.batch,account_fingerprint='b'*64),
            replace(self.batch,request_fields=tuple(sorted(query.items()))),
            replace(self.batch,captured_at='2026-10-06T09:59:59+09:00')):
            with self.assertRaises(CashflowReconciliationError): self.run_binding(batch=batch)

    def test_exclusion_cannot_silently_claim_completeness(self):
        review = replace(self.review,disposition='NON_CASH',movement=None)
        same_balance = replace(self.closing,deposit_cash_krw=self.opening.deposit_cash_krw)
        flags = dict(complete_settlement_scope_attested=True,
            signed_net_mapping_attested=True, fees_tax_completeness_attested=True)
        result = reconcile_reviewed_native_history(self.batch,self.opening,same_balance,[review],**flags)
        self.assertTrue(result.cash_balance_matched)
        self.assertFalse(result.fields_consistent)
        result = reconcile_reviewed_native_history(self.batch,self.opening,same_balance,[review],
            exclusions_attested=True,**flags)
        self.assertTrue(result.fields_consistent)

    def test_unclassified_or_movement_on_exclusion_block(self):
        for review in (replace(self.review,disposition='UNKNOWN'),
                       replace(self.review,disposition='OUTSIDE_WINDOW')):
            with self.assertRaises(CashflowReconciliationError): self.run_binding([review])

    def test_two_native_rows_cannot_collapse_to_one_cashflow_id(self):
        row = self.batch.records[0]
        other = replace(row,native_fields=tuple(sorted({**dict(row.native_fields),'trde_no':'SYN-2'}.items())))
        batch = replace(self.batch,records=(row,other))
        with self.assertRaises(CashflowReconciliationError):
            self.run_binding([self.review,replace(self.review,native_record=other)],batch=batch)

    def test_out_of_window_or_wrong_account_mapped_movement_block(self):
        for movement in (replace(self.movement,account_fingerprint='b'*64),
                         replace(self.movement,settled_at=self.opening.captured_at)):
            with self.assertRaises(CashflowReconciliationError):
                self.run_binding([replace(self.review,movement=movement)])

    def test_korean_date_conversion_overflow_is_blocked(self):
        query = dict(self.batch.request_fields)
        query.update(strt_dt='99991231',end_dt='99991231')
        self.opening = replace(self.opening,captured_at='9999-12-31T01:00:00Z')
        self.closing = replace(self.closing,captured_at='9999-12-31T23:00:00Z')
        batch = replace(self.batch,captured_at='9999-12-31T23:30:00Z',
                        request_fields=tuple(sorted(query.items())))
        with self.assertRaises(CashflowReconciliationError):
            self.run_binding(batch=batch)
