# IndexAlert independent profitability and offline runtime audit — 2026-11-06 10:20 KST

**Scope:** New isolated documentation-only branch from research HEAD; read-only GitHub PR, Actions, integration gate and Railway production evidence. No strategy/data/workflow/CI/runtime change, no model search, no performance backtest, no deployment/merge/trading.

## Directly resolved immutable GitHub refs
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406` (self-comparison identical).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (self-comparison identical).
- OPEN, Draft, unmerged: PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- #414 gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md`: Git blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`, fetched from PR branch; absent on research base is expected.

## Directly fetched Actions job results
- [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417): 6/6 success; [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223): 6/6 success; [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311): 6/6 success.
- [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): one-runner-offline-comparison 1/1 success; [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): OpenDART 2/2 success.
- [41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296): auto-anchor FAILURE, validation SKIPPED; no prospective chronology admission.
- Earlier reported 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic tests, serial 2.9656s / parallel 2.6209s = 1.1315x: **historical claims, not independently rehashed/timed this run**. Whole-CI and official-backtest speed NOT VERIFIED.

## Railway production read-only
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Environment inventory reports **staged=null**, unlike prior reports of pending patch; verify source of discrepancy before assuming any change was applied.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`: SUCCESS. KRX worker `16c93d7c-7cd0-4d84-a327-298d2805376c`: SUCCESS. Both returned zero deploy-log entries since 2026-11-06 00:00 UTC; neither current OHLC remediation nor actual live activity established.
- Runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`: SUCCESS. Backend `cce12a43-592a-4910-9b75-89c6b7cdd159` and Push `3ad3102d-ced6-416b-a6da-85c390c9a606`: FAILED. Kiwoom real-readonly deployment SUCCESS does not itself establish healthy replicas. No runtime orders or environment variables were changed.

## Admission decisions (scoped PASS / FAIL / NOT VERIFIED)
| Evidence gate | Result | Scope and next safe action |
| --- | --- | --- |
| Historical KRX weekday raw-pair storage | PASS (previous attestation only) | 1565/1565 SHA pairs; not an exchange calendar or tradability PASS. |
| KRX official session/calendar, halt/delist/corporate actions, historical mapping, executable prices, costs/taxes | NOT VERIFIED / FAIL-CLOSED | Preserve zero-activity 12003 veto and 90-day unresolved classification; require independently pinned official PIT evidence. |
| OpenDART original/correction SGML candidate extraction | PASS (historical 15 candidate row structural evidence only) | Original filing, available-at timestamp, 2021/2022 exact consolidated 3-month operating profit, correction lineage all NOT VERIFIED. |
| Chronology prospective anchor | FAIL | Run 41515392296 failed; validation skipped; investigate read-only evidence without changing workflow. |
| Offline optimization software CI jobs | PASS (job conclusions only) | Test-case SHA parity not rehashed; cache only with all approved source/data/code/Frozen/runtime/evidence SHA-256 keys; only independent read-only postprocessing parallel. |
| Whole CI speed / official PIT backtest speed | NOT VERIFIED | No permitted official experiment before PIT admission. |
| NetEV/PF/CAGR/MDD/ES95/99, concentration, temporal robustness, annual risk-adjusted after-tax net profit | NOT VERIFIED | No M20 run; consumed H5 Holdout/Dynamic cannot be recycled. |

**Final gate:** M20 NO-GO; ORDERING=false policy retained (live setting not independently read); no Champion promotion, Tiny Live, money movement, credential/permission change, PR merge or production deployment. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/Holdout/Top3/NO_TRADE and fixed cost/risk rules unchanged.

**Next:** obtain original-source timestamps/lineage from OpenDART Work, official KRX trading-state and corporate-action PIT proofs from KRX Work, inspect chronology anchor failure and any discrepancy in Railway staged patch via read-only evidence; only then independently reconsider the M20 gate. No cross-room code edits.
