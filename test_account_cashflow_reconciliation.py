"""Synthetic cashflow expectations, not native settlement observations."""
import unittest
from dataclasses import replace
from decimal import Decimal, localcontext

from account_cashflow_reconciliation import *
from kiwoom_account_settlement_evidence import normalize_kt00001_settlement


class CashflowTests(unittest.TestCase):
    def snapshot(self, amount, day):
        return normalize_kt00001_settlement(
            {'entr':amount,'pymn_alow_amt':'0','d2_entra':'999999','ord_alow_amt':'0'},
            account_fingerprint='a'*64, captured_at=f'2026-10-{day}T10:00:00+09:00')

    def movement(self, delta='-1001', fees='1'):
        return SettledCashMovement('synthetic-transaction','a'*64,
                                  '2026-10-07T09:00:00+09:00',Decimal(delta),Decimal(fees))

    def reconcile(self, opening='10000', closing='8999', movements=None, **flags):
        return reconcile_settled_cashflow(self.snapshot(opening,'06'),self.snapshot(closing,'07'),
                                          movements if movements is not None else [self.movement()], **flags)

    def test_net_settlement_already_includes_fee(self):
        result = self.reconcile(complete_settlement_scope_attested=True,
                                signed_net_mapping_attested=True,fees_tax_completeness_attested=True)
        self.assertTrue(result.fields_consistent)
        self.assertFalse(result.report()['account_settlement_admitted'])
        self.assertFalse(result.report()['real_orders_authorized'])

    def test_missing_scope_or_fee_attestation_does_not_pass(self):
        result = self.reconcile()
        self.assertTrue(result.cash_balance_matched)
        self.assertFalse(result.fields_consistent)

    def test_unsettled_estimates_never_credit_cash(self):
        self.assertFalse(self.reconcile(closing='10000').cash_balance_matched)

    def test_duplicate_delivery_is_counted_once(self):
        item = self.movement()
        result = self.reconcile(movements=[item,item])
        self.assertTrue(result.cash_balance_matched)
        self.assertEqual(result.unique_movement_count,1)
        self.assertEqual(result.duplicate_delivery_count,1)

    def test_conflicting_duplicate_account_and_time_fail_closed(self):
        item = self.movement()
        for changed in (replace(item,net_cash_delta_krw=Decimal('-1002')),
                        replace(item,fees_tax_krw=Decimal('2')),
                        replace(item,account_fingerprint='b'*64),
                        replace(item,settled_at='2026-10-08T09:00:00+09:00')):
            with self.assertRaises(CashflowReconciliationError):
                self.reconcile(movements=[item,changed])

    def test_low_decimal_precision_cannot_hide_one_won_mismatch(self):
        with localcontext() as context:
            context.prec=2
            self.assertFalse(self.reconcile(opening='100000000000000000000001',
                closing='100000000000000000000000',movements=[]).cash_balance_matched)

    def test_external_deposit_withdrawal_and_trade_net_offsets(self):
        first=self.movement('1000','0')
        second=replace(self.movement('-1500','1'),transaction_id='synthetic-second')
        self.assertTrue(self.reconcile(closing='9500',movements=[first,second]).cash_balance_matched)

    def test_invalid_original_types_fail_closed(self):
        with self.assertRaises(CashflowReconciliationError):
            self.reconcile(complete_settlement_scope_attested=1)
        with self.assertRaises(CashflowReconciliationError):
            self.reconcile(movements=[replace(self.movement(),net_cash_delta_krw=-1001)])


if __name__=='__main__':
    unittest.main()
