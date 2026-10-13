import asyncio
import json
import os
import time
import unittest
from unittest.mock import patch

from kiwoom_real_type00_readonly_smoke import (
    ReadOnlySmokeError,
    SmokeState,
    classify_detail,
    return_code,
    strict_json,
    _config,
    _run_ws,
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

    def test_login_rejection_never_subscribes_or_activates_orders(self):
        # Offline replay of the observed 805004/8050, malformed and out-of-order
        # broker replies.  No real socket, REST request, REG or order is allowed.
        cases = (
            ('8050', '{"trnm":"LOGIN","return_code":805004,"return_msg":"[8050: auth]"}',
             "WS_LOGIN", 8050, "TOKEN_OR_LOGIN_AUTH"),
            ('duplicate', '{"trnm":"LOGIN","return_code":0,"RETURN_CODE":0}',
             "WS_LOGIN_PROTOCOL", None, None),
            ('wrong_trnm', '{"trnm":"REG","return_code":0}',
             "WS_LOGIN_PROTOCOL", None, None),
        )

        class OfflineSocket:
            def __init__(self, frame):
                self.frame = frame
                self.sent = []
                self.received = False

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

            async def send(self, payload):
                self.sent.append(json.loads(payload))

            async def recv(self):
                if self.received:
                    raise AssertionError("unexpected extra websocket receive")
                self.received = True
                return self.frame

        for name, frame, expected_stage, detail, classification in cases:
            with self.subTest(case=name):
                sock = OfflineSocket(frame)
                state = SmokeState()
                with patch("kiwoom_real_type00_readonly_smoke.websockets.connect",
                           return_value=sock) as connect, \
                     patch("kiwoom_real_type00_readonly_smoke.requests.post",
                           side_effect=AssertionError("network HTTP forbidden")) as rest:
                    with self.assertRaises(ReadOnlySmokeError) as err:
                        asyncio.run(_run_ws(
                            "synthetic-token", "synthetic-account", time.monotonic(), state))
                self.assertEqual(err.exception.stage, expected_stage)
                self.assertEqual(err.exception.detail_code, detail)
                self.assertEqual(err.exception.error_class, classification)
                connect.assert_called_once()
                rest.assert_not_called()
                self.assertEqual(len(sock.sent), 1)  # LOGIN only, never REG
                self.assertEqual(sock.sent[0]["trnm"], "LOGIN")
                self.assertEqual(sock.sent[0]["token"], "synthetic-token")
                self.assertTrue(state.WS_CONNECTED)
                self.assertFalse(state.WS_LOGIN_OK)
                self.assertFalse(state.TYPE00_REG_SENT)
                self.assertFalse(state.TYPE00_REG_ACK_OK)
                self.assertEqual(state.TYPE00_EVENT_COUNT, 0)
                self.assertEqual(state.ORDERING, "DISABLED")
                self.assertFalse(state.REAL_ORDERS_AUTHORIZED)
                self.assertFalse(state.FUNDS_MOVEMENT_AUTHORIZED)
                self.assertFalse(state.PERMISSION_CHANGE_AUTHORIZED)
                self.assertFalse(state.GENUINE_LIVE_PROVENANCE_VERIFIED)
                self.assertNotIn("synthetic-token", json.dumps(state.__dict__))
                self.assertNotIn("synthetic-account", json.dumps(state.__dict__))

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
