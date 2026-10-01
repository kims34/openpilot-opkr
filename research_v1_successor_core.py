"""Fail-closed successor-Core staging for IndexAlert continuous research.

This module can automatically build a versioned successor artifact after a
challenger has passed preregistered independent development gates. It cannot
make that artifact the production Core and cannot authorize holdout/live use.
"""
from __future__ import annotations
import hashlib, json

REQUIRED_GATES=("accepted_challenger","independent_oos_passed","cost_stress_passed","tail_risk_passed","recent_stability_passed","pit_integrity_passed","no_leakage_verified","frozen_protocol_match")

def _fingerprint(x:dict)->str:
 return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def assess_successor_eligibility(*,trial:dict,gates:dict,current_core_version:str)->dict:
 blockers=[]
 if not current_core_version: blockers.append("CURRENT_CORE_VERSION_REQUIRED")
 if trial.get("classification")!="ACCEPTED_CHALLENGER": blockers.append("CHALLENGER_NOT_ACCEPTED")
 for g in REQUIRED_GATES:
  if gates.get(g) is not True: blockers.append("GATE_NOT_PASSED:"+g)
 if gates.get("sealed_holdout_used") is True: blockers.append("SEALED_HOLDOUT_FORBIDDEN_AT_SUCCESSOR_BUILD")
 if gates.get("criteria_changed_after_results") is True: blockers.append("POST_HOC_CHANGE_FORBIDDEN")
 eligible=not blockers
 return {"successor_build_eligible":eligible,"classification":"SUCCESSOR_BUILD_ELIGIBLE" if eligible else "SUCCESSOR_BUILD_BLOCKED","blockers":blockers,"production_core_replacement_allowed":False,"sealed_holdout_authorized":False,"live_order_authorized":False}

def build_successor_artifact(*,trial:dict,gates:dict,current_core_version:str,successor_version:str,policy_payload:dict)->dict:
 a=assess_successor_eligibility(trial=trial,gates=gates,current_core_version=current_core_version)
 if not a["successor_build_eligible"]: return {**a,"artifact":None}
 if not successor_version or successor_version==current_core_version: return {**a,"successor_build_eligible":False,"classification":"SUCCESSOR_BUILD_BLOCKED","blockers":["DISTINCT_SUCCESSOR_VERSION_REQUIRED"],"artifact":None}
 artifact={"artifact_type":"INDEXALERT_SUCCESSOR_CORE_CANDIDATE","current_core_version":current_core_version,"successor_version":successor_version,"trial_id":trial.get("trial_id"),"policy_fingerprint":_fingerprint(policy_payload),"state":"SHADOW_CANDIDATE","production_active":False,"requires_shadow_s1":True,"requires_fresh_confirmation_s2":True,"sealed_holdout_authorized":False,"live_order_authorized":False}
 artifact["artifact_fingerprint"]=_fingerprint(artifact)
 return {**a,"artifact":artifact}

def assess_shadow_promotion(*,artifact:dict,confirmation:dict)->dict:
 blockers=[]
 if not artifact or artifact.get("state")!="SHADOW_CANDIDATE": blockers.append("VALID_SHADOW_CANDIDATE_REQUIRED")
 if confirmation.get("shadow_s1_passed") is not True: blockers.append("SHADOW_S1_NOT_PASSED")
 if confirmation.get("fresh_confirmation_s2_passed") is not True: blockers.append("FRESH_CONFIRMATION_S2_NOT_PASSED")
 if confirmation.get("sealed_holdout_contract_passed") is not True: blockers.append("SEALED_HOLDOUT_CONTRACT_NOT_PASSED")
 if confirmation.get("all_external_blockers_closed") is not True: blockers.append("EXTERNAL_BLOCKERS_OPEN")
 if confirmation.get("execution_blocker_closed") is not True: blockers.append("EXECUTION_BLOCKER_OPEN")
 return {"promotion_eligible":not blockers,"classification":"PROMOTION_ELIGIBLE" if not blockers else "PROMOTION_BLOCKED","blockers":blockers,"automatic_code_update_allowed":not blockers,"automatic_live_order_activation_allowed":False,"live_order_authorized":False}
