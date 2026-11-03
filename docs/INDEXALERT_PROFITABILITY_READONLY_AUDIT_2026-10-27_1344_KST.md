# IndexAlert independent profitability / isolated runtime audit — 2026-10-27 13:44 KST

**Scope:** Read-only source and CI verification, with this one documentation-only commit on the existing Draft PR #414 isolation branch. No strategy replay, production deployment, workflow edit, market-data economic experiment, order, fund/permission change, Champion promotion or PR merge. Do not interpret this note as data or trade authorization.

## Exact checked GitHub refs

- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a` (branch REST API).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (branch REST API).
- PR #412 OpenDART: head `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`, Draft/unmerged.
- PR #413 isolated runtime: head `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`, Draft/unmerged.
- PR #414 integration: observed pre-write head `fb8b5d95c2511c37f843b8f722f8bc20580ab807`, Draft/unmerged.
- PR #418 single-runner: head `2f98401cc50a6c6a25808a98516efd5bf0c944ee`, Draft/unmerged.
- KRX PR #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`; all Draft/unmerged.

## Verified evidence and precise authority limits

1. [Latest listed read-only Watchdog run #40436115571](https://github.com/kims34/openpilot-opkr/actions/runs/40436115571), 2026-10-27 02:02 UTC: 1/1 job success; original job log shows 4+31=35 offline tests, `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Uploaded artifact ZIP digest reported by Actions: SHA-256 `3ea4af4d7f8dfe080b191901e6fcba21425d82cd24e57e48c8ef0eeb0d9ca7c5`. **PASS: offline policy controls only; NOT VERIFIED: official PIT, live ORDERING and investment results.** Actions recent-run listing contained no newer run at check time.
2. [Official OpenDART 2021 source run #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), official read-only job `121379096007`: original ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, initial index unambiguous, 1,728 tables, 13 operating-label table candidates, **0** same-table exact Q3-2021 period and **0** same-table 3-month matches. **PASS: original ZIP receipt/integrity; NOT VERIFIED: original 3-month consolidated operating profit, 2021/2022 comparison, first-publication available-at, correction lineage, historical issuer/security PIT.** Prior 2022 first/correction SGML receipts are only archive/candidate evidence; no financial semantics or timestamp admission.
3. [KRX PR #423 synthetic run #39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925), job `119612335677`: 32 offline tests PASS, including private snapshot drift and wrong 14-day set rejection. This job did **not** execute the private original-source comparison. The previously recorded 2017–2022 1,565/1,565 weekday-pair SHA storage check is historical **storage integrity PASS only**; official exchange calendar, session/security tradability, corporate actions, fills, tax/cost model and issuer mapping remain **NOT VERIFIED**. Keep 90 unresolved sessions and zero-activity quarantines blocked.
4. [Prospective chronology run #40360864884](https://github.com/kims34/openpilot-opkr/actions/runs/40360864884), job `121705590170`, **FAIL**: after retries, `https://indexalert-pit-rebuild-production.up.railway.app/anchor/latest` returned HTTP 404. Do not treat chronology anchor as available.
5. [Runtime #418 original one-runner run #38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711), job `115373285730`: 1/1 success, pinned 34-case digest SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` matches the existing immutable offline regression contract. Serial 2.9656 sec vs concurrent 2.6209 sec yields **1.1315x regression-phase only**. **PASS: isolated offline parity; NOT VERIFIED: complete CI wall-time and official PIT-admitted backtest acceleration.** Prior strict archive Git-blob SHA discrepancy remains unresolved, not silently reclassified as PASS.
6. Railway connector `list_projects` returned **"User input required but current turn is running in a non-interactive mode."** This is an access blocker, not proof of project absence or a deployment failure. No alternative access, credential or permission changes attempted. **NOT VERIFIED:** current production deployments, operational logs and actual runtime `ORDERING` environment variable. Required policy remains `ORDERING=false`.

## Admission ledger

| Gate | Status |
|---|---|
| Original DART archive bytes / selected official receipts | PASS for specifically verified receipts only |
| Original 2021/2022 three-month CFS operating profit, vintage/period/correction/public available-at | NOT VERIFIED |
| Historical issuer/security mapping and official KRX tradability/corporate actions/fillability | NOT VERIFIED |
| Transaction costs/tax/2x-cost stress grounded in approved executable market data | NOT VERIFIED |
| NetEV / PF / CAGR / MDD / ES95 / ES99 / profit concentration / date robustness | NOT VERIFIED — economic run forbidden |
| Offline safety/parity tests | PASS for cited job/SHA only |
| Prospective chronology anchor | FAIL — HTTP 404 |
| Railway current operational state / ordering | NOT VERIFIED — interactive access blocked |
| M20 profitability run / Independent Holdout / Champion / Tiny Live | **NO-GO** |

## Immutable protocol and next dependencies

Maintain Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT, Purged/CPCV, independent consumed Holdout boundary, Champion/Top3/NO_TRADE, fixed cost/tax and risk/upgrade rules. Cache requires independent source/data/code/Frozen/runtime/approval SHA-256 matching and fail-closed invalidation; only read-only independent post-processing may be parallelised. No dependent retraining or capital-transition parallelisation. Do not replay H5 or Dynamic on consumed holdout; do not run M20 economics until official source PIT and tradability are independently attested.

Next: OpenDART specialist proves exact first-edition 3-month CFS semantics and publication chronology; KRX specialist independently attests historical sessions, security state, corporate actions, fills and costs; authorised read-only Railway access is restored through the normal connection flow (not bypassed); runtime specialist resolves strict Git-blob archive mismatch and measures whole-CI wall time without touching real market returns. Then only reconsider whether the preregistered one-time M20 run is eligible. No live orders, funds, permission changes, deployment, PR merges or Champion changes were performed.
