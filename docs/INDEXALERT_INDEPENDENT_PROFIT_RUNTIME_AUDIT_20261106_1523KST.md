# IndexAlert independent profitability and offline runtime audit — 2026-11-06 15:23 KST

Read-only source inspection and isolated documentation only. This document does not approve PIT, M20 performance, trading, promotion, deployment or merges. No workflow modifications.

## GitHub source snapshot
- Research branch index-alert-research-v1: present; exact current HEAD NOT VERIFIED this run. PR #414 base SHA 3b8b7830612a6284d7c7a60628cb741627a is a PR snapshot, NOT asserted current branch HEAD. This audit branch was based on that immutable SHA.
- Development branch index-alert-position-regen-fix-v1: present; exact current HEAD NOT VERIFIED this run. Prior evidence SHA 1e6367d2863a86c3470da13d81a955d277eba485.
- PR #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f. All directly observed OPEN/Draft/unmerged.
- PR #414 gate docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md fetched from PR branch, NOT research base. Historical blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be (not re-read as SHA in this run).

## Actual Actions jobs inspected
- https://github.com/kims34/openpilot-opkr/actions/runs/38381997417 : 6/6 success.
- https://github.com/kims34/openpilot-opkr/actions/runs/38382214223 : 6/6 success.
- https://github.com/kims34/openpilot-opkr/actions/runs/38419111311 : 6/6 success.
- https://github.com/kims34/openpilot-opkr/actions/runs/38419649711 : 1/1 success.
- https://github.com/kims34/openpilot-opkr/actions/runs/38419439742 : 2/2 success.
- https://github.com/kims34/openpilot-opkr/actions/runs/41515392296 : auto-anchor FAILURE, validation SKIPPED. This is an observed unresolved blocker.
- 34-case fixed fingerprint SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and 13 adversarial / 28 synthetic assertions are PRIOR evidence, not freshly independently recalculated.
- Serial 2.9656s versus parallel 2.6209s = 1.1315x regression-phase only (prior measurement). Full CI and official PIT backtest speed NOT VERIFIED.

## Railway production snapshot and logs
- Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; production environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, replicas 1 running; KRX historical worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, 0 running (cron); runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, 1 running.
- Since 2026-11-06 05:00 UTC, PIT and KRX worker deploy log streams returned 0 rows. Cannot establish resolution of historical 27/803 nonpositive OHLC cases or 90 uncertain days.
- Runtime deploy log stream has current 06:23 UTC index monitoring messages; USD/KRW Investing failure with Yahoo fallback. These are NOT historical PIT or tradability evidence.
- Backend, push, db-query-readonly offline; db-query-readonly 1 critical. Kiwoom real readonly reports online but replicas 0 running/1 crashed. Existing staged patch e113dacb-6705-4416-9997-dc694539d382 retained unchanged.

## Strict admission table
| Gate | Status | Reason |
|---|---|---|
| Prior private 1565/1565 weekday original pairs | PASS, historical storage-only | Prior attestation; private bytes not independently rehashed this run |
| OpenDART original/correction SGML row candidate test | PASS, offline candidate matching only | 15 candidate row signatures; account semantics/period/public timestamp NOT VERIFIED |
| 2021 and 2022 original 3-month consolidated operating profit, corrections and public available-at | NOT VERIFIED | Exact first-original CFS semantics, period and disclosure time unproven |
| Historical issuer/security mapping | NOT VERIFIED | Complete as-of identity mapping absent |
| Official KRX calendar, security status, corporate actions, fills, fees and tax | NOT VERIFIED | Private stored bytes do not prove tradability |
| Frozen H5 and consumed Holdout | FAIL for promotion | Previously observed date concentration/negative robustness; no reuse or retuning |
| M20 PIT/NetEV/PF/CAGR/MDD/ES95/99/tax-adjusted risk-adjusted annual returns | NOT VERIFIED, NO-GO | No authorized source PIT or economic run |
| Offline-only optimization CI | PASS for selected regression jobs only | No evidence of official backtest speedup |
| Chronology anchor | FAIL | Action 41515392296 auto-anchor failure; validation skipped |

## Safe next steps
1. DART and KRX owners independently provide original-filing publication timestamp, CFS 3-month period lineage, official KRX state/tradability and issuer mappings with exact immutable SHA/CI proof. Do not replace missing original data with corrected vintages.
2. Independently diagnose chronology anchor failure without changing blocked workflow via an alternate channel.
3. Optimization only: fail-closed cache requiring independently approved source/data/code/Frozen/runtime/approval evidence SHA-256; parallelize read-only independent postprocessing, never dependent training or capital transitions. Preserve serial baseline and exact fingerprints.
4. Frozen H5; M20 horizon20/purge20, WF504/126/126, CPCV/independent Holdout/Champion/Top3/NO_TRADE unchanged. ORDERING=false; no M20 economics, model search, real trades, credentials, deployment, PR merges or Champion promotion.
