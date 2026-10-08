import json
import os
import unittest
from unittest.mock import patch

from kiwoom_real_type00_readonly_smoke import (
    ReadOnlySmokeError,
    SmokeState,
    classify_detail,
    return_code,
    strict_json,
    _config,
    _type00_observation,
)


class KiwoomRealType00PythonSmokeTests(unittest.TestCase):
    def test_strict_json_rejects_duplicate_keys_case_insensitive(self):
        with self.assertRaises(ValueError):
            strict_json('{"return_code":0,"RETURN_CODE":0}')

    def test_strict_json_rejects_non_object_and_nonstandard_constants(self):
        for raw in ('[]', '{"x":NaN}', ''):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    strict_json(raw)

    def test_return_code_requires_exact_nonnegative_integer(self):
        self.assertEqual(return_code({"return_code": 0}), 0)
        for value in (True, -1, 1.0, "0", None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    return_code({"return_code": value})

    def test_8050_is_token_or_login_auth(self):
        self.assertEqual(classify_detail("[8050: login auth]"), (8050, "TOKEN_OR_LOGIN_AUTH"))
        self.assertEqual(classify_detail("CODE=8010: device"), (8010, "DEVICE_AUTH"))

    def test_config_requires_real_disabled_ordering(self):
        good = {
            "KIWOOM_ENV": "REAL",
            "KIWOOM_BASE_URL": "https://api.kiwoom.com",
            "KIWOOM_ORDERING_ENABLED": "false",
            "KIWOOM_APP_KEY": "present",
            "KIWOOM_APP_SECRET": "present",
        }
        with patch.dict(os.environ, good, clear=True):
            self.assertEqual(_config(), ("present", "present"))
        for key, bad in (
            ("KIWOOM_ENV", "MOCK"),
            ("KIWOOM_BASE_URL", "https://mockapi.kiwoom.com"),
            ("KIWOOM_ORDERING_ENABLED", "true"),
            ("KIWOOM_APP_KEY", ""),
            ("KIWOOM_APP_SECRET", ""),
        ):
            env = dict(good)
            env[key] = bad
            with self.subTest(key=key), patch.dict(os.environ, env, clear=True):
                with self.assertRaises(ReadOnlySmokeError):
                    _config()

    def test_type00_observation_is_redacted_count_only(self):
        obj = {
            "trnm": "REAL",
            "data": [{
                "type": "00",
                "values": {
                    "9201": "private-account",
                    "913": "체결",
                    "909": "execution-id",
                    "908": "101010",
                    "914": "1000",
                    "915": "2",
                },
            }],
        }
        self.assertEqual(_type00_observation(obj, "private-account"), (1, 1, True))

    def test_output_state_cannot_claim_authority(self):
        state = SmokeState()
        self.assertEqual(state.ORDERING, "DISABLED")
        self.assertFalse(state.REAL_ORDERS_AUTHORIZED)
        self.assertFalse(state.FUNDS_MOVEMENT_AUTHORIZED)
        self.assertFalse(state.PERMISSION_CHANGE_AUTHORIZED)
        self.assertFalse(state.GENUINE_LIVE_PROVENANCE_VERIFIED)
        encoded = json.dumps(state.__dict__)
        # Redacted diagnostics may contain field names containing "TOKEN", but
        # never a token value, account identifier or credential-bearing field.
        self.assertNotIn("ACCESS_TOKEN", state.__dict__)
        self.assertNotIn("APP_KEY", state.__dict__)
        self.assertNotIn("APP_SECRET", state.__dict__)
        self.assertNotIn("ACCOUNT_NUMBER", state.__dict__)
        self.assertNotIn("private-account", encoded)
        self.assertNotIn("execution-id", encoded)


if __name__ == "__main__":
    unittest.main()
