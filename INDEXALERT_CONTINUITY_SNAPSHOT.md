# IndexAlert Continuity Snapshot — Canonical Cross-Chat Handoff

Updated: 2026-09-30 KST
Branch of record: `index-alert-research-v1`

## 0. Purpose and authority

This file keeps IndexAlert continuation independent of older Chat/Work rooms.

Authority order:
1. `INDEXALERT_MASTER_SPEC.md` — frozen statistical/validation contract.
2. `INDEXALERT_RESEARCH_LEDGER.md` — experiments, outcomes, dispositions, negative evidence.
3. Current GitHub code + reproducible Actions artifacts/logs — implementation/execution evidence.
4. `INDEXALERT_RESEARCH_STATUS.md` — current status summary.
5. This snapshot — cross-chat/cross-branch handoff and legacy evidence.
6. Older chats/notes — historical context only.

When sources conflict, current reproducible GitHub evidence wins.

## 1. Frozen contract that must survive chat deletion

- H5 = Core development horizon.
- H10 = `REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE`; do not sweep H6-H9 or retune H10 from completed outcomes.
- H20 = outside requested 5-10-session scope; archive only.
- Anchored walk-forward: train 504 / calibration 126 / test 126.
- H5/H10 common fold endpoints; horizon-matched purge/embargo and label-overlap protection.
- Calibration is disjoint and may use only information/outcomes available before test prediction.
- Test/holdout outcomes must not choose thresholds, quantiles, TopK, costs or policy.
- Correct CPCV: 6 contiguous groups; all two-test-group combinations; each remaining group once as calibration; other three train; **60 cases per horizon**.
- CPCV is stability evidence only, not forward OOS, holdout or promotion authority.
- Original decision-time Top3 frozen; vetoed/held/unfillable slots remain empty; **no rank-4+ backfill**.
- 0..3 trades and NO_TRADE valid.
- Strict PIT/availability lineage and KRX corporate-action-safe base-price returns mandatory.
- Primary evidence: executable cost-adjusted NetReturn/NetEV, PF, cluster uncertainty, MDD, ES95/ES99, cost stress, coverage/abstention, execution/capacity and tail dependence.
- Current square-root impact is a cost proxy, not empirical capacity-aware NetEV.
- Official historical security/status, exact halt/delisting economics, partial fills, fill time/price, markout, latency/expiry and empirical capacity are hard blockers.
- Sealed holdout stays one-shot and unburned until blockers/code/protocol are frozen; after it, require Shadow S1 then frozen Fresh Confirmation S2.
- Never relax q25, TopK, costs, recent-evidence or execution assumptions merely to manufacture trades.

## 2. Current research state

### H5 developmental reference

Strongest compact selection-conditioned result:
- 278 executed entries / 137 trade days
- mean NetReturn ~+1.150%, PF ~1.546
- cluster lower bound below zero
- 2x-cost mean ~+0.787%, PF ~1.344
- portfolio total ~+16.39%, CAGR ~1.83%, MDD ~-24.39%, Sharpe ~0.23
- admissions concentrated in 2018-2021; none in 2022-2026 / latest 504 OOS
- remove-best-5 turns mean economics negative and PF below 1

Classification: `DEVELOPMENTAL_NOT_CURRENTLY_PROMOTABLE`.

### Corrected 60-case CPCV — completed

Action `36637351334` completed successfully under the frozen 60-case protocol.

Authoritative values:
- H5 median PF **0.381**; positive NetEV **43.3%**; positive date-cluster LCB **11.7%**.
- H10 median PF **0.745**; positive NetEV **50.0%**; positive date-cluster LCB **33.3%**.

Verdict: CPCV does not establish robust edge.

The older H10 15-combination result is **HISTORICAL / SUPERSEDED**. Old-chat recollections including H10 PF ~0.454 are invalid for decisions. Earlier exit-137/143 runs failed from memory/process accumulation; splitwise generate -> evaluate -> release fixed execution without altering the statistical contract.

### Uncertainty Audit — completed

`EXP-2026-09-29-UNCERTAINTY-AUDIT-01`, Action `36637333875`.

Key conclusion: **KEEP_ABSTENTION**.
- all-OOS q25-blocked mean -0.8432%, PF 0.8425, cluster interval entirely below zero
- 2022+ q25-blocked mean -1.2551%, PF 0.8005
- latest-504 blocked mean -0.6263%, PF 0.9012; remove-best-5 -1.2697%, PF 0.8011
- latest conservative-positive subset only 4 rows, mean -22.5669%, PF 0.1381

Do not weaken q25 and do not launch conditional-q25 rescue from this result. Seek orthogonal PIT-valid information.

Audit artifact also states `common_stock_identity_validated=false`, `judge_eligible=false`.

### Policy-aligned calibration — completed

`EXP-2026-09-29-POLICY-CAL-01`, Action `36643183157`, artifact `11067383547`.

The calibration population was aligned to the same preliminary post-Top3 normal-market veto without changing q-level/model/features/windows/costs/admission or allowing backfill.

Result:
- reference and challenger have the **same 278 compact decision-date/symbol selections**
- no reference-only or challenger-only selected rows
- compact portfolio and cost-stress results exactly identical
- exported row differences are only model naming

Disposition: **ADOPT STRUCTURAL ALIGNMENT / NO PERFORMANCE CHANGE / NOT PROMOTION EVIDENCE**. The preliminary normal-market proxy still requires official historical status validation.

## 3. Other material dispositions

- Rolling-160 recency challenger: rejected; do not sweep nearby windows.
- CA-safe daily path family: rejected/do not retune.
- H10 anchored challenger: `REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE` despite strong historical point estimates because admissions are old, recent evidence is absent, corrected CPCV is weak, and blockers remain.
- H20: out of scope/archive.
- Price-only threshold/feature mining should stop; next information must be genuinely independent and PIT-valid.

## 4. KRX status / investor-flow blockers

Official historical KRX common-stock/security-status coverage remains incomplete for the Judge period.

Need before holdout/promotion:
- real official historical common-stock/security-status raw data
- stable security mapping
- PIT availability lineage
- exact halt, cleanup-trading and delisting status/economics

First independent feature candidate: official KRX investor-flow data. Before any performance test establish official reproducible historical access, coverage, mapping and `event_time/published_at/available_at/ingested_at`. Final day-D flow is only eligible for a later decision after publication. Authentication/source-probe success alone is not feature evidence. Do not use undocumented same-day substitutes.

## 5. Current explicit unfinished-work registry

Continue from the first unresolved item supported by latest GitHub state:
1. **DONE:** corrected 60-case H5/H10 CPCV read and archived.
2. **DONE:** `UNCERTAINTY-AUDIT-01` read; decision KEEP_ABSTENTION.
3. **DONE:** `POLICY-CAL-01` read; adopt structural population alignment with no performance claim.
4. **NEXT:** obtain/validate real official historical KRX common-stock/security-status raw data + PIT lineage; exact halt/cleanup/delisting economics.
5. Establish official reproducible KRX investor-flow historical access/lineage before any performance test.
6. Continue execution realism: empirical fill ratio/time/price, partial fills, post-fill markout, latency/expiry, empirical capacity.
7. Keep sealed holdout untouched until blockers/code/protocol freeze; then Shadow S1 -> Fresh Confirmation S2.
8. Separately re-verify current server + Android + FCM end-to-end health on latest branch heads before calling the operational app complete.

## 6. Realtime / server / Android legacy continuity

Audit anchors from the prior handoff:
- probability/realtime lineage `index-alert-v41-research` previously @ `85bfd892ef8cc8e36b434983945cf45ce9d7e070`
- server lineage `index-alert-server` previously @ `ccde47271fd85c3d5a880d7e18531131d625c309`
- Android/build lineage `index-alert-build` previously @ `d8f61cf2712eb91651b0ce25810aef0209697e00`

These are historical anchors only; always re-fetch current heads before work.

Legacy chat operational evidence preserved for deletion safety:
- an IndexAlert APK was installed on a Galaxy S25-class handset in the earlier operator-shell/FCM track
- client FCM token acquisition/copy worked
- server token registration was reported successful
- a server test push reached Firebase HTTP v1
- handset-visible notification delivery was not preserved as a separately verified current final checkpoint

Treat these as `LEGACY_CHAT_EVIDENCE`, not current proof. Re-test latest server/build before declaring current end-to-end notification health.

Older implementation-order note (`DB migration 001+ -> isolated KOSPI server skeleton -> exact FastAPI/Python schema -> Firebase payload -> Kotlin data class`) is `LEGACY_CHAT_PLANNING_CONTEXT`, not a frozen requirement.

## 7. Continuation rule

On every continuation:
- re-read current Master Spec, Ledger, this snapshot and relevant branch HEAD/Actions
- skip completed/rejected experiments
- never revive rejected candidates by threshold/cost/horizon mining
- if old chat conflicts with reproducible GitHub evidence, GitHub wins
- commit each material result to Ledger/Status/Snapshot so chat history remains nonessential

## 8. Old-chat deletion gate

Older IndexAlert Chat/Work rooms remain unnecessary as a project-state dependency. Their material continuity information is preserved in GitHub. Deleting old chats does not delete GitHub code, Actions artifacts, Master Spec, Ledger or this snapshot.
