# IndexAlert independent profitability/runtime audit — 2026-11-04 20:25 KST

Read-only evidence review. No PIT admission, model search, economic replay, workflow changes, merge, deployment, orders or permissions.

## GitHub evidence
- Research reference `index-alert-research-v1`: PR #414 base SHA `3b8b7830612a6284d7c7a60628cb527cb741627a` (base snapshot, **not independently verified as current branch HEAD**). Development `index-alert-position-regen-fix-v1`: KRX PR #420 base `1e6367d2863a86c3470da13d81a955d277eba485` (snapshot, **not independently verified as current branch HEAD**).
- Draft/open/unmerged PR HEADs fetched now: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- #414 gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` fetched at PR head branch, blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- Actions jobs fetched now: #38381997417 6/6 SUCCESS; #38382214223 6/6 SUCCESS; #38419111311 6/6 SUCCESS; #38419649711 1/1 SUCCESS; OpenDART #38419439742 2/2 SUCCESS; chronology #41515392296 anchor FAILURE, validation SKIPPED. Original 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, synthetic 28 and 13 adversarial mocks, and 2.9656/2.6209=1.1315 ratio are **prior attestations, not independently recalculated this run**.
- Optimisation PASS limited to historical synthetic CI job conclusions; actual end-to-end wall-time acceleration and production market backtest parity NOT VERIFIED. Serial dependent capital transition/retraining; only read-only independent postprocessing parallel; cache must fail closed on source/data/code/Frozen/runtime/approval evidence SHA-256 mismatch.

## Railway evidence (read-only, production)
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; KRX worker latest observed SUCCESS deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, 2026-10-12 13:07 UTC, commit `1e6367d2863a86c3470da13d81a955d277eba485`. 2026-11-04 18:00–20:26 KST worker deploy logs: 0 events (absence not source validation).
- PIT rebuild latest deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, SUCCESS. 2026-11-04 18:30–20:16 KST recurring `COMMON_OHLC_NONPOSITIVE` / `FAIL_CLOSED`; 803 common stock rows, 27 nonpositive OHLC, 27 zero volume/value, original source failure session 2026-09-28; source/model/chronology admission flags false, manifest SHA null, ordering DISABLED, real orders false, private rejected receipt saved. This is an active source-quality blocker, not a validated new session.
- Separate runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, market-quote and USD/KRW Yahoo fallback logs at 20:25 KST; not original filing PIT/official KRX historical execution evidence.

## Gate matrix
- KRX 2017–2022 private weekday raw-pair storage integrity 1565/1565: **PASS (historical evidence only)**; official calendar/90 uncertain dates, 12003 zero-activity classifications, corporate actions, trading state, execution and taxes: **NOT VERIFIED / FAIL-CLOSED**.
- OpenDART original SGML 15 candidate rows and adjacent numeric signatures: **PASS for candidate extraction only (historical evidence)**; 2021/2022 first 3-month consolidated operating-profit period semantics, amendment lineage, public available-at and original-filing PIT: **NOT VERIFIED / FAIL-CLOSED**.
- Historical entity/security mapping, costs and taxes, net EV/PF/CAGR/MDD/ES95/99/concentration/temporal robustness: **NOT VERIFIED**. M20 economics: **NOT EVALUABLE / NO-GO**. H5 holdout consumed and cannot be reused; Dynamic cannot be retrofitted.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, purged/CPCV, independent holdout, champion/Top3/NO_TRADE unchanged; ORDERING=false.

## Next safe steps
1. Independently reconcile original OpenDART filing time and Q3 consolidated first-3-month fact lineage against immutable original evidence; no derived returns.
2. Independently compare official KRX session calendar and exact private source-date sets, investigate 27 nonpositive rows and 90 uncertain sessions, and historical entity mapping without admission.
3. Recalculate fixed synthetic CI SHA/parity/wall time only in isolated offline environment after checking other Work-room ownership; no dependent parallelism or M20 run.
4. Keep all PRs draft; no merge, deploy, live order, permissions or Champion promotion. Any denied write must not be retried via workaround.
