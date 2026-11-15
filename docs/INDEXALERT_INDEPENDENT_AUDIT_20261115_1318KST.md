# IndexAlert independent audit — 2026-11-15 13:18 KST

## Scope and read-only evidence
Rechecked GitHub PR discovery, #414 integration gate at PR head 18c5418d9684d1717df58261ea27f28e514385b2 (blob content fetched), offline Actions 38381997417, 38382214223, 38419111311, 38419439742, 38419649711, 38486028854 and Railway IndexAlert production. Prior audit at commit 347e120d3709796634e814302b2423f49107feea used as baseline, not substituted for fresh evidence. No changes to specialist code or workflow.

## GitHub decisions
- PR #413 offline 38381997417 6/6 PASS, 38382214223 6/6 PASS, 38419111311 6/6 PASS. OpenDART 38419439742 2/2 PASS (software/row candidate only). PR #418 38419649711 1/1 PASS; integrated 38486028854 job 115599778959 FAIL at archived source identity check, downstream tamper/parity suites SKIPPED. Expected research_v1_runtime_manifest.py Git blob SHA-1 108f66714602a1bd3ae42c34dcca7c16e38f460b versus previously observed e428789e2e97ca7be3a4482e0df23b483a1ad69d. Do not repin or bypass.
- Historic 34-case outcome SHA256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 remains CI-reported; independent fresh recomputation NOT VERIFIED. Previously measured single runner 2.9656s serial / 2.6209s concurrent = 1.1315x regression-phase only; whole CI / official backtest speed NOT VERIFIED.
- Research index-alert-research-v1 and development index-alert-position-regen-fix-v1 exact current HEAD NOT VERIFIED in this pass; prior observed df474df348f22aa38b1dedaa59fcff66e548b406 and 1e6367d2863a86c3470da13d81a955d277eba485 are historical references, not current confirmations. PR #412/#413/#414/#418/#420/#422/#423 exact current heads and Draft flags not independently refreshed this pass. Last audit records #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f, #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0, #414 18c5418d9684d1717df58261ea27f28e514385b2, #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee, #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581, #422 c14857620973531013799e44625d43080904fd5f, #423 0e38004363cac9fc4475556b3a1c445de9af407f.

## Railway production verified
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, production 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS 1/1; Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS 1/1; KRX historical 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS but 0/1 running; Kiwoom real-readonly-run 0/1. Backend and push offline; db-query-readonly offline, 1 critical.
- Environment staged patch e113dacb-6705-4416-9997-dc694539d382 pending since 2026-10-29T06:20:53Z; no commit/deploy.
- Runtime logs window 2026-11-15 03:15–04:20 UTC: Investing USD/KRW HTTP errors, Yahoo fallback at 04:15:43Z; PIT and KRX each zero deploy log entries in same window. Market quote fallback is not source PIT approval.

## Independent admission
- Historical KRX 2017–2022 1565/1565 weekday original pairs: historical storage integrity PASS only (previous SHA evidence); official calendar/stock status/corporate actions/fills/taxes and 90 source gaps, 12003 zero-activity records NOT VERIFIED, fail-closed.
- OpenDART original/correction SGML candidate rows: row/signature comparison PASS limited to prior run; 2021/2022 first-filed consolidated 3-month operating profit exact period, correction lineage, public available-at/PIT, historical issuer-security mapping NOT VERIFIED.
- Frozen H5/consumed holdout not reusable. M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE and costs/tax thresholds unchanged. M20 performance authorization NO-GO.
- Post-cost/tax annual risk-adjusted NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness NOT VERIFIED; no economic run.
- Cache only with independently approved source/data/code/Frozen/runtime/evidence SHA256 all matched, fail-closed. Only independent read-only postprocessing parallelizable; retraining/capital transitions serial. ORDERING=false.

## Next safe steps
PR #418 owner: compare original expected vs observed Git blob content and lineage, do not change workflow or repin without independent proof. OpenDART owner: original first-filed Q3 CFS period/correction/publication chronology evidence for both years. KRX owner: official calendar and issuer tradability/fill/cost/tax proofs. Recompute 34-case SHA independently when safe. No deployment, merge, orders, funds, permission or Champion changes.
