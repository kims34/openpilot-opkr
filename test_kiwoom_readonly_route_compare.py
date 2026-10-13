"""Network-free contract tests for the local registered-PC REAL route comparison."""
import io
import json
import os
import subprocess
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import kiwoom_readonly_route_compare as probe


def state(*, stage="WS_LOGIN", code=805004, detail=8050, token_ok=True,
          account_ok=True, login_ok=False, ack_ok=False, events=0, policy="system"):
    return {
        "STAGE": stage,
        "RETURN_CODE": code,
        "DETAIL_CODE": detail,
        "ERROR_CLASS": "TOKEN_OR_LOGIN_AUTH" if detail == 8050 else None,
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
            dict(valid, WS_LOGIN_OK=False),
            dict(valid, TYPE00_REG_ACK_OK=False),
        ]:
            with self.subTest(mutation=mutation):
                with self.assertRaises(probe.DiagnosticError):
                    probe._safe_summary(json.dumps(mutation), 0, "system")
        with self.assertRaises(probe.DiagnosticError):
            probe._safe_summary(json.dumps(state()), 0, "system")
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

    def test_subprocess_invocation_limits_network_to_two_serial_smokes(self):
        samples = [
            state(policy="system"),
            state(stage="TYPE00_ACK_ONLY_NO_EVENTS", code=0, detail=None,
                  login_ok=True, ack_ok=True, policy="direct"),
        ]
        env = {
            "KIWOOM_ENV": "REAL", "KIWOOM_BASE_URL": "https://api.kiwoom.com",
            "KIWOOM_ORDERING_ENABLED": "false",
            "KIWOOM_APP_KEY": "synthetic-key", "KIWOOM_APP_SECRET": "synthetic-secret",
        }
        seen = []
        def fake_run(argv, **kwargs):
            self.assertEqual(kwargs["stderr"], subprocess.DEVNULL)
            self.assertEqual(argv[1], "-B")
            self.assertIn("kiwoom_real_type00_readonly_smoke.py", argv[2])
            self.assertFalse(kwargs["check"])
            self.assertLessEqual(kwargs["timeout"], 100)
            seen.append(kwargs["env"]["KIWOOM_WS_PROXY_POLICY"])
            val = samples[len(seen) - 1]
            return SimpleNamespace(stdout=json.dumps(val), returncode=2 if len(seen)==1 else 3)

        with patch.dict(os.environ, env, clear=True), \
             patch("kiwoom_readonly_route_compare.subprocess.run",
                   side_effect=fake_run) as run, \
             patch("sys.stdout", new_callable=io.StringIO) as capture:
            probe.main()
        self.assertEqual(seen, ["system", "direct"])
        self.assertEqual(run.call_count, 2)
        printed = capture.getvalue()
        report = json.loads(printed)
        self.assertTrue(report["broker_connected"])
        self.assertFalse(report["real_orders_authorized"])
        self.assertFalse(report["trading_readiness_proven"])
        self.assertEqual(report["assessment"], "ROUTE_DEPENDENT_OUTCOME_POSSIBLE")
        for sensitive in ("synthetic-key", "synthetic-secret", "synthetic-private-account"):
            self.assertNotIn(sensitive, printed)

    def test_if_first_run_fails_before_ws_skip_direct(self):
        env = {
            "KIWOOM_ENV": "REAL", "KIWOOM_BASE_URL": "https://api.kiwoom.com",
            "KIWOOM_ORDERING_ENABLED": "false",
            "KIWOOM_APP_KEY": "synthetic-key", "KIWOOM_APP_SECRET": "synthetic-secret",
        }
        payload = state(stage="TOKEN", code=3, detail=8050, token_ok=False, account_ok=False)
        with patch.dict(os.environ, env, clear=True), \
             patch("kiwoom_readonly_route_compare.subprocess.run",
                   return_value=SimpleNamespace(stdout=json.dumps(payload),returncode=2)) as run, \
             patch("sys.stdout", new_callable=io.StringIO) as capture:
            probe.main()
        self.assertEqual(run.call_count, 1)
        report = json.loads(capture.getvalue())
        self.assertIsNone(report["direct"])
        self.assertEqual(report["assessment"], "REST_PRECONDITION_NOT_MET")


if __name__ == "__main__":
    unittest.main()
