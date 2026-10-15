"""Network-free ka10001 quote-envelope and response-shape regressions."""
import inspect
import json
import unittest

import kiwoom_real_quote_readonly_contract as q


class QuoteReadonlyContractTests(unittest.TestCase):
    def test_official_ka10001_request_envelope_is_inert(self):
        req = q.offline_quote_envelope("005930")
        self.assertEqual(req["method"], "POST")
        self.assertEqual(req["path"], "/api/dostk/stkinfo")
        self.assertEqual(req["api_id"], "ka10001")
        self.assertEqual(req["body"], {"stk_cd": "005930"})
        for name in ("network_request_sent", "real_quote_verified",
                     "real_orders_authorized", "funds_movement_authorized"):
            self.assertIs(req[name], False)
        self.assertNotIn("Bearer", json.dumps(req))

    def test_invalid_stock_code_is_rejected(self):
        for value in ("", "5930", "005930_NX", "005930_AL", "0000007",
                      " 005930", "005930 ", "00593\n", "../stkinfo",
                      "00593?", "00593０", 5930, None, False, [], {}):
            with self.subTest(value=repr(value)):
                with self.assertRaises(q.QuoteContractError):
                    q.offline_quote_envelope(value)

    def test_synthetic_reply_structure_does_not_claim_live_evidence(self):
        reply = {"return_code": 0, "stk_cd": "005930", "cur_prc": "+12345",
                 "return_msg": "synthetic-secret-provider-message"}
        out = q.offline_quote_structure(stock_code="005930", http_status=200,
                                        response_body=json.dumps(reply))
        self.assertTrue(out["structural_contract_passed"])
        for k in ("live_broker_connection_verified", "real_quote_verified",
                  "real_orders_authorized", "funds_movement_authorized"):
            self.assertIs(out[k], False)
        self.assertNotIn("12345", json.dumps(out))
        self.assertNotIn("synthetic-secret", json.dumps(out))

    def test_quote_reply_wrong_symbol_fails_closed(self):
        with self.assertRaises(q.QuoteContractError):
            q.offline_quote_structure(
                stock_code="005930", http_status=200,
                response_body=b'{"return_code":0,"stk_cd":"000660","cur_prc":"12345"}')

    def test_http_redirect_and_error_are_denied_before_body(self):
        ok_body = b'{"return_code":0,"stk_cd":"005930","cur_prc":"12345"}'
        for code in (301, 302, 307, 308, 401, 429, 500, True, 200.0, None):
            with self.subTest(code=code):
                with self.assertRaises(q.QuoteContractError):
                    q.offline_quote_structure(stock_code="005930",
                                              http_status=code, response_body=ok_body)

    def test_malformed_and_duplicate_quote_messages_are_denied(self):
        cases = (
            '{"return_code":0,"return_code":0,"stk_cd":"005930","cur_prc":"12"}',
            '{"return_code":0,"stk_cd":"005930","cur_prc":"1","CUR_PRC":"1"}',
            '{"return_code":"0","stk_cd":"005930","cur_prc":"12"}',
            '{"return_code":true,"stk_cd":"005930","cur_prc":"12"}',
            '{"return_code":NaN,"stk_cd":"005930","cur_prc":"12"}',
            '{"return_code":0,"stk_cd":"005930","cur_prc":12345}',
            '{"return_code":0,"stk_cd":"005930","cur_prc":"12.3"}',
            '{"return_code":0,"stk_cd":"005930","cur_prc":""}',
            '{"return_code":805004,"stk_cd":"005930","cur_prc":"12"}',
            '[]', '{}',
        )
        for body in cases:
            with self.subTest(body=body):
                with self.assertRaises(q.QuoteContractError):
                    q.offline_quote_structure(
                        stock_code="005930", http_status=200, response_body=body)

    def test_payload_size_and_types_are_bounded(self):
        for body in (b"", b"x"*65_537, {}, [], 1):
            with self.subTest(type=type(body).__name__):
                with self.assertRaises(q.QuoteContractError):
                    q.offline_quote_structure(stock_code="005930", http_status=200,
                                              response_body=body)

    def test_no_http_transport_order_or_private_key_dependency(self):
        source = inspect.getsource(q)
        for forbidden in ("import requests", "import websockets", "http.client",
                          "urlopen(", "requests.post(", "/api/dostk/ordr",
                          "kt10000", "kt10001", "kt10002", "kt10003",
                          "os.environ", "KIWOOM_APP_SECRET"):
            self.assertNotIn(forbidden, source)
