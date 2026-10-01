import importlib
import unittest

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


if __name__ == "__main__":
    unittest.main()
