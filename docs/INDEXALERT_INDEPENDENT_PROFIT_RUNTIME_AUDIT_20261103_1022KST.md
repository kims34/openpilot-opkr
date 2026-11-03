# IndexAlert independent profitability/runtime audit — 2026-11-03 10:22 KST

Scope: read-only source/CI/Railway inspection; isolated documentation only. No market-performance execution, workflow modification, deployment, merge, ordering, or permission changes.

## Exact source refs observed
- research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a` (self-compare identical).
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (self-compare identical).
- Draft PR #414 `9ec3bc0959ba1b7b4505eb5c7db8798fe5bc2989`; gate document blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- Draft PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.

## CI source checks
- Action 38419111311: 6/6 jobs success (gates/cache/cost/risk/serial-reference/exact-parity). Synthetic-only; prior 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` is historical reference, **not independently recomputed this run**.
- Action 38419649711: 1/1 one-runner-offline-comparison job success. Prior archived manifest mismatch remains FAIL-CLOSED pending matching immutable evidence; no production wall-time proof.
- The earlier 38381997417/38382214223 6/6 and adversarial mocks are retained as historical, not a new authorization.

## Railway source checks
- Project IndexAlert `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; production service inventory inspected.
- Latest returned deployment list included Kiwoom REAL readonly SUCCESS `a77fb922-b679-4d88-92c4-03054ec579cd` at 2026-10-29T06:21:36Z, commit `85bb6fd10bcc9ff2b14abe1c774f0d99f8eb84ab`, and KRX worker SUCCESS `16c93d7c-7cd0-4d84-a327-298d2805376c` at 2026-10-12T13:07:31Z, commit `1e6367d2863a86c3470da13d81a955d277eba485`. Deployment SUCCESS does not establish live trading readiness.
- PIT rebuild deploy logs still return `COMMON_OHLC_NONPOSITIVE`, 27 nonpositive OHLC / 803 common stocks, `session_manifest_sha256=null`, `FAIL_CLOSED`, `ordering=DISABLED`, no independent source/model/chronology admission. No recovery proved.
- Runtime HTTP latest sample includes successful ordinary /status and /history requests; this is **not** an anchor proof. The sampled 500 HTTP entries did not include /anchor/latest; prior independent observation of 20 HTTP 404 and Action 41515392296 remains historical, not re-confirmed by this particular sample. Exact anchor response body/private storage remains NOT VERIFIED.

## Gate classification
- OpenDART original-filing meaning, 2021/2022 consolidated exact 3-month operating profit, amendments, public available-at, historical issuer/security mapping: **NOT VERIFIED / FAIL-CLOSED for admission**.
- KRX 1565/1565 weekday raw pairs: **historical storage-integrity PASS only**; official calendar, halts, corporate actions, execution, fees/taxes: **NOT VERIFIED**.
- Optimization #413 synthetic CI: **limited PASS**; #418 runner CI: **limited PASS**, archived manifest mismatch **FAIL-CLOSED**; full CI/official backtest acceleration **NOT VERIFIED**.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness after taxes/costs: **NOT EVALUABLE** because M20 PIT source authorization is absent.
- Final decision: **M20 NO-GO, ORDERING=DISABLED**. Preserve Frozen H5, horizon20/purge20, WF504/126/126, independent Holdout, Top3/NO_TRADE, cache evidence SHA-256 fail-closed, serial dependent state, no workflow/PR merges or live orders.

Next: source owners independently prove official original filing period/available-at and official KRX tradability with immutable raw SHA, then independently reconcile anchor response/private state and archived manifest. Only after all source gates pass can the frozen one-time M20 evaluation be separately authorized.
