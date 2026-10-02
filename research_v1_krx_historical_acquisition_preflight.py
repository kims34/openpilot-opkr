"""Network-free preflight for the frozen KRX historical acquisition plan.

It validates rights, plan identity/fingerprint, credential presence and an exact
user execution-consent sentinel. It never imports the KRX client and never
performs a network request.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from research_v1_krx_historical_acquisition_plan import validate_file as validate_plan_file
from research_v1_krx_historical_acquisition_rights import validate_file as validate_rights_file


PLAN_PATH = Path("INDEXALERT_KRX_HISTORICAL_ACQUISITION_PLAN.json")
CONSENT_ENV = "KRX_HISTORICAL_ACQUISITION_CONSENT"
CONSENT_SENTINEL = "I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v2"


def evaluate_historical_acquisition_preflight(
    *,
    environment: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    env=dict(os.environ if environment is None else environment)
    plan=validate_plan_file(PLAN_PATH)
    rights=validate_rights_file()

    id_present=bool(str(env.get("KRX_ID") or "").strip())
    pw_present=bool(str(env.get("KRX_PW") or "").strip())
    consent=str(env.get(CONSENT_ENV) or "").strip()
    consent_ok=consent == CONSENT_SENTINEL

    missing=[]
    if not id_present:
        missing.append("KRX_ID")
    if not pw_present:
        missing.append("KRX_PW")
    if not rights["rights_authorized"]:
        missing.append("KRX_FULL_HISTORY_RIGHTS")
    if not consent_ok:
        missing.append("EXPLICIT_HISTORICAL_ACQUISITION_EXECUTION_CONSENT")

    ready=not missing
    return {
        "plan_id":plan["plan_id"],
        "plan_fingerprint_sha256":plan["plan_fingerprint_sha256"],
        "rights_authorized":rights["rights_authorized"],
        "high_frequency_collection_authorized":rights["high_frequency_collection_authorized"],
        "full_historical_download_rights_authorized":rights["full_historical_download_rights_authorized"],
        "krx_id_present":id_present,
        "krx_pw_present":pw_present,
        "explicit_execution_consent_present":consent_ok,
        "historical_acquisition_network_execution_authorized":ready,
        "network_request_attempted":False,
        "missing_requirements":missing,
        "feature_performance_testing_authorized":False,
        "sealed_holdout_authorized":False,
        "live_trading_authorized":False,
        "guardrail":"This preflight is network-free. Even a ready result authorizes only execution of the frozen acquisition plan, not source admission, performance testing, holdout or trading.",
    }


if __name__=="__main__":
    print(json.dumps(evaluate_historical_acquisition_preflight(),ensure_ascii=False,indent=2))
