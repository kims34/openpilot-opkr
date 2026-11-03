# IndexAlert independent read-only integration / optimisation evidence — 2026-10-21 16:25 KST

**Scope and safety:** Read-only GitHub/Railway inspection; isolated evidence note only. No official price/return replay, economic test, model search, holdout, deployment, workflow edits, merge, permission change, fund transfer or order. `ORDERING=false`; Frozen H5 / M20 horizon20-purge20 / WF504-126-126 / PIT / Purged-CPCV / Holdout / Champion / Top3 / NO_TRADE unchanged. This note does not approve any source or experiment.

## Exact observed GitHub references
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Draft #414 head `29354a2f51f7b44ea572eb75ce9c1a7420892562`, base research HEAD above; original integration gate blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Prior note and current note are audit documentation only.
- Draft #412 OpenDART head `4d5be1c2c585bf095985e93198ac6d403cd202ea`: offline viewer/TOC guards Actions [39516614743](https://github.com/kims34/openpilot-opkr/actions/runs/39516614743), [39516614751](https://github.com/kims34/openpilot-opkr/actions/runs/39516614751) PASS. Historical original-first-receipt Action [39516110459](https://github.com/kims34/openpilot-opkr/actions/runs/39516110459) FAIL, first receipt not visible in bounded historical listing. Offline guard PASS is **not** official first-available-at or first 3-month consolidated operating-income PIT approval.
- Draft #413 optimisation head `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`: [38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) 6/6 jobs PASS, 34 pinned testcase digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` PASS.
- Draft #418 single-runner head `2f98401cc50a6c6a25808a98516efd5bf0c944ee`, base branch `index-alert-backtest-runtime-opt-v1-20261013` (current base head #413 as above). [39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) one-runner offline PASS; [39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) archived source gate **FAIL**: `research_v1_runtime_manifest.py` expected Git blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. This is an intentional archived-vs-reviewed-candidate difference but it means archived exact-source replay did **not** pass. [39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) separate candidate-merge gate PASS, explicitly `candidate_approved_for_merge=false`, `all_transitive_imports_pinned=false`, 22 checked blobs, 22 Python package versions only, exact wheel/OS native hashes NOT VERIFIED. Neither workflow grants a merge.
- KRX Draft #420 head `fc00f30b83df58a825e0f6fe30084a311c7bb27b`: [39515549147](https://github.com/kims34/openpilot-opkr/actions/runs/39515549147), [39515549166](https://github.com/kims34/openpilot-opkr/actions/runs/39515549166) offline PASS.
- KRX Draft #422 head `c14857620973531013799e44625d43080904fd5f`: [39001836000](https://github.com/kims34/openpilot-opkr/actions/runs/39001836000) offline PASS.
- KRX Draft #423 head `b2afad2528c25bf4cfbf8f28ad993c9878f680bd`: [39516412754](https://github.com/kims34/openpilot-opkr/actions/runs/39516412754) offline synthetic candidate PASS; real official historical calendar/state/tradability comparison NOT VERIFIED.
- Read-only watchdog [39552738497](https://github.com/kims34/openpilot-opkr/actions/runs/39552738497) PASS 2026-10-21 06:00Z, says `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`.

## Railway read-only production evidence
- Project IndexAlert `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`: 10 services, 3 with issues, no pending staged work.
- `db-query-readonly`: offline, one critical notification, no active deployment/logs available. `indexalert-push` and `indexalert-backend` offline. `indexalert-kiwoom-real-readonly` UI state online but replica running=0, crashed=1 (total=1); do not infer healthy execution from deployment SUCCESS.
- `indexalert-krx-historical-worker` latest SUCCESS deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` (2026-10-12), tied to development SHA `1e6367d...`; no fresh deployment logs returned in this check. Prior 2017–2022 private 1565/1565 weekday source-pair storage integrity PASS is *not* historical tradability or PIT approval.
- `indexalert-pit-rebuild` log retrieval returned 154 entries, last timestamp `2026-10-20T14:46:40.957109646Z`; last entries `COMMON_OHLC_NONPOSITIVE`, `nonpositive_ohlc_rows=27`, `fresh_alpha_observation_admitted=false`, `independent_source_admission_verified=false`, `live_order_authorized=false`. Explicit recent-window (2026-10-20T14:47Z–2026-10-21T07:30Z) log read returned zero entries; *logging visibility NOT VERIFIED*, not proof service stopped. Do not release fail-closed veto.

## Gate assessment
| Gate | Result | Rationale |
|---|---|---|
| Offline fixed 34-case parity (#413, #418) | PASS within cited CI scope | Pinned digest identical |
| Archived #418 source identity | FAIL | Actual archived manifest blob mismatch |
| Reviewed #418 candidate 22-file lineage | PASS in limited candidate scope | Does not cover all transitive imports or authenticate data |
| Exact runtime binary/wheel/native environment | NOT VERIFIED | Version match != artifact hash proof |
| Fail-closed cache and read-only fan-out | PARTIAL synthetic PASS / deployment NOT VERIFIED | Caller-authenticated upstream cache key, full runtime/path trust and atomic multi-file snapshot not established; no market cache admitted |
| Real full CI / official backtest speedup | NOT VERIFIED | One-runner synthetic phase ratio not end-to-end improvement |
| OpenDART first original available-at / 2022 & 2021 standalone 3-month consolidated operating income / correction lineage / historical security mapping | NOT VERIFIED | First receipt historical listing failed; offline viewer tests do not prove PIT |
| Official KRX historical calendar / corporate actions / order fill feasibility | NOT VERIFIED | Offline holiday fixtures, private storage SHA are insufficient |
| Cost/tax-adjusted NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness | NOT VERIFIED / RUN PROHIBITED | Prerequisite original PIT and tradability not approved |
| M20 economic execution, Holdout reuse, Champion, live ordering, PR merges | NO-GO | Frozen gate and no-order policy |

**Next allowed work:** Read-only inspect original DART available-at evidence and independent official KRX historical tradability proof when source owners publish real SHA/CI/logs. In optimisation isolation, inspect pinned source closure / wheel-native hashes and read-only handoff root-path trust, synthetic-only, without editing other owners' code. No workflow modifications or policy relaxation. New evidence only; do not replay failed H5 Holdout or run M20.
