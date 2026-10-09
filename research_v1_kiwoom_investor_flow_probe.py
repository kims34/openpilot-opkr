"""Bounded ka10059 source feasibility probe; no orders or public numeric rows."""
import datetime as dt
import hashlib
import json
import os
import re
import time
import urllib.request

BASE = "https://api.kiwoom.com"
BODY = {"dt": "20261008", "stk_cd": "005930", "amt_qty_tp": "1",
        "trde_tp": "0", "unit_tp": "1"}
FIELDS = ("dt", "frgnr_invsr", "orgn", "acc_trde_prica")
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def request(path, body, token=None, continuation=None):
    if path not in ("/oauth2/token", "/api/dostk/stkinfo"):
        raise ValueError("endpoint not allowed")
    headers = {"Content-Type": "application/json;charset=UTF-8"}
    if token:
        headers.update({"authorization": "Bearer " + token, "api-id": "ka10059"})
    if continuation:
        headers.update({"cont-yn": "Y", "next-key": continuation})
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(),
                                 headers=headers, method="POST")
    with urllib.request.build_opener(NoRedirect()).open(req, timeout=20) as resp:
        raw = resp.read(4000001)
        if len(raw) > 4000000:
            raise ValueError("response too large")
        return json.loads(raw), dict(resp.headers), hashlib.sha256(raw).hexdigest()

def run(env, send=request):
    result = {"purpose": "SOURCE_FEASIBILITY_NOT_PROFITABILITY",
              "ordering": False, "performance_admitted": False,
              "raw_rows_persisted": False, "pages": []}
    if env.get("KIWOOM_ORDERING_ENABLED", "").strip().lower() not in ("false","0","off","no"):
        return dict(result, status="ORDERING_CONFIG_BLOCKED")
    if env.get("KIWOOM_ENV", "").upper() != "REAL" or env.get("KIWOOM_BASE_URL", "").rstrip("/") != BASE:
        return dict(result, status="REAL_HOST_CONFIG_BLOCKED")
    key, secret = env.get("KIWOOM_APP_KEY"), env.get("KIWOOM_APP_SECRET")
    if not key or not secret:
        return dict(result, status="AUTH_NOT_CONFIGURED")
    try:
        auth, _, _ = send("/oauth2/token", {"grant_type":"client_credentials", "appkey":key, "secretkey":secret})
        rc = auth.get("return_code")
        result["auth_return_code"] = rc if type(rc) is int else None
        token = auth.get("token")
        if type(rc) is not int or rc != 0 or not isinstance(token, str) or not token:
            return dict(result, status="AUTH_REJECTED")
        continuation = None
        seen = set()
        all_dates = []
        for page in range(3):
            payload, headers, digest = send("/api/dostk/stkinfo", BODY, token, continuation)
            rc = payload.get("return_code")
            if type(rc) is not int or rc != 0:
                result["data_return_code"] = rc if type(rc) is int else None
                return dict(result, status="DATA_REQUEST_REJECTED")
            rows = payload.get("stk_invsr_orgn")
            if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
                return dict(result, status="SCHEMA_REJECTED")
            dates = []
            bad = 0
            for row in rows:
                d = row.get("dt", "")
                try:
                    if not isinstance(d, str) or not re.fullmatch(r"[0-9]{8}", d):
                        raise ValueError()
                    dt.datetime.strptime(d, "%Y%m%d")
                    if d > BODY["dt"]:
                        raise ValueError()
                    dates.append(d)
                except ValueError:
                    bad += 1
            missing = sum(any(row.get(k) in (None, "") for k in FIELDS) for row in rows)
            numeric_bad = sum(any(not re.fullmatch(r"[+-]?[0-9]+(?:\.[0-9]+)?", str(row.get(k, "")))
                                  for k in FIELDS[1:]) for row in rows)
            all_dates.extend(dates)
            h = {k.lower():v for k,v in headers.items()}
            more = h.get("cont-yn") == "Y"
            result["pages"].append({"rows":len(rows),"min_date":min(dates,default=None),
                "max_date":max(dates,default=None),"invalid_dates":bad,"missing_required_rows":missing,
                "invalid_numeric_rows":numeric_bad,"raw_sha256":digest,"more":more})
            if bad or missing or numeric_bad:
                return dict(result, status="ROW_VALIDATION_REJECTED")
            if not more:
                break
            continuation = h.get("next-key")
            if not continuation or continuation in seen:
                return dict(result, status="CONTINUATION_REJECTED")
            seen.add(continuation)
            if page < 2:
                time.sleep(0.3)
        result["duplicate_dates"] = len(all_dates)-len(set(all_dates))
        result["requested_body"] = BODY
        result["history_exhausted"] = not more
        result["status"] = "SOURCE_REACHABLE_METADATA_ONLY" if all_dates else "SOURCE_REACHABLE_EMPTY"
        result["publication_time_verified"] = False
        result["historical_revision_policy_verified"] = False
        return result
    except Exception as exc:
        return dict(result, status="TRANSPORT_OR_PARSE_FAILED", error_type=type(exc).__name__)

if __name__ == "__main__":
    print("INVESTOR_FLOW_PROBE=" + json.dumps(run(os.environ),sort_keys=True), flush=True)
