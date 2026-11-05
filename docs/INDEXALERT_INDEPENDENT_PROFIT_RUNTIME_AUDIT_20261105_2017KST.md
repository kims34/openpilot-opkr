# IndexAlert independent profitability / offline optimisation audit — 2026-11-05 20:17 KST

## Scope and read-only evidence
Repository kims34/openpilot-opkr, default branch HKG_community. Branch searches confirmed existence of index-alert-research-v1 and index-alert-position-regen-fix-v1; **their exact current HEAD SHAs were not independently resolved**. Do not substitute PR heads for branch HEADs.

PR metadata (all OPEN/DRAFT, checked this run):
- #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- #414 18c5418d9684d1717df58261ea27f28e514385b2
- #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581
- KRX #422 c14857620973531013799e44625d43080904fd5f
- KRX #423 0e38004363cac9fc4475556b3a1c445de9af407f

GitHub Actions job conclusions checked via API this run:
- optimisation #38381997417, #38382214223, #38419111311, #38466023642: each 6/6 SUCCESS
- independent runner #38419649711: 1/1 SUCCESS
- OpenDART #38419439742: 2/2 SUCCESS
- chronology #41515392296: auto-anchor FAILURE; validation SKIPPED
Previous fixed 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, 13 adversarial mocks, 28 synthetic tests and 2.9656s/2.6209s = 1.1315x are **historical reported evidence, not independently recomputed this run**. CI success does not prove official-backtest speedup.

Railway IndexAlert production environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7: no staged patch at inspection. PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS; KRX historical worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS; runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS. These are deployment statuses, not proof of healthy replicas or approved source data. Backend and push latest deployments FAILED.

**Fresh critical source observation**: PIT rebuild deploy logs at 2026-11-05 09:30:24–11:15:52 UTC repeatedly report `KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE`, `source_failure_session=2026-09-28`, 803 common-stock rows, 27 nonpositive OHLC rows, 27 zero-volume/value rows, `session_manifest_sha256=null`, `fresh_alpha_observation_admitted=false`, `private_rejected_source_receipt_saved=true`, `status=FAIL_CLOSED`, `ordering=DISABLED`. **Safety rejection PASS; KRX data acceptance FAIL for that session; source cause and official trading-state mapping NOT VERIFIED.** Do not silently coerce zeros to valid prices or suppress affected rows without official original evidence.

KRX historical worker: no new deploy logs in the 09:00 UTC onward query. Runtime 11:15 UTC logs contain Yahoo USD/KRW fallback, BOK ECOS previous-close basis and QQQ/SPY premarket quotes; these are display/runtime observations, **not** independently authorised PIT research inputs.

## Gates
- Original-filing, public available-at, 2021/2022 first three-month consolidated operating-profit lineage: NOT VERIFIED (OpenDART candidate-row CI is not source chronology approval).
- Historical issuer/security mapping and corporate actions: NOT VERIFIED.
- Official KRX calendar, trading halts, execution and price validity: FAIL for 2026-09-28 prospective source; broader historical eligibility NOT VERIFIED.
- Historical 1565/1565 weekday private storage pairs: historical storage-integrity PASS claim only, not fresh official calendar verification.
- Frozen H5 independent Holdout and M20 horizon20/purge20 WF504/126/126 PIT/Purged/CPCV: no new admission; M20 NOT EVALUABLE / NO-GO.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, stability after trading costs and tax: NOT VERIFIED; do not run M20 economics.
- Offline CI job conclusions PASS; independent whole-CI/official-backtest acceleration NOT VERIFIED.

## Next isolated read-only work
1. Resolve current research/development branch HEAD via authoritative Git ref API; preserve separate from PR HEADs.
2. Retrieve exact private rejected receipt and official KRX 2026-09-28 instrument-level halt/corporate-action/price/volume lineage; independent SHA and public-availability timestamps; no data correction or economic run.
3. Recheck chronology anchor original-filing publication time and 2021/2022 original/correction SGML accounting periods.
4. Offline-only synthetic policy regression for cache fail-closed, evidence SHA equality, read-only parallel postprocessing, serial capital transitions; no model search, holdout reuse or performance claims.
5. Keep ORDERING=false; no deploy, merge, workflow change, trading, credentials, Champion promotion or M20 run.

This document is isolated evidence bookkeeping; no operational or model code changed.
