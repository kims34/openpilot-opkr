# IndexAlert independent profitability / isolated optimisation audit — 2026-11-06 18:16 KST

Scope: read-only evidence verification. No economic backtest, model exploration, trading, deployment, merging, workflow edit, production variable change or Champion promotion. This document is independent of PR #413/#414/#418 and other active Work areas.

## Exact refs checked live
- research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All OPEN, Draft, unmerged at inspection.
- PR #414 gate file `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. This gate itself explicitly denies PIT/M20 approval.

## CI source verification
GitHub Actions run IDs and exact run HEADs (all completed):
- [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417): SUCCESS 6/6; HEAD `55e7fe2b3fe322e39f817914ff1ed5b589bbe0da`
- [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223): SUCCESS 6/6; HEAD `05d73661bcc879fe0dd66ffcea5fe1f5ee6fbd56`
- [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311): SUCCESS 6/6; HEAD `b22e4f39517c2bc38e173e63e8fd52f29a535dad`
- [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): SUCCESS 1/1; HEAD `8f363b8683d34a48754916b34810a5a8bb958896`
- [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): SUCCESS 2/2; HEAD `39af5b0043e122bc0e42935d8813759ff6c1a6e7`
- [41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296): FAILURE auto-anchor, validation SKIPPED; HEAD `f17283d9a5f0427c3d5b8a865d39455f92ee2f1d`.
CI job counts and conclusions independently retrieved. Historical 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic tests, 2.9656s vs 2.6209s / 1.1315x regression phase are inherited prior evidence, not independently recomputed this run. Full CI / actual official backtest acceleration NOT VERIFIED.

## Railway production read-only
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild SUCCESS `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, replica 1/1.
- KRX historical worker SUCCESS `16c93d7c-7cd0-4d84-a327-298d2805376c`, replica 0/1; has volume.
- Runtime SUCCESS `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`, replica 1/1. Logs around 2026-11-06 09:15 UTC: Investing.com USDKRW HTTPError, Yahoo fallback, premarket quotes. This is runtime availability evidence, NOT strategy PIT.
- Backend, Push, db-query-readonly offline; db-query-readonly Critical 1. Kiwoom real-readonly displayed online but replica running 0/crashed 1: status discrepancy.
- Environment status `pendingWork` contains `patch:e113dacb-6705-4416-9997-dc694539d382` STAGED since 2026-10-29 06:20:53Z, empty changes array. Do not deploy/apply; other environment detail endpoints have historically reported staged=null, unresolved view discrepancy.
- PIT and KRX service deploy logs queried since 2026-11-06 07:00 UTC: no entries. Existing OHLC anomaly resolution NOT VERIFIED.

## Gate decisions (source-grade)
- KRX 2017–2022 1565/1565 weekday raw-pair storage integrity: historical PASS (not independently recalculated today); official holiday/trading status, zero-activity 12003, corporate actions, security lifecycle and executable fills: NOT VERIFIED, fail-closed.
- OpenDART original/correction SGML 15 candidate rows / adjacent-number signature: historical software evidence PASS; original-filing meaning, public available-at, exact 2021/2022 first 3-month consolidated operating profit period/correction lineage: NOT VERIFIED, fail-closed.
- Historical corp/security mapping and PIT universe: NOT VERIFIED.
- Frozen H5 consumed holdout and Dynamic research: NO-GO for independent reuse. No tuning against used holdout.
- NetEV/PF/CAGR/MDD/ES95/99, after-cost/tax risk-adjusted annual return, concentration, temporal robustness: NOT VERIFIED (no authorised official economic run).
- M20 horizon20/purge20, WF504/126/126: RUN NOT APPROVED; NO-GO.
- PR #413/#418 offline-only isolated CI: job execution PASS; production-wide acceleration NOT VERIFIED.
- ORDERING=false remains mandated; actual live env value NOT independently read in this run.

## Next read-only evidence work
1. Inspect auto-anchor failed job log for precise chronology root cause and verify no valid subsequent anchor.
2. Independently map original OpenDART first-filing timestamp and period/lineage without accepting corrected backfills.
3. Reconcile KRX official trading calendar, security status and corporate actions against saved pairs; never promote zero-activity records.
4. Reconcile Railway staged status via read-only pending-work details; inspect OHLC worker evidence only when new logs exist.
5. Independently validate offline fixed-test SHA and runner timing using isolated synthetic artifacts; no strategy experiment until source PIT passes.

Frozen core, cost/tax/risk/promotion thresholds unchanged. Cache must fail closed unless all independently approved source/data/code/Frozen/runtime/evidence SHA-256 match. Parallelism restricted to independent read-only postprocessing. No writes beyond this isolated document.
