"""Extended 15/20-percent descriptive estimates; late computations are not prospective evidence."""
import hashlib
import json
import math
import sqlite3
import threading
import time
from datetime import date,timedelta
from pathlib import Path
import extended_touch_model as model

EVIDENCE=json.loads(Path(__file__).with_name('extended_touch_evidence.json').read_text())
DIGEST=hashlib.sha256(Path(model.__file__).read_bytes()).hexdigest()
LOCK=threading.Lock();RUNNING=set()


def connect(path=None):
    from monthly_prospective import DB_PATH
    con=sqlite3.connect(path or DB_PATH,timeout=20)
    con.execute('''CREATE TABLE IF NOT EXISTS extended_touch_v1(
        symbol TEXT,event TEXT,model TEXT,as_of TEXT,maturity TEXT,anchor REAL,
        probability REAL,baseline REAL,issued REAL,source_digest TEXT,model_digest TEXT,
        outcome INTEGER,scored REAL,PRIMARY KEY(symbol,event,model,as_of))''')
    return con


def calendar(as_of,horizon=252):
    import exchange_calendars as xcals
    day=date.fromisoformat(as_of)
    span=max(140,horizon*2+20)
    cal=xcals.get_calendar('XNYS',start=day-timedelta(days=5),end=day+timedelta(days=span))
    sessions=cal.sessions_in_range(day+timedelta(days=1),cal.last_session)
    return (float(cal.session_open(sessions[0]).timestamp()),
            float(cal.session_close(sessions[0]).timestamp()),sessions[horizon-1].date().isoformat())


def observe(symbol,closes,meta,path=None,supplier=None,clock=time.time):
    from monthly_touch_shadow import full_completed_rows
    from monthly_prospective import _validate_rows
    entries=[e for e in EVIDENCE['items'] if e['symbol']==symbol]
    if not entries or EVIDENCE['model_sha256']!=DIGEST:return
    _validate_rows(closes);as_of=closes[-1][0]
    if str(meta.get('as_of'))!=as_of:raise ValueError('anchor mismatch')
    opening,expires,maturity=calendar(as_of)
    with connect(path) as con:
        existing={r[0] for r in con.execute('SELECT event FROM extended_touch_v1 WHERE symbol=? AND model=? AND as_of=?',(symbol,model.MODEL,as_of))}
        pending=con.execute('SELECT event,as_of,maturity,anchor,issued FROM extended_touch_v1 WHERE symbol=? AND model=? AND outcome IS NULL',(symbol,model.MODEL)).fetchall()
        positions={d:i for i,(d,c) in enumerate(closes)}
        ready=[r for r in pending if r[1] in positions and r[2] in positions]
        issue=float(clock())<expires and len(existing)<len(entries)
        if not issue and not ready:return
        rows=(supplier or full_completed_rows)(symbol,closes);by_day={d:(h,l,c) for d,h,l,c in rows}
        lookup={e['event']:e for e in entries}
        for event,anchor_day,end,anchor,original_issue in ready:
            if event not in lookup:continue
            e=lookup[event];horizon=e['horizon_sessions']
            # A newly computed historical estimate may be displayed after open,
            # but it must not enter prospective scoring as if issued pre-open.
            if original_issue>=calendar(anchor_day,horizon)[0]:continue
            pos=positions[anchor_day];future=closes[pos+1:pos+horizon+1]
            if len(future)!=horizon or future[-1][0]!=end:continue
            if abs(closes[pos][1]/anchor-1)>.001:continue
            if any(d not in by_day or abs(by_day[d][2]/c-1)>.001 for d,c in future):continue
            e=lookup[event];threshold=e['threshold_percent']/100
            hit=any(by_day[d][0]>=anchor*(1+threshold) for d,c in future) if e['direction']=='up' else any(by_day[d][1]<=anchor*(1-threshold) for d,c in future)
            con.execute('UPDATE extended_touch_v1 SET outcome=?,scored=? WHERE symbol=? AND event=? AND model=? AND as_of=? AND outcome IS NULL',(int(hit),float(clock()),symbol,event,model.MODEL,anchor_day))
        predictions=model.estimate_all(rows) if issue else {}
        for e in entries:
            if not issue or e['event'] in existing:continue
            p=predictions[e['event']];issued=float(clock())
            _,_,maturity=calendar(as_of,e['horizon_sessions'])
            if issued>=expires:continue
            digest=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
            con.execute('INSERT OR IGNORE INTO extended_touch_v1 VALUES(?,?,?,?,?,?,?,?,?,?,?,NULL,NULL)',
                (symbol,e['event'],model.MODEL,as_of,maturity,closes[-1][1],p['probability'],p['baseline_probability'],issued,digest,DIGEST))


def schedule(symbol,rows,meta):
    if not any(e['symbol']==symbol for e in EVIDENCE['items']):return
    with LOCK:
        if symbol in RUNNING:return
        RUNNING.add(symbol)
    def run():
        try:observe(symbol,list(rows),dict(meta))
        except Exception as exc:print('extended estimate unavailable',symbol,type(exc).__name__,flush=True)
        finally:
            with LOCK:RUNNING.discard(symbol)
    threading.Thread(target=run,daemon=True).start()


def summary(path=None,now=None):
    now=time.time() if now is None else now;out=[]
    if EVIDENCE['model_sha256']!=DIGEST:return out
    with connect(path) as con:
        for e in EVIDENCE['items']:
            symbol,event=e['symbol'],e['event']
            row=con.execute('SELECT as_of,maturity,probability,issued,model_digest FROM extended_touch_v1 WHERE symbol=? AND event=? AND model=? ORDER BY as_of DESC LIMIT 1',(symbol,event,model.MODEL)).fetchone()
            if not row:continue
            as_of,maturity,p,issued,digest=row
            _,expires,expected=calendar(as_of,e['horizon_sessions'])
            if digest!=DIGEST or maturity!=expected or not issued<=now<expires or not math.isfinite(p) or not 0<=p<=1:continue
            n,scored=con.execute('SELECT COUNT(*),COUNT(outcome) FROM extended_touch_v1 WHERE symbol=? AND event=? AND model=?',(symbol,event,model.MODEL)).fetchone()
            out.append(dict(symbol=symbol,event=event,model_version=model.MODEL,model_sha256=DIGEST,
                display_policy_version='extended-estimates-v1',display_allowed=True,
                verification_status='historical_estimate',independent_confirmed=False,
                verification_evidence_id=EVIDENCE['id']+':'+symbol+':'+event,
                horizon_sessions=e['horizon_sessions'],threshold_percent=e['threshold_percent'],direction=e['direction'],
                probability=100*p,as_of=as_of,target_date=maturity,valid_until=expires,
                computed_at=issued,prospective_eligible=issued<calendar(as_of)[0],
                stored_count=n,scored_count=scored,evidence=e))
    return out
