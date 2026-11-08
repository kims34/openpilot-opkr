# IndexAlert independent read-only audit — 2026-11-08 13:18 KST

Scope: separate profitability gate and isolated offline-only backtest runtime verification. No strategy replay, live order, deployment, merge, workflow edit or promotion.

## Exact HEAD and evidence
- research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406` (GitHub branch API read this run).
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (branch API read this run).
- Draft OPEN PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft OPEN #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate document blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be` (fetched by exact PR HEAD).
- Actions jobs checked live: 38381997417, 38382214223, 38419111311 = 6/6 success each; 38419649711 = 1/1 success; 38419439742 = 2/2 success; 41515392296 = auto-anchor FAIL, validation SKIPPED. Existing 34-case checksum `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and 2.9656/2.6209 seconds are historical claims, **not rehashed or remeasured in this run**.

## Railway production direct status / logs
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. PIT rebuild replica running 1/1, Runtime 1/1. Real-readonly displayed online/SUCCESS but running 0, crashed 1 (health discrepancy); db-query-readonly offline/critical 1; backend offline/warnings 4; push offline/warning 1. Pending empty staged patch `e113dacb-6705-4416-9997-dc694539d382` persists. Deployment log query from 2026-11-08 03:00 UTC: PIT/KRX/real-readonly zero rows; runtime 26 rows, including Yahoo USDKRW fallback. Zero logs do not prove healthy operation.

## Independent PASS / FAIL / NOT VERIFIED
- PASS limited: prior KRX 1565/1565 private weekday pair storage integrity; directly checked offline CI job conclusions (software-only). These do **not** authorize market PIT.
- FAIL: chronology auto-anchor workflow run 41515392296; real-readonly replica operational health (0 running/1 crashed), despite online display.
- NOT VERIFIED / fail-closed: official first-filed public available-at/PIT, 2021/2022 first three-month consolidated operating-profit period and restatement lineage, historic entity/security mapping, official KRX calendar/trading statuses/corporate actions, executable fills/cost/tax, net EV/PF/CAGR/MDD/ES95/ES99/concentration/time stability; full CI and actual backtest acceleration. Prior KRX 90 uncertain sessions, 12,003 zero-activity and 27 suspicious OHLC remain excluded. No new official data provenance approval.

## Frozen policy and next actions
M20 NO-GO; ORDERING=false. H5 spent holdout and Dynamic results cannot be retuned or independently reused. Frozen H5 and M20 horizon20/purge20 WF504/126/126, PIT, Purged/CPCV, holdout, Champion/Top3/NO_TRADE, cost, tax, execution, risk and promotion criteria unchanged. Cache requires exact independent approved source/data/code/Frozen policy/runtime/approval evidence SHA-256 and fail-closed; only read-only independent postprocessing may parallelize; no dependent retraining/capital transitions in parallel. Next: independent official original filing timestamps and corrected-lineage anchors; official KRX calendar/status and executable market facts; recover chronology anchor; resolve real-readonly replica discrepancy via authorized owner, without changing deployment here. Synthetic offline software/policy tests only until PIT approval. No PR merges, operational writes, live orders, account permission changes or Champion promotion.
