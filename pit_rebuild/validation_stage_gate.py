"""Fail-closed stage gate for IndexAlert validation lifecycle.

This module deliberately does not execute a holdout, shadow, confirmation, or live
order. It validates that prerequisites exist before any stage-specific runner may
be invoked.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

BASELINE=Path("/pit/private/abstention_v3_positions.parquet")
SEALED_MANIFEST=Path("/pit/private/sealed_holdout_manifest.json")
SEALED_RESULT=Path("/pit/private/sealed_holdout_result.json")
SHADOW_RESULT=Path("/pit/private/shadow_s1_result.json")
FRESH_RESULT=Path("/pit/private/fresh_confirmation_s2_result.json")

def load_json(p):
    if not p.exists(): return None
    return json.loads(p.read_text(encoding="utf-8"))

def require(cond,msg):
    if not cond: raise SystemExit("GATE_BLOCKED: "+msg)

def check(stage):
    require(BASELINE.exists(),"official baseline missing")
    if stage=="sealed_holdout":
        m=load_json(SEALED_MANIFEST)
        require(m is not None,"sealed holdout manifest missing; fresh never-inspected data window must be provisioned first")
        require(m.get("never_inspected_by_development") is True,"holdout is not attested as never inspected")
        require(m.get("frozen_before_data_access") is True,"model/policy was not attested frozen before data access")
        require(m.get("network_collection_authorized") is True,"fresh holdout acquisition authorization not recorded")
        return {"stage":stage,"ready":True}
    if stage=="shadow_s1":
        r=load_json(SEALED_RESULT)
        require(r is not None and r.get("passed") is True,"sealed holdout has not passed")
        require(r.get("policy_changed_after_unseal") is False,"policy changed after holdout unseal")
        return {"stage":stage,"ready":True}
    if stage=="fresh_confirmation_s2":
        r=load_json(SHADOW_RESULT)
        require(r is not None and r.get("passed") is True,"Shadow S1 has not passed")
        require(r.get("real_orders_sent") is False,"Shadow S1 must be order-free")
        return {"stage":stage,"ready":True}
    if stage=="live":
        r=load_json(FRESH_RESULT)
        require(r is not None and r.get("passed") is True,"Fresh Confirmation S2 has not passed")
        require(r.get("fresh_data") is True,"S2 is not attested fresh")
        require(r.get("real_orders_sent") is False,"S2 must be order-free")
        raise SystemExit("GATE_BLOCKED: broker/order connector and explicit account-level risk configuration are required before live orders")
    raise SystemExit("GATE_BLOCKED: unknown stage")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("stage",choices=["sealed_holdout","shadow_s1","fresh_confirmation_s2","live"])
    args=ap.parse_args()
    print("VALIDATION_GATE="+json.dumps(check(args.stage),sort_keys=True))
