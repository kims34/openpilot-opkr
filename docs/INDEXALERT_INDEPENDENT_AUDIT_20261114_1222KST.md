# IndexAlert independent audit — 2026-11-14 12:22 KST

Scope: read-only profitability gate and separate isolated offline optimisation review. No production or economic experiments.

## GitHub evidence checked this run
- Research branch `index-alert-research-v1` HEAD `df474df348f22aa38b1dedaa59fcff66e548b406` (compare identical, ahead/behind 0/0).
- Development branch `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485` (compare identical, 0/0).
- Audit branch HEAD before write `6003bd6b78e308171a31c8194b5fbe50b161fb01` (compare identical).
- Previous audit 11:17 KST blob Git SHA-1 `d3c9f2eee77aaf79b7695fdb24f647834fe83d13` contains historical PR HEAD snapshots: #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581, #422 c14857620973531013799e44625d43080904fd5f, #423 0e38004363cac9fc4475556b3a1c445de9af407f. THESE ARE PREVIOUS AUDIT VALUES, NOT independently refreshed current PR HEADs. GitHub search for open PRs returned empty, so current PR states NOT VERIFIED; do not infer closure or merging. PR #414 gate file direct fetch on research branch returned 404, so document source independently NOT VERIFIED this run. Previously reported blob SHA-1 984c933651f39f1ee9e26a1d7ac3893aaa5335be is not SHA-256.
- Actions checked directly: 38381997417 6/6 PASS, 38382214223 6/6 PASS, 38419111311 6/6 PASS, 38419439742 2/2 PASS, 38419649711 1/1 PASS; 38486028854 1/1 FAIL. Failed job 115599778959 step 6 'Enforce original CI regression-source blob identities before any test' FAIL; subsequent tamper and four regression suites SKIPPED. Success of earlier synthetic jobs is not parity approval of integrated PR #418.
- 34-case expected SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`: historical evidence only, no independent source-byte recomputation this run. 13 adversarial mocks and 28 synthetic cases: historical only. Serial 2.9656s / concurrent 2.6209s = 1.1315x regression-phase only; overall CI and official backtest acceleration NOT VERIFIED.

## Railway production evidence checked this run
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild SUCCESS running 1/1; Runtime SUCCESS running 1/1. KRX historical worker SUCCESS deployment but running 0/1; Kiwoom real-readonly-run SUCCESS deployment but running 0/1. Backend, Push, db-query-readonly offline. Note service display 'online' is not evidence of a running replica when 0/1.
- Pending patch `e113dacb-6705-4416-9997-dc694539d382` still staged since 2026-10-29 06:20:53Z; not committed.
- 2026-11-14 02:15–03:25 UTC: PIT deploy logs 0, KRX deploy logs 0, Runtime returned 251 entries (limit 250; truncation possible), including 03:21:42Z Investing USD/KRW HTTP errors and Yahoo fallback. This is runtime data-source fallback, not approved PIT/market evidence. No evidence that earlier OHLC anomalies 27/803 were fixed.

## Independent PASS / FAIL / NOT VERIFIED gates
- PASS (narrow historical technical evidence): designated older offline Actions completed successfully; OpenDART SGML candidate-row signature comparison; Railway historical weekday raw-pair storage 1565/1565 (previously established, not rerun).
- FAIL: PR #418 integrated archived-source identity gate (Action 38486028854).
- NOT VERIFIED: official original-filing semantic selection and public available-at/PIT; 2021/2022 first-quarter consolidated operating-profit period/correction lineage; historical entity-security mapping; official KRX calendar/trading status/corporate actions/executability; fees/taxes; post-cost post-tax annual risk-adjusted NetEV/PF/CAGR/MDD/ES95/ES99/concentration/time robustness; full CI acceleration; current PR HEADs; independent 34-case SHA-256 reproduction.
- NO-GO M20. Holdout H5 consumed/failed; never independently reuse or retune against H5/Dynamic. Frozen H5 and M20 horizon20/purge20 WF504/126/126, PIT, labels, Purged/CPCV, independent Holdout, Champion/Top3/NO_TRADE and all financial gates unchanged. ORDERING=false.

## Next permitted steps
1. Read-only obtain precise PR #412/#413/#414/#418 and KRX PR current HEAD and PR #414 gate blob from their actual HEAD refs; compare with prior audit without changing other teams' code.
2. Read-only inspect failed job logs and original regression-source Git blobs; recompute archived 34-case SHA-256 from exact bytes offline before proposing any change. Do not change workflows to bypass security gates.
3. Obtain independently approved official original filing and public available-at lineage, KRX tradeability/cost/tax evidence before any economic test. Synthetic offline safety-only work permitted.
4. Cache only with all independent approved source/data/code/Frozen/runtime/evidence SHA-256 equal and fail-closed. Parallelise read-only postprocessing only, never dependent retraining or capital transitions.
5. No deploy, merges, Champion promotion, orders, fund movements, authentication or account changes.
