# IndexAlert Internal Completeness Audit

Updated: 2026-10-02 KST
Branch: `index-alert-research-v1`

## Scope

Internal-only audit. No KRX approval/data, genuine LIVE evidence, sealed holdout, or real-account ordering is fabricated or consumed.

Reviewed boundaries: continuous research/preregistration, research orchestrator, successor-Core staging, promotion evidence, KRX daily-panel staging/source admission, automation-capital control, Kiwoom offline normalization/reconciliation, execution evidence/sufficiency, relevant CI and authority documents.

## Findings

### IC-001 — successor promotion authority too close to caller-supplied confirmation — FIXED FAIL-CLOSED

Earlier `assess_shadow_promotion` could return caller-controlled promotion/code-update eligibility from confirmation booleans. A first hardening correctly forced `automatic_code_update_allowed=false`, but still left `promotion_eligible=true` and `automatic_code_update_eligible=true` when a caller supplied all gate booleans as true. Although no deployment actuator was connected, those fields could still be misread or later consumed as independently established promotion authority.

Final fail-closed fix:
- caller-supplied confirmation booleans may establish only `promotion_conditions_structurally_satisfied`;
- `promotion_eligible=false` remains mandatory until an independent canonical gate-admission adapter exists;
- `automatic_code_update_eligible=false` and `automatic_code_update_allowed=false` remain mandatory;
- `independent_gate_admission_verified=false`, `promotion_authority_verified=false`, and `promotion_authority_granted=false` remain mandatory;
- `INDEPENDENT_GATE_ADMISSION_NOT_IMPLEMENTED` is always retained as a blocker;
- spoofed caller flags claiming authority are ignored;
- live-order and sealed-holdout authority remain false.

A future promotion adapter must verify immutable, provenance-bound outputs from the authoritative source, execution, holdout, Shadow S1 and Fresh Confirmation S2 auditors. Caller booleans, labels, filenames, hashes, self-authored manifests and status strings are not evidence admission.

### IC-002 — legacy KRX daily-panel builder self-labeled Judge eligibility — FIXED FAIL-CLOSED

The older `research_v1_krx.py` staging builder defaulted `BuildStats.judge_eligible=true` and labeled rows `KRX via authenticated pykrx`. That was too strong: successful date-specific OHLCV retrieval does not establish the frozen KRX A-F source contract, authenticated/approved route admission, complete history, PIT lineage, status-event coverage or exact status economics.

Fail-closed fix:
- `judge_eligible=false` is now the immutable default from this builder;
- `source_governance_admission_required=true`;
- `sealed_holdout_authorized=false`;
- `live_trading_authorized=false`;
- the transport label no longer claims authenticated source admission;
- source failure text no longer calls this a "Judge-grade path";
- CI statically rejects restoration of the old authority-bearing labels/defaults.

This does not invalidate date-specific panel staging as engineering infrastructure. It prevents staging success from being interpreted as Final-Judge/source admission.

### IC-003 — Data Marketplace account access could be mistaken for automation permission — FIXED FAIL-CLOSED

The official KRX Data Marketplace homepage terms prohibit unauthorized automated collection. Existing source-governance code already required credentials, structured authorization evidence and explicit per-run consent, but did not separately encode the legal/terms distinction between ordinary member login and permission for automated collection.

Fail-closed fix:
- `research_v1_krx_authorization_evidence.py` requires explicit `automated_collection_authorized=true` for the Data Marketplace web-session route;
- `research_v1_krx_auth_preflight.py` independently requires `EXPLICIT_KRX_AUTOMATED_COLLECTION_PERMISSION`;
- readiness/probe code propagates that permission signal rather than inferring it from credentials;
- the official terms constraint is frozen in `INDEXALERT_KRX_DATA_MARKETPLACE_TERMS_AUDIT.md/.json` and validated in CI;
- confirmed `KRX_ID/KRX_PW` presence therefore does not authorize any automated KRX web-session request.

### Order-path audit

No Kiwoom network/auth/order-submission implementation is present in the reviewed native execution module; it is offline normalization/reconciliation only and hard-codes project LIVE admission/provenance false. Automation control validates broker-neutral intents/capital ceilings and does not submit orders. No internal evidence was found that authorizes real-account ordering.

### Research/holdout audit

Continuous-research and orchestrator paths keep sealed holdout forbidden for discovery/tuning and emit research IDEA/challenger states without production-write authority. Successor staging remains non-production. Even a structurally complete caller confirmation cannot independently establish promotion eligibility or Core-mutation authority.

## Remaining items are external/evidence-bound

This audit does not close KRX A-F external evidence, exact affected-position status-event economics, genuine broker-native LIVE provenance, empirical execution sufficiency, sealed holdout, Shadow S1, Fresh Confirmation S2, or live-trading authorization.

## Current fail-closed project state

- `genuine_live_provenance_verified=false`
- `empirical_execution_blocker_closed=false`
- `sealed_holdout_authorized=false`
- `live_trading_authorized=false`
- caller-supplied successor confirmation is structural diagnostic input only
- `promotion_eligible=false` until independent gate admission is implemented and verified
- automatic Core mutation remains unauthorized
- legacy KRX daily-panel retrieval cannot self-grant Judge/source admission
