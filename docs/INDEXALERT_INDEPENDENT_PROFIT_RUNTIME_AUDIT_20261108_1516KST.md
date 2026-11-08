# IndexAlert independent profitability / isolated runtime audit — 2026-11-08 15:16 KST

Read-only evidence check. No M20 run, trading, merge, deployment, workflow edit, model tuning or policy alteration. This document is an isolated audit record, not an admission or approval.

## GitHub exact immutable refs
- Research branch `index-alert-research-v1`: comparison with `3b8b7830612a6284d7c7a60628cb527cb741627a` yielded ahead 2 / behind 0. Previous independently recorded head `df474df348f22aa38b1dedaa59fcff66e548b406`; current exact head not independently resolved in this execution. Do not treat the comparison base as current HEAD.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`, comparison identical 0/0.
- OPEN Draft, not merged: PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- Integration gate document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` at #414 blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.

## CI evidence checked directly
- [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311): 6/6 jobs success each.
- [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): 1/1 success, isolated synthetic one-runner.
- [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): 2/2 success, OpenDART candidate safety tests.
- [41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296): auto-anchor FAIL; validation SKIPPED. This is a concrete chronology blocker.
- Historical fixed 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic cases and regression-phase 2.9656s/2.6209s=1.1315x are previous evidence only, NOT rederived from artifacts in this run. End-to-end CI and official backtest speed NOT VERIFIED.

## Railway production read-only
- Project IndexAlert `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS (2026-10-10), KRX worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS (2026-10-12), real readonly `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS (2026-10-29), Runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS (2026-10-05). Deploy SUCCESS is not proof of running healthy replicas.
- PIT/KRX/real-readonly deploy log queries since 2026-11-08 05:00 UTC: 0 entries each; absence is not evidence of correction. No staged changes on these services; db-query-readonly has no latest deployment in describe-service. No production writes.
- Previously recorded KRX 1565/1565 private weekday pairs: storage integrity PASS (historical attestation only); official session status, corporate actions, executable liquidity, 90 uncertain sessions, 27 abnormal OHLC and 12003 zero-activity records: not admitted as market PIT.

## Independent PASS/FAIL/NOT VERIFIED
- Offline CI job completion: PASS for the exact runs above; original-filing semantics / public available-at / 2021-2022 Q1 consolidated operating-profit period and correction lineage: NOT VERIFIED.
- Chronology Anchor: FAIL; historical company-security mapping, official KRX calendar/status, corporate actions, fillability and cost/tax: NOT VERIFIED.
- NetEV/PF/CAGR/MDD/ES95/ES99, concentration, temporal robustness, independent Holdout and real end-to-end acceleration: NOT VERIFIED.
- M20 horizon20/purge20, WF504/126/126, Frozen H5, PIT/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE gates unchanged; M20 NO-GO. ORDERING=false; no Holdout reuse, no Dynamic hindsight adjustments.
- Cache must fail closed unless independently approved original/data/code/Frozen/runtime/approval SHA-256 all match. Parallelism only for independent read-only postprocessing; no dependent retraining or capital-transition parallelism.

## Next safe steps
Resolve official original-filing/public timestamp and Q1 period/correction lineage, official KRX sessions/corporate actions/tradability and chronology failure from immutable source artifacts, then independent SHA-backed admission review. Only synthetic offline safety checks before source PIT approval. No user authorization inferred for trading, credential changes, promotion, merge or deploy.
