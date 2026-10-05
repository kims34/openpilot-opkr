import json
import unittest
from unittest.mock import patch
from kiwoom_holdings_diagnostics import normalize_holdings_rows, HoldingsDiagnosticError


class HoldingsTests(unittest.TestCase):
    def setUp(self):
        self.row=dict(stk_cd='SYNTHETIC-PRIVATE',rmnd_qty='10',trde_able_qty='4',evlt_amt='1,000',crd_tp='0',crd_loan_dt='')
    def normalize(self,rows=None,**changes):
        args=dict(account_fingerprint='sha256:'+'a'*64,captured_at='2026-10-05T23:00:00+09:00');args.update(changes)
        return normalize_holdings_rows([self.row] if rows is None else rows,**args)
    def test_private_quantity_view_does_not_attest_ownership_cash_or_settlement(self):
        with patch('socket.socket',side_effect=AssertionError('network forbidden')):view=self.normalize()
        self.assertEqual(view.rows[0]['held_quantity'],10)
        self.assertEqual(view.rows[0]['broker_reported_tradeable_quantity'],4)
        self.assertNotIn('SYNTHETIC-PRIVATE',repr(view));self.assertNotIn('SYNTHETIC-PRIVATE',json.dumps(view.report()))
        for field in ('automation_ownership_attested','available_cash_attested','fees_settled','capital_release_authorized',
            'snapshot_completeness_attested','snapshot_freshness_attested','project_live_evidence_admitted'):
            self.assertFalse(view.report()[field])
    def test_empty_rows_are_not_account_completeness_or_verified_zero_position(self):
        report=self.normalize([]).report();self.assertEqual(report['row_count'],0)
        self.assertFalse(report['snapshot_completeness_attested'])
    def test_negative_fraction_boolean_and_noncanonical_quantity_fail_closed(self):
        for qty in ('-1','1.5','NaN','1e1','1,23',True,str(2**63)):
            self.row['rmnd_qty']=qty
            with self.assertRaises(HoldingsDiagnosticError):self.normalize()
    def test_tradeable_cannot_exceed_held(self):
        self.row['trde_able_qty']='11'
        with self.assertRaises(HoldingsDiagnosticError):self.normalize()
    def test_raw_account_and_unknown_extra_fields_never_retained(self):
        self.row['acnt_no']='private-account'
        with self.assertRaises(HoldingsDiagnosticError) as raised:self.normalize()
        self.assertNotIn('private-account',str(raised.exception))
    def test_credit_loan_lots_stay_distinct_but_exact_duplicate_lot_blocks(self):
        second=dict(self.row,crd_tp='3',crd_loan_dt='20261001')
        self.assertEqual(len(self.normalize([self.row,second]).rows),2)
        with self.assertRaises(HoldingsDiagnosticError):self.normalize([self.row,dict(self.row)])
    def test_timezone_scope_and_account_shape_required_without_origin_attestation(self):
        for changes in ({'captured_at':'2026-10-05T23:00:00'},{'captured_at':'bad'},
            {'account_fingerprint':'private-account'}):
            with self.assertRaises(HoldingsDiagnosticError):self.normalize(**changes)
    def test_valuation_fees_names_dropped_without_mutating_input(self):
        self.row.update(pur_cmsn='private-fee',sell_cmsn='estimated-fee',tax='estimated-tax',stk_nm='private-name')
        before=dict(self.row);view=self.normalize()
        self.assertEqual(self.row,before)
        for value in ('private-fee','estimated-fee','estimated-tax','private-name'):
            self.assertNotIn(value,json.dumps(view.rows))


if __name__=='__main__':unittest.main()
