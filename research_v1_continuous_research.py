"""Fail-closed governance primitives for continuous IndexAlert research."""
from __future__ import annotations
import hashlib, json

REQUIRED = ("schema_version","trial_id","core_version","hypothesis","dataset_window","pit_contract","target_horizon","primary_metrics","acceptance_criteria","cost_assumptions","evaluation_protocol","preregistered_at")
FORBIDDEN_DATA_ROLES = {"sealed_holdout","holdout","final_holdout"}
TERMINAL = {"ACCEPTED_CHALLENGER","REJECTED","INVALIDATED"}

def canonical_protocol(protocol: dict) -> str:
    return json.dumps(protocol, sort_keys=True, separators=(",",":"), ensure_ascii=False)

def protocol_fingerprint(protocol: dict) -> str:
    return hashlib.sha256(canonical_protocol(protocol).encode()).hexdigest()

def validate_preregistration(protocol: dict) -> dict:
    missing=[k for k in REQUIRED if not protocol.get(k)]
    roles={str(x).strip().lower() for x in protocol.get("data_roles", [])}
    blockers=[]
    if missing: blockers.append("MISSING_REQUIRED_FIELDS:"+",".join(missing))
    if roles & FORBIDDEN_DATA_ROLES: blockers.append("SEALED_HOLDOUT_FORBIDDEN")
    if protocol.get("automatic_production_promotion") is True: blockers.append("AUTO_PROMOTION_FORBIDDEN")
    if protocol.get("live_order_authorized") is True: blockers.append("RESEARCH_CANNOT_AUTHORIZE_LIVE_ORDER")
    return {"valid":not blockers,"blockers":blockers,"fingerprint":protocol_fingerprint(protocol)}

def evaluate_trial(protocol: dict, registered_fingerprint: str, results: dict) -> dict:
    pre=validate_preregistration(protocol)
    blockers=list(pre["blockers"])
    if pre["fingerprint"] != registered_fingerprint: blockers.append("PROTOCOL_CHANGED_AFTER_PREREGISTRATION")
    if results.get("sealed_holdout_accessed"): blockers.append("SEALED_HOLDOUT_ACCESSED")
    if results.get("criteria_changed_after_results"): blockers.append("POST_HOC_CRITERIA_CHANGE")
    if blockers:
        classification="INVALIDATED"
    elif not results.get("all_preregistered_acceptance_criteria_passed", False):
        classification="REJECTED"
    else:
        classification="ACCEPTED_CHALLENGER"
    return {"classification":classification,"blockers":blockers,"production_promotion_allowed":False,"live_order_authorized":False,"sealed_holdout_authorized":False,"protocol_fingerprint":pre["fingerprint"]}

def queue_item(trigger: str, hypothesis: str, core_version: str) -> dict:
    if not trigger or not hypothesis or not core_version: raise ValueError("trigger, hypothesis and core_version are required")
    return {"state":"IDEA","trigger":trigger,"hypothesis":hypothesis,"core_version":core_version,"production_write_authority":False}
