"""Synthetic-only regression: credential-bearing REST requests never follow redirects.

No external API, API keys, order endpoints or account data are used.
"""
from __future__ import annotations

import io
import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from kiwoom_real_type00_readonly_smoke import main, SmokeState, _token_and_account

ENV = {
    "KIWOOM_ENV": "REAL",
    "KIWOOM_BASE_URL": "https://api.kiwoom.com",
    "KIWOOM_ORDERING_ENABLED": "false",
    "KIWOOM_APP_KEY": "synthetic-app-key",
    "KIWOOM_APP_SECRET": "synthetic-app-secret",
}
TOKEN_SUCCESS = b'{"return_code":0,"token":"synthetic-private-token","expires_dt":"20991231235959","token_type":"bearer"}'
ACCOUNT_SUCCESS = b'{"return_code":0,"acctNo":"synthetic-private-account"}'

class KiwoomRedirectGuardTests(unittest.TestCase):
    def _assert_blocked(self, responses, expected_stage: str, expected_calls: int):
        with patch.dict(os.environ, ENV, clear=True), \
             patch("kiwoom_real_type00_readonly_smoke.requests.post",
                   side_effect=responses) as post, \
             patch("kiwoom_real_type00_readonly_smoke._run_ws",
                   side_effect=AssertionError("WebSocket must never run")) as ws, \
             patch("sys.stdout", new_callable=io.StringIO) as stdout:
            with self.assertRaises(SystemExit) as exit_signal:
                main()
        self.assertEqual(exit_signal.exception.code, 2)
        ws.assert_not_called()
        self.assertEqual(post.call_count, expected_calls)
        for call in post.call_args_list:
            self.assertIs(call.kwargs["allow_redirects"], False)
        emitted = stdout.getvalue()
        state = json.loads(emitted)
        self.assertEqual(state["STAGE"], expected_stage)
        self.assertFalse(state["WS_CONNECTED"])
        self.assertFalse(state["WS_LOGIN_OK"])
        self.assertFalse(state["TYPE00_REG_SENT"])
        self.assertFalse(state["REAL_ORDERS_AUTHORIZED"])
        self.assertFalse(state["FUNDS_MOVEMENT_AUTHORIZED"])
        self.assertFalse(state["PERMISSION_CHANGE_AUTHORIZED"])
        for private in ("synthetic-private-token", "synthetic-private-account",
                        "synthetic-app-key", "synthetic-app-secret", "evil.invalid"):
            self.assertNotIn(private, emitted)

    def test_oauth_redirect_cannot_continue_to_account_or_websocket(self):
        # Body looks like success; HTTP redirect must nevertheless block it.
        self._assert_blocked([
            SimpleNamespace(status_code=307, headers={"Location": "https://evil.invalid/collect"},
                            content=TOKEN_SUCCESS)
        ], "TOKEN_PROTOCOL", 1)

    def test_account_redirect_cannot_continue_to_websocket(self):
        self._assert_blocked([
            SimpleNamespace(status_code=200, content=TOKEN_SUCCESS),
            SimpleNamespace(status_code=308, headers={"Location": "https://evil.invalid/collect"},
                            content=ACCOUNT_SUCCESS),
        ], "ACCOUNT_PROTOCOL", 2)

    def test_http_failures_never_reclassified_as_success_from_body(self):
        for status in (301, 302, 303, 307, 308, 401, 429, 500, True, None):
            with self.subTest(status=status):
                self._assert_blocked(
                    [SimpleNamespace(status_code=status, content=TOKEN_SUCCESS)],
                    "TOKEN_PROTOCOL", 1)

    def test_http_200_is_still_readonly_and_never_sends_orders(self):
        with patch.dict(os.environ, ENV, clear=True), \
             patch("kiwoom_real_type00_readonly_smoke.requests.post",
                   side_effect=[
                       SimpleNamespace(status_code=200, content=TOKEN_SUCCESS),
                       SimpleNamespace(status_code=200, content=ACCOUNT_SUCCESS),
                   ]) as post:
            state = SmokeState()
            token, account, _issued = _token_and_account(state)
        self.assertEqual(token, "synthetic-private-token")
        self.assertEqual(account, "synthetic-private-account")
        self.assertTrue(state.REST_ACCOUNT_ACCEPTED_ISSUED_TOKEN)
        self.assertEqual(post.call_count, 2)
        for call in post.call_args_list:
            self.assertIs(call.kwargs["allow_redirects"], False)
            self.assertEqual(call.kwargs["timeout"], 15)
        self.assertFalse(state.REAL_ORDERS_AUTHORIZED)
        self.assertEqual(state.ORDERING, "DISABLED")

if __name__ == "__main__":
    unittest.main()
