"""Append-only prospective validation for frozen historically screened 5% candidates.

Only completed OHLC and pre-open first issues are admitted. Historical display
admission is separate from independent confirmation. No backfill or orders.
"""
import hashlib
import json
import sqlite3
import threading
import time
from datetime import datetime,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import requests
import monthly_touch_shadow_model as model

LOCK=threading.Lock()
RUNNING=set()
MODEL_DIGEST=hashlib.sha256(Path(model.__file__).read_bytes()).hexdigest()
NY=ZoneInfo('America/New_York')


def connect(path=None):
    from monthly_prospective import DB_PATH
    con=sqlite3.connect(path or DB_PATH,timeout=20)
    con.execute('PRAGMA busy_timeout=20000')
    con.execute('''CREATE TABLE IF NOT EXISTS monthly_touch_shadow_v1(
      symbol TEXT,model TEXT,direction TEXT,as_of TEXT,maturity TEXT,anchor REAL,
      probability REAL,baseline_probability REAL,issued_at REAL,
      source_digest TEXT,model_digest TEXT,training_latest TEXT,training_count INTEGER,
      outcome INTEGER,scored_at REAL,PRIMARY KEY(symbol,model,as_of))''')
    return con


def full_completed_rows(symbol,close_rows):
    as_of=close_rows[-1][0]
    r=requests.get('https://query1.finance.yahoo.com/v8/finance/chart/'+symbol,
        params={'period1':0,'period2':int(time.time()),'interval':'1d','includePrePost':'false','events':'div,splits'},
        headers={'User-Agent':'Mozilla/5.0 IndexAlert-touch-shadow/1'},timeout=30)
    r.raise_for_status();chart=r.json().get('chart') or {}
    if chart.get('error'):raise ValueError('provider error')
    results=chart.get('result') or []
    if len(results)!=1 or results[0].get('meta',{}).get('symbol')!=symbol:raise ValueError('symbol mismatch')
    raw=results[0];ts=raw.get('timestamp') or [];q=((raw.get('indicators') or {}).get('quote') or [{}])[0]
    hs,ls,cs=(q.get('high') or []),(q.get('low') or []),(q.get('close') or [])
    if not len(ts)==len(hs)==len(ls)==len(cs):raise ValueError('OHLC length mismatch')
    rows=[]
    for stamp,h,l,c in zip(ts,hs,ls,cs):
        day=datetime.fromtimestamp(int(stamp),timezone.utc).astimezone(NY).date().isoformat()
        if day>as_of:continue
        if any(v is None for v in (h,l,c)):raise ValueError('missing completed daily bar')
        h,l,c=map(float,(h,l,c))
        if not all(__import__('math').isfinite(v) and v>0 for v in (h,l,c)) or not l<=c<=h:raise ValueError('invalid OHLC')
        rows.append((day,h,l,c))
    dates=[x[0] for x in rows]
    if not dates or dates!=sorted(set(dates)) or dates[-1]!=as_of:raise ValueError('bad completed session range')
    import exchange_calendars as xcals
    cal=xcals.get_calendar('XNYS',start=dates[0],end=dates[-1])
    expected=[d.date().isoformat() for d in cal.sessions_in_range(dates[0],dates[-1])]
    if expected!=dates:raise ValueError('missing exchange session')
    by_day={d:c for d,h,l,c in rows}
    if any(d not in by_day or abs(by_day[d]/float(c)-1)>1e-6 for d,c in close_rows):raise ValueError('close basis mismatch')
    if any(abs(rows[i][3]/rows[i-1][3]-1)>.4 for i in range(1,len(rows))):raise ValueError('discontinuous price basis')
    return rows


def observe(symbol,close_rows,meta,db_path=None,supplier=None,clock=time.time):
    if symbol not in model.DIRECTIONS:return {'status':'not_tracked'}
    from monthly_prospective import _validate_rows,_maturity
    _validate_rows(close_rows)
    as_of=str(close_rows[-1][0]);now=float(clock())
    if str(meta.get('as_of'))!=as_of:raise ValueError('anchor metadata mismatch')
    with connect(db_path) as con:
        existing=con.execute('SELECT 1 FROM monthly_touch_shadow_v1 WHERE symbol=? AND model=? AND as_of=?',(symbol,model.MODEL,as_of)).fetchone()
        pending=con.execute('SELECT model,direction,as_of,maturity,anchor FROM monthly_touch_shadow_v1 WHERE symbol=? AND outcome IS NULL',(symbol,)).fetchall()
        dates={d for d,c in close_rows}
        ready=[p for p in pending if p[2] in dates and p[3] in dates]
        issue=not existing and now<float(meta.get('target_open') or 0)
        if not issue and not ready:return {'status':'recorded_or_waiting','inserted':False,'scored':0}
        rows=(supplier or full_completed_rows)(symbol,close_rows)
        by_day={d:(h,l,c) for d,h,l,c in rows}
        positions={d:i for i,(d,c) in enumerate(close_rows)}
        scored=0
        for old_model,direction,anchor_day,maturity,anchor in ready:
            pos=positions[anchor_day];future=close_rows[pos+1:pos+22]
            if len(future)!=21 or future[-1][0]!=maturity:continue
            if abs(float(close_rows[pos][1])/anchor-1)>.001:continue
            if any(d not in by_day or abs(by_day[d][2]/float(c)-1)>.001 for d,c in future):continue
            outcome=int(any(by_day[d][0]>=anchor*1.05 for d,c in future)) if direction=='up' else int(any(by_day[d][1]<=anchor*.95 for d,c in future))
            con.execute('UPDATE monthly_touch_shadow_v1 SET outcome=?,scored_at=? WHERE symbol=? AND model=? AND as_of=? AND outcome IS NULL',(outcome,float(clock()),symbol,old_model,anchor_day));scored+=1
        inserted=False
        if issue:
            pred=model.estimate(rows,symbol);issued=float(clock())
            # The issue time is AFTER inference, never a reconstructed timestamp.
            if issued<float(meta.get('target_open') or 0):
                maturity=_maturity(meta['target_date'],issued)
                digest=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
                before=con.total_changes
                con.execute('INSERT OR IGNORE INTO monthly_touch_shadow_v1 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,NULL,NULL)',
                  (symbol,model.MODEL,pred['direction'],as_of,maturity,float(close_rows[-1][1]),pred['probability'],pred['baseline_probability'],issued,digest,MODEL_DIGEST,pred['training_latest'],pred['training_count']))
                inserted=con.total_changes>before
        return {'status':'ok','inserted':inserted,'scored':scored}


def schedule(symbol,rows,meta):
    if symbol not in model.DIRECTIONS:return
    with LOCK:
        if symbol in RUNNING:return
        RUNNING.add(symbol)
    def run():
        try:observe(symbol,list(rows),dict(meta))
        except Exception as exc:print('5-percent shadow observer unavailable',symbol,type(exc).__name__,flush=True)
        finally:
            with LOCK:RUNNING.discard(symbol)
    threading.Thread(target=run,daemon=True).start()


def summary(db_path=None):
    out={}
    with connect(db_path) as con:
        for symbol,direction in model.DIRECTIONS.items():
            n,pending,last=con.execute('SELECT COUNT(*),SUM(CASE WHEN outcome IS NULL THEN 1 ELSE 0 END),MAX(as_of) FROM monthly_touch_shadow_v1 WHERE symbol=? AND model=?',(symbol,model.MODEL)).fetchone()
            maturity=con.execute('SELECT MIN(maturity) FROM monthly_touch_shadow_v1 WHERE symbol=? AND model=? AND outcome IS NULL',(symbol,model.MODEL)).fetchone()[0]
            scored=con.execute('SELECT probability,baseline_probability,outcome FROM monthly_touch_shadow_v1 WHERE symbol=? AND model=? AND outcome IS NOT NULL',(symbol,model.MODEL)).fetchall()
            result={'symbol':symbol,'model':model.MODEL,'target_label':f'{symbol} 21거래일 내 {"+5%" if direction=="up" else "-5%"} 도달',
                'stored_count':n,'pending_count':int(pending or 0),'scored_count':len(scored),'last_forecast_date':last,'next_maturity_session':maturity,
                'status':'INDEPENDENT_CONFIRMATION_PENDING','display_allowed':False,'baseline_type':'same-date full-history unconditional 5% touch frequency'}
            if scored:
                result['candidate_brier']=sum((p-y)**2 for p,b,y in scored)/len(scored)
                result['baseline_brier']=sum((b-y)**2 for p,b,y in scored)/len(scored)
            from monthly_touch_backtested_display import admitted_forecast
            forecast=admitted_forecast(con,symbol,MODEL_DIGEST)
            if forecast is not None:
                result['backtested_forecast']=forecast
            out[symbol]=result
    return out
