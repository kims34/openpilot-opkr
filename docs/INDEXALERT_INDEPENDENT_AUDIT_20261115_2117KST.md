# IndexAlert independent read-only evidence audit — 2026-11-15 21:17 KST

Scope: source and software evidence only. No market-return experiment, deployment, merge, order, authority change, policy modification or champion promotion. This is NOT an approval.

## Exact GitHub refs (read-only observed this run)
- research index-alert-research-v1 HEAD: df474df348f22aa38b1dedaa59fcff66e548b406
- development index-alert-position-regen-fix-v1 HEAD: 1e6367d2863a86c3470da13d81a955d277eba485
- Draft, open, unmerged PR heads: #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f.
- PR #414 gate document blob Git SHA-1: 984c933651f39f1ee9e26a1d7ac3893aaa5335be (NOT SHA-256).

## Actions (jobs observed through GitHub API)
- 38381997417 6/6 PASS; 38382214223 6/6 PASS; 38419111311 6/6 PASS.
- OpenDART 38419439742 2/2 PASS (software/candidate row verification only; NOT first-filing semantics or PIT).
- single runner 38419649711 1/1 PASS (synthetic/offline only).
- integration 38486028854 0/1 PASS, 1/1 FAIL. Job 115599778959 log: SourceDriftError research_v1_runtime_manifest.py expected Git blob SHA-1 108f66714602a1bd3ae42c34dcca7c16e38f460b, observed e428789e2e97ca7be3a4482e0df23b483a1ad69d. Do not relax source pin. Historical 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 is supplied baseline, NOT independently recomputed this run. Overall CI and real official backtest acceleration NOT VERIFIED.

## Railway production (read-only)
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, replicas 1/1.
- KRX worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, running replicas 0/1; latest inspected window had zero deploy log entries.
- Runtime deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, replicas 1/1; Investing USD/KRW HTTPError, Yahoo fallback.
- backend/push/db-query-readonly offline; db-query-readonly critical 1; staged environment patch e113dacb-6705-4416-9997-dc694539d382 still pending since 2026-10-29 06:20:53 UTC.
- PIT deploy log window 2026-11-15 10:10–12:20 UTC: 9 repeated approximately 15-minute fail-closed reports (10:15 through 12:15), error COMMON_OHLC_NONPOSITIVE, 27/803 common-stock OHLC nonpositive, zero_volume_value_rows=27; fresh_alpha_observation_admitted=false, independent source/model/chronology admission=false, live_order_authorized=false, ordering=DISABLED. Source quality FAIL, safe veto PASS. Repeated records may refer to the same session and are not independent samples. Private receipt content and original SHA NOT independently obtained.

## Independent gate verdict
PASS: historical offline software CI listed above; current runtime rejects suspect OHLC without granting trading authority. Historical 1565/1565 weekday KRX pairs storage SHA integrity is previously reported PASS, not independently rehashed in this run.
FAIL: current prospective KRX OHLC source-quality gate; #418 immutable archived source-pin CI.
NOT VERIFIED: official DART original filing semantics, exact public available-at/PIT, 2021/2022 first three-month consolidated operating income period/correction lineage, historical corporation/security mapping, official KRX calendar/trading status/corporate actions/execution feasibility, full cost/tax, annual risk-adjusted net return, NetEV/PF/CAGR/MDD/ES95/99, concentration and temporal robustness, overall performance acceleration and independent 34-case SHA-256 rehash.
M20 economic run NO-GO. H5 consumed/failed holdout cannot be re-used; no post-hoc Dynamic rescue.

## Next independent evidence (no policy changes)
1. KRX owner: classify 27 nonpositive OHLC rows by official session/status and original raw receipts, with exact source hashes and independent time-bound authority; never silently exclude to pass.
2. DART owner: original-filing exact 2021/2022 Q3 3-month consolidated operating-profit period, correction lineage and public availability time with independent original SHA.
3. Optimization owner: diagnose archived manifest SHA mismatch without changing frozen reference or CI workflow; separately reproduce 34-case SHA-256, then compare only offline software runtimes.
4. Integrator: only after PIT and KRX source gates PASS, verify tax/fees/slippage/marketability and independently authorized frozen M20 run. Maintain H5 frozen, M20 horizon20/purge20, WF504/126/126, Top3/NO_TRADE, cache fail-closed SHA-256 binding, serial dependency and read-only postprocessing parallelism. ORDERING=false.
