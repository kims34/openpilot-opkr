"""Deterministic, fail-closed research-queue orchestrator for IndexAlert.

Consumes diagnostic snapshots and emits IDEA queue items only. It never runs a
candidate, changes Core, opens a sealed holdout, or authorizes live orders.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

@dataclass(frozen=True)
class ResearchSignal:
    kind: str
    observed: bool
    evidence_ref: str
    detail: str = ""

ALLOWED = {
 "CALIBRATION_DRIFT": "Investigate calibration deterioration without changing the frozen admission threshold.",
 "EXECUTION_COST_DRIFT": "Investigate broker execution-cost/slippage drift against preregistered budgets.",
 "FEATURE_FRESHNESS_DRIFT": "Investigate PIT feature freshness/missingness deterioration.",
 "REGIME_DRIFT": "Investigate a preregistered regime-robust challenger without subgroup mining.",
 "DATA_QUALITY_DRIFT": "Investigate upstream PIT-safe data quality or lineage deterioration.",
}

def build_research_queue(signals: list[ResearchSignal], *, core_version: str) -> list[dict[str, Any]]:
    if not core_version: raise ValueError("core_version is required")
    out=[]
    for s in signals:
        if not s.observed: continue
        if s.kind not in ALLOWED: continue
        if not s.evidence_ref: continue
        out.append({"state":"IDEA","trigger":s.kind,"core_version":core_version,"hypothesis":ALLOWED[s.kind],"evidence_ref":s.evidence_ref,"detail":s.detail,"requires_preregistration":True,"may_use_sealed_holdout":False,"production_write_authority":False,"automatic_promotion":False,"live_order_authorized":False})
    return out

def signals_from_snapshot(snapshot: dict[str, Any]) -> list[ResearchSignal]:
    """Translate explicit diagnostic booleans into queue signals; no threshold tuning."""
    mapping={
      "calibration_drift":"CALIBRATION_DRIFT",
      "execution_cost_drift":"EXECUTION_COST_DRIFT",
      "feature_freshness_drift":"FEATURE_FRESHNESS_DRIFT",
      "regime_drift":"REGIME_DRIFT",
      "data_quality_drift":"DATA_QUALITY_DRIFT",
    }
    refs=snapshot.get("evidence_refs",{}) or {}
    return [ResearchSignal(kind, bool(snapshot.get(key,False)), str(refs.get(key,"")), str(snapshot.get(key+"_detail",""))) for key,kind in mapping.items()]

def orchestrate(snapshot: dict[str, Any], *, core_version: str) -> dict[str, Any]:
    if snapshot.get("sealed_holdout_accessed") is True:
        return {"status":"INVALID_INPUT","blockers":["SEALED_HOLDOUT_INPUT_FORBIDDEN"],"queue":[],"core_mutation_allowed":False,"live_order_authorized":False}
    queue=build_research_queue(signals_from_snapshot(snapshot),core_version=core_version)
    return {"status":"QUEUE_READY","queue":queue,"core_mutation_allowed":False,"sealed_holdout_authorized":False,"live_order_authorized":False,"automatic_promotion_allowed":False}
