# IndexAlert independent profitability / offline runtime audit — 2026-11-05 01:16 KST

Read-only evidence collection performed this run; no PIT admission, economic run, order, deployment, merge, workflow modification or shared code edits.

## Source anchors and limitations
- GitHub branch search confirms `index-alert-research-v1` and `index-alert-position-regen-fix-v1` exist, but the search does not return commit SHAs. Prior verified heads: research `df474df348f22aa38b1dedaa59fcff66e548b406`, development `1e6367d2863a86c3470da13d81a955d277eba485`; **current exact HEAD NOT VERIFIED this run**.
- PR #414 gate file directly fetched at pinned commit `18c5418d9684d1717df58261ea27f28e514385b2`, blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. This is a pinned historical commit, not proof of current PR HEAD. PR #412/#413/#414/#418 and KRX #420/#422/#423 current draft/merge/HEAD status NOT VERIFIED this run; earlier confirmed PR SHAs are historical evidence only.
- Latest independent audit predecessor fetched from branch `indexalert-independent-audit-20261104-0222kst`: `docs/INDEXALERT_INDEPENDENT_PROFIT_RUNTIME_AUDIT_20261105_0024KST.md`, blob SHA-1 `e4d48f807523854ccbe221b56ef6eb70045048b4`.

## Independently checked Actions jobs
- `38381997417`, `38382214223`, `38419111311`: all jobs returned success (6/6 each).
- `38419649711`: 1/1 success, offline one-runner comparison.
- `38419439742`: 2/2 success, OpenDART candidate row diff / offline security tests. Does not establish original filing financial semantics or public available-at.
- `41515392296`: auto-anchor failure at public hash-only prospective payload fetch, validation skipped. This is a concrete chronology blocker.
- Prior reported 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic checks, and regression-phase 2.9656s / 2.6209s = 1.1315x are historical; NOT independently rehashed/timed this run. Whole-CI and official PIT backtest speed NOT VERIFIED.

## Railway production — read-only fresh query
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild `225f2279-d728-4e1a-a3f3-2447ff0f9dc1`: latest deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, 2026-10-10, commit `e57054ecdb3e734ced3c9a981b887d9b5fc60f97`. **0 log entries** UTC 2026-11-04 15:00–16:20 (KST 00:00–01:20); prior `COMMON_OHLC_NONPOSITIVE` / `FAIL_CLOSED` remains historical, not resolved by log silence.
- KRX worker `003812ee-102b-42b6-bda4-36925885b428`: latest deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, 2026-10-12, commit `1e6367d2863a86c3470da13d81a955d277eba485`; **0 log entries** in same window. Storage SHA audit ≠ official trading status.
- Runtime `37902fde-ca05-43e0-bc76-278992bf7732`: latest deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, 2026-10-05, commit `8a68b01bca5d551d083ccda263df38d86fa54166`. Live quote/FX monitoring records observed through 2026-11-04 16:16Z; unrelated to PIT authority.

## Gate disposition
- KRX 2017–2022 1565/1565 weekday private raw-pair integrity: historical PASS only. Official session calendar, security status, corporate actions, issuer/security mapping, zero-activity execution feasibility, cost/tax source: NOT VERIFIED / FAIL-CLOSED.
- OpenDART 2021/2022 initial consolidated three-month operating profit, original filing/correction lineage, exact public available-at: NOT VERIFIED / FAIL-CLOSED. 15 candidate rows do not establish semantic period/time.
- Chronology anchor: FAIL (payload fetch); downstream validation SKIPPED.
- Synthetic CI software regressions: limited PASS. Full acceleration NOT VERIFIED.
- NetEV/PF/CAGR/MDD/ES95/99, return concentration, regime robustness after costs/taxes: NOT EVALUABLE. M20 PIT/economic RUN NOT AUTHORISED / NO-GO.
- Frozen H5; M20 horizon20/purge20, WF504/126/126, Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and risk/fee/tax gates unchanged. Consumed holdout and dynamic output not independent reuse.
- Fail-closed cache requires independent approved source/data/code/Frozen/runtime/approval evidence SHA-256 identity; parallelise only independent read-only post-processing. No dependent retraining/capital transitions. ORDERING=false.

Next permitted work: independently pin original-filing/public available-at and exact 3-month consolidated lineage; official KRX status/calendar/corporate-action/mapping/feasibility evidence; offline-only cache invalidation and deterministic parity tests. Do not run M20, change protected workflows, merge, deploy or trade.
