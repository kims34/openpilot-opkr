"""Prepare a fail-closed manifest for a genuinely future sealed holdout.

This does not download or inspect market data. It freezes the eligibility boundary
before acquisition. The actual acquisition runner must only write dates strictly
after DEVELOPMENT_CUTOFF and must not expose outcomes to development code.
"""
from __future__ import annotations
import json, os
from datetime import datetime, timezone
from pathlib import Path

OUT=Path("/pit/private/sealed_holdout_manifest.json")
DEVELOPMENT_CUTOFF="2026-09-25"
BASELINE_SELECTION_FINGERPRINT="8a442cbf42ff8449e9d7d6a28e9ac7e4215e2997d45aa6e17e109318598a6156"
BASELINE_POSITION_FINGERPRINT="53c6e32d18fb75f61825da07423f0f6e21b839ea234069e69e3d1c153a81387f"

payload={
 "manifest_version":"indexalert-sealed-holdout-v1",
 "development_cutoff":DEVELOPMENT_CUTOFF,
 "eligible_rule":"market sessions strictly after development_cutoff; never inspected by development/model-selection code before unseal",
 "baseline_selection_fingerprint":BASELINE_SELECTION_FINGERPRINT,
 "baseline_position_fingerprint":BASELINE_POSITION_FINGERPRINT,
 "frozen_before_data_access":True,
 "never_inspected_by_development":True,
 "network_collection_authorized":True,
 "sealed":True,
 "data_acquired":False,
 "outcomes_unsealed":False,
 "created_at":datetime.now(timezone.utc).isoformat(),
}
OUT.parent.mkdir(parents=True,exist_ok=True)
flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
try:
    fd=os.open(str(OUT),flags,0o600)
except FileExistsError:
    raise SystemExit("MANIFEST_BLOCKED: manifest already exists; refusing overwrite")
with os.fdopen(fd,"w",encoding="utf-8") as f:
    json.dump(payload,f,ensure_ascii=False,indent=2,sort_keys=True); f.write("\n")
print(json.dumps({"manifest_created":str(OUT),"development_cutoff":DEVELOPMENT_CUTOFF,"data_acquired":False,"outcomes_unsealed":False},sort_keys=True))
