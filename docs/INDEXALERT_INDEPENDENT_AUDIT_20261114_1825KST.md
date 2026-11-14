# IndexAlert independent audit — 2026-11-14 18:25 KST

Read-only evidence snapshot. No economic backtest, policy change, deployment, merge, or live ordering.

## Verified PR heads
- #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- #414 18c5418d9684d1717df58261ea27f28e514385b2
- #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581
- #422 c14857620973531013799e44625d43080904fd5f
- #423 0e38004363cac9fc4475556b3a1c445de9af407f
All above Draft and unmerged at query time. Research/development branch HEAD independently NOT VERIFIED in this run. PR #414 gate document blob SHA-1 984c933651f39f1ee9e26a1d7ac3893aaa5335be.

## CI
Actions 38381997417 and 38382214223 6/6 SUCCESS each; 38419111311 6/6 SUCCESS; OpenDART 38419439742 2/2 SUCCESS; PR #418 38419649711 1/1 SUCCESS. This verifies job status, not original filing meaning/PIT or independent 34-case SHA recomputation.
Action 38486028854 1/1 FAIL: SourceDriftError archived blob mismatch research_v1_runtime_manifest.py expected Git blob SHA-1 108f66714602a1bd3ae42c34dcca7c16e38f460b observed e428789e2e97ca7be3a4482e0df23b483a1ad69d. Do not change expected SHA or bypass gate without independent byte lineage. Serial 2.9656 s vs concurrent 2.6209 s is previously reported regression-phase only, whole-CI speedup NOT VERIFIED.

## Railway production
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a. Latest deploys PIT 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5, KRX 16c93d7c-7cd0-4d84-a327-298d2805376c, runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 all SUCCESS (historical deployments, not new). Health PIT and runtime 1/1 running; KRX and Kiwoom real-readonly-run 0/1 running; backend, push, db-query-readonly offline. Environment inventory staged=null but status pendingWork patch:e113dacb-6705-4416-9997-dc694539d382 (2026-10-29) remains; discrepancy unresolved.
2026-11-14 08:10–09:25 UTC: PIT 0 deploy log entries, KRX 0, runtime 251 returned (limit 250, possible truncation). At 09:24:42 UTC Investing USD/KRW HTTPError, Yahoo fallback. This does not prove market data integrity.

## Independent gate
Official original-filing semantic period/2021–2022 first-three-month consolidated operating profit amendment lineage, public available-at/PIT, historic issuer/security mapping, official KRX calendar/status/corporate actions/executability, transaction costs/taxes, NetEV/PF/CAGR/MDD/ES95/99/concentration/temporal robustness: NOT VERIFIED. Historical KRX weekday raw pair storage 1565/1565 PASS only as previously recorded, not tradeability. M20 economic RUN NO-GO. H5 holdout consumed; no post-hoc reuse. ORDERING=false. Frozen H5, M20 horizon20/purge20, WF504/126/126 and all original risk/approval criteria unchanged. Cache fail-closed on independently approved source/data/code/policy/runtime/evidence SHA-256; parallelize read-only postprocessing only. No new official performance experiments until source PIT approval.

## Next safe steps
1. Compare archived manifest bytes and provenance across #418 and immutable approved baseline, without changing expected hash.
2. Obtain official original-filing time/period/lineage and KRX market-state proof independently, then re-evaluate gates.
3. Reconcile Railway pendingWork vs staged=null in read-only mode.
4. Recalculate 34-case test SHA-256 in an isolated synthetic-only environment; benchmark whole CI only after safety gate, never infer economic speedup.
