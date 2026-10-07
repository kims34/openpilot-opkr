"""Explicit REAL-account read-only transport.

The host is fixed to Kiwoom's official REAL REST host. Only reviewed read-only
account/query API IDs are admitted. Order/cancel/amend/revoke APIs are not
reachable through this transport. No retry, redirect, token refresh, persistence
or evidence admission is performed.
"""
from datetime import datetime, timedelta, timezone
import http.client
import json
import ssl

from kiwoom_real_readonly_preparation import (
    READ_ONLY_API_IDS, assess_real_readonly_preparation, require_readonly_api,
)

KST = timezone(timedelta(hours=9))
HOST = "api.kiwoom.com"
PATH = "/api/dostk/acnt"
MAX_RESPONSE_BYTES = 1024 * 1024
SCOPES = {
    "ka00001": (frozenset(), frozenset()),
    "kt00001": (
        frozenset({"qry_tp"}),
        frozenset({"qry_tp"}),
    ),
    "kt00017": (frozenset(), frozenset()),
    "kt00007": (
        frozenset("qry_tp stk_bond_tp sell_tp dmst_stex_tp".split()),
        frozenset("qry_tp stk_bond_tp sell_tp dmst_stex_tp ord_dt stk_cd fr_ord_no".split()),
    ),
    "ka10076": (
        frozenset("qry_tp sell_tp stex_tp".split()),
        frozenset("qry_tp sell_tp stex_tp stk_cd ord_no".split()),
    ),
    "kt00018": (
        frozenset("qry_tp dmst_stex_tp".split()),
        frozenset("qry_tp dmst_stex_tp".split()),
    ),
}


class RealReadOnlyError(ValueError):
    pass


def _require(condition):
    if not condition:
        raise RealReadOnlyError("REAL_READ_ONLY_REQUEST_BLOCKED")


def _unique_response_fields(pairs):
    fields = {}
    for key, value in pairs:
        _require(key not in fields)
        fields[key] = value
    return fields


def _reject_non_json_constant(value):
    _require(False)


class PrivateRealPage:
    __slots__ = ("body", "continuation", "next_key", "continuation_header_present")

    def __init__(self, body, continuation, next_key, *, continuation_header_present=True):
        self.body = body
        self.continuation = continuation
        self.next_key = next_key
        self.continuation_header_present = continuation_header_present

    def __repr__(self):
        return "<PrivateRealPage redacted; REAL read-only; unadmitted>"


class KiwoomRealReadOnlyTransport:
    def __init__(self, configuration, *, _connection_factory=None, _clock=None):
        _require(type(configuration) is dict)
        assess_real_readonly_preparation(configuration)
        self._config = dict(configuration)
        self._factory = _connection_factory or http.client.HTTPSConnection
        self._clock = _clock or (lambda: datetime.now(KST))
        self._token = None
        self._expiry = None

    def __repr__(self):
        return "<KiwoomRealReadOnlyTransport redacted; REAL read-only>"

    def _post(self, path, body, headers):
        connection = None
        try:
            connection = self._factory(
                HOST, port=443, timeout=10, context=ssl.create_default_context()
            )
            connection.request(
                "POST",
                path,
                body=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json;charset=UTF-8", **headers},
            )
            response = connection.getresponse()
            _require(response.status == 200)
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            _require(len(raw) <= MAX_RESPONSE_BYTES)
            data = json.loads(raw, object_pairs_hook=_unique_response_fields,
                              parse_constant=_reject_non_json_constant)
            _require(
                type(data) is dict
                and type(data.get("return_code")) is int
                and data["return_code"] == 0
            )
            raw_continuation = response.getheader("cont-yn")
            continuation = raw_continuation or "N"
            next_key = response.getheader("next-key") or ""
            _require(continuation in ("N", "Y"))
            _require(
                type(next_key) is str
                and len(next_key) <= 4096
                and "\r" not in next_key
                and "\n" not in next_key
            )
            _require(continuation != "Y" or bool(next_key))
            return PrivateRealPage(
                data,
                continuation,
                next_key,
                continuation_header_present=raw_continuation in ("N", "Y"),
            )
        except Exception:
            self._token = None
            self._expiry = None
            raise RealReadOnlyError("REAL_READ_ONLY_REQUEST_BLOCKED") from None
        finally:
            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass

    def authenticate(self):
        self._token = None
        self._expiry = None
        assess_real_readonly_preparation(self._config)
        page = self._post(
            "/oauth2/token",
            {
                "grant_type": "client_credentials",
                "appkey": self._config["KIWOOM_APP_KEY"],
                "secretkey": self._config["KIWOOM_APP_SECRET"],
            },
            {},
        )
        try:
            token = page.body.get("token")
            expiry = page.body.get("expires_dt")
            _require(
                type(token) is str
                and 0 < len(token) <= 8192
                and all(33 <= ord(c) <= 126 for c in token)
            )
            _require(str(page.body.get("token_type", "")).lower() == "bearer")
            _require(
                type(expiry) is str
                and len(expiry) == 14
                and expiry.isascii()
                and expiry.isdigit()
            )
            expires_at = datetime.strptime(expiry, "%Y%m%d%H%M%S").replace(tzinfo=KST)
            _require(expires_at > self._clock())
            self._token = token
            self._expiry = expires_at
        except Exception:
            raise RealReadOnlyError("REAL_READ_ONLY_REQUEST_BLOCKED") from None
        return {
            "mode": "REAL_READ_ONLY_TRANSPORT",
            "real_token_response_validated": True,
            "account_identity_authenticated": False,
            "genuine_live_provenance_verified": False,
            "project_live_evidence_admitted": False,
            "live_trading_authorized": False,
            "real_orders_authorized": False,
        }

    def query(self, api_id, body, *, continuation="N", next_key=""):
        assess_real_readonly_preparation(self._config)
        require_readonly_api(api_id)
        _require(api_id in READ_ONLY_API_IDS and api_id in SCOPES)
        required, allowed = SCOPES[api_id]
        _require(type(body) is dict and required <= set(body) <= allowed)
        _require(all(type(v) is str and len(v) <= 256 for v in body.values()))
        _require(all(body[k].strip() for k in required))
        if api_id == "kt00001":
            _require(body == {"qry_tp": "2"})
        if api_id == "kt00018":
            _require(body == {"qry_tp": "2", "dmst_stex_tp": "KRX"})
        _require(
            continuation in ("N", "Y")
            and type(next_key) is str
            and len(next_key) <= 4096
        )
        _require("\r" not in next_key and "\n" not in next_key)
        _require((continuation == "Y") == bool(next_key))
        _require(self._token is not None and self._expiry > self._clock())
        return self._post(
            PATH,
            dict(body),
            {
                "authorization": "Bearer " + self._token,
                "api-id": api_id,
                "cont-yn": continuation,
                "next-key": next_key,
            },
        )
