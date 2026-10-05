import contextlib
import io
import json
import unittest
from unittest.mock import patch

from kiwoom_demo_readonly_transport import PrivateDemoPage
from kiwoom_demo_holdings_verifier import main,verify_holdings


class HoldingsVerifierTests(unittest.TestCase):
    def setUp(self):self.calls=[]

    def probe(self,mode):
        owner=self
        class Transport:
            def __init__(self,config):self.index=0
            def authenticate(self):return {'demo_token_response_validated':mode!='auth'}
            def query(self,api,body,**kwargs):
                owner.calls.append((api,body,kwargs))
                if api=='ka00001':return PrivateDemoPage({'acctNo':'synthetic-private-account'},'N','')
                i=self.index;self.index+=1
                row=dict(stk_cd='synthetic-private-stock',rmnd_qty='10',trde_able_qty='6',
                    evlt_amt='100',crd_tp='00',crd_loan_dt=str(i))
                if mode=='duplicate':row['crd_loan_dt']='same'
                if mode=='quantity':row['trde_able_qty']='11'
                rows=[] if mode=='empty' else [row]
                marker='Y' if mode in ('cap','loop') or (i==0 and mode!='empty') else 'N'
                return PrivateDemoPage({'acnt_evlt_remn_indv_tot':rows},marker,
                    'private-key-'+str(i if mode!='loop' else 0),
                    continuation_header_present=mode!='header')
        with patch('time.sleep'),patch('socket.socket',side_effect=AssertionError('network forbidden')):
            return verify_holdings({},execute=True,transport_factory=Transport)

    def test_dry_run_has_no_construction_or_zero_holding_claim(self):
        def fail(config):raise AssertionError('constructed')
        out=verify_holdings({},transport_factory=fail)
        self.assertEqual(out['status'],'NOT_REQUESTED')
        self.assertIsNone(out['holdings_row_count'])

    def test_distinct_credit_lots_complete_without_private_values_or_admission(self):
        out=self.probe('success')
        self.assertEqual(out['status'],'DEMO_READ_ONLY_HOLDINGS_DIAGNOSTICS_ONLY')
        self.assertEqual(out['snapshot_pages_received'],2)
        self.assertEqual(out['holdings_row_count'],2)
        self.assertTrue(out['cursor_collection_terminated'])
        self.assertNotIn('private-',json.dumps(out))
        self.assertEqual(self.calls[1][1],{'qry_tp':'2','dmst_stex_tp':'KRX'})
        for field in ('source_account_origin_authenticated','snapshot_completeness_attested',
            'automation_ownership_attested','available_cash_attested','fees_settled',
            'capital_release_authorized','genuine_live_provenance_verified',
            'sealed_holdout_authorized','live_trading_authorized','orders_requested'):
            self.assertFalse(out[field])

    def test_explicit_empty_page_is_not_whole_account_zero_proof(self):
        out=self.probe('empty')
        self.assertEqual(out['holdings_row_count'],0)
        self.assertFalse(out['snapshot_completeness_attested'])

    def test_failed_auth_loop_cap_duplicate_or_quantity_never_returns_partial_counts(self):
        for mode in ('auth','header','loop','cap','duplicate','quantity'):
            with self.subTest(mode=mode):
                self.calls=[];out=self.probe(mode)
                self.assertEqual(out['status'],'DEMO_READ_ONLY_HOLDINGS_BLOCKED')
                self.assertIsNone(out['holdings_row_count'])
                self.assertEqual(out['snapshot_pages_received'],0)
                self.assertFalse(out['cursor_collection_terminated'])
                self.assertNotIn('private-',json.dumps(out))
                self.assertLessEqual(len(self.calls),11)

    def test_cli_exact_flag_only(self):
        for args,expected in (([],False),(['--execute-demo-holdings-readonly'],True),
            (['--execute-demo-holdings-readonly','--real'],False)):
            with patch('kiwoom_demo_holdings_verifier.verify_holdings',
                return_value={'status':'NOT_REQUESTED'}) as mock,contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(args),0)
                self.assertEqual(mock.call_args.kwargs,{'execute':expected})


if __name__=='__main__':unittest.main()
