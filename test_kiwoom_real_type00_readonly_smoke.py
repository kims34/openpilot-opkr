import asyncio
import io
import json
import os
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from kiwoom_real_type00_readonly_smoke import (
    ReadOnlySmokeError,
    SmokeState,
    classify_detail,
    return_code,
    ws_return_code,
    strict_json,
    _config,
    _ws_proxy_options,
    _proxy_route_snapshot,
    _run_ws,
    main,
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

    def test_one_shot_completion_requires_events_and_admission(self):
        # REG ACK only is a valuable read-only broker-auth milestone, but
        # cannot be mistaken for observed broker-native events. This test
        # performs zero real REST or WS requests, and it never authorizes orders.
        def synthetic_account(state):
            state.TOKEN_OK = True
            state.ACCOUNT_ENDPOINT_OK = True
            state.REST_ACCOUNT_ACCEPTED_ISSUED_TOKEN = True
            return "synthetic-token", "synthetic-account", time.monotonic()

        def fake_ws(kind):
            async def run(_token, _account, _issued, state):
                state.WS_CONNECTED = True
                state.WS_LOGIN_OK = True
                state.TYPE00_REG_SENT = True
                state.TYPE00_REG_ACK_OK = kind != "no_ack"
                state.TYPE00_EVENT_COUNT = 1 if kind == "event" else 0
            return run

        for kind, exit_code, stage in (
            ("no_ack", 2, "TYPE00_ADMISSION_INCOMPLETE"),
            ("ack_only", 3, "TYPE00_ACK_ONLY_NO_EVENTS"),
            ("event", 0, "REAL_TYPE00_READ_ONLY_SMOKE"),
        ):
            with self.subTest(kind=kind):
                with patch("kiwoom_real_type00_readonly_smoke._token_and_account",
                           side_effect=synthetic_account) as account, \
                     patch("kiwoom_real_type00_readonly_smoke._run_ws",
                           side_effect=fake_ws(kind)) as ws, \
                     patch("kiwoom_real_type00_readonly_smoke.requests.post",
                           side_effect=AssertionError("real HTTP forbidden")) as rest, \
                     patch("sys.stdout", new_callable=io.StringIO) as output:
                    with self.assertRaises(SystemExit) as stopped:
                        main()
                self.assertEqual(stopped.exception.code, exit_code)
                state = json.loads(output.getvalue())
                self.assertEqual(state["STAGE"], stage)
                self.assertEqual(state["ORDERING"], "DISABLED")
                self.assertFalse(state["REAL_ORDERS_AUTHORIZED"])
                self.assertFalse(state["FUNDS_MOVEMENT_AUTHORIZED"])
                self.assertFalse(state["PERMISSION_CHANGE_AUTHORIZED"])
                self.assertFalse(state["GENUINE_LIVE_PROVENANCE_VERIFIED"])
                self.assertEqual(state["TYPE00_EVENT_COUNT"], 1 if kind == "event" else 0)
                self.assertEqual(state["TYPE00_REG_ACK_OK"], kind != "no_ack")
                self.assertNotIn("synthetic-token", output.getvalue())
                self.assertNotIn("synthetic-account", output.getvalue())
                account.assert_called_once()
                ws.assert_called_once()
                rest.assert_not_called()

    def test_type00_data_before_registration_ack_is_never_admitted(self):
        # A broker-like REAL message can arrive before any successful REG
        # acknowledgement. It must never count as a subscribed event or
        # broker-native execution proof, even if the payload looks authentic.
        frames = [
            '{"trnm":"LOGIN","return_code":0}',
            json.dumps({
                "trnm": "REAL",
                "data": [{
                    "type": "00",
                    "values": {
                        "9201": "synthetic-account", "913": "체결",
                        "909": "synthetic-order-no", "908": "103012",
                        "914": "1000", "915": "1",
                    },
                }],
            }),
            '{"trnm":"REG","return_code":0}',
        ]

        class OfflineSocket:
            def __init__(self):
                self.frames = list(frames)
                self.sent = []

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

            async def send(self, payload):
                self.sent.append(json.loads(payload))

            async def recv(self):
                if not self.frames:
                    raise AssertionError("unexpected read after pre-ACK REAL")
                return self.frames.pop(0)

        socket, state = OfflineSocket(), SmokeState()
        with patch("kiwoom_real_type00_readonly_smoke.websockets.connect",
                   return_value=socket) as connect, \
             patch("kiwoom_real_type00_readonly_smoke.requests.post",
                   side_effect=AssertionError("real network forbidden")) as rest:
            with self.assertRaises(ReadOnlySmokeError) as thrown:
                asyncio.run(_run_ws(
                    "synthetic-token", "synthetic-account", time.monotonic(), state))
        self.assertEqual(thrown.exception.stage, "TYPE00_FRAME_BEFORE_REG_ACK")
        self.assertTrue(state.WS_LOGIN_OK)
        self.assertTrue(state.TYPE00_REG_SENT)
        self.assertFalse(state.TYPE00_REG_ACK_OK)
        self.assertEqual(state.TYPE00_EVENT_COUNT, 0)
        self.assertEqual(state.ACCOUNT_MATCHED_TYPE00_EVENT_COUNT, 0)
        self.assertFalse(state.BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED)
        self.assertFalse(state.GENUINE_LIVE_PROVENANCE_VERIFIED)
        self.assertEqual(state.ORDERING, "DISABLED")
        self.assertFalse(state.REAL_ORDERS_AUTHORIZED)
        self.assertFalse(state.FUNDS_MOVEMENT_AUTHORIZED)
        self.assertEqual([x["trnm"] for x in socket.sent], ["LOGIN", "REG"])
        self.assertEqual(len(socket.frames), 1)  # later REG ACK never consumed
        connect.assert_called_once()
        rest.assert_not_called()
        self.assertNotIn("synthetic-account", json.dumps(state.__dict__))
        self.assertNotIn("synthetic-token", json.dumps(state.__dict__))

    def test_ws_return_code_accepts_official_numeric_strings_only(self):
        # The official Kiwoom client accepts numeric strings on WS replies.
        # Preserve fail-closed behavior for missing and ambiguous formats.
        for value in (0, "0", "0000", "805004", " 0 "):
            with self.subTest(valid=value):
                expected = 805004 if value == "805004" else 0
                self.assertEqual(ws_return_code({"return_code": value}), expected)
        for value in (True, 0.0, -1, "-1", "0x0", "", " ", "zero",
                      "0.0", "1e0", None, [], "00000000000"):
            with self.subTest(invalid=value):
                with self.assertRaises(ValueError):
                    ws_return_code({"return_code": value})
        with self.assertRaises(ValueError):
            ws_return_code({})

    def test_official_ws_string_success_codes_do_not_override_fault_barriers(self):
        # Numeric-string LOGIN and REG codes permit only the readonly
        # registration path; a later malformed REAL event must still stop.
        class SyntheticSocket:
            def __init__(self):
                self.frames = [
                    '{"trnm":"LOGIN","return_code":"0"}',
                    '{"trnm":"REG","return_code":"0000"}',
                    '{"trnm":"REAL","data":"malformed"}',
                ]
                self.sent = []

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

            async def send(self, payload):
                self.sent.append(json.loads(payload))

            async def recv(self):
                return self.frames.pop(0)

        sock, state = SyntheticSocket(), SmokeState()
        with patch("kiwoom_real_type00_readonly_smoke.websockets.connect",
                   return_value=sock) as connect, \
             patch("kiwoom_real_type00_readonly_smoke.requests.post",
                   side_effect=AssertionError("no real REST request")) as rest:
            with self.assertRaises(ReadOnlySmokeError) as err:
                asyncio.run(_run_ws(
                    "synthetic-token", "synthetic-account", time.monotonic(), state))
        self.assertEqual(err.exception.stage, "TYPE00_FRAME_PROTOCOL")
        self.assertTrue(state.WS_LOGIN_OK)
        self.assertTrue(state.TYPE00_REG_SENT)
        self.assertTrue(state.TYPE00_REG_ACK_OK)
        self.assertEqual([msg["trnm"] for msg in sock.sent], ["LOGIN", "REG"])
        self.assertFalse(state.GENUINE_LIVE_PROVENANCE_VERIFIED)
        self.assertFalse(state.REAL_ORDERS_AUTHORIZED)
        self.assertFalse(state.FUNDS_MOVEMENT_AUTHORIZED)
        self.assertEqual(state.TYPE00_EVENT_COUNT, 0)
        self.assertNotIn("synthetic-token", json.dumps(state.__dict__))
        connect.assert_called_once()
        rest.assert_not_called()

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

    def test_direct_route_is_reported_even_before_websocket_exists(self):
        # The paired diagnostic must be able to classify a second-run
        # token-stage failure without confusing it with the system route.
        env = {
            "KIWOOM_ENV": "REAL",
            "KIWOOM_BASE_URL": "https://api.kiwoom.com",
            "KIWOOM_ORDERING_ENABLED": "false",
            "KIWOOM_APP_KEY": "synthetic-key",
            "KIWOOM_APP_SECRET": "synthetic-secret",
            "KIWOOM_WS_PROXY_POLICY": "direct",
        }
        with patch.dict(os.environ, env, clear=True), \
             patch("kiwoom_real_type00_readonly_smoke.requests.post",
                   side_effect=[SimpleNamespace(content=b'{"return_code":3,"return_msg":"[8050: auth]"}')]) as post, \
             patch("kiwoom_real_type00_readonly_smoke._run_ws",
                   side_effect=AssertionError("WS must not start")) as ws, \
             patch("sys.stdout", new_callable=io.StringIO) as output:
            with self.assertRaises(SystemExit) as stopped:
                main()
        self.assertEqual(stopped.exception.code, 2)
        emitted = json.loads(output.getvalue())
        self.assertEqual(emitted["STAGE"], "TOKEN")
        self.assertEqual(emitted["WS_PROXY_POLICY"], "DIRECT")
        self.assertFalse(emitted["WS_CONNECTED"])
        self.assertFalse(emitted["REAL_ORDERS_AUTHORIZED"])
        post.assert_called_once()
        ws.assert_not_called()

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

    def test_token_or_account_8050_never_enters_websocket(self):
        # Both REAL failure stages have been observed independently. Only
        # synthetic provider bodies are supplied. No broker API is called.
        token_good = json.dumps({
            "return_code": 0, "token": "synthetic-secret-token",
            "expires_dt": "20991231235959", "token_type": "bearer",
        }).encode()
        denial = b'{"return_code":805004,"return_msg":"[8050: auth]"}'
        cases = (
            ("railway_token_8050", [b'{"return_code":3,"return_msg":"[8050: auth]"}'],
             "TOKEN", 3, False, 1),
            ("rest_account_8050", [token_good, denial],
             "ACCOUNT", 805004, True, 2),
        )
        safe_env = {
            "KIWOOM_ENV": "REAL",
            "KIWOOM_BASE_URL": "https://api.kiwoom.com",
            "KIWOOM_ORDERING_ENABLED": "false",
            "KIWOOM_APP_KEY": "synthetic-app-key",
            "KIWOOM_APP_SECRET": "synthetic-app-secret",
        }
        for name, replies, stage, code, token_ok, count in cases:
            with self.subTest(case=name):
                with patch.dict(os.environ, safe_env, clear=True), \
                     patch("kiwoom_real_type00_readonly_smoke.requests.post",
                           side_effect=[SimpleNamespace(content=item) for item in replies]) as post, \
                     patch("kiwoom_real_type00_readonly_smoke._run_ws",
                           side_effect=AssertionError("WebSocket must never start")) as ws, \
                     patch("sys.stdout", new_callable=io.StringIO) as capture:
                    with self.assertRaises(SystemExit) as stopped:
                        main()
                self.assertEqual(stopped.exception.code, 2)
                self.assertEqual(post.call_count, count)
                ws.assert_not_called()
                emitted = capture.getvalue()
                outcome = json.loads(emitted)
                self.assertEqual(outcome["STAGE"], stage)
                self.assertEqual(outcome["RETURN_CODE"], code)
                self.assertEqual(outcome["DETAIL_CODE"], 8050)
                self.assertEqual(outcome["ERROR_CLASS"], "TOKEN_OR_LOGIN_AUTH")
                self.assertEqual(outcome["TOKEN_OK"], token_ok)
                self.assertFalse(outcome["ACCOUNT_ENDPOINT_OK"])
                self.assertFalse(outcome["WS_CONNECTED"])
                self.assertFalse(outcome["WS_LOGIN_OK"])
                self.assertFalse(outcome["TYPE00_REG_SENT"])
                self.assertEqual(outcome["TYPE00_EVENT_COUNT"], 0)
                self.assertEqual(outcome["ORDERING"], "DISABLED")
                for flag in ("REAL_ORDERS_AUTHORIZED", "FUNDS_MOVEMENT_AUTHORIZED",
                             "PERMISSION_CHANGE_AUTHORIZED", "GENUINE_LIVE_PROVENANCE_VERIFIED"):
                    self.assertFalse(outcome[flag])
                for private in ("synthetic-secret-token", "synthetic-app-key",
                                "synthetic-app-secret", "Bearer "):
                    self.assertNotIn(private, emitted)

    def test_failed_type00_registration_does_not_claim_stream_readiness(self):
        # Successful synthetic LOGIN must not be confused with subscription
        # success: REG rejection and malformed ACK both fail closed.
        cases = (
            ("reg_8050", '{"trnm":"REG","return_code":805004,"return_msg":"[8050: auth]"}',
             "TYPE00_REG", 8050),
            ("duplicate_ack", '{"trnm":"REG","return_code":0,"RETURN_CODE":0}',
             "TYPE00_JSON_PROTOCOL", None),
        )

        class OfflineSocket:
            def __init__(self, ack):
                self.frames = [
                    '{"trnm":"LOGIN","return_code":0}',
                    ack,
                ]
                self.sent = []

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

            async def send(self, payload):
                self.sent.append(json.loads(payload))

            async def recv(self):
                if not self.frames:
                    raise AssertionError("unexpected extra read")
                return self.frames.pop(0)

        for label, ack, stage, detail in cases:
            with self.subTest(case=label):
                sock, state = OfflineSocket(ack), SmokeState()
                with patch("kiwoom_real_type00_readonly_smoke.websockets.connect",
                           return_value=sock) as connect, \
                     patch("kiwoom_real_type00_readonly_smoke.requests.post",
                           side_effect=AssertionError("HTTP network forbidden")) as rest:
                    with self.assertRaises(ReadOnlySmokeError) as thrown:
                        asyncio.run(_run_ws(
                            "synthetic-token", "synthetic-account", time.monotonic(), state))
                self.assertEqual(thrown.exception.stage, stage)
                self.assertEqual(thrown.exception.detail_code, detail)
                connect.assert_called_once()
                rest.assert_not_called()
                self.assertEqual([item["trnm"] for item in sock.sent], ["LOGIN", "REG"])
                self.assertEqual(sock.sent[1]["data"], [{"item": [], "type": ["00"]}])
                self.assertTrue(state.WS_LOGIN_OK)
                self.assertTrue(state.TYPE00_REG_SENT)
                self.assertFalse(state.TYPE00_REG_ACK_OK)
                self.assertEqual(state.TYPE00_EVENT_COUNT, 0)
                self.assertFalse(state.BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED)
                self.assertEqual(state.ORDERING, "DISABLED")
                self.assertFalse(state.REAL_ORDERS_AUTHORIZED)
                self.assertFalse(state.GENUINE_LIVE_PROVENANCE_VERIFIED)
                self.assertNotIn("synthetic-account", json.dumps(state.__dict__))

    def test_proxy_route_snapshot_is_offline_redacted_and_non_authoritative(self):
        # Identifies configuration-level mismatches without emitting credentials,
        # private routing addresses, full URLs, or asserting real public-IP parity.
        cases = (
            (None, None, (False, False, True)),
            ("http://rest-proxy.internal:8080", None, (True, False, False)),
            ("http://common.internal:8080", "http://common.internal:8080",
             (True, True, True)),
            ("http://rest-proxy.internal:8080", "http://ws-proxy.internal:8080",
             (True, True, False)),
        )
        for rest_url, ws_url, expected in cases:
            with self.subTest(expected=expected):
                settings = {"https": rest_url} if rest_url else {}
                with patch("kiwoom_real_type00_readonly_smoke.requests.utils.get_environ_proxies",
                           return_value=settings) as rest_read, \
                     patch("kiwoom_real_type00_readonly_smoke._websockets_get_proxy",
                           return_value=ws_url) as ws_read, \
                     patch("kiwoom_real_type00_readonly_smoke.requests.post",
                           side_effect=AssertionError("HTTP network forbidden")) as net:
                    observed = _proxy_route_snapshot()
                self.assertEqual(observed, expected)
                rest_read.assert_called_once()
                ws_read.assert_called_once()
                net.assert_not_called()
                state = SmokeState()
                state.REST_CONFIGURED_PROXY_PRESENT, \
                    state.WS_SYSTEM_CONFIGURED_PROXY_PRESENT, \
                    state.REST_WS_CONFIGURED_PROXY_URLS_EQUAL = observed
                redacted = json.dumps(state.__dict__)
                self.assertNotIn("internal", redacted)
                self.assertNotIn("8080", redacted)
                self.assertFalse(state.REAL_ORDERS_AUTHORIZED)

        with patch("kiwoom_real_type00_readonly_smoke.requests.utils.get_environ_proxies",
                   side_effect=ValueError("redact endpoint")):
            self.assertEqual(_proxy_route_snapshot(), (None, None, None))

    def test_ws_proxy_routing_requires_explicit_opt_in(self):
        # websockets 15 auto-selects proxies by default. The opt-in direct
        # policy must be explicit, never inferred from broker 8050 alone.
        safe_env = {
            "KIWOOM_ENV": "REAL",
            "KIWOOM_BASE_URL": "https://api.kiwoom.com",
            "KIWOOM_ORDERING_ENABLED": "false",
            "KIWOOM_APP_KEY": "synthetic-key",
            "KIWOOM_APP_SECRET": "synthetic-secret",
        }
        with patch.dict(os.environ, safe_env, clear=True):
            self.assertEqual(_ws_proxy_options(), {})
            _config()
        with patch.dict(os.environ,
                        dict(safe_env, KIWOOM_WS_PROXY_POLICY="direct"),
                        clear=True):
            self.assertEqual(_ws_proxy_options(), {"proxy": None})
            _config()
        with patch.dict(os.environ,
                        dict(safe_env, KIWOOM_WS_PROXY_POLICY="auto-fix-8050"),
                        clear=True):
            with self.assertRaises(ReadOnlySmokeError) as blocked:
                _config()
            self.assertEqual(blocked.exception.stage, "CONFIG")

        class LoginDeniedSocket:
            def __init__(self):
                self.sent = []

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

            async def send(self, payload):
                self.sent.append(json.loads(payload))

            async def recv(self):
                return '{"trnm":"LOGIN","return_code":805004,"return_msg":"[8050: auth]"}'

        for policy, expected_kwarg, expected_state in (
            ("system", False, "SYSTEM"), ("direct", True, "DIRECT"),
        ):
            with self.subTest(policy=policy):
                sock, state = LoginDeniedSocket(), SmokeState()
                with patch.dict(os.environ, dict(safe_env, KIWOOM_WS_PROXY_POLICY=policy),
                                clear=True), \
                     patch("kiwoom_real_type00_readonly_smoke.websockets.connect",
                           return_value=sock) as connect, \
                     patch("kiwoom_real_type00_readonly_smoke.requests.post",
                           side_effect=AssertionError("real HTTP forbidden")) as rest:
                    with self.assertRaises(ReadOnlySmokeError) as denied:
                        asyncio.run(_run_ws(
                            "synthetic-token", "synthetic-account", time.monotonic(), state))
                self.assertEqual(denied.exception.stage, "WS_LOGIN")
                self.assertEqual(state.WS_PROXY_POLICY, expected_state)
                self.assertEqual("proxy" in connect.call_args.kwargs, expected_kwarg)
                if expected_kwarg:
                    self.assertIsNone(connect.call_args.kwargs["proxy"])
                self.assertEqual([m["trnm"] for m in sock.sent], ["LOGIN"])
                rest.assert_not_called()
                self.assertFalse(state.WS_LOGIN_OK)
                self.assertFalse(state.TYPE00_REG_SENT)
                self.assertFalse(state.REAL_ORDERS_AUTHORIZED)
                self.assertFalse(state.FUNDS_MOVEMENT_AUTHORIZED)

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
