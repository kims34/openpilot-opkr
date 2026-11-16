"""Explicit historical-evidence admission, separate from independent verification."""
import math
import time
from datetime import date, timedelta

POLICY = 'backtested-touch-v1'
MODEL = 'volatility-scaled-5pct-touch-shadow-v1'
MODEL_SHA256 = '2b0f049d9258a5e8d569b8d46a7d40ca1ce50ce09a9fcb559cbea7bd0547b581'
EVIDENCE = {
 'SPY': dict(direction='down', samples=7387, first='1997-06-05', gain=6.264584563351444,
             reference_brier=.1838471652568552, candidate_brier=.17232990412201504),
 'QQQ': dict(direction='up', samples=5845, first='2003-07-24', gain=7.205203487833598,
             reference_brier=.23244189744830682, candidate_brier=.21569398574617485),
}


def validity(as_of):
    import exchange_calendars as xcals
    day = date.fromisoformat(as_of)
    cal = xcals.get_calendar('XNYS', start=day-timedelta(days=5), end=day+timedelta(days=60))
    sessions = cal.sessions_in_range(day+timedelta(days=1), day+timedelta(days=60))
    return float(cal.session_close(sessions[0]).timestamp()), sessions[20].date().isoformat()


def admitted_forecast(con, symbol, model_digest, now=None):
    evidence = EVIDENCE.get(symbol)
    if evidence is None or model_digest != MODEL_SHA256:
        return None
    row = con.execute('''SELECT direction,as_of,maturity,probability,issued_at,model_digest
        FROM monthly_touch_shadow_v1 WHERE symbol=? AND model=? ORDER BY as_of DESC LIMIT 1''',
        (symbol, MODEL)).fetchone()
    if not row:
        return None
    direction, as_of, maturity, probability, issued, digest = row
    now = time.time() if now is None else now
    if (direction != evidence['direction'] or digest != MODEL_SHA256 or
            not math.isfinite(probability) or not 0 <= probability <= 1 or issued > now):
        return None
    try:
        expires, expected_maturity = validity(as_of)
    except (ValueError, IndexError):
        return None
    if now >= expires or maturity != expected_maturity:
        return None
    return dict(display_policy_version=POLICY, display_allowed=True,
        verification_status='historical_backtest_passed', independent_confirmed=False,
        verification_evidence_id='five-percent-historical-v1-20261116:'+symbol,
        model_version=MODEL, model_sha256=digest, symbol=symbol,
        event='down5_touch' if direction == 'down' else 'up5_touch',
        label=f'{symbol} 21거래일 내 {"-5%" if direction == "down" else "+5%"} 도달',
        probability=100*probability, as_of=as_of, target_date=maturity,
        horizon_sessions=21, threshold_percent=5, valid_until=expires,
        evidence=dict(evidence, last='2026-10-15',
            scope='과거 개발 백테스트 · 동일 역사 재사용',
            status='과거 백테스트 통과 · 실전 검증 진행 중',
            target='기준 종가 대비 다음 21거래일 고가·저가 도달 여부'))
