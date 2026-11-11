# IndexAlert independent read-only audit — 2026-11-11 20:17 KST

Scope: independent profitability gate and isolated offline-only runtime optimization; **not** an authorization for M20 performance, live orders, promotion, merge or deployment. No original issuer values or credentials reproduced.

## GitHub evidence
- Development comparison base commit: `1e6367d2863a86c3470da13d81a955d277eba485` from direct compare API (base ref `index-alert-position-regen-fix-v1`); research-v1 vs development diverged, 281 ahead / 1148 behind. Research exact HEAD not returned by this API: NOT VERIFIED; do not substitute an old SHA.
- PR #412/#413/#414/#418/#420/#422/#423 issue API: all OPEN as of this run. Draft flag, PR head SHAs and merge state not independently returned by this endpoint: NOT VERIFIED. Do not infer Draft from previous run.
- PR #414 gate content fetched at `refs/pull/414/head`: Git blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; gate explicitly states KRX storage-only PASS, DART PIT FAIL-CLOSED, H5 NO-GO, M20 not authorized.
- Actions jobs fetched directly: 38381997417 6/6 SUCCESS; 38382214223 6/6; 38419111311 6/6; 38419649711 1/1; 38419439742 2/2; 38498552499 6/6. These prove job conclusions, not original-source semantic validity.
- Prior fixed 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 additional synthetic cases, and 2.9656s/2.6209s = 1.1315x regression-phase comparison: historical reported evidence; independent artifact rehash and current wall-clock replay NOT VERIFIED. Full CI speed and official PIT backtest speed NOT VERIFIED.

## Railway production direct read-only evidence
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild and runtime each 1/1 running. KRX worker 0/1 running; real Kiwoom readonly 0/1 running, 1/1 crashed (replica FAIL); backend/push/db-query-readonly offline, db-query-readonly 1 critical. Deployment SUCCESS does not prove replica health.
- Environment inventory says staged=null but status endpoint reports empty staged patch `e113dacb-6705-4416-9997-dc694539d382` (changes=[]). Do not apply.
- 2026-11-11 10:15–11:20 UTC: PIT deploy logs 5 messages at 10:16, 10:30, 10:46, 11:01, 11:16 UTC, `KRXProspectiveOpenAPISourceError` / `COMMON_OHLC_NONPOSITIVE`; `fresh_alpha_observation_admitted=false`, `funds_movement_authorized=false`, independent chronology/model admission false. Repeated official input invalidity is a **current source admission blocker**, while observed fail-closed response is PASS for blocking only.
- Same window: KRX worker and Kiwoom readonly logs 0; absence is not health PASS. Runtime logs show Investing.com USD/KRW HTTP failure and Yahoo fallback; not PIT source evidence.

## Gate decisions
- Historical KRX 1565/1565 weekday original-pair storage integrity: historical PASS only, not rehashed this run. Official holiday/status/corporate actions/marketable execution/fees/tax: NOT VERIFIED, source gate CLOSED. Historical 90 uncertain days and 12003 zero-activity records remain quarantined.
- OpenDART 2021/2022 first-filed consolidated exact three-month operating income, correction lineage, original publication timestamp/public available-at, issuer-security historical mapping: NOT VERIFIED, source gate CLOSED. 15 SGML candidate rows and adjacent number signatures from Action 38419439742 are only structural candidates.
- H5 archived holdout exhausted/failed, no retuning or independent reuse. Frozen M20 horizon20/purge20, WF504/126/126, PIT, purging/CPCV, independent holdout, Champion/Top3/NO_TRADE and risk/cost/tax/execution rules unchanged.
- M20 net-of-fees/tax NetEV, PF, CAGR, MDD, ES95/99, return concentration and time robustness: NOT VERIFIED / NO-GO; no economics run.
- Optimization PR #413 and isolated runner #418: offline CI jobs PASS; parity SHA independently NOT VERIFIED; overall speed NOT VERIFIED. Cache must fail closed on independent source/data/code/frozen/runtime/approval SHA-256 match. Only independent read-only postprocessing may parallelize; no dependent retraining or capital transitions.

## Next safe steps
1. DART owner independently prove original filing semantic/period/correction/available-at lineage with source digests; no corrected-value backfill.
2. KRX owner resolve repeated COMMON_OHLC_NONPOSITIVE, official session and trading-state/CA/lot/fee/tax source evidence, preserving all vetoes.
3. Optimization owner rehash immutable 34-case artifact and verify per-phase/total wall-clock only in isolated synthetic offline CI; no new performance experiment.
4. Independently obtain exact research HEAD, PR head/draft/merge metadata, job artifacts and runtime replica/critical root-cause evidence. Do not edit other owners' code.
5. Only after independently verified source admission, seek explicit separate authorization before M20 economics or any trade/Champion action. ORDERING=false; no deployment, merge, auth change or funds transfer.

All operations this run were read-only except this dedicated audit branch and document. No workflow changes, production writes, PR merge or model/performance execution.
