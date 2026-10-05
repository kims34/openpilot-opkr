"""Stdlib read-only artifact byte hashes and retired gates. No outcome parsing."""
import hashlib
import json
from pathlib import Path

import validation_stage_gate as gate

ROOT=Path('/pit/private')
EXPECTED={
    'sealed_holdout_result.json':'30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82',
    'sealed_holdout_manifest.json':'ff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907',
    'sealed_holdout/acquisition_receipt.json':'3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63',
}


def audit():
    artifacts, stages = {}, {}
    for name, expected in EXPECTED.items():
        path=ROOT/name
        try:
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            artifacts[name]={'sha256':digest,'matches_preserved_hash':digest==expected}
        except OSError:
            artifacts[name]={'sha256':None,'matches_preserved_hash':False}
    for stage in gate.STAGES:
        try:
            gate.check(stage)
            stages[stage]={'blocked':False,'reason':'UNEXPECTED_READINESS'}
        except SystemExit as exc:
            reason='CONSUMED_WINDOW' if 'window is consumed' in str(exc) else (
                'RETIRED_LINEAGE' if 'RETIRED_VALIDATION_LINEAGE' in str(exc) else 'UNEXPECTED_BLOCKER')
            stages[stage]={'blocked':True,'reason':reason}
    return dict(mode='READ_ONLY_RETIRED_VALIDATION_GATE_AUDIT',artifacts=artifacts,stages=stages,
        validation_boundary_preserved=all(a['matches_preserved_hash'] for a in artifacts.values())
            and all(s['blocked'] and s['reason'] in ('CONSUMED_WINDOW','RETIRED_LINEAGE') for s in stages.values()),
        private_artifacts_mutated=False, outcome_metrics_parsed=False, model_executed=False,
        network_request_attempted=False, real_orders_sent=False, live_trading_authorized=False)


if __name__=='__main__':
    print(json.dumps(audit(),sort_keys=True),flush=True)
