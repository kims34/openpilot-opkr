import json
import unittest
from datetime import datetime

from kiwoom_real_readonly_transport import (
    KST, KiwoomRealReadOnlyTransport, RealReadOnlyError,
)


class Response:
    def __init__(self, body, status=200, headers=None):
        self.body = json.dumps(body).encode() if type(body) is dict else body
        self.status = status
        self.headers = headers or {}

    def read(self, limit):
        return self.body[:limit]

    def getheader(self, key):
        return self.headers.get(key)


class RealTransportTests(unittest.TestCase):
    def setUp(self):
        self.cfg = {
            "KIWOOM_ENV": "REAL",
            "KIWOOM_BASE_URL": "https://api.kiwoom.com",
            "KIWOOM_ORDERING_ENABLED": "false",
            "KIWOOM_APP_KEY": "synthetic-private-key",
            "KIWOOM_APP_SECRET": "synthetic-private-secret",
        }
        self.now = datetime(2026, 10, 7, 2, tzinfo=KST)
        self.requests = []
        self.connections = []
        self.responses = []
        owner = self

        class Connection:
            def __init__(self, host, **kwargs):
                owner.connections.append((host, kwargs))

            def request(self, *args, **kwargs):
                owner.requests.append((args, kwargs))

            def getresponse(self):
                return owner.responses.pop(0)

            def close(self):
                pass

        self.transport = KiwoomRealReadOnlyTransport(
            self.cfg, _connection_factory=Connection, _clock=lambda: self.now
        )

    def auth(self):
        self.responses.append(
            Response(
                {
                    "return_code": 0,
                    "token": "synthetic-private-token",
                    "token_type": "bearer",
                    "expires_dt": "20261007030000",
                }
            )
        )
        return self.transport.authenticate()

    def test_auth_uses_fixed_real_host_and_emits_no_secret(self):
        report = self.auth()
        self.assertEqual(self.connections[0][0], "api.kiwoom.com")
        self.assertEqual(self.requests[0][0], ("POST", "/oauth2/token"))
        blob = json.dumps(report)
        self.assertNotIn(self.cfg["KIWOOM_APP_KEY"], blob)
        self.assertNotIn(self.cfg["KIWOOM_APP_SECRET"], blob)
        self.assertFalse(report["real_orders_authorized"])

    def test_account_query_only_after_auth(self):
        with self.assertRaises(RealReadOnlyError):
            self.transport.query("ka00001", {})
        self.auth()
        self.responses.append(Response({"return_code": 0, "acctNo": "private-account"}))
        page = self.transport.query("ka00001", {})
        self.assertEqual(page.body["acctNo"], "private-account")
        self.assertNotIn("private-account", repr(page))
        self.assertEqual(self.requests[-1][1]["headers"]["api-id"], "ka00001")

    def test_ambiguous_or_non_json_response_fails_privately_and_discards_token(self):
        for raw in (b'{"return_code":1,"return_code":0}',
                    b'{"return_code":0,"items":[{"value":1,"value":2}]}',
                    b'{"return_code":0,"value":NaN}',
                    b'{"return_code":0,"value":Infinity}',
                    b'{"return_code":0,"value":-Infinity}'):
            with self.subTest(raw=raw):
                self.auth()
                self.responses.append(Response(raw))
                with self.assertRaisesRegex(RealReadOnlyError, '^REAL_READ_ONLY_REQUEST_BLOCKED$'):
                    self.transport.query('ka00001', {})
                count = len(self.requests)
                with self.assertRaises(RealReadOnlyError):
                    self.transport.query('ka00001', {})
                self.assertEqual(len(self.requests), count)

    def test_settlement_query_is_exact_readonly_scope(self):
        self.auth()
        self.responses.append(Response({
            "return_code": 0,
            "entr": "100000",
            "pymn_alow_amt": "90000",
            "d2_entra": "95000",
            "ord_alow_amt": "50000",
        }))
        page = self.transport.query("kt00001", {"qry_tp": "2"})
        self.assertEqual(page.body["ord_alow_amt"], "50000")
        self.assertEqual(self.requests[-1][1]["headers"]["api-id"], "kt00001")
        count = len(self.requests)
        for body in ({}, {"qry_tp": "3"}, {"qry_tp": 2}, {"qry_tp": "2", "extra": "x"}):
            with self.assertRaises(Exception):
                self.transport.query("kt00001", body)
        self.assertEqual(len(self.requests), count)

    def test_today_status_query_is_bodyless_readonly_scope(self):
        self.auth()
        self.responses.append(Response({"return_code": 0, "d2_entra": "0"}))
        page = self.transport.query("kt00017", {})
        self.assertEqual(page.body["return_code"], 0)
        self.assertEqual(self.requests[-1][1]["headers"]["api-id"], "kt00017")
        count = len(self.requests)
        for body in ({"x":"1"}, {"qry_tp":"2"}):
            with self.assertRaises(Exception):
                self.transport.query("kt00017", body)
        self.assertEqual(len(self.requests), count)

    def test_contradictory_response_pagination_fails_closed_and_discards_token(self):
        for headers in (
            {"cont-yn": "N", "next-key": "unexpected-cursor"},
            {"cont-yn": "Y", "next-key": ""},
            {"next-key": "unexpected-cursor"},
        ):
            with self.subTest(headers=headers):
                self.auth()
                self.responses.append(Response({"return_code": 0}, headers=headers))
                with self.assertRaisesRegex(RealReadOnlyError, '^REAL_READ_ONLY_REQUEST_BLOCKED$'):
                    self.transport.query("ka00001", {})
                count = len(self.requests)
                with self.assertRaises(RealReadOnlyError):
                    self.transport.query("ka00001", {})
                self.assertEqual(len(self.requests), count)

    def test_order_cancel_amend_and_arbitrary_ids_never_send(self):
        self.auth()
        count = len(self.requests)
        for api in ("kt10000", "kt10001", "kt10002", "kt10003", "/oauth2/revoke", "KA00001"):
            with self.assertRaises(Exception):
                self.transport.query(api, {})
        self.assertEqual(len(self.requests), count)

    def test_ordering_enabled_or_wrong_host_block_before_connection(self):
        for change in (
            {"KIWOOM_ORDERING_ENABLED": "true"},
            {"KIWOOM_ENV": "DEMO"},
            {"KIWOOM_BASE_URL": "https://mockapi.kiwoom.com"},
        ):
            with self.assertRaises(Exception):
                KiwoomRealReadOnlyTransport(dict(self.cfg, **change))
        self.assertEqual(self.connections, [])


if __name__ == "__main__":
    unittest.main()
