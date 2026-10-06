"""User-operated REAL read-only credential/connectivity smoke.

Prints only redacted booleans/status. It never prints credentials, token,
account identifiers or provider response bodies. It makes exactly two provider
requests: OAuth token, then reviewed account query ka00001. No order API exists
in this path.
"""
import json
import os

from kiwoom_real_readonly_transport import KiwoomRealReadOnlyTransport


def main():
    cfg = {
        "KIWOOM_ENV": os.environ.get("KIWOOM_ENV", ""),
        "KIWOOM_BASE_URL": os.environ.get("KIWOOM_BASE_URL", ""),
        "KIWOOM_ORDERING_ENABLED": os.environ.get("KIWOOM_ORDERING_ENABLED", ""),
        "KIWOOM_APP_KEY": os.environ.get("KIWOOM_APP_KEY", ""),
        "KIWOOM_APP_SECRET": os.environ.get("KIWOOM_APP_SECRET", ""),
    }
    result = {
        "mode": "REAL_READ_ONLY_SMOKE",
        "ordering_configuration": "DISABLED",
        "TOKEN_OK": False,
        "ACCOUNT_ENDPOINT_OK": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "broker_permission_change_authorized": False,
        "genuine_live_provenance_verified": False,
    }
    transport = KiwoomRealReadOnlyTransport(cfg)
    transport.authenticate()
    result["TOKEN_OK"] = True
    page = transport.query("ka00001", {})
    result["ACCOUNT_ENDPOINT_OK"] = type(page.body) is dict
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
