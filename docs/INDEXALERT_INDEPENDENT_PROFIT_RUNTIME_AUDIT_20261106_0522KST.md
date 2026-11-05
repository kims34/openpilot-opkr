# IndexAlert independent profitability and runtime audit — 2026-11-06 05:22 KST

Read-only snapshot; no official backtest, model search, deployment, order or policy modification. No original private source values reproduced.

## Pinned refs
- research index-alert-research-v1 HEAD df474df348f22aa38b1dedaa59fcff66e548b406
- development index-alert-position-regen-fix-v1 HEAD 1e6367d2863a86c3470da13d81a955d277eba485
- OPEN Draft PRs: #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581, #422 c14857620973531013799e44625d43080904fd5f, #423 0e38004363cac9fc4475556b3a1c445de9af407f.
- PR #414 gate document blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be, read directly from refs/pull/414/head. Explicit M20 PIT NO-GO.

## Independently inspected Actions
- 38381997417, 38382214223, 38419111311: each six completed successful jobs (serial, four independent groups, exact parity).
- 38419649711: one-runner-offline-comparison successful.
- 38419439742: offline-row-security-tests and official-safe-candidate-row-diff successful.
- 41515392296: auto-anchor FAILURE; validation SKIPPED. Chronology/PIT gate blocked.
- 34-case fixed SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and 2.9656s/2.6209s = 1.1315x are historical claims, not independently rehashed/timed this run. End-to-end speed NOT VERIFIED.

## Railway production snapshot
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- pit-rebuild SUCCESS deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5, 1/1 running.
- krx-historical-worker SUCCESS deployment 16c93d7c-7cd0-4d84-a327-298d2805376c, 0/1 running.
- runtime SUCCESS deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00, 1/1 running.
- backend, push, db-query-readonly offline; kiwoom-real-readonly deployment SUCCESS but replica running 0/crashed 1.
- one pending staged operation observed, left untouched.
- pit-rebuild and KRX worker log query from 2026-11-05 18:00Z yielded no entries. Therefore cannot claim the previous 27/803 COMMON_OHLC_NONPOSITIVE error is still repeating or resolved.

## Gate decisions
- Historical 1565/1565 weekday source-pair storage integrity: PASS only as earlier evidence, not rerun.
- Official KRX session/calendar, zero-activity exclusion, status, corporate actions, actual execution and historical mapping: NOT VERIFIED, fail-closed.
- OpenDART original filing public available-at, 2021/2022 first 3-month consolidated operating profit period and correction lineage: NOT VERIFIED; prior 15-row signature match is not semantic or timing approval.
- Chronology Anchor: FAIL; downstream validation SKIPPED.
- Software-only CI on fixed synthetic tests: PASS for listed jobs, limited to their scope.
- NetEV/PF/CAGR/MDD/ES95/99, taxes, costs, concentration, temporal robustness, official M20 economic backtest: NOT VERIFIED, M20 NO-GO.
- Runtime optimization end-to-end acceleration: NOT VERIFIED. Cache must fail closed on approved data/code/Frozen/runtime/evidence SHA mismatch; parallelize read-only postprocessing only.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, CPCV/Holdout/Champion/Top3/NO_TRADE and ORDERING=false unchanged. No reused H5 holdout, no market performance experiment.

## Next independent evidence
1. Acquire official timestamped original filing + correction lineage and hash-only PIT attestation.
2. Reconcile 27 suspicious OHLC rows and 90 uncertain sessions against official KRX session/status/corporate-action sources without allowing entry.
3. Diagnose failed Chronology Anchor using immutable run artifacts; do not bypass workflow security.
4. Independently pin optimization parity SHA and full CI wall-time in offline-only isolation, with no performance or market-data run.
