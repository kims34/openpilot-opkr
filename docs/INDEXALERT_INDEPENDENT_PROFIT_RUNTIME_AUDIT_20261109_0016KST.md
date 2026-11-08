# IndexAlert independent profitability and isolated optimization audit — 2026-11-09 00:16 KST

## Read-only source evidence
- Research `index-alert-research-v1` compared with `df474df348f22aa38b1dedaa59fcff66e548b406`: identical, 0 ahead/behind. Development `index-alert-position-regen-fix-v1` compared with `1e6367d2863a86c3470da13d81a955d277eba485`: identical.
- PR #412/#413/#414/#418 and KRX PR #420/#422/#423: current PR HEAD and Draft state NOT VERIFIED this run; GitHub issue search returned no entries, so do not infer closure.
- Actions #38381997417/#38382214223/#38419111311: historical successful six-job suites (job details inspected); #38419649711: 1/1 successful; OpenDART #38419439742: 2/2 successful. Chronology #41515392296: auto-anchor FAIL on public hash-only prospective payload fetch; validation SKIPPED.
- Historical 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks and 28 synthetic tests, serial 2.9656s vs concurrent 2.6209s: historical claims only, not independently recalculated this run. Whole CI and real official backtest acceleration NOT VERIFIED.

## Railway production (read-only)
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. PIT rebuild and Runtime each 1/1 running; real-readonly shows online/SUCCESS but replicas 0 running/1 crashed; db-query-readonly offline Critical 1; backend and push offline.
- Environment inventory says staged=null; environment health API separately reports an empty staged patch `e113dacb-6705-4416-9997-dc694539d382` (changes=[]). Treat API discrepancy as NOT VERIFIED, no mutation.
- PIT logs 2026-11-08 23:00–23:46 KST: `KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE`, original failure session 2026-09-28; 803 common-stock rows, 27 nonpositive OHLC and 27 zero-volume/value rows; `FAIL_CLOSED`, `ordering=DISABLED`, fresh alpha not admitted, session manifest SHA null. No KRX worker deploy logs in same queried window.

## Independent gate decision
- OpenDART 15 original/correction candidate SGML row signatures: historical candidate evidence only. Original filing semantics, public available-at/PIT, 2021/2022 consolidated first 3-month operating-profit period and correction lineage: NOT VERIFIED.
- Historical corporate/security mapping, official KRX calendar/state/corporate actions/tradability/fillability/fees/tax: NOT VERIFIED. Historical 1565/1565 weekday-pair storage integrity PASS is a prior claim, not newly rehashed.
- NetEV/PF/CAGR/MDD/ES95/ES99/return concentration/time-slice robustness after executable costs/taxes: NOT VERIFIED. Chronology anchor FAIL. M20 PIT and profitability RUN NO-GO.
- Offline-only optimization CI job completion PASS; frozen parity SHA, real-world speedup and source admissibility NOT VERIFIED. Do not interpret synthetic tests as economic approval.

## Frozen safety and next actions
Frozen H5; M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE, fees/taxes/risk/promotion thresholds unchanged. H5 failed/consumed Holdout and Dynamic results not independently reusable. ORDERING=false; no trade, transfer, credential/permission changes, Champion promotion, deployment, merge or workflow writes.
Independent source owners must supply immutable original-filing, exact public availability, period/correction lineage, historical security mapping, official KRX session/tradability/corporate-action receipts and SHA/CI logs. Diagnose chronology fetch failure and real-readonly replica separately without deployment. Cache must fail closed on source/data/code/Frozen/runtime/approval evidence SHA-256 mismatch; parallelize only read-only postprocessing, not dependent retraining or capital transitions.
