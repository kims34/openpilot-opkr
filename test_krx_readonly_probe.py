from __future__ import annotations

import hashlib
import json
import os
import unittest
from unittest.mock import patch

from fastapi import FastAPI

import krx_readonly_probe as krx


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


class FakeSession:
    def __init__(self, payloads):
        self.payloads = payloads
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append(("GET", url, kwargs))
        return FakeResponse(self.payloads[url])

    def post(self, url, **kwargs):
        self.calls.append(("POST", url, kwargs))
        return FakeResponse(self.payloads[url])


def row_for(expected):
    return {name: "x" for name in expected}


def canonical_sha256(value):
    payload = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class KrxReadonlyProbeTests(unittest.TestCase):
    def setUp(self):
        self.old = os.environ.get("KRX_AUTH_KEY")

    def tearDown(self):
        if self.old is None:
            os.environ.pop("KRX_AUTH_KEY", None)
        else:
            os.environ["KRX_AUTH_KEY"] = self.old

    def test_missing_key_fails_closed(self):
        os.environ.pop("KRX_AUTH_KEY", None)
        out = krx.run_probe(candidate_dates=["20261001"])
        self.assertFalse(out["ok"])
        self.assertFalse(out["auth_key_present"])
        self.assertEqual(out["error"], "missing_auth_key")
        self.assertFalse(out["promotion_authority"])
        self.assertFalse(out["sealed_holdout_authorized"])
        self.assertFalse(out["live_trading_authorized"])

    def test_success_is_schema_only_and_never_exposes_key(self):
        secret = "TOP-SECRET-KRX-KEY"
        os.environ["KRX_AUTH_KEY"] = secret
        payloads = {
            spec["url"]: {"OutBlock_1": [row_for(spec["expected_fields"])]}
            for spec in krx.ENDPOINTS.values()
        }
        session = FakeSession(payloads)
        out = krx.run_probe(session=session, candidate_dates=["20261001"])

        self.assertTrue(out["ok"])
        self.assertEqual(out["basDd"], "20261001")
        self.assertTrue(out["auth_key_present"])
        self.assertFalse(out["promotion_authority"])
        self.assertFalse(out["krx_gate_closed"])
        self.assertFalse(out["sealed_holdout_authorized"])
        self.assertFalse(out["live_trading_authorized"])
        self.assertNotIn(secret, json.dumps(out))
        self.assertIsInstance(out["probe_observed_at"], str)
        self.assertTrue(out["probe_observed_at"].endswith("+00:00"))

        for name, spec in krx.ENDPOINTS.items():
            row = out["endpoints"][name]
            expected_payload = {"OutBlock_1": [row_for(spec["expected_fields"])]}
            self.assertEqual(
                row["response_schema_sha256"],
                canonical_sha256(sorted(spec["expected_fields"])),
            )
            self.assertEqual(
                row["response_payload_sha256"],
                canonical_sha256(expected_payload),
            )
            self.assertIsInstance(row["observed_at"], str)
            self.assertTrue(row["observed_at"].endswith("+00:00"))
            self.assertEqual(len(row["response_schema_sha256"]), 64)
            self.assertEqual(len(row["response_payload_sha256"]), 64)

        self.assertEqual(len(session.calls), 2)
        for method, _, kwargs in session.calls:
            self.assertEqual(method, "GET")
            self.assertEqual(kwargs["headers"]["AUTH_KEY"], secret)
            self.assertEqual(kwargs["params"], {"basDd": "20261001"})

    def test_get_failure_can_fallback_to_readonly_post(self):
        os.environ["KRX_AUTH_KEY"] = "secret"

        class FallbackSession:
            def __init__(self):
                self.calls = []

            def get(self, url, **kwargs):
                self.calls.append(("GET", url, kwargs))
                return FakeResponse({}, status_code=405)

            def post(self, url, **kwargs):
                self.calls.append(("POST", url, kwargs))
                expected = next(
                    set(spec["expected_fields"])
                    for spec in krx.ENDPOINTS.values()
                    if spec["url"] == url
                )
                return FakeResponse({"OutBlock_1": [row_for(expected)]})

        session = FallbackSession()
        out = krx.run_probe(session=session, candidate_dates=["20261001"])
        self.assertTrue(out["ok"])
        self.assertEqual([c[0] for c in session.calls], ["GET", "POST", "GET", "POST"])
        for method, _, kwargs in session.calls:
            if method == "POST":
                self.assertEqual(kwargs["json"], {"basDd": "20261001"})

    def test_schema_mismatch_never_becomes_ready(self):
        os.environ["KRX_AUTH_KEY"] = "secret"
        payloads = {spec["url"]: {"OutBlock_1": [{"unexpected": "x"}]} for spec in krx.ENDPOINTS.values()}
        session = FakeSession(payloads)
        out = krx.run_probe(session=session, candidate_dates=["20261001"])
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "no_verified_business_date")
        self.assertTrue(all(not v["schema_ok"] for v in out["endpoints"].values()))

    def test_attach_exposes_cached_health_only(self):
        app = FastAPI()
        with patch.object(krx, "refresh_probe") as refresh:
            krx.attach(app)
            paths = {route.path for route in app.routes}
            self.assertIn("/krx-health", paths)
            self.assertFalse(refresh.called)


if __name__ == "__main__":
    unittest.main()
