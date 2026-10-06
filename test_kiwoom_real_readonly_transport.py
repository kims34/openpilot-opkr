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
