"""Opt-in, one-shot Kiwoom REAL stock-info read-only diagnostic.

NEVER invoked by CI or the bundled registered-PC WS diagnostic.
Run ONLY on the owner's registered-IP PC, after explicit local opt-in:
    KIWOOM_ENABLE_READONLY_QUOTE_DIAGNOSTIC=YES
    python kiwoom_real_quote_local_probe.py --run-readonly-quote 005930

Preflight uses the existing REAL / ORDERING=disabled / fixed-host guard.
One token, one account-identity read, and at most one ka10001 stock-info
request. Never sends orders, writes broker state, or prints tokens, account,
quote price, provider message, network addresses, or raw exceptions.
An offline test with synthetic responses cannot prove a genuine broker quote.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any

import requests

import kiwoom_real_type00_readonly_smoke as smoke
from kiwoom_real_quote_readonly_contract import (
    QUOTE_API_ID, QUOTE_PATH, QuoteContractError, offline_quote_envelope,
    offline_quote_structure,
)


def _empty_result() -> dict[str, Any]:
    return {
        "classification": "KIWOOM_REAL_QUOTE_LOCAL_READONLY_DIAGNOSTIC",
        "stage": "PREFLIGHT_BLOCKED",
        "token_ok": False,
        "account_endpoint_ok": False,
        "quote_response_structure_ok": False,
        "genuine_live_provenance_verified": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "permission_change_authorized": False,
        "ordering": "DISABLED",
    }


def one_shot(symbol: str) -> dict[str, Any]:
    """Return a redacted summary; never call on a cloud CI runner."""
    result = _empty_result()
    if os.getenv("KIWOOM_ENABLE_READONLY_QUOTE_DIAGNOSTIC") != "YES":
        return result
    try:
        request = offline_quote_envelope(symbol)
        # The existing smoke preflight rejects non-REAL hosts, proxy policy
        # violations, missing keys and any enabled or ambiguous ordering.
        state = smoke.SmokeState()
        token, _account, _issued = smoke._token_and_account(state)
        result["token_ok"] = state.TOKEN_OK
        result["account_endpoint_ok"] = state.ACCOUNT_ENDPOINT_OK
        if not (state.TOKEN_OK and state.ACCOUNT_ENDPOINT_OK
                and state.REST_ACCOUNT_ACCEPTED_ISSUED_TOKEN):
            result["stage"] = "REST_PRECONDITION_NOT_MET"
            return result
        response = requests.post(
            smoke.REAL_BASE_URL + QUOTE_PATH,
            headers={
                "Content-Type": "application/json;charset=UTF-8",
                "authorization": "Bearer " + token,
                "api-id": QUOTE_API_ID,
                "cont-yn": "N",
                "next-key": "",
            },
            json=request["body"],
            timeout=15,
            allow_redirects=False,
        )
        offline_quote_structure(
            stock_code=symbol,
            http_status=response.status_code,
            response_body=response.content,
        )
        result["stage"] = "QUOTE_STRUCTURE_ACCEPTED_PROVENANCE_UNVERIFIED"
        result["quote_response_structure_ok"] = True
    except QuoteContractError:
        result["stage"] = "QUOTE_CONTRACT_BLOCKED"
    except smoke.ReadOnlySmokeError as exc:
        # The stage is a fixed local enum, not a provider response string.
        result["stage"] = (
            "REST_PRECONDITION_NOT_MET"
            if exc.stage in {"TOKEN", "TOKEN_PROTOCOL", "TOKEN_CANONICALITY",
                             "ACCOUNT", "ACCOUNT_PROTOCOL"}
            else "PREFLIGHT_BLOCKED"
        )
    except Exception:
        # Never print request headers, response bodies, proxy URLs, stack
        # traces or untrusted exception text.
        result["stage"] = "QUOTE_TRANSPORT_OR_LOCAL_ERROR"
    return result


def main() -> None:
    result = _empty_result()
    if (len(sys.argv) == 3 and sys.argv[1] == "--run-readonly-quote"
            and os.getenv("KIWOOM_ENABLE_READONLY_QUOTE_DIAGNOSTIC") == "YES"):
        result = one_shot(sys.argv[2])
    print(json.dumps(result, sort_keys=True, separators=(",", ":")), flush=True)
    raise SystemExit(0 if result["quote_response_structure_ok"] else 2)


if __name__ == "__main__":
    main()
