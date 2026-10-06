import ast
from pathlib import Path
import shutil
import subprocess
import unittest

class DashboardScriptTests(unittest.TestCase):
    def test_refresh_error_clears_partially_rendered_status(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node is required for the dashboard script check")
        tree = ast.parse(Path("shadow_operational_dashboard.py").read_text(encoding="utf-8"))
        script = next(ast.literal_eval(n.value) for n in tree.body
                      if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SCRIPT" for t in n.targets))
        harness = r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const script=fs.readFileSync(0,'utf8');
(async()=>{
 for(const fail of ['status','settlement']){
  const elements=Object.fromEntries(['refresh','error','state','blockers','capital','settlement'].map(id=>[id,{
   textContent:'',disabled:false,children:[],append(...nodes){this.children.push(...nodes)},
   replaceChildren(){this.children=[]},addEventListener(){}
  }]));
  let completion;
  const context={
   document:{getElementById:id=>elements[id],createElement:()=>({textContent:''})},
   fetch:async url=>{
    if(url==='/api/status'){
     if(fail==='status')throw Error('transport');
     return {ok:true,json:async()=>({diagnostics_complete:true,shadow_mode:'SHADOW',journal_epoch:1,
      snapshot_revision:1,unresolved_intent_count:0,native_inbox_pending_count:0,native_inbox_conflict_count:0,
      local_blockers:[],capital:{maximum_krw:100,total_committed_krw:0}})};
    }
    throw Error('settlement transport');
   }
  };
  vm.createContext(context);
  // Await the script's automatic refresh instead of starting a second request.
  vm.runInContext(script.replace(/refresh\(\);$/, 'globalThis.completion=refresh();'),context);
  await context.completion;
  for(const id of ['state','blockers','capital','settlement'])
   assert.equal(elements[id].children.length,0,fail+' leaves partial '+id);
  assert.ok(elements.error.textContent.length>0);
  assert.equal(elements.refresh.disabled,false);
 }
})().catch(e=>{process.stderr.write(String(e));process.exitCode=1});
"""
        result = subprocess.run([node, "-e", harness], input=script, text=True, encoding="utf-8", capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

if __name__ == "__main__":
    unittest.main()
