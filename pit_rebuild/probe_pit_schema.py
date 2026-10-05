from pathlib import Path
import json,pandas as pd
root=Path("/pit/marcap_kospi_pit")
files=sorted(root.glob("kospi-pit-*.parquet"))
if not files: raise SystemExit("SCHEMA_BLOCKED:no files")
out=[]
for p in (files[:1]+files[-1:]):
 d=pd.read_parquet(p)
 out.append({"file":p.name,"columns":list(d.columns),"index_name":d.index.name,"rows":len(d)})
print("PIT_SCHEMA="+json.dumps(out,sort_keys=True))
