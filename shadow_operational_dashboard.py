"""Local-only, read-only Shadow dashboard; no broker or production deployment.

Run: python shadow_operational_dashboard.py --journal EXISTING.sqlite --port 8765
Only 127.0.0.1 is bound. The journal is fixed at startup, never a request path.
"""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json

from shadow_operational_status import inspect_shadow_operational_status
from native_settlement_review_cli import review_native_settlement_file


PAGE = '''<!doctype html><html lang="ko"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>IndexAlert Shadow 운영 점검</title>
<style>body{font:16px system-ui;max-width:760px;margin:32px auto;padding:0 18px;background:#f6f8fb;color:#142238}
section{background:white;padding:20px;border-radius:12px;margin:16px 0}h1{font-size:24px}button{padding:10px 20px;cursor:pointer}
dt{color:#52647b}dd{margin:4px 0 18px;font-weight:600}li{margin:10px 0}.notice{color:#8b3100}#error{color:#a02020}</style>
<h1>IndexAlert Shadow 운영 점검</h1>
<p class="notice">실제 주문은 꺼져 있습니다. 이 화면은 로컬 저널 점검용이며 실제 계좌·전략 검증 완료를 의미하지 않습니다.</p>
<button id="refresh" type="button">상태 새로고침</button><p id="error" role="alert"></p>
<section><h2>조회 상태</h2><dl id="state"></dl></section>
<section><h2>확인할 항목</h2><ul id="blockers"></ul></section>
<section><h2>자금 예약</h2><dl id="capital"></dl></section>
<section><h2>결제 자료 대조</h2><dl id="settlement"></dl>
<p>아래 결과는 결제 자료를 별도로 조회한 시점의 진단입니다. 잔액 일치로 실제 계좌 출처나 결제 의미가 검증되지는 않습니다.</p></section>
<p>조회 시점의 상태입니다. 이후 도착한 체결·재접속·Kill Switch로 상태가 달라질 수 있습니다.</p>
<script src="/dashboard.js"></script></html>'''

SCRIPT = ''''use strict';
const byId=id=>document.getElementById(id);
const labels={KILL_SWITCH_LATCHED:'Kill Switch가 잠겨 있습니다',BATCH_RECONCILIATION_REQUIRED:'전체 주문 내역 대조가 필요합니다',
UNRESOLVED_DURABLE_INTENTS:'처리 여부가 확인되지 않은 주문이 있습니다',ORDER_SNAPSHOT_BINDING_STALE:'주문 대조 결과가 현재 상태와 맞지 않습니다',
NATIVE_INBOX_PENDING:'미처리 체결 수신 내역이 있습니다',NATIVE_INBOX_CONFLICTED:'서로 충돌하는 체결 수신 내역이 있습니다',
CAPITAL_NOT_CONFIGURED:'Shadow 자금 설정이 없습니다',CAPITAL_CONTROL_DISABLED:'Shadow 자금 사용이 꺼져 있습니다',
CAPITAL_CEILING_EXCEEDED:'현재 예약 자금이 설정 한도를 넘었습니다',OPERATIONAL_SNAPSHOT_UNAVAILABLE:'저널을 읽을 수 없거나 필수 정보가 없습니다'};
function field(parent,label,value){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=String(value);parent.append(dt,dd);}
async function refresh(){const button=byId('refresh');button.disabled=true;byId('error').textContent='';
for(const id of ['state','blockers','capital','settlement'])byId(id).replaceChildren();
try{const response=await fetch('/api/status',{cache:'no-store'});if(!response.ok)throw Error('status unavailable');const data=await response.json();
field(byId('state'),'조회 결과',data.diagnostics_complete?'조회 완료':'조회 불가');
field(byId('state'),'실제 주문','꺼짐');
if(data.diagnostics_complete){field(byId('state'),'Shadow 상태',data.shadow_mode==='SHADOW'?'로컬 Shadow 활성':'정지');
field(byId('state'),'저널 epoch / 대조 revision',data.journal_epoch+' / '+data.snapshot_revision);
field(byId('state'),'미확인 주문',data.unresolved_intent_count);field(byId('state'),'미처리 / 충돌 체결',data.native_inbox_pending_count+' / '+data.native_inbox_conflict_count);}
for(const key of data.local_blockers){const li=document.createElement('li');li.textContent=labels[key]||'추가 점검이 필요합니다';byId('blockers').append(li);}
if(data.diagnostics_complete&&data.local_blockers.length===0){const li=document.createElement('li');li.textContent='로컬 진단 항목의 막힘은 없습니다. 외부 검증과 실제 운영 승인은 별도로 필요합니다.';byId('blockers').append(li);}
if(data.capital){field(byId('capital'),'설정 한도 (원)',data.capital.maximum_krw);field(byId('capital'),'기존 사용·예약 (원)',data.capital.baseline_committed_krw);
field(byId('capital'),'저널 관리 예약 (원)',data.capital.managed_reserve_krw);field(byId('capital'),'전체 사용·예약 (원)',data.capital.total_committed_krw);}
else field(byId('capital'),'자금 정보','확인되지 않음');
const settlementResponse=await fetch('/api/settlement',{cache:'no-store'});
if(!settlementResponse.ok)throw Error('settlement unavailable');
const settlement=await settlementResponse.json();
if(settlement.assessment_completed){field(byId('settlement'),'자료 점검','완료');
field(byId('settlement'),'예수금 증감 대조',settlement.cashflow_reconciliation.cash_balance_matched?'일치':'불일치');
field(byId('settlement'),'결제 조회 epoch / revision',settlement.journal_epoch+' / '+settlement.snapshot_revision);
field(byId('settlement'),'독립 계좌·결제 승인','미확인');
if(data.diagnostics_complete&&(data.journal_epoch!==settlement.journal_epoch||data.snapshot_revision!==settlement.snapshot_revision))
field(byId('settlement'),'조회 시점 차이','저널 상태가 변경됐습니다. 다시 조회하세요');
}else field(byId('settlement'),'자료 점검',settlement.review_errors.includes('SETTLEMENT_INPUT_NOT_CONFIGURED')?'결제 자료 파일이 연결되지 않았습니다':'자료의 범위·형식·저널 연결을 확인하세요');
}catch(error){for(const id of ['state','blockers','capital','settlement'])byId(id).replaceChildren();byId('error').textContent='상태를 가져오지 못했습니다. 이전 상태는 표시하지 않습니다.';}finally{button.disabled=false;}}
byId('refresh').addEventListener('click',refresh);refresh();'''


class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # No request identities/paths in operational logs.

    def _respond(self,status,body,content_type):
        encoded = body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type',content_type+'; charset=utf-8')
        self.send_header('Content-Length',str(len(encoded)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        # Prevent foreign-host DNS rebinding. No CORS or remote bind option.
        host = self.headers.get('Host','')
        allowed = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
        if host not in allowed:
            self._respond(403,'Forbidden','text/plain'); return
        if self.path == '/': self._respond(200,PAGE,'text/html')
        elif self.path == '/dashboard.js': self._respond(200,SCRIPT,'text/javascript')
        elif self.path == '/api/status':
            self._respond(200,json.dumps(inspect_shadow_operational_status(self.server.journal_path),sort_keys=True),'application/json')
        elif self.path == '/api/settlement':
            if self.server.settlement_input_path is None:
                report = dict(assessment_completed=False,review_errors=['SETTLEMENT_INPUT_NOT_CONFIGURED'],
                    real_orders_authorized=False,genuine_live_provenance_verified=False,
                    broker_request_sent=False,journal_mutation_attempted=False)
            else:
                report = review_native_settlement_file(self.server.settlement_input_path,self.server.journal_path)
            self._respond(200,json.dumps(report,sort_keys=True),'application/json')
        else: self._respond(404,'Not found','text/plain')

    def do_POST(self): self._respond(405,'Read only','text/plain')
    do_PUT = do_POST
    do_PATCH = do_POST
    do_DELETE = do_POST


def create_dashboard_server(journal_path, port=8765, *, settlement_input_path=None):
    server = ThreadingHTTPServer(('127.0.0.1',port),DashboardHandler)
    server.journal_path = journal_path
    server.settlement_input_path = settlement_input_path
    return server


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--journal',required=True)
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--settlement-input',help='Optional offline native settlement review input JSON')
    args = parser.parse_args(argv)
    server = create_dashboard_server(args.journal,args.port,settlement_input_path=args.settlement_input)
    print(f'IndexAlert Shadow: http://127.0.0.1:{server.server_port}',flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__': main()
