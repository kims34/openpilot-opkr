from datetime import datetime
import json
import unittest
from unittest.mock import patch

from kiwoom_demo_readonly_transport import (
    DemoReadOnlyError, KiwoomDemoReadOnlyTransport, KST, MAX_RESPONSE_BYTES,
)


class Response:
    def __init__(self, body, status=200, headers=None):
        self.body = json.dumps(body).encode() if type(body) is dict else body
        self.status, self.headers = status, headers or {}
    def read(self, limit): return self.body[:limit]
    def getheader(self, key): return self.headers.get(key)


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.config = dict(KIWOOM_ENV='DEMO', KIWOOM_BASE_URL='https://mockapi.kiwoom.com',
            KIWOOM_ORDERING_ENABLED='false', KIWOOM_APP_KEY='synthetic-private-key',
            KIWOOM_APP_SECRET='synthetic-private-secret')
        self.now = datetime(2026,10,5,12,tzinfo=KST)
        self.requests, self.connections, self.responses = [], [], []
        owner = self
        class Connection:
            def __init__(self, host, **kwargs):
                owner.connections.append((host,kwargs));self.closed=False
            def request(self, *args, **kwargs): owner.requests.append((args,kwargs))
            def getresponse(self):
                item=owner.responses.pop(0)
                if isinstance(item,Exception):raise item
                return item
            def close(self): self.closed=True
        self.factory=Connection
        self.transport=KiwoomDemoReadOnlyTransport(self.config,
            _connection_factory=Connection,_clock=lambda:self.now)

    def authenticate(self, **changes):
        self.responses.append(Response(dict(return_code=0,token='synthetic-private-token',
            token_type='bearer',expires_dt='20261005130000',**changes)))
        return self.transport.authenticate()

    def test_authentication_is_explicit_fixed_mock_tls_no_real_socket_or_authority(self):
        self.assertEqual(self.requests,[])
        with patch('socket.socket',side_effect=AssertionError('no real network')):
            report=self.authenticate()
        args,kwargs=self.requests[0]
        self.assertEqual(args,('POST','/oauth2/token'))
        self.assertEqual(self.connections[0][0],'mockapi.kiwoom.com')
        self.assertEqual(self.connections[0][1]['port'],443)
        self.assertEqual(self.connections[0][1]['timeout'],10)
        self.assertTrue(self.connections[0][1]['context'].check_hostname)
        self.assertEqual(json.loads(kwargs['body'])['grant_type'],'client_credentials')
        self.assertFalse(report['account_identity_authenticated'])
        self.assertFalse(report['project_live_evidence_admitted'])
        for secret in (self.config['KIWOOM_APP_KEY'],self.config['KIWOOM_APP_SECRET'],'synthetic-private-token'):
            self.assertNotIn(secret,json.dumps(report))
        self.assertNotIn('private',repr(self.transport))

    def test_real_or_ambiguous_configuration_is_rejected_before_factory(self):
        for changes in ({'KIWOOM_ENV':'REAL'},{'KIWOOM_ENV':''},
            {'KIWOOM_BASE_URL':'https://api.kiwoom.com'},
            {'KIWOOM_BASE_URL':'https://mockapi.kiwoom.com/redirect'},
            {'KIWOOM_ORDERING_ENABLED':'true'},{'KIWOOM_APP_SECRET':''}):
            with self.assertRaises(DemoReadOnlyError):
                KiwoomDemoReadOnlyTransport(dict(self.config,**changes),_connection_factory=self.factory)
        self.assertEqual(self.connections,[])

    def test_account_query_is_private_no_auto_auth_and_read_only_fixed_path(self):
        with self.assertRaises(DemoReadOnlyError):self.transport.query('ka00001',{})
        self.assertEqual(self.requests,[])
        self.authenticate();self.responses.append(Response({'return_code':0,'acctNo':'synthetic-private-account'}))
        page=self.transport.query('ka00001',{})
        self.assertEqual(page.body['acctNo'],'synthetic-private-account')
        self.assertNotIn('synthetic-private-account',repr(page))
        self.assertEqual(self.requests[-1][0],('POST','/api/dostk/acnt'))
        self.assertEqual(self.requests[-1][1]['headers']['api-id'],'ka00001')

    def test_all_order_cancel_amend_revoke_and_arbitrary_api_ids_are_blocked(self):
        self.authenticate();count=len(self.requests)
        for api in ('kt10000','kt10001','kt10002','kt10003','/oauth2/revoke','https://api.kiwoom.com','KA00001'):
            with self.assertRaises(DemoReadOnlyError):self.transport.query(api,{})
        self.assertEqual(len(self.requests),count)

    def test_unknown_fields_or_missing_required_filters_are_blocked(self):
        self.authenticate();count=len(self.requests)
        for api,body in (('ka00001',{'api-id':'kt10000'}),('kt00007',{}),
            ('ka10076',{'qry_tp':'0','sell_tp':'0','stex_tp':'0','password':'private'})):
            with self.assertRaises(DemoReadOnlyError):self.transport.query(api,body)
        self.assertEqual(len(self.requests),count)

    def test_both_reviewed_snapshot_apis_are_queries_not_execution_creation(self):
        self.authenticate()
        for api,body in (('kt00007',dict(qry_tp='1',stk_bond_tp='1',sell_tp='0',dmst_stex_tp='KRX')),
            ('ka10076',dict(qry_tp='0',sell_tp='0',stex_tp='1'))):
            self.responses.append(Response({'return_code':0}))
            self.transport.query(api,body)
            self.assertEqual(self.requests[-1][1]['headers']['api-id'],api)

    def test_expiry_blocks_query_without_refresh_or_retry(self):
        self.authenticate();count=len(self.requests);self.now=datetime(2026,10,5,13,tzinfo=KST)
        with self.assertRaises(DemoReadOnlyError):self.transport.query('ka00001',{})
        self.assertEqual(len(self.requests),count)

    def test_redirect_and_provider_error_never_follow_or_echo_body(self):
        for status in (301,302,307,400,500):
            self.responses.append(Response({'return_code':99,'return_msg':'private-secret'},status=status))
            before=len(self.requests)
            with self.assertRaises(DemoReadOnlyError) as raised:self.transport.authenticate()
            self.assertNotIn('private-secret',str(raised.exception))
            self.assertEqual(len(self.requests),before+1)

    def test_network_exception_is_sanitized_and_token_invalidated(self):
        self.authenticate();self.responses.append(RuntimeError('synthetic-private-token'))
        with self.assertRaises(DemoReadOnlyError) as raised:self.transport.query('ka00001',{})
        self.assertNotIn('synthetic-private-token',str(raised.exception))
        before=len(self.requests)
        with self.assertRaises(DemoReadOnlyError):self.transport.query('ka00001',{})
        self.assertEqual(len(self.requests),before)

    def test_malformed_or_oversize_responses_are_rejected(self):
        for body in (b'not-json',b'[]',b'x'*(MAX_RESPONSE_BYTES+1),{'return_code':True},
            {'return_code':'0'},{'return_code':3,'return_msg':'private'}):
            self.responses.append(Response(body))
            with self.assertRaises(DemoReadOnlyError):self.transport.authenticate()

    def test_bad_auth_token_expiry_or_type_never_allows_query(self):
        for change in ({'token':'bad\r\nheader'},{'token':''},{'expires_dt':'20261005120000'},
            {'expires_dt':'20260230130000'},{'token_type':'other'}):
            body=dict(return_code=0,token='synthetic',token_type='bearer',expires_dt='20261005130000');body.update(change)
            self.responses.append(Response(body))
            with self.assertRaises(DemoReadOnlyError):self.transport.authenticate()
            with self.assertRaises(DemoReadOnlyError):self.transport.query('ka00001',{})

    def test_continuation_is_explicit_no_hidden_page_loop(self):
        self.authenticate();self.responses.append(Response({'return_code':0},headers={'cont-yn':'Y','next-key':'synthetic-page'}))
        page=self.transport.query('ka00001',{})
        self.assertEqual(page.continuation,'Y');self.assertEqual(len(self.requests),2)
        self.responses.append(Response({'return_code':0}))
        self.transport.query('ka00001',{},continuation='Y',next_key=page.next_key)
        self.assertEqual(len(self.requests),3)

    def test_header_injection_and_incomplete_continuation_are_rejected(self):
        self.authenticate();count=len(self.requests)
        for continuation,key in (('Y',''),('N','private'),('Y','bad\nheader'),('other','')):
            with self.assertRaises(DemoReadOnlyError):self.transport.query('ka00001',{},continuation=continuation,next_key=key)
        self.assertEqual(len(self.requests),count)

    def test_external_configuration_mutation_cannot_change_host_or_credentials(self):
        self.config.update(KIWOOM_ENV='REAL',KIWOOM_BASE_URL='https://api.kiwoom.com',KIWOOM_APP_KEY='changed')
        self.authenticate()
        self.assertEqual(self.connections[-1][0],'mockapi.kiwoom.com')
        self.assertEqual(json.loads(self.requests[-1][1]['body'])['appkey'],'synthetic-private-key')


if __name__=='__main__':unittest.main()
