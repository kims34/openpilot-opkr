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

if __name__=="__main__":
    unittest.main()
