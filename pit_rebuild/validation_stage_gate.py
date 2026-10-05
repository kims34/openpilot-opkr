"""Retired v1 validation lineage. No stage can grant readiness.

The consumed v1 evaluator is invalid for independent promotion and retired.
Caller-controlled JSON booleans cannot resurrect its downstream stages. An
independently admitted prospective protocol must have its own lineage/gates;
it must never reuse this window or mutate the frozen criteria to rescue it.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

BASELINE=Path('/pit/private/abstention_v3_positions.parquet')
SEALED_MANIFEST=Path('/pit/private/sealed_holdout_manifest.json')
SEALED_RESULT=Path('/pit/private/sealed_holdout_result.json')
SHADOW_RESULT=Path('/pit/private/shadow_s1_result.json')
FRESH_RESULT=Path('/pit/private/fresh_confirmation_s2_result.json')
STAGES=('sealed_holdout','shadow_s1','fresh_confirmation_s2','live')


def load_json(p):
    # Compatibility helper only; check() never reads outcome/authority files.
    if not p.exists(): return None
    return json.loads(p.read_text(encoding='utf-8'))


def require(cond,msg):
    if not cond: raise SystemExit('GATE_BLOCKED: '+msg)


def check(stage):
    require(stage in STAGES, 'unknown stage')
    if stage=='sealed_holdout':
        require(not SEALED_RESULT.exists(), 'holdout result already exists; this window is consumed and cannot be reused')
    raise SystemExit('GATE_BLOCKED: RETIRED_VALIDATION_LINEAGE; v1 cannot grant stage readiness. An independently admitted prospective protocol is required.')


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('stage',choices=STAGES)
    args=ap.parse_args()
    print('VALIDATION_GATE='+json.dumps(check(args.stage),sort_keys=True))
