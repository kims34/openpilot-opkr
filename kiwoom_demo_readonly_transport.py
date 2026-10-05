"""Explicit DEMO-only authentication and reviewed read-only account APIs.

No order/revoke/REAL paths, redirects, retries, automatic refresh, file cache,
logging, source admission or runtime activation. Private pages stay in memory.
"""
from datetime import datetime, timedelta, timezone
import http.client
import json
import ssl

from kiwoom_readonly_configuration_audit import audit_configuration


KST = timezone(timedelta(hours=9))
HOST = 'mockapi.kiwoom.com'
PATH = '/api/dostk/acnt'
MAX_RESPONSE_BYTES = 1024 * 1024
SCOPES = {
    'ka00001': (frozenset(), frozenset()),
    'kt00007': (frozenset('qry_tp stk_bond_tp sell_tp dmst_stex_tp'.split()),
                frozenset('qry_tp stk_bond_tp sell_tp dmst_stex_tp ord_dt stk_cd fr_ord_no'.split())),
    'ka10076': (frozenset('qry_tp sell_tp stex_tp'.split()),
                frozenset('qry_tp sell_tp stex_tp stk_cd ord_no'.split())),
    'kt00018': (frozenset('qry_tp dmst_stex_tp'.split()),
                frozenset('qry_tp dmst_stex_tp'.split())),
}


class DemoReadOnlyError(ValueError):
    pass


def require(condition):
    if not condition:
        raise DemoReadOnlyError('DEMO_READ_ONLY_REQUEST_BLOCKED')


class PrivateDemoPage:
    __slots__ = ('body', 'continuation', 'next_key', 'continuation_header_present')

    def __init__(self, body, continuation, next_key, *, continuation_header_present=True):
        self.body, self.continuation, self.next_key = body, continuation, next_key
        self.continuation_header_present = continuation_header_present

    def __repr__(self):
        return '<PrivateDemoPage redacted; DEMO only; no evidence admission>'


class KiwoomDemoReadOnlyTransport:
    def __init__(self, configuration, *, _connection_factory=None, _clock=None):
        require(type(configuration) is dict)
        self._config = dict(configuration)
        require(audit_configuration(self._config)['demo_configuration_preconditions_met'])
        self._factory = _connection_factory or http.client.HTTPSConnection
        self._clock = _clock or (lambda: datetime.now(KST))
        self._token = self._expiry = None

    def __repr__(self):
        return '<KiwoomDemoReadOnlyTransport redacted; DEMO read-only>'

    def _post(self, path, body, headers):
        connection = None
        try:
            # Fixed host/port and verified TLS. HTTPSConnection neither follows
            # redirects nor uses environment proxy settings.
            connection = self._factory(HOST, port=443, timeout=10,
                context=ssl.create_default_context())
            connection.request('POST', path, body=json.dumps(body).encode('utf-8'),
                headers={'Content-Type': 'application/json;charset=UTF-8', **headers})
            response = connection.getresponse()
            require(response.status == 200)
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            require(len(raw) <= MAX_RESPONSE_BYTES)
            data = json.loads(raw)
            require(type(data) is dict and type(data.get('return_code')) is int and data['return_code'] == 0)
            raw_continuation = response.getheader('cont-yn')
            continuation = raw_continuation or 'N'
            next_key = response.getheader('next-key') or ''
            require(continuation in ('N', 'Y'))
            require(type(next_key) is str and len(next_key) <= 4096 and '\r' not in next_key and '\n' not in next_key)
            require(continuation != 'Y' or bool(next_key))
            return PrivateDemoPage(data, continuation, next_key,
                continuation_header_present=raw_continuation in ('N', 'Y'))
        except Exception:
            # Network/provider/JSON errors may contain private request bodies.
            self._token = self._expiry = None
            raise DemoReadOnlyError('DEMO_READ_ONLY_REQUEST_BLOCKED') from None
        finally:
            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass

    def authenticate(self):
        self._token = self._expiry = None
        require(audit_configuration(self._config)['demo_configuration_preconditions_met'])
        page = self._post('/oauth2/token', {
            'grant_type': 'client_credentials', 'appkey': self._config['KIWOOM_APP_KEY'],
            'secretkey': self._config['KIWOOM_APP_SECRET'],
        }, {})
        try:
            token, expiry = page.body.get('token'), page.body.get('expires_dt')
            require(type(token) is str and 0 < len(token) <= 8192 and all(33 <= ord(c) <= 126 for c in token))
            require(str(page.body.get('token_type', '')).lower() == 'bearer')
            require(type(expiry) is str and len(expiry) == 14 and expiry.isascii() and expiry.isdigit())
            expires_at = datetime.strptime(expiry, '%Y%m%d%H%M%S').replace(tzinfo=KST)
            require(expires_at > self._clock())
            self._token, self._expiry = token, expires_at
        except Exception:
            raise DemoReadOnlyError('DEMO_READ_ONLY_REQUEST_BLOCKED') from None
        return dict(mode='DEMO_READ_ONLY_TRANSPORT', demo_token_response_validated=True,
            account_identity_authenticated=False, genuine_live_provenance_verified=False,
            project_live_evidence_admitted=False, live_trading_authorized=False)

    def query(self, api_id, body, *, continuation='N', next_key=''):
        require(audit_configuration(self._config)['demo_configuration_preconditions_met'])
        require(type(api_id) is str and api_id in SCOPES)
        required, allowed = SCOPES[api_id]
        require(type(body) is dict and required <= set(body) <= allowed)
        require(all(type(v) is str and len(v) <= 256 for v in body.values()))
        require(all(body[k].strip() for k in required))
        if api_id == 'kt00018':
            require(body == {'qry_tp': '2', 'dmst_stex_tp': 'KRX'})
        require(continuation in ('N', 'Y') and type(next_key) is str and len(next_key) <= 4096)
        require('\r' not in next_key and '\n' not in next_key)
        require((continuation == 'Y') == bool(next_key))
        require(self._token is not None and self._expiry > self._clock())
        return self._post(PATH, dict(body), {'authorization': 'Bearer ' + self._token,
            'api-id': api_id, 'cont-yn': continuation, 'next-key': next_key})
