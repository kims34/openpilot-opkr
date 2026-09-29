# IndexAlert Continuity Snapshot — Canonical Cross-Chat Handoff

Updated: 2026-09-30 KST
Branch of record: `index-alert-research-v1`

## 0. Purpose and authority

This file exists so IndexAlert development can continue from the current GitHub state and the current continuation chat without depending on older Chat/Work rooms.

Authority order when sources conflict:

1. `INDEXALERT_MASTER_SPEC.md` — frozen statistical / validation contract.
2. `INDEXALERT_RESEARCH_LEDGER.md` — preregistered experiments, outcomes, dispositions and negative evidence.
3. Current GitHub code + reproducible Actions artifacts/logs — implementation/execution evidence.
4. `INDEXALERT_RESEARCH_STATUS.md` — convenient status summary; historical sections may be superseded by the Master Spec/Ledger.
5. This continuity snapshot — cross-branch and legacy-chat handoff, discrepancy registry and deletion-safe continuity notes.
6. Older chats/notes — historical context only; they never override current GitHub evidence.

If a remembered result conflicts with an Action artifact or current code, the Action artifact/current code wins.

## 1. Current branch map captured during continuity audit

Branch heads at the time of this audit:

- research authority: `index-alert-research-v1` @ `b1ae66a39fdb01ff852cd4758b1befb85e978943` before this snapshot commit. Commit message: `Test calibration q25 uncertainty diagnostic`.
- probability/realtime research lineage: `index-alert-v41-research` @ `85bfd892ef8cc8e36b434983945cf45ce9d7e070`. Commit: `Run simple v4.1b two-hour probability research`.
- server/runtime lineage: `index-alert-server` @ `ccde47271fd85c3d5a880d7e18531131d625c309`. Commit: `Align USDKRW daily chart with official 15:30 ECOS closes`.
- Android/build lineage: `index-alert-build` @ `d8f61cf2712eb91651b0ce25810aef0209697e00`. Commit: `Name APK artifacts for v4.4`.

These SHAs are audit anchors, not permanent branch pins. Future work must re-read the actual branch heads before editing.

## 2. Frozen statistical / validation contract that must survive chat deletion

The Master Spec is the authority. The following items are specifically preserved here because they were repeatedly relied upon in earlier rooms:

- H5 is the Core development horizon.
- H10 is `REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE`; do not sweep H6-H9 or retune H10 from completed outcomes.
- H20 is out of the requested 5-10-session scope and is archived evidence only.
- anchored walk-forward uses train 504 / calibration 126 / test 126.
- H5/H10 use common fold endpoints/common OOS decision dates; purge and embargo equal the evaluated horizon.
- calibration is disjoint and must use only information/outcomes available before each test prediction.
- test/holdout outcomes must not choose thresholds, quantiles, TopK, costs or other policy parameters.
- frozen CPCV protocol: six contiguous groups; every two-group test combination; each remaining group once as calibration; remaining three train; 60 split/calibration cases; horizon-length label-overlap purge + embargo.
- CPCV is a secondary stability diagnostic, not forward OOS, sealed holdout evidence or a standalone promotion gate.
- repeated test rows in CPCV are not independent observations.
- sealed holdout is one-shot and must not be burned until data/execution blockers, code and protocol are frozen; it cannot tune the same model.
- prospective Shadow S1 and frozen Fresh Confirmation S2 remain mandatory after holdout.
- original decision-time Top3 is frozen; held/unfillable/vetoed slots remain empty; rank-4+ backfill is forbidden.
- 0..3 trades and NO_TRADE are valid outputs.
- corporate-action-safe KRX base-price return axis and PIT/availability lineage are mandatory.
- required economic evidence includes executable cost-adjusted NetReturn/NetEV, PF, date-cluster uncertainty, MDD, ES95/ES99, coverage/abstention, cost stress, execution/capacity realism and tail dependence. Precision@Selected is secondary.
- current fixed-participation square-root-impact estimate is a cost proxy, not empirical capacity-aware NetEV.
- official security/status, exact halt/delisting economics, partial fills, fill time/price, post-fill markout, latency/expiry and empirical capacity are hard promotion blockers.
- never relax q25, TopK, cost assumptions, recent-evidence standards or execution assumptions merely to manufacture trades.

## 3. Current research state that must survive chat deletion

### 3.1 H5 / developmental candidate

Current price/volume/context research is not live-promotable. The strongest selection-conditioned developmental candidate showed positive average historical economics but a negative cluster lower bound, material best-day dependence and no admissions in the most recent 504 OOS sessions. The Ledger remains the numeric authority.

### 3.2 Selection-conditioned promotion audit

Preserved from the current Ledger:

- classification: `DEVELOPMENTAL_NOT_CURRENTLY_PROMOTABLE` / developmental-only.
- approximately 278 trades in the strongest all-context selection-conditioned result.
- mean NetReturn about +1.15%, PF about 1.55.
- cluster 95% lower bound remains below zero.
- removing the best five decision dates turns mean economics negative and PF below 1.
- latest 504 OOS test sessions contain no admissions.

Do not retune against this weakness or against sealed/future holdout evidence.

### 3.3 Uncertainty / policy calibration

Current Ledger state at the handoff:

- `EXP-2026-09-29-UNCERTAINTY-AUDIT-01`: `RUNNING`.
- purpose: audit realised economics of q25-blocked rows without changing model/policy.
- if blocked rows are weak/jackpot-dependent, keep abstention and seek orthogonal information; if they have positive economics but wide conditional tails, a conditional q25 estimator may be tested at the same 25th-percentile target.
- `EXP-2026-09-29-POLICY-CAL-01`: `PREREGISTERED, NOT YET READ`.
- policy-cal challenger may align the calibration population with the same post-Top3 normal-market veto, but it is not a q25 relaxation and cannot promote from development evidence.

### 3.4 KRX status / investor-flow blockers

- The official-security-status adapter is fail-closed and only makes already-fetched official tables structurally usable.
- A current snapshot is not historical PIT identity/status lineage back to 2015.
- official common-stock/security-status, trading halt, cleanup/delisting status/economics remain open Final Judge blockers until real historical raw data + availability lineage are validated.
- KRX investor-flow requires an official reproducible historical source and `event_time/published_at/available_at/ingested_at` lineage before any performance interpretation.
- authentication/source-probe success is not feature-promotion evidence.

## 4. CPCV discrepancy registry — important

### 4.1 Superseded status text

`INDEXALERT_RESEARCH_STATUS.md` currently contains an H10 purged-CPCV section describing a provisional **15-combination** protocol and its historical numeric outcome.

That section is **HISTORICAL / SUPERSEDED FOR CURRENT VALIDATION**.

The Master Spec and Ledger later froze the corrected **60-case** CPCV protocol. Therefore no future agent/developer may treat the 15-combination H10 CPCV result as the current frozen CPCV validation result.

### 4.2 Memory/OOM implementation incident

Earlier 60-case H5/H10 CPCV Actions failed with H5 exit 137 and H10 exit 143. The diagnosed engineering issue was memory/process termination while accumulating many prediction DataFrames, not a reason to alter the statistical protocol. The implementation was changed to process a split at a time (generate -> evaluate -> release), preserving the frozen statistical contract.

### 4.3 Current authoritative run

At this continuity audit, GitHub Actions run `36637351334` (`IndexAlert Research v1 Short-Swing Purged CPCV`, head SHA `b1ae66a39fdb01ff852cd4758b1befb85e978943`) is still `in_progress`. H5 and H10 jobs passed checkout/setup/dependencies/unit tests/cache preparation and are in the CPCV calculation step; artifact upload is pending.

Final current 60-case CPCV numbers must be read from a completed reproducible Action artifact. Do not infer success/failure from runtime duration alone.

### 4.4 Quarantined legacy-chat numeric recollections

Older chat summaries contained conflicting recollections of a completed 60-case CPCV result. One recollection reported roughly H5 median PF 0.381 / unique percentile 0.225 and H10 median PF 0.454 / unique percentile 0.333, with very high turnover and hard-anchor collapse; another recollection mentioned an H10 PF near 0.745.

Because these recollections conflict and were not matched to a currently verified Action artifact during this audit, they are preserved here **only as `LEGACY_CHAT_UNVERIFIED_CONFLICT`**. They must never be used for scientific, promotion or implementation decisions. The reproducible completed Action artifact is the only authority for final 60-case values.

## 5. Realtime / server / Android continuity

The older chats mixed research, server and Android work. Those operational tracks are preserved separately from statistical promotion evidence.

### 5.1 GitHub-verified branch lineage

- `index-alert-v41-research` has continued probability/realtime research through 2026-09-27; its current head is newer than several older handoff notes.
- `index-alert-server` has continued runtime/server work through 2026-09-28, including market display/history updates.
- `index-alert-build` has continued Android build work through 2026-09-28 and names v4.4 APK artifacts.

Future continuity work must inspect these branch heads rather than relying on old room summaries.

### 5.2 Legacy chat operational evidence preserved for deletion safety

The following was established in earlier operational chats but is not scientific promotion evidence:

- an IndexAlert Android APK was installed on a Galaxy S25-class handset during the operator-shell/FCM track;
- client FCM token acquisition/copy worked;
- server token registration was reported successful;
- a server-side test push reached Firebase HTTP v1 successfully;
- handset-visible notification delivery was not consistently preserved as a separately verified final checkpoint in the old handoff material.

Treat these as `LEGACY_CHAT_EVIDENCE`. Re-test against the current build/server heads before declaring present-day end-to-end notification health.

Older chats also contained broad statements that v4.4 server/Android integration was largely mature. Those statements are preserved as historical context only; current code, CI and live smoke tests must decide present status.

## 6. Older implementation-order note

A prior room carried an implementation sequence resembling:

`DB migration 001+ -> isolated KOSPI server skeleton -> exact FastAPI/Python schema -> Firebase payload -> Kotlin data class`.

This is preserved as `LEGACY_CHAT_PLANNING_CONTEXT`, not a frozen current requirement. Branches have moved materially since that note. Before applying it, compare it with current `index-alert-server`, `index-alert-build` and Master Spec blockers.

## 7. Explicit unfinished-work registry at handoff

Do not restart completed work. Continue from the first unresolved item supported by the latest GitHub state:

1. finish/read the current 60-case H5/H10 CPCV Action and archive authoritative artifacts/results; reconcile `RESEARCH_STATUS` historical 15-case wording after the final result is known;
2. finish/read `UNCERTAINTY-AUDIT-01` without policy/model retuning;
3. only then read/run the preregistered `POLICY-CAL-01` according to its gate;
4. obtain/validate real official KRX historical security/status raw data and PIT availability lineage; exact halt/cleanup/delisting economics remain blockers;
5. establish official reproducible KRX investor-flow historical access/lineage before performance testing;
6. continue execution realism: empirical fill ratio/time/price, partial fills, post-fill markout, latency/expiry, capacity;
7. do not burn sealed holdout until blockers/code/protocol are frozen; then prospective Shadow S1 and frozen Fresh Confirmation S2;
8. separately re-verify current server + Android + FCM end-to-end health on the latest branch heads before calling the operational app complete.

## 8. Continuation rule for this project

For future IndexAlert work:

- start by re-reading current `INDEXALERT_MASTER_SPEC.md`, `INDEXALERT_RESEARCH_LEDGER.md`, this continuity snapshot and the relevant branch HEAD/Actions;
- skip experiments already completed/rejected;
- never revive a rejected candidate by threshold/cost/horizon mining;
- if old chat text conflicts with GitHub, current reproducible GitHub evidence wins;
- when a new material result is produced, commit it to the Ledger/Status/this snapshot as appropriate so chat history is never required for continuity again.

## 9. Old-chat deletion gate

This snapshot intentionally preserves the material items that were found only or partly in older chats, including the CPCV memory incident, quarantined conflicting CPCV recollections, Android/FCM device-test history and the older server/build implementation-order note.

After this file is committed and re-read successfully from GitHub, older IndexAlert chats are no longer required as a project-state dependency. Their deletion must not be treated as deletion of GitHub code, Actions artifacts or the Master Spec/Ledger.
