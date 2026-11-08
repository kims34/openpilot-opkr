# IndexAlert independent read-only audit — 2026-11-09 08:21 KST

Scope: independent profitability gate and isolated offline-only backtest environment optimization. This document records only evidence actually checked in this run; prior reported figures are historical, not revalidated.

## Exact repository anchors
- research index-alert-research-v1 HEAD: df474df348f22aa38b1dedaa59fcff66e548b406 (GitHub compare identical).
- development index-alert-position-regen-fix-v1 HEAD: 1e6367d2863a86c3470da13d81a955d277eba485 (GitHub compare identical).
- independent audit branch previous HEAD: 35bc5993bde93411985acbaf0a789cf759c677b6.
- PR #412, #413, #414, #418, #420, #422, #423: OPEN by GitHub issue API. Draft flags and exact PR HEADs NOT VERIFIED by this endpoint. The integration-gate file was NOT FOUND on the research branch; this is not evidence of absence from PR #414.

## CI verified directly
- Actions 38381997417 and 38382214223: six of six jobs success each.
- Action 38419111311: six of six success.
- Action 38419649711: one of one success (one-runner-offline-comparison).
- Action 38419439742: two of two success (offline-row-security-tests; official-safe-candidate-row-diff).
- Chronology Anchor Action 41515392296: auto-anchor FAILURE, validation SKIPPED. This is a blocking FAIL.
- Historical fixed 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and 1.1315x regression-phase timing: NOT independently recomputed this run. Full CI and official backtest acceleration NOT VERIFIED.

## Railway production (read-only)
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild latest deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS; KRX worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS; Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS. Deployment success does not prove data or runtime correctness.
- Backend and Push latest deployments FAILED; db-query-readonly has no latest deployment.
- Production status stagedChanges null, but pendingWork includes empty staged patch e113dacb-6705-4416-9997-dc694539d382; describe-environment staged null. Do not apply.
- Deploy logs since 2026-11-08T22:00:00Z: PIT rebuild 0, KRX worker 0, real-readonly 0. No inference about health from absent logs.
- Actual runtime instance health and ORDERING variable value NOT independently checked this run.

## Independent gate decisions
- Official original-filing/public available-at PIT, 2021/2022 first-three-month consolidated operating-profit period/correction lineage, historical issuer/security mapping: NOT VERIFIED.
- Official KRX calendar/trading status/corporate actions/executability and costs/taxes: NOT VERIFIED. Prior 1565/1565 weekday raw-pair storage integrity does not establish market availability.
- Post-cost/tax NetEV, PF, CAGR, MDD, ES95/99, concentration and temporal robustness: NOT VERIFIED. M20 economics: NO-GO.
- Chronology Anchor: FAIL; downstream validation SKIPPED.
- Optimization: offline CI job success PASS; deterministic output parity SHA and real-world acceleration NOT VERIFIED in this run.

## Frozen constraints and next safe steps
Maintain Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE, cost/tax/risk/promotion gates. Preserve ORDERING=false policy, fail-closed cache with all independent SHA-256 approvals, parallelize only independent read-only postprocessing; no dependent retraining/capital-transition parallelism. Do not reuse consumed H5 Holdout or Dynamic results. Do not run M20 economic experiments or tune models until official PIT and chronology evidence independently pass. Next: obtain official filing timing and correction lineage, formal KRX trading calendar/status and corporate actions, investigate failed chronology anchor and service runtime health in read-only mode, and independently reverify test fixture SHA before considering any new offline-only software validation. No merge, deployment, workflow edits, live orders, funds movement, credentials change or Champion promotion.
