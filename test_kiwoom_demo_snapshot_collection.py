import json
import unittest
from unittest.mock import patch
from kiwoom_demo_readonly_transport import PrivateDemoPage
from kiwoom_demo_snapshot_collection import collect_demo_snapshot, SnapshotCollectionError


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.pages=[];self.calls=[]
        owner=self
        class Transport:
            def query(self,api,body,**kwargs):
                owner.calls.append((api,body,kwargs))
                item=owner.pages.pop(0)
                if isinstance(item,Exception):raise item
                return item
        self.transport=Transport()
    def page(self,order='private-order',cont='N',key=''):
        return PrivateDemoPage({'cntr':[{'ord_no':order}] if order else [],'acnt_ord_cntr_prps_dtl':[]},cont,key)
    def collect(self,**kwargs):
        with patch('time.sleep'):return collect_demo_snapshot(self.transport,'ka10076',{'qry_tp':'0'},**kwargs)
    def test_multiple_pages_require_explicit_cursor_and_finish_without_admission(self):
        self.pages=[self.page('one','Y','private-cursor'),self.page('two')]
        snapshot=self.collect();self.assertEqual(snapshot.page_count,2)
        self.assertEqual(len(snapshot.rows),2)
        self.assertEqual(self.calls[1][2],{'continuation':'Y','next_key':'private-cursor'})
        self.assertNotIn('private',json.dumps(snapshot.report()));self.assertNotIn('one',repr(snapshot))
        for flag in ('query_scope_completeness_attested','snapshot_freshness_attested',
            'source_account_origin_authenticated','fees_settled','project_live_evidence_admitted',
            'empirical_execution_blocker_closed','live_trading_authorized'):
            self.assertFalse(snapshot.report()[flag])
    def test_empty_terminated_page_is_not_verified_zero_account_scope(self):
        self.pages=[self.page('')];snapshot=self.collect()
        self.assertEqual(snapshot.report()['row_count'],0)
        self.assertFalse(snapshot.report()['query_scope_completeness_attested'])
    def test_capped_continuation_never_returns_partial_success(self):
        self.pages=[self.page('one','Y','private-cursor')]
        with self.assertRaises(SnapshotCollectionError):self.collect(max_pages=1)
        self.assertEqual(len(self.calls),1)
    def test_loop_cursor_and_duplicate_order_both_block(self):
        for pages in ([self.page('one','Y','loop'),self.page('two','Y','loop')],
            [self.page('one','Y','next'),self.page('one')]):
            self.pages=pages
            with self.assertRaises(SnapshotCollectionError):self.collect()
    def test_invalid_api_or_page_budget_never_requests(self):
        for budget in (0,11,True,'10'):
            with self.assertRaises(SnapshotCollectionError):self.collect(max_pages=budget)
        with self.assertRaises(SnapshotCollectionError):collect_demo_snapshot(self.transport,'kt10000',{})
        self.assertEqual(self.calls,[])
    def test_missing_table_or_order_is_not_empty_success(self):
        for body in ({},{'cntr':None},{'cntr':[{}]}):
            self.pages=[PrivateDemoPage(body,'N','')]
            with self.assertRaises(SnapshotCollectionError):self.collect()
    def test_bad_or_missing_cursor_blocks(self):
        for key in ('','private\nheader'):
            self.pages=[self.page('one','Y',key)]
            with self.assertRaises(SnapshotCollectionError):self.collect()
    def test_partial_provider_failure_is_sanitized_without_retry(self):
        self.pages=[self.page('one','Y','next'),ValueError('private-secret')]
        with self.assertRaises(SnapshotCollectionError) as raised:self.collect()
        self.assertNotIn('private-secret',str(raised.exception));self.assertEqual(len(self.calls),2)
    def test_captured_rows_do_not_alias_provider_pages(self):
        page=self.page();self.pages=[page];snapshot=self.collect()
        page.body['cntr'][0]['ord_no']='changed'
        self.assertEqual(snapshot.rows[0]['ord_no'],'private-order')


if __name__=='__main__':unittest.main()
