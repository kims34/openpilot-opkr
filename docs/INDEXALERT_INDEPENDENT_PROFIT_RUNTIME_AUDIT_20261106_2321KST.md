# IndexAlert independent profitability and offline runtime audit — 2026-11-06 23:21 KST

Scope: read-only verification of GitHub PRs, existing Actions and Railway production; this document is evidence only, not authorization. No official economic run, deployment, merge, workflow change, order, account or credential operation.

## GitHub evidence (queried this run)
- Research branch `index-alert-research-v1` and development branch `index-alert-position-regen-fix-v1`: existence confirmed by branch search. Exact current branch HEAD **NOT VERIFIED** (branch search exposes names, not HEAD); historical reference commits `df474df348f22aa38b1dedaa59fcff66e548b406` and `1e6367d2863a86c3470da13d81a955d277eba485` are NOT represented as fresh HEAD.
- PR #412 OPEN/Draft HEAD `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 OPEN/Draft HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 OPEN/Draft HEAD `18c5418d9684d1717df58261ea27f28e514385b2`; #418 OPEN/Draft HEAD `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX #420 OPEN/Draft HEAD `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 OPEN/Draft HEAD `c14857620973531013799e44625d43080904fd5f`; #423 OPEN/Draft HEAD `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 integration gate document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` at PR HEAD blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. This was fetched directly at PR HEAD; research branch lookup returned 404, not a negative existence conclusion.
- GitHub Actions [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311): each 6/6 jobs SUCCESS. [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): 1/1 SUCCESS. [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): 2/2 SUCCESS. These are software/source-check CI outcomes, not PIT or financial-profit PASS.
- [Chronology Anchor 41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296): auto-anchor FAILURE, validation SKIPPED. FAIL for that workflow, chronology admission NOT VERIFIED.
- Prior offline regression identity SHA256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 34 fixed cases, 13 adversarial mocks and 28 additional synthetic cases remain *historical* claims; the job conclusions were freshly checked but raw artifacts and digest were not rehashed this run. Serial 2.9656 s / simultaneous 2.6209 s = 1.1315x regression-phase only, not whole CI or approved official backtest acceleration.

## Railway production evidence (read-only)
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild service `225f2279-d728-4e1a-a3f3-2447ff0f9dc1`, SUCCESS deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, running 1/1. Actual deploy logs at 2026-11-06 21:01 through 23:16 KST (12:01–14:16 UTC) repeatedly show `KRXProspectiveOpenAPISourceError` / `COMMON_OHLC_NONPOSITIVE`: 803 common-stock rows, 27 nonpositive OHLC, 27 zero-volume/value rows, all-zero OHLC 0. Data quality **FAIL**; admission `fresh_alpha_observation_admitted=false`, `live_order_authorized=false`, `funds_movement_authorized=false`: fail-closed safety **PASS**.
- KRX historical worker `003812ee-102b-42b6-bda4-36925885b428`, SUCCESS deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, running 0/1, no new deploy logs in queried period. Historical private 1565/1565 weekday pairs is storage-integrity PASS from previous evidence, NOT official market-state/feasibility approval.
- Runtime `37902fde-ca05-43e0-bc76-278992bf7732` SUCCESS, running 1/1; latest 23:21 KST logs show Investing.com USDKRW HTTPError then Yahoo fallback. Not a PIT gate.
- Backend and Push offline; db-query-readonly offline with 1 critical issue. Kiwoom real-readonly service reported online yet replica running 0/crashed 1; do not equate service label with health.
- Pending staged patch `e113dacb-6705-4416-9997-dc694539d382` since 2026-10-29 remains staged, untouched.

## Independent gate decisions
| Gate | Decision |
|---|---|
| Official OpenDART original ZIP / candidate SGML extraction | historical artifact acquisition/CI PASS only; original-filing semantic identity and exact public available-at/PIT NOT VERIFIED |
| 2021/2022 original 3-month consolidated operating income period, correction lineage | NOT VERIFIED |
| Historical corp/security mapping, delistings, actions, KRX official trading calendar and status, fill feasibility | NOT VERIFIED |
| Prospective KRX OHLC quality | FAIL; fail-closed safety PASS |
| Frozen H5 / independent holdout and dynamic reuse | NO-GO, do not reuse spent holdout |
| M20 horizon20/purge20, WF504/126/126 source admission | NO-GO; no profitability run |
| NetEV, PF, CAGR, MDD, ES95/99, after-cost/after-tax risk-adjusted annual net return, concentration, time robustness | NOT VERIFIED, no official performance run |
| PR #413/#418 offline CI | CI PASS only; actual whole-CI and approved official backtest acceleration NOT VERIFIED |
| Live execution, Champion promotion | NOT AUTHORIZED; ORDERING=false policy unchanged (runtime environment variable not independently read) |

## Next evidence steps, without policy drift
1. OpenDART owner to prove original filing and available-at, exact 2021/2022 first 3-month consolidated operating-income lineage from independent original bytes; do not backfill with corrected editions.
2. KRX owner to compare 27 OHLC anomalies and 90 uncertain sessions against official source and market states, corporate actions, historical identifiers, execution and costs; do not simply exclude failures to manufacture PASS.
3. Chronology owner to resolve failed anchor with original logs and rerun only independently authorized offline safety tests.
4. Optimization owner to rehash fixed regression evidence, test fail-closed cache identity and read-only postprocessing parity in isolated synthetic offline tests only; dependent training/capital transitions stay serial. Do not modify other Work-owned code or workflow.
5. Only after all independent PIT and market gates PASS may an explicitly approved one-time frozen M20 economics evaluation be considered. No current approval. No PR merge, deployment, funds movement, ordering, credential change or Champion promotion.
