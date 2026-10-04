"""Network-free aggregate inventory for the mounted KRX private volume."""
from __future__ import annotations
import json, os
from pathlib import Path

ROOT=Path(os.environ.get("KRX_PRIVATE_RAW_DIR") or "/data")

def main():
    allowed={"batch_state","task_manifests","receipts","manifests","checkpoints","raw","objects","identity"}
    counts={}
    known={}
    if not ROOT.exists():
        raise SystemExit("OFFLINE_AUDIT_ERROR=private_root_missing")
    for p in ROOT.rglob("*"):
        if not p.is_file(): continue
        try: rel=p.relative_to(ROOT)
        except ValueError: continue
        top=rel.parts[0] if rel.parts else ""
        bucket=top if top in allowed else "other"
        counts[bucket]=counts.get(bucket,0)+1
    for rel in [
        "batch_state/PER_SECURITY_HISTORY.json",
        "batch_state/STATUS_ECONOMICS.json",
        "task_manifests/per-security-history-v3.json",
        "task_manifests/status-economics-v3.json",
    ]:
        known[rel]=bool((ROOT/rel).is_file())
    out={
        "mode":"OFFLINE_PRIVATE_VOLUME_INVENTORY",
        "private_root_exists":True,
        "file_counts_by_safe_bucket":dict(sorted(counts.items())),
        "known_artifacts_present":known,
        "network_request_attempted":False,
        "raw_rows_emitted":False,
        "security_identifiers_emitted":False,
        "sealed_holdout_authorized":False,
        "live_trading_authorized":False,
    }
    print("OFFLINE_AUDIT="+json.dumps(out,sort_keys=True),flush=True)

if __name__=="__main__": main()
