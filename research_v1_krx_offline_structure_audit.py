"""Network-free structural audit of KRX private volume; no identifiers/content."""
from __future__ import annotations
import json, os
from pathlib import Path
ROOT=Path(os.environ.get("KRX_PRIVATE_RAW_DIR") or "/data")
def shape(x):
    if isinstance(x,dict): return {"type":"object","keys":sorted(str(k) for k in x.keys())}
    if isinstance(x,list): return {"type":"array","length":len(x)}
    return {"type":type(x).__name__}
def main():
    out={"mode":"OFFLINE_PRIVATE_STRUCTURE_AUDIT","network_request_attempted":False,
         "raw_rows_emitted":False,"security_identifiers_emitted":False}
    ext={}
    top={}
    for p in ROOT.rglob("*"):
        if not p.is_file(): continue
        rel=p.relative_to(ROOT); bucket=rel.parts[0] if rel.parts else ""
        top[bucket]=top.get(bucket,0)+1
        ext[p.suffix.lower() or "<none>"]=ext.get(p.suffix.lower() or "<none>",0)+1
    out["top_level_file_counts"]=dict(sorted(top.items()))
    out["extension_counts"]=dict(sorted(ext.items()))
    states={}
    for name in ("PER_SECURITY_HISTORY","STATUS_ECONOMICS"):
        p=ROOT/"batch_state"/f"{name}.json"
        if p.is_file():
            obj=json.loads(p.read_text(encoding="utf-8"))
            states[name]=shape(obj.get("value") if isinstance(obj,dict) and "value" in obj else obj)
    out["batch_state_shapes"]=states
    print("OFFLINE_STRUCTURE_AUDIT="+json.dumps(out,sort_keys=True),flush=True)
if __name__=="__main__": main()
