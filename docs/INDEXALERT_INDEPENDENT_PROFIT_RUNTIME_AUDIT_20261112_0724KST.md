# IndexAlert independent audit — 2026-11-12 07:24 KST

Read-only independent review. No strategy, trading, deploy, merge, workflow or economic test changes.

## Current evidence
- PR #412 head bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f. All OPEN/DRAFT at this read.
- Prior known research HEAD df474df348f22aa38b1dedaa59fcff66e548b406 and development HEAD 1e6367d2863a86c3470da13d81a955d277eba485: **NOT VERIFIED fresh branch HEAD** in this run (no branch-ref API used); do not assert unchanged.
- #414 gate blob 984c933651f39f1ee9e26a1d7ac3893aaa5335be fetched from #414 head. Frozen M20/NO-GO confirmed in document.
- GitHub Actions job endpoints: 38381997417 6/6 success; 38382214223 6/6 success; 38419111311 6/6 success; 38419649711 1/1 success; 38419439742 2/2 success. Existing 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 NOT VERIFIED independently (no artifact recomputation). Synthetic 28 and adversarial 13 claims limited to earlier evidence. Regression-phase 2.9656s serial vs 2.6209s concurrent => 1.1315x earlier reported, NOT VERIFIED current end-to-end speed.
- Railway IndexAlert production project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7. PIT rebuild and Runtime running 1/1; KRX historical worker running 0/1; Kiwoom real readonly service UI online but replica running 0/1, crashed 1/1 (**FAIL**). Backend, Push, db-query-readonly offline; db-query-readonly 1 critical.
- Railway 2026-11-11 21:00–22:30 UTC logs: PIT 0, KRX 0, Kiwoom 0; Runtime 101 returned entries, including USD/KRW Investing HTTP errors and Yahoo fallback at 22:24:45 UTC. Zero log lines are not evidence of healthy processing.
- Railway describe_environment staged=null, environment_status pendingWork lists patch e113dacb-6705-4416-9997-dc694539d382, changes=[]; **inconsistent read surfaces, NOT VERIFIED**. No patch applied.

## Independent gates
| Gate | Decision | Evidence/limitation |
|---|---|---|
| 2017–2022 KRX private 1565/1565 stored weekday pairs | PASS historical storage integrity only | Not official trading calendar, tradability or PIT |
| Official KRX session/status, corporate actions, fill feasibility, taxes/costs | NOT VERIFIED / fail closed | 90 uncertain days, 12003 zero-activity records remain excluded |
| Original filing public available-at/PIT; 2021/2022 consolidated 3-month operating profit period/correction lineage | NOT VERIFIED / fail closed | 15 SGML candidate rows and matching signatures do not prove semantics or timestamps |
| Historical corporation/security mapping, labels, Purged/CPCV, independent holdout | NOT VERIFIED | No independent source-approved evidence |
| NetEV/PF/CAGR/MDD/ES95/ES99, concentration, year/date robustness net of taxes/costs | NOT VERIFIED | M20 performance run forbidden |
| Offline CI of #413/#418 | PASS job status only | 34-case content hash not independently recomputed; no end-to-end acceleration approval |
| Runtime Kiwoom real readonly replica | FAIL | crashed 1/1; not permission for account changes |

## Frozen policy and next evidence
M20 NO-GO, ORDERING=false required (runtime value not independently read), Frozen H5 and M20 horizon20/purge20 WF504/126/126, Top3/NO_TRADE and holdout boundaries unchanged. Never reuse failed/consumed H5 holdout or Dynamic for independent proof. Only source owner can independently prove first-filed PIT/available-at and KRX tradability; after that independently approve cost/tax/fill source and the exact evidence SHA before considering a single frozen economic run. Cache fail-closed across source/data/code/policy/runtime/approval SHA-256; parallelize read-only independent postprocessing only. No deployment, merges, workflow writes, model search, performance tests, capital movement, ordering, account changes, or Champion promotion.
