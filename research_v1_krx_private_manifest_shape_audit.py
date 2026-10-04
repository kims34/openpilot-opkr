"""Aggregate/key-only audit of PER_SECURITY_HISTORY private task manifest. No identifiers."""
import json
from pathlib import Path
P=Path("/data/task_manifests/per-security-history-v3.json")
obj=json.loads(P.read_text())
tasks=obj.get("tasks") if isinstance(obj,dict) else None
if not isinstance(tasks,list) or not tasks: raise SystemExit("manifest tasks missing")
def shape(t):
    out={"task_keys":sorted(t.keys())}
    spec=t.get("request_spec")
    out["request_spec_keys"]=sorted(spec.keys()) if isinstance(spec,dict) else []
    if isinstance(spec,dict):
        params=spec.get("params")
        out["params_keys"]=sorted(params.keys()) if isinstance(params,dict) else []
    return out
shapes={}
for t in tasks:
    s=shape(t); k=json.dumps(s,sort_keys=True); shapes[k]=shapes.get(k,0)+1
print("PRIVATE_MANIFEST_SHAPES="+json.dumps({"task_count":len(tasks),"shapes":[{"count":n,**json.loads(k)} for k,n in shapes.items()],"network_request_attempted":False,"security_identifiers_emitted":False,"sealed_holdout_authorized":False,"live_trading_authorized":False},sort_keys=True))
