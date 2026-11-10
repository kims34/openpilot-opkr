# IndexAlert independent profitability and isolated optimisation audit — 2026-11-11 01:21 KST

## Provenance and limitations
Read-only GitHub connector and Railway production connector checks during this run. No source PIT admission, economic backtest, model search, merge, deploy, trading, workflow modification, or credential changes. This is an independent audit record, not an approval.

- GitHub repository: kims34/openpilot-opkr.
- Research ref `index-alert-research-v1`: compare API base SHA `df474df348f22aa38b1dedaa59fcff66e548b406`; merge base `c490974ff6619bb978dc6f83f9c24f2c46622f85`.
- Development ref `index-alert-position-regen-fix-v1`: compare API reports DIVERGED, ahead 1148 / behind 281 relative to research. Exact development HEAD was not returned: NOT VERIFIED.
- PR #412/#413/#414/#418 and KRX #420/#422/#423: targeted GitHub issue search unexpectedly returned zero items; current PR HEAD/draft/merge status NOT VERIFIED this run. Do not infer closed or merged. Integration gate path `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` returned 404 on both tested refs; its current blob SHA NOT VERIFIED.
- Actions run 38381997417: 6/6 successful jobs; 38382214223: 6/6; 38419111311: 6/6; 38419649711: 1/1; OpenDART 38419439742: 2/2. Verified only latest-attempt first-page job conclusions, not artifacts, raw inputs, tests, nor 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`.
- Prior reported 13 adversarial mocks, 28 synthetic cases and 34-case parity remain NOT VERIFIED independently this run. Serial 2.9656s vs concurrent 2.6209s gives 1.1315x for regression phase only; whole CI and official backtest speed NOT VERIFIED.

## Railway production evidence
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild: deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS; replicas running 1/1.
- Runtime: deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS; replicas 1/1.
- KRX historical worker: deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS; replicas running 0/1, crashed 0/1. Operational readiness NOT VERIFIED.
- Kiwoom real readonly: deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS but replicas running 0/1, crashed 1/1: runtime FAIL, irrespective of UI online label.
- Backend, push and db-query-readonly offline; db-query-readonly 1 critical issue.
- Staged Railway patch `e113dacb-6705-4416-9997-dc694539d382` reports zero changes. Not applied.
- Deploy log searches for PIT/KRX/Kiwoom for `2026-11-10T15:00:00Z` to `2026-11-10T16:30:00Z`: 0 entries each. No inference of health or safety from absent logs. Previous OHLC 27/803 and FAIL_CLOSED observations were not re-established in this window.

## Admission matrix
| Gate | Verdict | Reason |
|---|---|---|
| Prior KRX 2017–2022 private weekday-pair storage 1565/1565 | HISTORICAL PASS (limited) | Previously reported storage-integrity evidence only; no fresh raw SHA replay |
| Offline Actions job conclusions | PASS (job status only) | 6/6, 6/6, 6/6, 1/1, 2/2 |
| OpenDART original filing, public available-at, 2021/2022 Q1 consolidated operating profit amendment lineage | NOT VERIFIED | Candidate rows/signatures do not prove semantics or availability time |
| Historical company/security mapping | NOT VERIFIED | Independent historical identifiers not established |
| Official KRX trading calendar/status/corporate actions/fillability/cost/tax | NOT VERIFIED | Storage pairs do not certify trading availability |
| PIT and M20 admission | FAIL CLOSED / NO-GO | Mandatory upstream evidence absent |
| NetEV, PF, CAGR, MDD, ES95/99, concentration, chronological robustness after tax and costs | NOT VERIFIED | Official market economic run forbidden until admission |
| Whole CI / real-market backtest acceleration | NOT VERIFIED | Only offline regression-phase comparison |
| Kiwoom readonly runtime health | FAIL | 0 running, 1 crashed replica |
| ORDERING production environment variable | NOT VERIFIED | No independent environment-value inspection; retain ORDERING=false policy |

## Frozen and optimisation guardrails
Frozen H5; M20 horizon20/purge20; WF504/126/126; PIT, labels, Purged/CPCV, independent holdout, Champion/Top3/NO_TRADE, cost/tax/NetEV/fill/risk/promotion rules unchanged. H5 spent holdout and Dynamic outcomes cannot be reused or post-hoc tuned. Only synthetic offline policy/software verification is admissible. Cache requires matching independent approved raw data, code, Frozen policy, runtime and approval-evidence SHA-256 (fail closed); parallelise read-only postprocessing only, not dependent retraining or capital transition. No ordering, live orders, funds movement, permissions, promotion, deploy or merge.

## Next safe steps
1. Re-establish PR metadata and exact development HEAD through an independently accessible GitHub endpoint; review PR #414 integration-gate blob in its actual head ref and KRX action artifacts without modifying owners' work.
2. Obtain independently verifiable original-filing/PIT availability timestamps, 2021/2022 operating-profit correction lineage, corporate-action and fillability evidence before any economic run.
3. Diagnose Kiwoom readonly crashed replica via read-only deployment logs, coordinate with service owner; never restart or deploy without approval.
4. For optimisation, compare frozen 34-case artifact hashes and synthetic adversarial outcomes in offline-only isolation; no new official-market performance experiments.
