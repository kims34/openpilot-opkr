# IndexAlert independent read-only audit — 2026-11-15 06:23 KST

Scope: independent profitability admission and isolated offline-only runner optimisation. This document is evidence, NOT approval, deployment, merge or market performance.

## Exact verified GitHub HEADs
- research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- PR #412 OpenDART: `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`
- PR #413 optimisation: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`
- PR #414 integration: `18c5418d9684d1717df58261ea27f28e514385b2`
- PR #418 isolated single runner: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`
- KRX PR #420: `fab3cbbd63a951a4e081f9e7f08c1391ca308581`
- KRX PR #422: `c14857620973531013799e44625d43080904fd5f`
- KRX PR #423: `0e38004363cac9fc4475556b3a1c445de9af407f`
All seven PRs observed Draft and unmerged.

## Actual Actions results (read-only REST)
- 38381997417 SUCCESS SHA 55e7fe2b3fe322e39f817914ff1ed5b589bbe0da
- 38382214223 SUCCESS SHA 05d73661bcc879fe0dd66ffcea5fe1f5ee6fbd56
- 38419111311 SUCCESS SHA b22e4f39517c2bc38e173e63e8fd52f29a535dad
- 38419439742 SUCCESS SHA 39af5b0043e122bc0e42935d8813759ff6c1a6e7
- 38419649711 SUCCESS SHA 8f363b8683d34a48754916b34810a5a8bb958896
- 38486028854 FAILURE SHA 8f9a473d7751afd85e39f24bfa956d3283f77347; job 115599778959 step 6 'Enforce original CI regression-source blob identities before any test' FAILED, subsequent tampering/parity tests SKIPPED.
- Historical 34-case digest supplied: `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`. Fresh independent reproduction NOT VERIFIED.
- Single-runner 2.9656s serial versus 2.6209s concurrent is historical regression-phase evidence only; whole CI or official backtest acceleration NOT VERIFIED.

## Railway production read-only
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, replicas 1/1.
- Runtime deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, replicas 1/1.
- KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS but replicas 0/1; real readonly runner also 0/1.
- Pending staged patch `e113dacb-6705-4416-9997-dc694539d382` since 2026-10-29, changes []: unresolved administrative state, do not commit or deploy.
- 2026-11-14 20:15–21:30 UTC PIT and KRX worker logs 0 entries; absence of logs is NOT evidence of successful audit.
- Runtime log 2026-11-14 21:23:42 UTC: Investing USD/KRW HTTPError, Yahoo fallback; not official PIT evidence.
- Service health also identifies offline backend/push and critical alert for db-query-readonly; not sufficient to infer new market-data correctness.

## Independent admission matrix
- Historical KRX private raw weekday-pair storage 1565/1565: historical storage-integrity PASS only, not freshly rehashed.
- DART original filing 2021/2022 first independent three-month consolidated operating profit, original/correction lineage, public available-at, corporate/security historical mapping: NOT VERIFIED; M20 source admission FAIL-CLOSED.
- Official KRX exchange session calendar, suspension/delisting, corporate actions, fillability, costs/tax: NOT VERIFIED; 90-day classification and 12003 zero-activity rows excluded.
- NetEV/PF/CAGR/MDD/ES95/ES99/concentration/year and date robustness after all costs/tax: NOT VERIFIED, no authorized economic run.
- H5 consumed/failed holdout: NO-GO; never independently reuse or post-hoc tune.
- PR #418 integrated source identity gate: FAIL; offline optimisation not promotion-ready.
- M20 profitability gate: NO-GO. Frozen H5, M20 horizon20/purge20, WF504/126/126, independent holdout, Champion/Top3/NO_TRADE and all risk/cost/tax policies unchanged; ORDERING=false.

## Next independently permissible steps
1. Reconcile #418 original source blob identities and archived 34-case SHA from original immutable bytes; synthetic-only checks and fail-closed parity, no workflow changes circumventing prior security rejection.
2. Obtain separately verified original DART period/consolidation/public timestamp lineage and official KRX session/security/fill/corporate-action proof from respective owners, without copying their active code.
3. Read-only diagnose PIT nonpositive OHLC and Railway staged patch discrepancy. Do not apply patch.
4. Only after all source and PIT gates PASS, seek distinct approval before any official M20 economic evaluation. Never place orders, transfer funds, alter credentials, promote Champion, deploy, auto-merge or merge #413/#414/#418.

No source PIT promotion, economic experiment, live trade, deployment, merge, workflow modification or external credential write performed in this run.
