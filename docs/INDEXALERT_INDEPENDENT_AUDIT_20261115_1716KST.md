# IndexAlert independent audit — 2026-11-15 17:16 KST

Read-only verification; no economic backtest, model search, merge, deployment, workflow modification, or trading action.

## Source identity and scope
- PR #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f. All open, draft, unmerged as observed.
- Branch names index-alert-research-v1 and index-alert-position-regen-fix-v1 exist; their *current commit HEADs* were not independently resolved this run: NOT VERIFIED.
- PR #414 gate document at its pinned PR HEAD: Git blob SHA-1 984c933651f39f1ee9e26a1d7ac3893aaa5335be. This is not SHA-256 and not a source approval.
- Actions [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417) 6/6 PASS; [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223) 6/6 PASS; [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) 6/6 PASS; [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 PASS; [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 PASS. Job conclusions only; archived 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 not independently recalculated: NOT VERIFIED.
- [38486028854](https://github.com/kims34/openpilot-opkr/actions/runs/38486028854) 1/1 FAIL, job 115599778959: research_v1_runtime_manifest.py expected Git blob SHA-1 108f66714602a1bd3ae42c34dcca7c16e38f460b, observed e428789e2e97ca7be3a4482e0df23b483a1ad69d. No mutation/repair attempted.

## Railway production (read-only)
- Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7. describe_environment returned **staged=null** on this check, unlike older reports of staged changes; verify through a second independent source before treating prior staged patch as resolved. No deployment performed.
- Latest deployment status PIT rebuild SUCCESS (8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5), KRX worker SUCCESS (16c93d7c-7cd0-4d84-a327-298d2805376c), runtime SUCCESS (eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00); these are deployment states, not proof of running replicas or PIT correctness.
- Deploy log window 2026-11-15 07:10–08:20 UTC: PIT 0 entries; KRX 0 entries; runtime 101 returned, including 08:16:44 UTC Investing USD/KRW HTTPError then Yahoo fallback. This is operational telemetry, not official historical pricing approval.

## Economic and optimisation gates
- Official original-filing / public available-at / exact 2021–22 first-three-month consolidated operating profit period and correction lineage: NOT VERIFIED.
- Historical corp/security identity; KRX exchange calendar, suspension/corporate actions, executable prices and costs/taxes: NOT VERIFIED. Historical private 1565/1565 pair-storage PASS is prior evidence only, not current independently replayed official calendar verification. 90 uncertain days and 12003 zero-activity rows remain blocked.
- NetEV, PF, CAGR, MDD, ES95/99, concentration and time robustness after trading costs and taxes: NOT VERIFIED; M20 PIT/economics NO-GO. Consumed H5 holdout and dynamic results not eligible for independent reuse.
- Offline synthetic software CI PASS for named jobs only. Regression-phase serial 2.9656s vs concurrent 2.6209s (reported 1.1315x), not independently rebenchmarked; full CI and official market backtest acceleration NOT VERIFIED.
- Frozen H5/M20 horizon20 purge20 WF504/126/126, PIT/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE unchanged. Cache fail-closed on all approved source/data/code/policy/runtime/evidence SHA-256. Only independent read-only post-processing parallel; no dependent training/capital transitions. ORDERING=false, no live order, capital transfer, account/auth change, champion promotion, PR merge or production deployment.

## Next safe steps
1. Resolve actual research/development branch HEAD and archived 34-case SHA-256 via immutable evidence.
2. Diagnose PR #418 manifest SHA mismatch strictly in an independent offline-only area, without editing a workflow or other owners' code.
3. Independently establish official OpenDART first-filed publication timestamps/lineage and KRX status/calendar/corporate actions before any M20 economic run.
4. Cross-check Railway staged=null and runtime service health independently; do not treat a successful deployment as PIT admission.
