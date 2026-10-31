# IndexAlert independent profitability / isolated runtime audit — 2026-10-29 22:25 KST

**Scope and authority:** GitHub PR/HEAD/Actions and Railway production read-only evidence; non-admitting audit. No official market-return experiment, H5/Dynamic/Holdout replay, strategy exploration, model change, broker order, deployment, workflow edit, merge, permission change or capital transfer. This is an isolated documentation-only record; specialist code is untouched.

## Pinned source state (read this execution)

- Research `index-alert-research-v1` SHA `3b8b7830612a6284d7c7a60628cb527cb741627a` (PR #412/#413/#414 base); development `index-alert-position-regen-fix-v1` SHA `1e6367d2863a86c3470da13d81a955d277eba485` (PR #420 base).
- Open/Draft/unmerged PR HEADs: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 pre-write `5db7297ef442065c03259b2b3e4fe7d8fcda4c9e`; #416 `053de553646fc4765d2616544ca1e8d6bbdde35f`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 latest prior independent document commit `5db7297ef442065c03259b2b3e4fe7d8fcda4c9e` contains only `docs/INDEXALERT_PROFITABILITY_INDEPENDENT_GATE_20261029_2147KST_AUTOMATION11.md`. Reviewed that document and preceding 21:23 independent audit to avoid duplicating other Work changes. KRX specialist branch SHA `073d2d49...` is prior documented evidence, **not re-established as current branch HEAD here**.

## Official source, financial and KRX verdicts

- OpenDART [Actions #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) both offline/official jobs SUCCESS: original/corrected 2022 SGML 15 candidate operating-profit row/signature matches are **not** proof of exact first-filed 2022 and 2021 Q3 standalone three-month consolidated operating-income facts, sign/unit/period, correction lineage, issuer-security historical mapping or first public available-at. Original ZIP/correction ZIP historical SHA256 receipts `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` / `606be9d03928808f0a2a05f052444587bd2457bdef7a47a8f4bff3d2ea098a30` were **not independently rehashed from original bytes today**. **PIT/semantic NOT VERIFIED**.
- KRX original 2017–2022 1,565/1,565 weekday daily/master private stored pairs historically SHA-verified **PASS for storage integrity only**. Exact official calendar and 90 uncertain sessions, 2021 13/2022 14 candidate days, historic issuer/security, suspension/delist, corporate actions, fillability, fees/taxes remain **NOT VERIFIED**. [KRX synthetic Actions #39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) one offline job SUCCESS, no market admission. Private original corpus not rehashed this run.
- [Watchdog #40853112299](https://github.com/kims34/openpilot-opkr/actions/runs/40853112299), job `123377258416` SUCCESS: 4 watchdog + 31 research-governance tests; log `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This is synthetic/governance-only evidence. Prior chronology [#40726273259](https://github.com/kims34/openpilot-opkr/actions/runs/40726273259) anchor HTTP 404, validation skipped: independent chronology **NOT VERIFIED**.

## Isolated optimization (PR #413 / PR #418)

- [#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) #413 6/6 jobs SUCCESS; 34-case immutable software parity SHA256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` historical PASS. Offline test parity is not market-profit proof.
- [#39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395` **FAIL**: archived `research_v1_runtime_manifest.py` expected Git blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b` (#418) versus observed `e0055c66c59398fd4a1158077446d886b54c4e37` (#413 merge context). Re-fetched both file blobs this run, 103 versus 188 lines; #418 rejects only literal `True` on holdout/live-order flags while #413 requires explicit `False` and uses `O_NOFOLLOW`. **Security semantics not equivalent. Cache FAIL-CLOSED; do not simply repin SHA**.
- [#39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) limited 22-file candidate lineage PASS but transitive imports not fully pinned; not merge approval. [#39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) one-runner offline 34-case parity PASS, serial 2.3911s versus parallel 2.0755s (test phase 1.1521x), both-modes 4.4674s. Full CI and real official backtest acceleration **NOT VERIFIED**. Cache only if independently approved original/data/code/Frozen/runtime/authority SHA-256 all match; parallelize only read-only independent postprocessing, never dependent retraining or capital transitions.

## Railway production — new operational discrepancy requiring owner diagnosis

- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. `get_staged_changes` and `describe_service`: `staged=null`, no staged resources. However `environment_status` and `get_status` expose stale-looking `pendingWork` patch `e113dacb-6705-4416-9997-dc694539d382`, `changes=[]`; do not infer pending config write.
- **New independently confirmed twice:** `indexalert-kiwoom-real-readonly` deployment `a77fb922-b679-4d88-92c4-03054ec579cd` is labelled `SUCCESS` (2026-10-29 06:21:36 UTC), while `environment_status` simultaneously says `state=online`, `replicaStatus={running:0,crashed:1,total:1}` in two reads. `describe_service` shows `startCommand=python -B smoke.py`, `restartPolicyType=NEVER`; last-hour CPU and memory samples 61 each, all zero, and recent runtime logs empty. This is **operational health INCONSISTENT / NOT VERIFIED**, not proof of active broker connectivity, continuous running, or trading capability. An intentionally short-lived smoke process or stale health telemetry cannot be excluded without owner-side independent read-only diagnosis. **Do not restart or redeploy without separate explicit approval.**
- The service declares variable name `KIWOOM_ORDERING_ENABLED`, but OAuth `list_variables` redacts values; **cannot verify its value**. PIT service declares `ORDERING` and `REAL_ORDERS_AUTHORIZED` names, also redacted. Never infer account-wide order state from one service's logs.
- `indexalert-pit-rebuild` latest read-only log **2026-10-29 13:16:10 UTC / 22:16:10 KST**: `status=FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 803 common-stock rows, 27 nonpositive OHLC / 27 zero-volume-value; `session_manifest_sha256=null`, source/chronology/model admissions false, `ordering=DISABLED`, `live_order_authorized=false`, `real_orders_authorized=false`, funds/permission changes false. This verifies only the PIT service's runtime report.
- Latest KRX historical-worker and Kiwoom real-readonly current-window deploy logs empty. No independent fresh KRX source SHA or broker connection claim. No service changes performed.

## Final gate and safe next steps

| Gate | Decision |
|---|---|
| Offline synthetic parity and historical KRX stored-source integrity | **PASS, scope limited** |
| #418 archived source/merge semantic identity | **FAIL; FAIL-CLOSED cache** |
| 2022/2021 first-original 3-month CFS operating-profit, public available-at and correction PIT | **NOT VERIFIED** |
| Official KRX historical trading states, issuer mapping, corporate actions, fills, fee/tax evidence | **NOT VERIFIED** |
| Prospective OHLC input | **FAIL-CLOSED** |
| Kiwoom real-readonly sustained replica health / service-wide ordering flag | **NOT VERIFIED; contradictory health evidence** |
| M20 PIT admission and economic RUN | **NO-GO** |
| After-cost/tax NetEV, PF, CAGR, MDD, ES95/99, concentration and temporal robustness | **NOT EVALUABLE, not zero** |
| Full CI / official backtest speedup | **NOT VERIFIED** |

Next: source owners supply independently original-byte/PIT/CFS semantic lineage and official KRX dated status/corporate-action/fill/tax proofs; optimization owner reconciles pinned SHA **and** explicit-false security semantics/transitive dependencies without altering archived policy; Railway owner independently diagnoses 0/1 crashed smoke replica and confirms ordering configuration through an authorised read-only control, without restarting or exposing secrets. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV, independent Holdout, Champion/Top3/NO_TRADE and costs/taxes remain unchanged. No H5 consumed Holdout reuse, M20 performance run, orders, funding, credential changes, PR merges or deployment. Every privileged action requires separate explicit user approval.
