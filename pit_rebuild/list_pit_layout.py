from pathlib import Path
import json
root=Path("/pit/marcap_kospi_pit")
items=[]
for p in sorted(root.rglob("*")):
    if p.is_file():
        rel=str(p.relative_to(root))
        items.append({"path":rel,"size":p.stat().st_size})
print("PIT_FILE_LAYOUT="+json.dumps({"mode":"OFFLINE_LAYOUT","network_request_attempted":False,"files":items,"security_identifiers_emitted":False},sort_keys=True))
