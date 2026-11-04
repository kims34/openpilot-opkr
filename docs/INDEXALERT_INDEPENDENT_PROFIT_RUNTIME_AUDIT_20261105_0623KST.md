# IndexAlert independent profitability/runtime audit — 2026-11-05 06:23 KST

Scope: read-only independent evidence check. This document is not an original-filing approval, strategy change, market performance run, deployment authorization, or order authorization. Source evidence is separated from historical claims.

## Exact current refs (GitHub connector, 2026-11-05 06:23 KST)
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Draft OPEN/unmerged: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft OPEN/unmerged: #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- #414 gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.

## CI verification
- Actions [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311): each 6/6 jobs success (individual job conclusions independently read).
- [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): 1/1 job success; [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): 2/2 success.
- [41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296): auto-anchor FAIL, validation SKIPPED; not a PIT approval.
- Previously reported fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic tests, serial 2.9656 s vs suite 2.6209 s (1.1315x regression-phase): historical claims, NOT independently recomputed in this run. Whole CI/official backtest acceleration NOT VERIFIED.

## Railway live read-only check
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild: SUCCESS deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, 1 running replica. KRX worker: SUCCESS `16c93d7c-7cd0-4d84-a327-298d2805376c`, 0 running replicas (scheduled/idle state not independently classified). No deploy logs for either service in 2026-11-05 05:15–06:30 KST query window; absence is not a PASS.
- Runtime: SUCCESS `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`, 1 running; live FX/index lookups and Yahoo fallback through 06:24 KST. These are not approved historical PIT evidence.
- Kiwoom real-readonly: UI state online, replicas running 0/crashed 1. Push and backend offline with warnings; db-query-readonly offline with critical notification. These are pre-existing observations, not proof of a newly introduced failure.
- Existing environment patch `e113dacb-6705-4416-9997-dc694539d382` remains staged, untouched.

## Independent gate adjudication
- Historical KRX raw pair storage 1565/1565 weekday pairs: **historical storage-integrity PASS only**, not freshly recomputed; official trading calendar, status, corporate actions, historical entity/ticker mapping, executable liquidity, taxes and costs: **NOT VERIFIED / FAIL-CLOSED**. Zero-activity 12003 and 90-day classification remain excluded from tradability approval.
- OpenDART original vs correction SGML candidate rows 15: historical job SUCCESS; exact first public available-at/PIT, 2021/2022 first three months consolidated operating-profit semantics and period/correction lineage: **NOT VERIFIED / FAIL-CLOSED**.
- Frozen H5 and consumed holdout/dynamic reuse prohibited; M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE and risk/cost/tax criteria unchanged.
- NetEV/PF/CAGR/MDD/ES95/ES99, concentration, temporal robustness, risk-adjusted after-tax annual profit: **NOT VERIFIED / NOT EVALUABLE**; M20 economic RUN **NO-GO**.
- ORDERING=false; no live orders, capital transfer, credential change, promotion, deployment or merge.

## Next permitted work
1. Independently reconcile official original-filing timestamps, consolidated quarterly period semantics, and amendment lineage without promoting SGML candidate rows.
2. Independently prove official KRX calendar, trading status, corporate actions and historical mappings with immutable source hashes and public available-at evidence; keep zero-activity excluded.
3. Optimization isolation: only synthetic offline fail-closed cache identity (source/data/code/Frozen/runtime/approval SHA-256), read-only postprocessing parallelism and nonparallel dependent training/capital transition. No new market returns, M20 economic tests or model search before source approval.
4. Maintain separation from PR #413/#414/#418 and other workspaces; no workflow/security bypass. No changes beyond this audit note.
