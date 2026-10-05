import contextlib
import io
import json
import unittest
from unittest.mock import patch

from kiwoom_demo_readonly_transport import PrivateDemoPage
from kiwoom_demo_readonly_verifier import main, verify


class VerifierTests(unittest.TestCase):
    def setUp(self):
        self.calls=[]
        owner=self
        class FakeTransport:
            def __init__(self,config):owner.calls.append('construct')
            def authenticate(self):
                owner.calls.append('auth')
                return {'demo_token_response_validated':True}
            def query(self,api,body):
                owner.calls.append(api)
                return PrivateDemoPage({'acctNo':'synthetic-private-account','cntr':[],
                    'acnt_ord_cntr_prps_dtl':[{'ord_no':'synthetic-private-order'}]},'Y','synthetic-private-next')
        self.factory=FakeTransport

    def run_probe(self, factory=None):
        with patch('time.sleep'):
            return verify({},execute=True,transport_factory=factory or self.factory)

    def test_default_dry_run_never_constructs_or_requests(self):
        report=verify({},transport_factory=self.factory)
        self.assertEqual(report['status'],'NOT_REQUESTED')
        self.assertEqual(self.calls,[])
        self.assertFalse(report['request_attempted'])

    def test_counts_only_without_private_values_authority_or_completeness(self):
        report=self.run_probe()
        self.assertEqual(self.calls,['construct','auth','ka00001','kt00007','ka10076'])
        self.assertEqual(report['status'],'DEMO_READ_ONLY_CONNECTIVITY_ONLY')
        self.assertEqual(report['snapshot_row_counts'],{'kt00007':1,'ka10076':0})
        serialized=json.dumps(report)
        self.assertNotIn('synthetic-private',serialized)
        for name in ('snapshot_completeness_attested','broker_account_origin_authenticated',
            'genuine_live_provenance_verified','project_live_evidence_admitted',
            'empirical_execution_blocker_closed','sealed_holdout_authorized',
            'live_trading_authorized','orders_requested'):
            self.assertFalse(report[name])

    def test_configuration_failure_never_claims_request_attempt(self):
        def fail(config):raise ValueError('private-secret')
        report=self.run_probe(fail)
        self.assertEqual(report['status'],'DEMO_READ_ONLY_CONNECTIVITY_BLOCKED')
        self.assertFalse(report['request_attempted'])
        self.assertNotIn('private-secret',json.dumps(report))

    def test_missing_account_field_blocks_before_snapshots(self):
        factory=self.factory
        class MissingAccount(factory):
            def query(self,api,body):return PrivateDemoPage({},'N','')
        report=self.run_probe(MissingAccount)
        self.assertEqual(report['status'],'DEMO_READ_ONLY_CONNECTIVITY_BLOCKED')
        self.assertEqual(report['snapshot_pages_received'],0)

    def test_malformed_snapshot_table_never_means_verified_zero(self):
        factory=self.factory
        class InvalidPage(factory):
            def query(self,api,body):
                if api=='ka00001':return super().query(api,body)
                return PrivateDemoPage({'cntr':None,'acnt_ord_cntr_prps_dtl':'private'},'N','')
        report=self.run_probe(InvalidPage)
        self.assertEqual(report['status'],'DEMO_READ_ONLY_CONNECTIVITY_BLOCKED')
        self.assertEqual(report['snapshot_row_counts'],{})

    def test_cli_unknown_args_remain_dry_run_json_only(self):
        output=io.StringIO()
        with contextlib.redirect_stdout(output),patch('socket.socket',side_effect=AssertionError('network forbidden')):
            status=main(['--real'])
        self.assertEqual(status,0)
        self.assertEqual(json.loads(output.getvalue())['status'],'NOT_REQUESTED')


if __name__=='__main__':unittest.main()

class PaginatedVerifierTests(unittest.TestCase):
    def probe(self, mode):
        calls=[]
        class Transport:
            def __init__(self,config):self.indices={}
            def authenticate(self):return {'demo_token_response_validated':True}
            def query(self,api,body,**kwargs):
                calls.append((api,kwargs))
                if api=='ka00001':return PrivateDemoPage({'acctNo':'private-account'},'N','')
                index=self.indices.get(api,0);self.indices[api]=index+1
                table='cntr' if api=='ka10076' else 'acnt_ord_cntr_prps_dtl'
                if mode=='malformed' and api=='ka10076':return PrivateDemoPage({table:None},'N','')
                order='private-order-'+str(index if mode!='duplicate' else 0)
                marker='Y' if mode in ('cap','loop','duplicate') or index==0 else 'N'
                key='private-key-'+str(index if mode!='loop' else 0)
                return PrivateDemoPage({table:[{'ord_no':order}]},marker,key)
        with patch('time.sleep'):
            report=verify({},execute=True,paginated=True,transport_factory=Transport)
        return report,calls

    def test_multiple_pages_terminate_without_admission_or_private_output(self):
        report,calls=self.probe('success')
        self.assertEqual(report['status'],'DEMO_READ_ONLY_CONNECTIVITY_ONLY')
        self.assertEqual(report['snapshot_page_counts'],{'kt00007':2,'ka10076':2})
        self.assertEqual(report['snapshot_pages_received'],4)
        self.assertTrue(report['cursor_collection_terminated'])
        self.assertNotIn('private-',json.dumps(report))
        self.assertEqual(calls[2][1],{'continuation':'Y','next_key':'private-key-0'})
        for key in ('snapshot_completeness_attested','broker_account_origin_authenticated',
                    'genuine_live_provenance_verified','project_live_evidence_admitted',
                    'sealed_holdout_authorized','live_trading_authorized','orders_requested'):
            self.assertFalse(report[key])

    def test_cap_loop_duplicates_and_second_api_failure_clear_partial_result(self):
        for mode in ('cap','loop','duplicate','malformed'):
            with self.subTest(mode=mode):
                report,calls=self.probe(mode)
                self.assertEqual(report['status'],'DEMO_READ_ONLY_CONNECTIVITY_BLOCKED')
                self.assertEqual(report['snapshot_row_counts'],{})
                self.assertEqual(report['snapshot_page_counts'],{})
                self.assertEqual(report['snapshot_pages_received'],0)
                self.assertFalse(report['cursor_collection_terminated'])
                self.assertNotIn('private-',json.dumps(report))
                self.assertLessEqual(len(calls),11)

    def test_explicit_cli_dispatch_and_extra_argument_dry_run(self):
        for args,execute,paginated in ((['--execute-demo-paginated-readonly'],True,True),
            (['--execute-demo-readonly'],True,False),
            (['--execute-demo-paginated-readonly','--real'],False,False),([],False,False)):
            with self.subTest(args=args),patch('kiwoom_demo_readonly_verifier.verify',
                return_value={'status':'NOT_REQUESTED'}) as mock,contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(args),0)
                self.assertEqual(mock.call_args.kwargs,{'execute':execute,'paginated':paginated})
