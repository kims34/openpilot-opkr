import ast
from pathlib import Path
import shutil
import subprocess
import unittest

class DashboardScriptTests(unittest.TestCase):
    def test_refresh_clears_stale_state_and_reports_integer_precision(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node is required for the dashboard script check")
        tree = ast.parse(Path("shadow_operational_dashboard.py").read_text(encoding="utf-8"))
        script = next(ast.literal_eval(n.value) for n in tree.body
                      if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SCRIPT" for t in n.targets))
        harness = r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const script=fs.readFileSync(0,'utf8');
(async()=>{
 for(const fail of ['status','settlement','quarantine','missing_history','unsafe_integer','safe_integer']){
  const elements=Object.fromEntries(['refresh','error','state','blockers','capital','settlement'].map(id=>[id,{
   textContent:'',disabled:false,children:[{textContent:'STALE_VALUE'}],append(...nodes){this.children.push(...nodes)},
   replaceChildren(){this.children=[]},addEventListener(){}
  }]));
  let completion;
  const context={
   document:{getElementById:id=>elements[id],createElement:()=>({textContent:''})},
   fetch:async url=>{
    if(url==='/api/status'){
     if(fail==='status')throw Error('transport');
     if((fail==='quarantine'||fail==='missing_history'))return {ok:true,json:async()=>({diagnostics_complete:false,
      local_blockers:[fail==='quarantine'?'SAFETY_METADATA_QUARANTINED':'INITIALIZED_HISTORY_MISSING'],real_orders_authorized:false})};
     return {ok:true,json:async()=>({diagnostics_complete:true,shadow_mode:'SHADOW',journal_epoch:fail==='unsafe_integer'?Number('9223372036854775807'):fail==='safe_integer'?Number('9007199254740991'):1,
      snapshot_revision:1,unresolved_intent_count:0,native_inbox_pending_count:0,native_inbox_conflict_count:0,
      local_blockers:[],capital:{maximum_krw:100,total_committed_krw:fail==='unsafe_integer'?Number('9007199254740993'):fail==='safe_integer'?Number('9007199254740991'):0}})};
    }
    if(fail==='unsafe_integer'||fail==='safe_integer')return {ok:true,json:async()=>({assessment_completed:true,
     cashflow_reconciliation:{cash_balance_matched:true,settlement_fields_consistent:true},local_reconciliation_errors:[],
     journal_epoch:fail==='unsafe_integer'?Number('9223372036854775806'):Number('9007199254740990'),snapshot_revision:1})};
    if((fail==='quarantine'||fail==='missing_history'))return {ok:true,json:async()=>({assessment_completed:false,
     review_errors:['SETTLEMENT_INPUT_NOT_CONFIGURED']})};
    throw Error('settlement transport');
   }
  };
  vm.createContext(context);
  // Await the script's automatic refresh instead of starting a second request.
  vm.runInContext(script.replace(/refresh\(\);$/, 'globalThis.completion=refresh();'),context);
  await context.completion;
  if(fail==='unsafe_integer'){
   assert.equal(elements.error.textContent,'');
   const text=['state','capital','settlement'].flatMap(id=>elements[id].children.map(n=>n.textContent)).join(' ');
   assert.ok(text.includes('정확한 수치 확인 불가'));
   assert.ok(!text.includes('9223372036854776000'));
   assert.ok(!text.includes('9007199254740992'));
   assert.ok(text.includes('100'));
   assert.ok(text.includes('조회 시점 연결'));
   assert.ok(text.includes('미확인'));
  }else if(fail==='safe_integer'){
   assert.equal(elements.error.textContent,'');
   const text=['state','capital','settlement'].flatMap(id=>elements[id].children.map(n=>n.textContent)).join(' ');
   assert.ok(!text.includes('정확한 수치 확인 불가'));
   assert.ok(text.includes('9007199254740991'));
   assert.ok(text.includes('9007199254740990'));
   assert.ok(text.includes('조회 시점 차이'));
  }else if((fail==='quarantine'||fail==='missing_history')){
   assert.equal(elements.error.textContent,'');
   assert.equal(elements.blockers.children.length,1);
   assert.ok(elements.blockers.children[0].textContent.includes('재시작과 활성화가 차단'));
   const text=['state','blockers','capital','settlement'].flatMap(id=>elements[id].children.map(n=>n.textContent)).join(' ');
   assert.ok(!text.includes('STALE_VALUE'));
   assert.ok(!text.includes('로컬 Shadow 활성'));
   assert.ok(!text.includes('로컬 진단 항목의 막힘은 없습니다'));
   assert.ok(text.includes('꺼짐'));
   assert.ok(text.includes('확인되지 않음'));
  }else{
   for(const id of ['state','blockers','capital','settlement'])
    assert.equal(elements[id].children.length,0,fail+' leaves partial '+id);
   assert.ok(elements.error.textContent.length>0);
  }
  assert.equal(elements.refresh.disabled,false);
 }
})().catch(e=>{process.stderr.write(String(e));process.exitCode=1});
"""
        result = subprocess.run([node, "-e", harness], input=script, text=True, encoding="utf-8", capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

if __name__ == "__main__":
    unittest.main()
