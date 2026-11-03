# IndexAlert independent profitability/runtime audit — 2026-11-03 11:16 KST

Read-only evidence audit, isolated document only. No PIT authorization, economic test, workflow edit, merge, deployment, order or permission change.

## GitHub immutable references
- Research `index-alert-research-v1`: previous verified HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`; branch existence rechecked this run, **HEAD not independently fetched**.
- Development `index-alert-position-regen-fix-v1`: previous verified HEAD `1e6367d2863a86c3470da13d81a955d277eba485`; branch existence rechecked this run, **HEAD not independently fetched**.
- Current Draft PR HEADs obtained from GitHub PR metadata: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `9ec3bc0959ba1b7b4505eb5c7db8798fe5bc2989`; #416 `053de553646fc4765d2616544ca1e8d6bbdde35f`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All listed PRs remain open draft.
- #414 integration gate document GitHub blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be` from previous audit; content re-read this run; latest blob SHA **not fetched**.
- GitHub Actions #38419111311: six of six jobs SUCCESS, #38419649711 one of one SUCCESS; #41515392296 auto-anchor FAILED and validation SKIPPED. These are job conclusion checks, not newly recomputed SHA-256 parity.
- Historical synthetic 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` remains reference, not independently recalculated this run. #418 archived manifest mismatch FAIL-CLOSED; no end-to-end acceleration proof.

## Railway production evidence
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Service inventory re-read.
- PIT rebuild service `225f2279-d728-4e1a-a3f3-2447ff0f9dc1`: four returned deploy entries 2026-11-02 14:01:18 through 14:46:22 UTC (23:01–23:46 KST) all `COMMON_OHLC_NONPOSITIVE`, 27/803 common-stock OHLC invalid, `session_manifest_sha256=null`, `FAIL_CLOSED`, `ordering=DISABLED`, `live_order_authorized=false`. No later deploy entries returned in queried interval; absence is not proof of service outage.
- Runtime service `37902fde-ca05-43e0-bc76-278992bf7732`: 50 HTTP records returned since 2026-11-02 14:00 UTC, none `/anchor/latest`; prior 20 HTTP 404 anchor records and Action #41515392296 are historical and not contradicted by this sample. Exact response body and private anchor state NOT VERIFIED.
- Railway deployment list rechecked: Kiwoom REAL read-only deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS, source commit `85bb6fd10bcc9ff2b14abe1c774f0d99f8eb84ab`; KRX worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, source commit `1e6367d2863a86c3470da13d81a955d277eba485`. Deployment SUCCESS is not PIT approval.

## Gate decisions
- Original-filing 2021/2022 consolidated standalone three-month operating profit, public available-at, correction lineage, issuer/security historical mapping: NOT VERIFIED, admission FAIL-CLOSED.
- KRX 1565/1565 weekday private raw pairs: historical storage-integrity PASS only; official session calendar, halts, corporate actions, executable prices, fees/taxes: NOT VERIFIED.
- PR #413 synthetic CI parity limited PASS, PR #418 synthetic runner CI limited PASS; archived manifest SHA mismatch FAIL-CLOSED. Production wall-time acceleration NOT VERIFIED.
- NetEV/PF/CAGR/MDD/ES95/ES99, concentration, time robustness after costs/taxes: NOT EVALUABLE, M20 NO-GO. No M20 economic run permitted.
- Frozen H5 and M20 horizon20/purge20, WF504/126/126, Purged/CPCV, independent holdout, Top3/NO_TRADE unchanged. Cache only with full independent SHA-256 evidence match; dependent retraining/capital transition serial. ORDERING=false.

Next independent gates: original first-filed exact Q3 fact/period/available-at lineage, official KRX historical tradability/corporate actions, anchor response/private storage reconciliation, archived manifest SHA reconciliation. Never substitute a synthetic CI PASS for source PIT admission.
