"""Offline-only verification of optional REAL ka10001 read-only local probe.

Every test mocks all Kiwoom HTTP requests; no broker secrets, orders,
permissions, remote-network connections, or production settings are accessed.
"""
from __future__ import annotations

import io
import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import kiwoom_real_quote_local_probe as probe

ENV = {
    "KIWOOM_ENV": "REAL",
    "KIWOOM_BASE_URL": "https://api.kiwoom.com",
    "KIWOOM_ORDERING_ENABLED": "false",
    "KIWOOM_APP_KEY": "synthetic-test-key",
    "KIWOOM_APP_SECRET": "synthetic-test-secret",
    "KIWOOM_ENABLE_READONLY_QUOTE_DIAGNOSTIC": "YES",
}
TOKEN = b'{"return_code":0,"token":"synthetic-test-token","expires_dt":"20991231235959","token_type":"bearer"}'
ACCOUNT = b'{"return_code":0,"acctNo":"synthetic-test-account"}'
QUOTE = b'{"return_code":0,"stk_cd":"005930","cur_prc":"+12345"}'


def reply(body, status=200):
    return SimpleNamespace(content=body, status_code=status)


class QuoteLocalProbeOfflineTests(unittest.TestCase):
    def test_opt_in_missing_never_calls_broker(self):
        env = dict(ENV)
        env.pop("KIWOOM_ENABLE_READONLY_QUOTE_DIAGNOSTIC")
        with patch.dict(os.environ, env, clear=True), \
             patch("kiwoom_real_type00_readonly_smoke.requests.post",
                   side_effect=AssertionError("no HTTP permitted")) as post:
            result = probe.one_shot("005930")
        post.assert_not_called()
        self.assertEqual(result["stage"], "PREFLIGHT_BLOCKED")

    def test_known_hosted_runtime_markers_prevent_broker_network(self):
        # A deliberately opted-in quote probe is not permitted from cloud CI
        # or Railway; even an empty/false marker means hosted provenance may
        # be present. No token is issued and no provider content is leaked.
        for marker in sorted(probe._HOSTED_RUNTIME_MARKERS):
            for marker_value in ("", "false", "synthetic-runner"):
                with self.subTest(marker=marker, value=marker_value), \
                     patch.dict(os.environ, dict(ENV, **{marker: marker_value}),
                                clear=True), \
                     patch("kiwoom_real_type00_readonly_smoke.requests.post",
                           side_effect=AssertionError("no hosted HTTP permitted")) as post:
                    result = probe.one_shot("005930")
                post.assert_not_called()
                self.assertEqual(result["stage"], "HOSTED_RUNTIME_BLOCKED")
                self.assertFalse(result["token_ok"])
                self.assertFalse(result["quote_response_structure_ok"])
                self.assertFalse(result["genuine_live_provenance_verified"])
                self.assertFalse(result["real_orders_authorized"])
                self.assertFalse(result["funds_movement_authorized"])
                # "false" is an expected JSON boolean literal, not a
                # leaked environment value. Assert only unique private data.
                self.assertNotIn("synthetic-runner", json.dumps(result))

    def test_hosted_runtime_cli_exits_failure_not_success(self):
        with patch.dict(os.environ, dict(ENV, RAILWAY_PROJECT_ID="synthetic-project"),
                        clear=True), \
             patch("sys.argv", ["kiwoom_real_quote_local_probe.py",
                                "--run-readonly-quote", "005930"]), \
             patch("kiwoom_real_type00_readonly_smoke.requests.post",
                   side_effect=AssertionError("no hosted HTTP permitted")) as post, \
             patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as done:
                probe.main()
        post.assert_not_called()
        self.assertEqual(done.exception.code, 2)
        report = json.loads(out.getvalue())
        self.assertEqual(report["stage"], "HOSTED_RUNTIME_BLOCKED")
        self.assertIs(report["genuine_live_provenance_verified"], False)
        self.assertIs(report["real_orders_authorized"], False)
        self.assertNotIn("synthetic-project", out.getvalue())

    def test_real_disabled_orders_and_credentials_are_preconditions(self):
        for override in (
            {"KIWOOM_ORDERING_ENABLED": "true"},
            {"KIWOOM_ORDERING_ENABLED": ""},
            {"KIWOOM_ENV": "DEMO"},
            {"KIWOOM_BASE_URL": "https://mockapi.kiwoom.com"},
            {"KIWOOM_APP_KEY": ""},
            {"KIWOOM_APP_SECRET": ""},
        ):
            with self.subTest(override=sorted(override)):
                with patch.dict(os.environ, dict(ENV, **override), clear=True), \
                     patch("kiwoom_real_type00_readonly_smoke.requests.post",
                           side_effect=AssertionError("no HTTP permitted")) as post:
                    result = probe.one_shot("005930")
                post.assert_not_called()
                self.assertFalse(result["quote_response_structure_ok"])
                self.assertFalse(result["real_orders_authorized"])

    def test_invalid_symbol_never_reaches_oauth_or_quote(self):
        for sym in ("00593", "005930_AL", "../005930", "", None, 5930, True):
            with self.subTest(symbol=repr(sym)):
                with patch.dict(os.environ, ENV, clear=True), \
                     patch("kiwoom_real_type00_readonly_smoke.requests.post",
                           side_effect=AssertionError("no HTTP permitted")) as post:
                    result = probe.one_shot(sym)
                post.assert_not_called()
                self.assertEqual(result["stage"], "QUOTE_CONTRACT_BLOCKED")

    def test_one_token_account_and_quote_no_redirects_without_authority(self):
        with patch.dict(os.environ, ENV, clear=True), \
             patch("kiwoom_real_type00_readonly_smoke.requests.post",
                   side_effect=[reply(TOKEN), reply(ACCOUNT), reply(QUOTE)]) as post:
            result = probe.one_shot("005930")
        self.assertEqual(post.call_count, 3)
        self.assertEqual(result["stage"], "QUOTE_STRUCTURE_ACCEPTED_PROVENANCE_UNVERIFIED")
        self.assertTrue(result["quote_response_structure_ok"])
        self.assertTrue(result["token_ok"])
        self.assertTrue(result["account_endpoint_ok"])
        self.assertFalse(result["genuine_live_provenance_verified"])
        for name in ("real_orders_authorized", "funds_movement_authorized",
                     "permission_change_authorized"):
            self.assertFalse(result[name])
        for call in post.call_args_list:
            self.assertIs(call.kwargs["allow_redirects"], False)
            self.assertEqual(call.kwargs["timeout"], 15)
        self.assertEqual(post.call_args_list[0].args[0],
                         "https://api.kiwoom.com/oauth2/token")
        self.assertEqual(post.call_args_list[1].kwargs["headers"]["api-id"], "ka00001")
        self.assertEqual(post.call_args_list[2].args[0],
                         "https://api.kiwoom.com/api/dostk/stkinfo")
        self.assertEqual(post.call_args_list[2].kwargs["headers"]["api-id"], "ka10001")
        self.assertEqual(post.call_args_list[2].kwargs["json"], {"stk_cd": "005930"})
        serialized=json.dumps(result)
        for secret in ("synthetic-test-token","synthetic-test-account",
                       "synthetic-test-key","synthetic-test-secret","12345"):
            self.assertNotIn(secret, serialized)

    def test_token_device_auth_denied_before_account_and_quote(self):
        with patch.dict(os.environ, ENV, clear=True), \
             patch("kiwoom_real_type00_readonly_smoke.requests.post",
                   side_effect=[reply(b'{"return_code":805004,"return_msg":"[8050: masked]"}')]) as post:
            result=probe.one_shot("005930")
        self.assertEqual(post.call_count, 1)
        self.assertEqual(result["stage"], "REST_PRECONDITION_NOT_MET")
        self.assertFalse(result["quote_response_structure_ok"])

    def test_account_device_auth_denied_before_quote(self):
        with patch.dict(os.environ, ENV, clear=True), \
             patch("kiwoom_real_type00_readonly_smoke.requests.post",
                   side_effect=[reply(TOKEN),reply(b'{"return_code":805004,"return_msg":"[8050: masked]"}')]) as post:
            result=probe.one_shot("005930")
        self.assertEqual(post.call_count,2)
        self.assertEqual(result["stage"],"REST_PRECONDITION_NOT_MET")
        self.assertFalse(result["account_endpoint_ok"])

    def test_http_redirect_and_denial_cannot_promote_quote(self):
        for status in (301,302,307,308,401,429,500,True,None):
            with self.subTest(status=status):
                with patch.dict(os.environ, ENV, clear=True), \
                     patch("kiwoom_real_type00_readonly_smoke.requests.post",
                           side_effect=[reply(TOKEN), reply(ACCOUNT),
                                        reply(QUOTE,status)]) as post:
                    result=probe.one_shot("005930")
                self.assertEqual(post.call_count,3)
                self.assertFalse(result["quote_response_structure_ok"])
                self.assertEqual(result["stage"],"QUOTE_CONTRACT_BLOCKED")
                self.assertIs(post.call_args_list[-1].kwargs["allow_redirects"],False)

    def test_wrong_symbol_and_malformed_quote_never_admitted(self):
        for body in (
            b'{"return_code":0,"stk_cd":"000660","cur_prc":"12345"}',
            b'{"return_code":0,"stk_cd":"005930","cur_prc":true}',
            b'{"return_code":0,"stk_cd":"005930","cur_prc":"12345","CUR_PRC":"789"}',
            b'{"return_code":805004,"return_msg":"[8050: redacted]"}',
        ):
            with self.subTest(case=body[:25]):
                with patch.dict(os.environ, ENV, clear=True), \
                     patch("kiwoom_real_type00_readonly_smoke.requests.post",
                           side_effect=[reply(TOKEN),reply(ACCOUNT),reply(body)]) as post:
                    result=probe.one_shot("005930")
                self.assertEqual(post.call_count,3)
                self.assertFalse(result["quote_response_structure_ok"])

    def test_quote_network_exception_is_private_and_no_retry(self):
        with patch.dict(os.environ, ENV, clear=True), \
             patch("kiwoom_real_type00_readonly_smoke.requests.post",
                   side_effect=[reply(TOKEN),reply(ACCOUNT),
                                RuntimeError("private synthetic-token proxy-secret 12345")]) as post:
            result=probe.one_shot("005930")
        self.assertEqual(post.call_count,3)
        self.assertEqual(result["stage"],"QUOTE_TRANSPORT_OR_LOCAL_ERROR")
        self.assertFalse(result["quote_response_structure_ok"])
        for private in ("synthetic-token","proxy-secret","12345"):
            self.assertNotIn(private,json.dumps(result))

    def test_main_synthetic_quote_only_exits_inconclusive_never_success(self):
        # A synthetic provider reply can prove JSON structure only, not
        # authentic REAL provenance. It must not exit 0 like a verified probe.
        with patch.dict(os.environ, ENV, clear=True), \
             patch("sys.argv", ["kiwoom_real_quote_local_probe.py",
                                "--run-readonly-quote", "005930"]), \
             patch("kiwoom_real_type00_readonly_smoke.requests.post",
                   side_effect=[reply(TOKEN), reply(ACCOUNT), reply(QUOTE)]) as post, \
             patch("sys.stdout", new_callable=io.StringIO) as output:
            with self.assertRaises(SystemExit) as exit_signal:
                probe.main()
        self.assertEqual(exit_signal.exception.code, 3)
        self.assertEqual(post.call_count, 3)
        report = json.loads(output.getvalue())
        self.assertEqual(report["stage"],
                         "QUOTE_STRUCTURE_ACCEPTED_PROVENANCE_UNVERIFIED")
        self.assertTrue(report["quote_response_structure_ok"])
        self.assertIs(report["genuine_live_provenance_verified"], False)
        self.assertIs(report["real_orders_authorized"], False)
        self.assertNotIn("synthetic-test-token", output.getvalue())
        self.assertNotIn("12345", output.getvalue())

    def test_main_rejected_quote_exits_failure_never_inconclusive(self):
        with patch.dict(os.environ, ENV, clear=True), \
             patch("sys.argv", ["kiwoom_real_quote_local_probe.py",
                                "--run-readonly-quote", "005930"]), \
             patch("kiwoom_real_type00_readonly_smoke.requests.post",
                   side_effect=[reply(TOKEN), reply(ACCOUNT),
                                reply(b'{"return_code":805004,"return_msg":"8050"}')]) as post, \
             patch("sys.stdout", new_callable=io.StringIO) as output:
            with self.assertRaises(SystemExit) as exit_signal:
                probe.main()
        self.assertEqual(exit_signal.exception.code, 2)
        self.assertEqual(post.call_count, 3)
        report = json.loads(output.getvalue())
        self.assertEqual(report["stage"], "QUOTE_CONTRACT_BLOCKED")
        self.assertFalse(report["quote_response_structure_ok"])

    def test_main_without_explicit_cli_flag_never_opens_network(self):
        with patch.dict(os.environ, ENV, clear=True), \
             patch("sys.argv", ["kiwoom_real_quote_local_probe.py"]), \
             patch("kiwoom_real_type00_readonly_smoke.requests.post",
                   side_effect=AssertionError("no HTTP permitted")) as post, \
             patch("sys.stdout",new_callable=io.StringIO) as output:
            with self.assertRaises(SystemExit) as exit_signal:
                probe.main()
        self.assertEqual(exit_signal.exception.code,2)
        post.assert_not_called()
        self.assertEqual(json.loads(output.getvalue())["stage"],"PREFLIGHT_BLOCKED")

if __name__=="__main__":
    unittest.main()
