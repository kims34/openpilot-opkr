import unittest
from unittest.mock import Mock, patch
from kiwoom_token_mode_probe import _detail_code, attempt

class TokenModeProbeTests(unittest.TestCase):
    def test_detail_code_is_numeric_only(self):
        self.assertEqual(_detail_code("[8030: mode mismatch]"),8030)
        self.assertEqual(_detail_code("CODE=8050: auth"),8050)
        self.assertIsNone(_detail_code("no code"))

    @patch("kiwoom_token_mode_probe.requests.post")
    def test_attempt_never_returns_token_or_message(self, post):
        response=Mock(status_code=200)
        response.json.return_value={
            "return_code":0,"return_msg":"secret-ish provider text",
            "token":"private-token","expires_dt":"20261009235959","token_type":"Bearer"
        }
        post.return_value=response
        out=attempt("https://example.invalid","key","secret")
        self.assertEqual(out["return_code"],0)
        self.assertTrue(out["token_present"])
        self.assertNotIn("token", out)
        self.assertNotIn("return_msg", out)
        self.assertNotIn("message", out)

    @patch("kiwoom_token_mode_probe.requests.post")
    def test_broker_8050_denial_cannot_claim_token_issuance(self, post):
        # Even if a malformed/hostile response includes token-like fields,
        # broker denial takes precedence over structural field presence.
        for code in (805004, 8050, -1, None, True, "0"):
            with self.subTest(code=repr(code)):
                response = Mock(status_code=200)
                response.json.return_value = {
                    "return_code": code,
                    "return_msg": "[8050: synthetic redacted denial]",
                    "token": "synthetic-private-token",
                    "expires_dt": "20991231235959",
                    "token_type": "Bearer",
                }
                post.return_value = response
                out = attempt("https://api.kiwoom.com",
                              "synthetic-key", "synthetic-secret")
                self.assertFalse(out["token_present"])
                self.assertFalse(out["expiry_present"])
                self.assertFalse(out["token_type_present"])
                self.assertEqual(out["detail_code"], 8050)
                self.assertEqual(out["return_code"],
                                 code if type(code) is int else None)
                self.assertIs(post.call_args.kwargs["allow_redirects"], False)
                self.assertNotIn("synthetic-private-token", str(out))

    @patch("kiwoom_token_mode_probe.requests.post")
    def test_success_code_with_empty_token_does_not_fake_token_presence(self, post):
        response = Mock(status_code=200)
        response.json.return_value = {
            "return_code": 0,
            "token": " ",
            "expires_dt": "20991231235959",
            "token_type": "Bearer",
        }
        post.return_value = response
        out = attempt("https://api.kiwoom.com",
                      "synthetic-key", "synthetic-secret")
        self.assertEqual(out["return_code"], 0)
        self.assertFalse(out["token_present"])
        self.assertTrue(out["expiry_present"])
        self.assertTrue(out["token_type_present"])

    @patch("kiwoom_token_mode_probe.requests.post")
    def test_redirect_does_not_consume_provider_body(self, post):
        for status in (301, 302, 303, 307, 308):
            with self.subTest(status=status):
                response=Mock(status_code=status)
                response.json.side_effect=AssertionError("Never inspect redirect body")
                post.reset_mock()
                post.return_value=response
                out=attempt("https://api.kiwoom.com","synthetic-key","synthetic-secret")
                self.assertEqual(out["http_status"],status)
                self.assertIsNone(out["return_code"])
                self.assertFalse(out["token_present"])
                self.assertFalse(out["expiry_present"])
                self.assertFalse(out["token_type_present"])
                response.json.assert_not_called()
                post.assert_called_once()
                self.assertIs(post.call_args.kwargs["allow_redirects"],False)

    @patch("kiwoom_token_mode_probe.requests.post")
    def test_http_error_or_malformed_status_never_grants_token(self, post):
        for status in (401, 429, 500, None, True):
            with self.subTest(status=status):
                response=Mock(status_code=status)
                response.json.side_effect=AssertionError("Non-200 cannot be successful")
                post.return_value=response
                out=attempt("https://mockapi.kiwoom.com","synthetic-key","synthetic-secret")
                self.assertFalse(out["token_present"])
                self.assertIsNone(out["return_code"])
                response.json.assert_not_called()
                self.assertIs(post.call_args.kwargs["allow_redirects"],False)

if __name__=="__main__":
    unittest.main()
