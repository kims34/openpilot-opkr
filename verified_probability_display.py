"""Public presentation boundary: no unadmitted probability can be displayed.

Internal inference, historical diagnostics and prospective ledgers remain raw.
The current repository has research/historical evidence, but no admitted
independent confirmation bound to the exact public event, symbol and model.
Consequently there are currently NO publicly displayable forecasts. A payload
flag, historical skill, fallback base rate or research screen cannot approve
itself. Independent evidence admission must be implemented and reviewed before
adding a public allow path; this module deliberately contains no such shortcut.
"""
from __future__ import annotations

POLICY_VERSION = 'verified-only-v1'
MESSAGE = '검증 완료된 확률이 없습니다.'
LAYERS = ('one_month','preopen_futures','extended_session','after_open','first_hour')
SAFE_METADATA = frozenset(('symbol','index_id','name','model_version','as_of',
    'target_date','target_open','target_close','valid_until','computed_at',
    'price_basis','horizon_sessions','threshold_percent','available_from'))


def _unavailable(node):
    node = node if isinstance(node,dict) else {}
    out={key:value for key,value in node.items() if key in SAFE_METADATA
         and (value is None or isinstance(value,(str,int,float,bool)))}
    out.update(display_policy_version=POLICY_VERSION,display_allowed=False,
        verification_status='insufficient_independent_evidence',available=False,
        probability=None,error=MESSAGE,status=MESSAGE,verified_forecasts=[])
    for layer in LAYERS:
        if layer in node:
            out[layer]=_unavailable(node[layer])
    return out


def public_probability_payload(payload):
    """Strip all raw estimates, including fallback/candidate/unknown fields.

    A fresh object is constructed so the raw cache/ledger is never overwritten.
    Unknown future nested fields are not allowed to bypass the public policy.
    """
    payload=payload if isinstance(payload,dict) else {}
    source=payload.get('items')
    source=source if isinstance(source,dict) else {}
    out={key:payload[key] for key in ('updated_at','model_version','pipeline_status',
        'pipeline_updated_at') if key in payload}
    out.update(display_policy_version=POLICY_VERSION,display_allowed=False,
        verification_status='insufficient_independent_evidence',status=MESSAGE,
        items={key:_unavailable(value) for key,value in source.items() if isinstance(key,str)})
    return out
