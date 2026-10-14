"""Network-free contract tests for the local registered-PC REAL route comparison."""
import io
import json
import os
import unittest
from unittest.mock import patch

import kiwoom_readonly_route_compare as probe


def state(*, stage="WS_LOGIN", code=805004, detail=8050, token_ok=True,
          account_ok=True, login_ok=False, ack_ok=False, events=0, policy="system"):
    return {
        "STAGE": stage,
        "RETURN_CODE": code,
        "DETAIL_CODE": detail,
        "ERROR_CLASS": "DEVICE_AUTH" if detail == 8050 else None,
        "WS_PROXY_POLICY": policy.upper(),
        "TOKEN_OK": token_ok,
        "ACCOUNT_ENDPOINT_OK": account_ok,
        "WS_CONNECTED": token_ok and account_ok,
        "WS_LOGIN_OK": login_ok,
        "TYPE00_REG_SENT": ack_ok,
        "TYPE00_REG_ACK_OK": ack_ok,
        "REST_ACCOUNT_ACCEPTED_ISSUED_TOKEN": account_ok,
        "REST_CONFIGURED_PROXY_PRESENT": False,
        "WS_SYSTEM_CONFIGURED_PROXY_PRESENT": False,
        "REST_WS_CONFIGURED_PROXY_URLS_EQUAL": True,
        "TYPE00_EVENT_COUNT": events,
        "ACCOUNT_MATCHED_TYPE00_EVENT_COUNT": events if account_ok and ack_ok else 0,
        "ORDERING": "DISABLED",
        "REAL_ORDERS_AUTHORIZED": False,
        "FUNDS_MOVEMENT_AUTHORIZED": False,
        "PERMISSION_CHANGE_AUTHORIZED": False,
        "GENUINE_LIVE_PROVENANCE_VERIFIED": False,
        "PRIVATE_ACCESS_TOKEN": "synthetic-never-print",
        "PRIVATE_ACCOUNT": "synthetic-private-account",
        "PRIVATE_PROXY_URL": "http://private-proxy/",
    }


class ReadonlyRouteCompareTests(unittest.TestCase):
    def test_fails_closed_before_network_with_missing_or_unsafe_configuration(self):
        good = {
            "KIWOOM_ENV": "REAL",
            "KIWOOM_BASE_URL": "https://api.kiwoom.com",
            "KIWOOM_ORDERING_ENABLED": "false",
            "KIWOOM_APP_KEY": "dummy-key",
            "KIWOOM_APP_SECRET": "dummy-secret",
        }
        probe._preflight(good)
        for key, value in [
            ("KIWOOM_ENV", "DEMO"),
            ("KIWOOM_BASE_URL", "https://mockapi.kiwoom.com"),
            ("KIWOOM_ORDERING_ENABLED", "true"),
            ("KIWOOM_APP_KEY", ""),
            ("KIWOOM_APP_SECRET", ""),
        ]:
            with self.subTest(key=key):
                changed = dict(good, **{key: value})
                with self.assertRaises(probe.DiagnosticError):
                    probe._preflight(changed)

    def test_only_allowlisted_fields_returned_from_subprocess(self):
        sample = state()
        reduced = probe._safe_summary(json.dumps(sample), 2, "system")
        self.assertEqual(reduced["DETAIL_CODE"], 8050)
        self.assertNotIn("PRIVATE_ACCESS_TOKEN", reduced)
        self.assertNotIn("PRIVATE_ACCOUNT", reduced)
        self.assertNotIn("PRIVATE_PROXY_URL", reduced)
        for secret in ("synthetic-never-print", "synthetic-private-account", "private-proxy"):
            self.assertNotIn(secret, json.dumps(reduced))
        for field, replacement in [
            ("STAGE", []),
            ("ERROR_CLASS", []),
            ("TYPE00_EVENT_COUNT", True),
            ("ACCOUNT_MATCHED_TYPE00_EVENT_COUNT", True),
            ("ACCOUNT_MATCHED_TYPE00_EVENT_COUNT", -1),
            ("ACCOUNT_MATCHED_TYPE00_EVENT_COUNT", 2),
            ("ORDERING", "ENABLED"),
            ("REAL_ORDERS_AUTHORIZED", True),
            ("FUNDS_MOVEMENT_AUTHORIZED", True),
            ("PERMISSION_CHANGE_AUTHORIZED", True),
            ("GENUINE_LIVE_PROVENANCE_VERIFIED", True),
            ("WS_PROXY_POLICY", "DIRECT"),
        ]:
            with self.subTest(field=field):
                bad = dict(sample, **{field: replacement})
                with self.assertRaises(probe.DiagnosticError):
                    probe._safe_summary(json.dumps(bad), 2, "system")

    def test_success_requires_ack_and_real_event_and_rejects_fake_exit(self):
        valid = state(stage="REAL_TYPE00_READ_ONLY_SMOKE", code=0, detail=None,
                      login_ok=True, ack_ok=True, events=1)
        self.assertEqual(probe._safe_summary(json.dumps(valid), 0, "system")["STAGE"],
                         "REAL_TYPE00_READ_ONLY_SMOKE")
        for mutation in [
            dict(valid, TYPE00_EVENT_COUNT=0),
            dict(valid, ACCOUNT_MATCHED_TYPE00_EVENT_COUNT=0),
            dict(valid, WS_LOGIN_OK=False),
            dict(valid, TYPE00_REG_ACK_OK=False),
        ]:
            with self.subTest(mutation=mutation):
                with self.assertRaises(probe.DiagnosticError):
                    probe._safe_summary(json.dumps(mutation), 0, "system")
        with self.assertRaises(probe.DiagnosticError):
            probe._safe_summary(json.dumps(state()), 0, "system")
        foreign_event = state(
            stage="TYPE00_EVENTS_UNMATCHED_ACCOUNT", code=0, detail=None,
            login_ok=True, ack_ok=True, events=1,
        )
        foreign_event["ACCOUNT_MATCHED_TYPE00_EVENT_COUNT"] = 0
        self.assertEqual(
            probe._safe_summary(json.dumps(foreign_event), 3, "system")["STAGE"],
            "TYPE00_EVENTS_UNMATCHED_ACCOUNT",
        )
        with self.assertRaises(probe.DiagnosticError):
            probe._safe_summary(json.dumps(foreign_event), 0, "system")
        incomplete = state()
        incomplete.pop("WS_LOGIN_OK")
        with self.assertRaises(probe.DiagnosticError):
            probe._safe_summary(json.dumps(incomplete), 2, "system")
        ack = state(stage="TYPE00_ACK_ONLY_NO_EVENTS", code=0, detail=None,
                    login_ok=True, ack_ok=True)
        self.assertEqual(probe._safe_summary(json.dumps(ack), 3, "system")["STAGE"],
                         "TYPE00_ACK_ONLY_NO_EVENTS")

    def test_only_retry_ws_specific_blocker_never_token_or_rest_or_success(self):
        blocked = state()
        self.assertTrue(probe._eligible_for_direct(blocked))
        self.assertFalse(probe._eligible_for_direct(
            state(stage="TOKEN", token_ok=False, account_ok=False)))
        self.assertFalse(probe._eligible_for_direct(
            state(stage="ACCOUNT", account_ok=False)))
        self.assertFalse(probe._eligible_for_direct(
            state(stage="REAL_TYPE00_READ_ONLY_SMOKE", code=0, detail=None,
                  login_ok=True, ack_ok=True, events=1)))
        self.assertFalse(probe._eligible_for_direct(
            state(stage="TYPE00_REG", login_ok=True)))
        self.assertEqual(probe._interpret(blocked, dict(blocked, WS_PROXY_POLICY="DIRECT")),
                         "8050_PERSISTS_IN_BOTH_WS_MODES")
        self.assertEqual(probe._interpret(
            blocked, dict(blocked, WS_PROXY_POLICY="DIRECT", WS_LOGIN_OK=True)),
            "ROUTE_DEPENDENT_OUTCOME_POSSIBLE")

    def test_one_token_and_one_rest_lookup_across_two_ws_policies(self):
        # Re-issuing OAuth would confound the intended 8050 route comparison.
        from kiwoom_real_type00_readonly_smoke import ReadOnlySmokeError
        env = {
            "KIWOOM_ENV": "REAL", "KIWOOM_BASE_URL": "https://api.kiwoom.com",
            "KIWOOM_ORDERING_ENABLED": "false",
            "KIWOOM_APP_KEY": "synthetic-key", "KIWOOM_APP_SECRET": "synthetic-secret",
            "KIWOOM_WS_PROXY_POLICY": "owner-original-setting",
        }
        issued, seen = 12345.678, []

        def account(state):
            state.TOKEN_OK = True
            state.ACCOUNT_ENDPOINT_OK = True
            state.REST_ACCOUNT_ACCEPTED_ISSUED_TOKEN = True
            return "synthetic-secret-token", "synthetic-account", issued

        async def ws(token, account_no, token_time, state):
            policy = os.environ.get("KIWOOM_WS_PROXY_POLICY")
            seen.append((policy, token, account_no, token_time))
            state.WS_CONNECTED = True
            if policy == "system":
                raise ReadOnlySmokeError("WS_LOGIN", 805004, 8050, "DEVICE_AUTH")
            if policy != "direct":
                raise AssertionError("unexpected route")
            state.WS_LOGIN_OK = True
            state.TYPE00_REG_SENT = True
            state.TYPE00_REG_ACK_OK = True
            state.TYPE00_EVENT_COUNT = 0

        with patch.dict(os.environ, env, clear=True), \
             patch("kiwoom_readonly_route_compare.smoke._token_and_account",
                   side_effect=account) as rest, \
             patch("kiwoom_readonly_route_compare.smoke._run_ws",
                   side_effect=ws) as stream, \
             patch("kiwoom_readonly_route_compare.smoke.requests.post",
                   side_effect=AssertionError("no real REST")) as network, \
             patch("sys.stdout", new_callable=io.StringIO) as capture:
            probe.main()
            self.assertEqual(os.environ["KIWOOM_WS_PROXY_POLICY"], "owner-original-setting")
        self.assertEqual(rest.call_count, 1)
        self.assertEqual(stream.call_count, 2)
        network.assert_not_called()
        self.assertEqual(seen, [
            ("system", "synthetic-secret-token", "synthetic-account", issued),
            ("direct", "synthetic-secret-token", "synthetic-account", issued),
        ])
        result = json.loads(capture.getvalue())
        self.assertEqual(result["assessment"], "ROUTE_DEPENDENT_OUTCOME_POSSIBLE")
        self.assertTrue(result["broker_connected"])
        self.assertEqual(result["direct"]["STAGE"], "TYPE00_ACK_ONLY_NO_EVENTS")
        self.assertTrue(result["direct"]["TYPE00_REG_ACK_OK"])
        self.assertFalse(result["real_orders_authorized"])
        self.assertFalse(result["funds_movement_authorized"])
        self.assertFalse(result["trading_readiness_proven"])
        self.assertNotIn("synthetic-secret-token", capture.getvalue())
        self.assertNotIn("synthetic-account", capture.getvalue())

    def test_token_error_never_attempts_any_websocket(self):
        from kiwoom_real_type00_readonly_smoke import ReadOnlySmokeError
        env = {
            "KIWOOM_ENV": "REAL", "KIWOOM_BASE_URL": "https://api.kiwoom.com",
            "KIWOOM_ORDERING_ENABLED": "false",
            "KIWOOM_APP_KEY": "synthetic-key", "KIWOOM_APP_SECRET": "synthetic-secret",
        }
        def deny(_state):
            raise ReadOnlySmokeError("TOKEN", 3, 8050, "DEVICE_AUTH")
        with patch.dict(os.environ, env, clear=True), \
             patch("kiwoom_readonly_route_compare.smoke._token_and_account",
                   side_effect=deny) as rest, \
             patch("kiwoom_readonly_route_compare.smoke._run_ws",
                   side_effect=AssertionError("WS forbidden")) as stream, \
             patch("kiwoom_readonly_route_compare.smoke.requests.post",
                   side_effect=AssertionError("real REST forbidden")) as network, \
             patch("sys.stdout", new_callable=io.StringIO) as capture:
            probe.main()
        rest.assert_called_once()
        stream.assert_not_called()
        network.assert_not_called()
        report = json.loads(capture.getvalue())
        self.assertEqual(report["assessment"], "REST_PRECONDITION_NOT_MET")
        self.assertIsNone(report["direct"])
        self.assertEqual(report["system"]["DETAIL_CODE"], 8050)

    def test_broker_exception_never_leaks_secrets(self):
        env = {
            "KIWOOM_ENV": "REAL", "KIWOOM_BASE_URL": "https://api.kiwoom.com",
            "KIWOOM_ORDERING_ENABLED": "false",
            "KIWOOM_APP_KEY": "synthetic-key", "KIWOOM_APP_SECRET": "synthetic-secret",
        }
        def sensitive_error(_state):
            raise RuntimeError("secret from provider synthetic-key")
        with patch.dict(os.environ, env, clear=True), \
             patch("kiwoom_readonly_route_compare.smoke._token_and_account",
                   side_effect=sensitive_error), \
             patch("sys.stdout", new_callable=io.StringIO) as capture:
            probe.main()
        report = json.loads(capture.getvalue())
        self.assertEqual(report["system"]["STAGE"], "LOCAL_COMPATIBILITY_OR_NETWORK")
        self.assertEqual(report["assessment"], "REST_PRECONDITION_NOT_MET")
        self.assertIsNone(report["direct"])
        self.assertNotIn("synthetic-key", capture.getvalue())


if __name__ == "__main__":
    unittest.main()
