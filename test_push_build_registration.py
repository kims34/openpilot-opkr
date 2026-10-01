import importlib
import unittest
from unittest import mock

from fastapi import FastAPI


class PushBuildRegistrationOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # unittest discovery imports every test module before test_monitor runs.
        # The overlay imports the production stack, which mutates shared monitor
        # globals, so delay that import until this suite actually executes.
        cls.build_overlay = importlib.import_module("push_build_registration")

    def test_attach_is_idempotent_and_exposes_client_build_schema(self):
        build_overlay = self.build_overlay
        app = FastAPI()

        # Seed legacy operational routes to prove the overlay replaces rather
        # than stacks duplicate handlers.
        @app.post("/register")
        def legacy_register():
            return {"legacy": True}

        @app.get("/push-health")
        def legacy_health():
            return {"legacy": True}

        # Build a schema before attach so the test also proves schema cache
        # invalidation when routes are replaced.
        app.openapi()
        build_overlay.attach(app)
        build_overlay.attach(app)

        register_routes = [
            route for route in app.router.routes
            if getattr(route, "path", None) == "/register"
        ]
        health_routes = [
            route for route in app.router.routes
            if getattr(route, "path", None) == "/push-health"
        ]
        self.assertEqual(len(register_routes), 1)
        self.assertEqual(len(health_routes), 1)
        self.assertIs(register_routes[0].endpoint, build_overlay.register_v32)
        self.assertIs(health_routes[0].endpoint, build_overlay.push_health_v32)

        schema = app.openapi()
        register_post = schema["paths"]["/register"]["post"]
        body_schema = register_post["requestBody"]["content"]["application/json"]["schema"]
        schema_name = body_schema["$ref"].rsplit("/", 1)[-1]
        properties = schema["components"]["schemas"][schema_name]["properties"]
        self.assertIn("client_build", properties)

    def test_contract_markers_are_frozen(self):
        build_overlay = self.build_overlay
        self.assertEqual(
            build_overlay.REGISTRATION_BUILD_CONTRACT,
            "register-client-build-v1",
        )
        self.assertEqual(
            build_overlay.SELF_TEST_TRIGGER_CONTRACT,
            "android-register-direct-v1",
        )
        self.assertEqual(
            build_overlay.PHYSICAL_E2E_BINDING_CONTRACT,
            "registered-device-build-receipt-v1",
        )
        self.assertEqual(
            build_overlay.PHYSICAL_E2E_BLOCKER_CONTRACT,
            "physical-e2e-blocker-v1",
        )
        self.assertEqual(
            set(build_overlay.PHYSICAL_E2E_BLOCKERS),
            {
                "NO_REGISTERED_BUILD",
                "NO_SELF_TEST",
                "DEVICE_MISMATCH",
                "BUILD_MISMATCH",
                "SELF_TEST_NOT_SENT",
                "RECEIPT_PENDING",
                "CONFIRMED",
            },
        )

    def test_display_only_server_rules_are_filled_without_synthesizing_alert_rules(self):
        build_overlay = self.build_overlay
        rules = build_overlay.monitor.RULES
        original = dict(rules)
        try:
            rules.clear()
            rules.update({
                "sp500": {"levels": [(5, 10)]},
                "ndx": {"levels": [(10, 10)]},
                "djdiv": {"levels": [(5, 15)]},
                "kospi100": {"levels": []},
                "usdkrw": {"levels": []},
            })
            supplied = {
                "sp500": [5],
                "ndx": [10],
                "djdiv": [5],
                "kospi100": [],
            }
            normalized = build_overlay._complete_display_only_levels(supplied)
            self.assertEqual(normalized["usdkrw"], [])
            self.assertEqual(normalized["sp500"], [5])

            # A missing alert-bearing rule must stay missing so the established
            # exact-key/threshold validator can still reject it fail-closed.
            missing_alert_rule = dict(supplied)
            missing_alert_rule.pop("ndx")
            normalized_missing = build_overlay._complete_display_only_levels(missing_alert_rule)
            self.assertNotIn("ndx", normalized_missing)
            self.assertEqual(normalized_missing["usdkrw"], [])
        finally:
            rules.clear()
            rules.update(original)

    def test_v47_registration_passes_completed_display_only_settings_to_base_validator(self):
        build_overlay = self.build_overlay
        rules = build_overlay.monitor.RULES
        original = dict(rules)
        captured = {}
        try:
            rules.clear()
            rules.update({
                "sp500": {"levels": [(5, 10)]},
                "ndx": {"levels": [(10, 10)]},
                "djdiv": {"levels": [(5, 15)]},
                "kospi100": {"levels": []},
                "usdkrw": {"levels": []},
            })

            def fake_register(body):
                captured["body"] = body
                return {"ok": True, "registered": True, "firebase": True, "protocol": 2}

            body = build_overlay.RegisterBodyV32(
                token="t" * 80,
                platform="android",
                protocol=2,
                client_build="4.7-47",
                enabled_levels={
                    "sp500": [5],
                    "ndx": [10],
                    "djdiv": [5],
                    "kospi100": [],
                },
            )
            with mock.patch.object(build_overlay.production, "register", side_effect=fake_register), \
                 mock.patch.object(build_overlay, "_record_device_build"):
                result = build_overlay.register_v32(body)

            self.assertEqual(captured["body"].enabled_levels["usdkrw"], [])
            self.assertEqual(captured["body"].enabled_levels["kospi100"], [])
            self.assertEqual(result["client_build"], "4.7-47")
            self.assertTrue(result["client_build_observed"])
        finally:
            rules.clear()
            rules.update(original)

    def test_v31_runtime_installs_the_same_build_bound_routes(self):
        build_overlay = self.build_overlay
        runtime = importlib.import_module("production_v31")
        register_routes = [
            route for route in runtime.app.router.routes
            if getattr(route, "path", None) == "/register"
        ]
        health_routes = [
            route for route in runtime.app.router.routes
            if getattr(route, "path", None) == "/push-health"
        ]
        self.assertEqual(len(register_routes), 1)
        self.assertEqual(len(health_routes), 1)
        self.assertIs(register_routes[0].endpoint, build_overlay.register_v32)
        self.assertIs(health_routes[0].endpoint, build_overlay.push_health_v32)

        schema = runtime.app.openapi()
        register_post = schema["paths"]["/register"]["post"]
        body_schema = register_post["requestBody"]["content"]["application/json"]["schema"]
        schema_name = body_schema["$ref"].rsplit("/", 1)[-1]
        properties = schema["components"]["schemas"][schema_name]["properties"]
        self.assertIn("client_build", properties)


if __name__ == "__main__":
    unittest.main()
