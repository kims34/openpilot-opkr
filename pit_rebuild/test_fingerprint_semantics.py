"""Offline regression test for selection-vs-position fingerprint semantics."""
import hashlib
import pandas as pd

SORT=["horizon","coverage","decision_idx","rank","symbol"]
SEL=["fold","horizon","coverage","decision_idx","decision_date","symbol","rank","score"]

def fps(df):
    s=df.sort_values(SORT)
    return (
        hashlib.sha256(s[SEL].to_csv(index=False).encode()).hexdigest(),
        hashlib.sha256(s.to_csv(index=False).encode()).hexdigest(),
    )

base=pd.DataFrame([{
 "fold":1,"horizon":2,"coverage":0.05,"decision_idx":100,"decision_date":"2026-01-02",
 "entry_day":"2026-01-05","exit_day":"2026-01-06","symbol":"TEST","rank":1,
 "score":0.8,"gross_return":0.02,"entry_price":100.0
}])
s0,p0=fps(base)
for col,val in [("entry_day","2026-01-07"),("exit_day","2026-01-08"),("entry_price",101.0),("gross_return",-0.03)]:
    x=base.copy(); x.loc[0,col]=val; s,p=fps(x)
    assert s==s0, f"{col} incorrectly changes selection fingerprint"
    assert p!=p0, f"{col} failed to change position fingerprint"
for col,val in [("symbol","OTHER"),("rank",2),("score",0.7),("decision_date","2026-01-03")]:
    x=base.copy(); x.loc[0,col]=val; s,_=fps(x)
    assert s!=s0, f"{col} failed to change selection fingerprint"
print("FINGERPRINT_SEMANTICS_TEST=PASS")
