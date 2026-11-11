# IndexAlert independent evidence audit — 2026-11-12 04:20 KST

Scope: read-only GitHub/Railway cross-check; this isolated document is the only write. No official market backtest, model search, workflow change, deployment, merge, order, fund movement, credentials change or Champion promotion.

## Exact refs
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`, compare against this exact SHA: identical, 0 ahead / 0 behind.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`, identical, 0/0.
- GitHub PRs #412, #413, #414, #418, #420, #422, #423: independently fetched; OPEN, Draft, unmerged. PR #414 HEAD `18c5418d9684d1717df58261ea27f28e514385b2`, base `3b8b7830612a6284d7c7a60628cb527cb741627a` (base SHA recorded on PR, not the current research branch HEAD).
- PR #414 integration gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` fetched on its draft branch: blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Absent from frozen research base is not a missing gate.
- Actions [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417) and [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223): each 6/6 successful; [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) 6/6 successful; [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 successful; [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 successful. Job conclusions rechecked this run; independent rehash of 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` NOT VERIFIED.

## Railway production read-only
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild and runtime each 1/1 running; KRX worker 0/1 running (health NOT VERIFIED); Kiwoom real-readonly 0/1 running, 1/1 crashed (replica FAIL); backend, push, db-query-readonly offline, last has one critical issue.
- Deploy log window 2026-11-11 18:00–19:25 UTC: PIT, KRX, Kiwoom 0 lines. Runtime had 101 retrieved lines (query limit 100; response includes 101); Investing USD/KRW HTTP errors and Yahoo fallback observed. This is not official KRX/PIT admission evidence.
- Environment status reports a staged patch `e113dacb-6705-4416-9997-dc694539d382` with zero changes; describe-environment reports staged=null. Treat as inconsistent read-only metadata; do not apply.
- Latest deployment inventory has no new production change evidenced by this check. KRX worker latest SUCCESS deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, but running replica remains unverified.

## PASS / FAIL / NOT VERIFIED and strict gates
- PASS only within original evidence scope: historical KRX 2017–2022 1565/1565 weekday raw-pair storage integrity (prior source attestation, not independently rehashed this run); offline CI job conclusions above. OpenDART 15 candidate-row adjacency signature is prior software-level evidence, not approved semantic/temporal PIT.
- FAIL: Kiwoom real-readonly runtime replica; production PIT input admission remains fail-closed.
- NOT VERIFIED: original-filing meaning and exact public available-at; first-filed 2021/2022 connected three-month operating profit period and amendment lineage; historical corp/security mappings; official KRX calendar/trading state/corporate actions/executability/fees/tax; label/Purged/CPCV/independent Holdout; post-cost/post-tax NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness; actual official backtest acceleration.
- Historical KRX 90-day classification and zero-activity 12003 rows remain excluded; no extrapolation from stored bytes to tradability. H5 failed/consumed Holdout and Dynamic results may not be reused or tuned. M20 PIT and economic run NO-GO.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, Top3/NO_TRADE, costs/tax/execution/risk/promotion criteria unchanged. ORDERING=false. Only synthetic offline policy/security verification permitted. Cache must fail closed unless independently approved source/data/code/Frozen policy/runtime/approval SHA-256 all match; parallelize only independent read-only postprocessing, never dependent retraining/capital transitions.
- Offline runner comparison 2.9656s serial vs 2.6209s concurrent suite (1.1315x regression-phase ratio) is historical limited evidence, not full CI or official backtest speedup.

## Next independent steps
1. Request source-owning workrooms' immutable original-filing public timestamp/period-lineage evidence and KRX official calendar/status/action/execution evidence, with SHA and independent CI logs; do not duplicate their code.
2. Independently verify 34-case artifact SHA if a safe immutable artifact becomes available; no synthetic test result may be described as economic validation.
3. Continue Railway read-only runtime/log checks; flag Kiwoom crashed replica and KRX non-running replica without restart or staged-patch application.
4. Only after independent PIT admission, seek explicit separate user authorization before any official M20 economic evaluation, trading, account change or Champion promotion.
