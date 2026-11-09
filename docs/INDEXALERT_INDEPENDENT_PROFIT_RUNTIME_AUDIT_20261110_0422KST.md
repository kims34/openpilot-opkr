# IndexAlert independent profitability/runtime audit — 2026-11-10 04:22 KST

Scope: read-only GitHub/Railway independent verification, offline-only optimisation evidence; no source PIT admission or economic run. No workflow/code/model/production modifications.

## GitHub immutable evidence
Repository kims34/openpilot-opkr. Development base SHA 1e6367d2863a86c3470da13d81a955d277eba485. Research vs development compare: DIVERGED, research ahead 281 and behind 1148. Research exact current HEAD SHA NOT VERIFIED by this compare response; do not substitute PR base SHA.
PRs (all OPEN/Draft/unmerged at inspection): #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581, #422 c14857620973531013799e44625d43080904fd5f, #423 0e38004363cac9fc4475556b3a1c445de9af407f.
Integration gate: docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md on PR #414, content blob not independently rehashed this run.
Actions jobs directly rechecked: 38381997417 6/6 SUCCESS; 38382214223 6/6 SUCCESS; 38419111311 6/6 SUCCESS; 38419649711 1/1 SUCCESS; OpenDART 38419439742 2/2 SUCCESS; Chronology Anchor 41515392296 auto-anchor FAILURE and validation SKIPPED. Historical frozen 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and synthetic 28/13 mock evidence were NOT rehashed this run. Historical regression-phase serial 2.9656s / parallel 2.6209s = 1.1315x; full CI and official backtest acceleration NOT VERIFIED.

## Railway production live check
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, running 1/1; runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, running 1/1. Kiwoom real-readonly a77fb922-b679-4d88-92c4-03054ec579cd deployment SUCCESS but replicas running 0/crashed 1/total 1: operational FAIL despite summary state online. Backend, push and db-query-readonly offline. Environment inventory staged=null but health endpoint reports pending empty patch e113dacb-6705-4416-9997-dc694539d382; NOT VERIFIED discrepancy; do not apply.
PIT, KRX historical worker and real-readonly deploy logs requested from 2026-11-09 18:00 UTC through current run: all returned zero entries. Therefore 27/803 invalid OHLC historical blocker resolution NOT VERIFIED, not asserted as current failure.

## Independent gate
PASS: selected historical offline CI job conclusions; production PIT/runtime running replicas; previous fail-closed evidence only historical.
FAIL: Chronology Anchor job; Kiwoom real-readonly running replica health; backend/push/db-query-readonly offline.
NOT VERIFIED: exact original-filing public available-at/PIT, 2021/2022 first three-month consolidated operating-profit period/correction lineage, issuer/security historical mappings, official KRX calendar/trade states/corporate actions/fillability, 27/803 anomaly resolution, 1565/1565 weekday-pair official trading calendar, costs/taxes, NetEV/PF/CAGR/MDD/ES95/ES99, concentration, temporal robustness, full CI/official runtime acceleration.
M20 PIT and profitability RUN: NO-GO. H5 consumed holdout/Dynamic reuse prohibited. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE and risk/cost/tax policies unchanged. ORDERING=false required. Cache fail-closed unless independently approved data/code/Frozen/runtime/evidence SHA-256 match; parallelise read-only postprocessing only. No trades, transfers, credential changes, champion promotion, merges, deployments, economic tests or workflow edits.

Next: obtain independent original filing/public available-at lineage and official KRX trade-status/corporate-action source SHA, reconcile 27/803 and chronology anchor 404 using read-only original logs, then reassess admission. No source approval inferred from synthetic CI.
