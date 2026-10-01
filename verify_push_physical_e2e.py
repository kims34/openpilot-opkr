"""Read-only verifier for IndexAlert Android Physical E2E push evidence.

This verifier never sends FCM, registers a device or writes a receipt. It only
checks the privacy-safe production /push-health payload for evidence that the
specified Android build's most recent self-test was sent and acknowledged by a
real client receipt.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

import requests


class PhysicalE2EVerificationError(ValueError):
    pass


def _build(value: str) -> str:
    build = str(value or "").strip()
    if not build or len(build) > 80:
        raise PhysicalE2EVerificationError("expected_build must be non-empty and <= 80 characters")
    if any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-+" for ch in build):
        raise PhysicalE2EVerificationError("expected_build contains unsupported characters")
    return build


def verify_push_health(payload: Mapping[str, Any], *, expected_build: str) -> dict[str, Any]:
    """Return a fail-closed, read-only audit of current-build physical receipt evidence."""
    build = _build(expected_build)
    if not isinstance(payload, Mapping):
        raise PhysicalE2EVerificationError("push health payload must be an object")

    checks = {
        "health_ok": payload.get("ok") is True,
        "firebase_ready": payload.get("firebase") is True,
        "tokens_not_exposed": payload.get("tokens_exposed") is False,
        "client_receipts_supported": payload.get("client_receipts_supported") is True,
        "latest_self_test_build_matches": payload.get("latest_self_test_build") == build,
        "latest_self_test_sent": payload.get("latest_self_test_sent") is True,
        "latest_self_test_receipt_confirmed": payload.get("latest_self_test_receipt_confirmed") is True,
        "current_build_physical_e2e_confirmed": payload.get("current_build_physical_e2e_confirmed") is True,
        "real_receipt_timestamp_present": bool(payload.get("last_client_receipt_at")),
        "received_delivery_count_positive": isinstance(payload.get("received_deliveries"), int)
        and payload.get("received_deliveries", 0) >= 1,
    }
    passed = all(checks.values())
    return {
        "expected_build": build,
        "physical_e2e_confirmed": passed,
        "checks": checks,
        "observed": {
            "latest_self_test_build": payload.get("latest_self_test_build"),
            "latest_self_test_sent": payload.get("latest_self_test_sent"),
            "latest_self_test_receipt_confirmed": payload.get("latest_self_test_receipt_confirmed"),
            "current_build_physical_e2e_confirmed": payload.get("current_build_physical_e2e_confirmed"),
            "received_deliveries": payload.get("received_deliveries"),
            "last_client_receipt_at": payload.get("last_client_receipt_at"),
        },
        "guardrail": (
            "This is read-only verification. Provider send success or an older-build receipt cannot pass. "
            "The expected build must be the latest self-test build and its exact receipt must already be confirmed."
        ),
    }


def fetch_and_verify(*, base_url: str, expected_build: str, timeout: float = 15.0) -> dict[str, Any]:
    base = str(base_url or "").strip().rstrip("/")
    if not base.startswith("https://"):
        raise PhysicalE2EVerificationError("base_url must use https")
    response = requests.get(f"{base}/push-health", timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    return verify_push_health(payload, expected_build=expected_build)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--expected-build", required=True)
    parser.add_argument("--output", default="physical_e2e_verification.json")
    args = parser.parse_args()

    result = fetch_and_verify(base_url=args.base_url, expected_build=args.expected_build)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    if not result["physical_e2e_confirmed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
