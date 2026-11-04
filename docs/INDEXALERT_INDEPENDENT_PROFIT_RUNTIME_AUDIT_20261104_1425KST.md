# IndexAlert independent profitability/runtime audit — 2026-11-04 14:25 KST

Read-only source/CI/Railway evidence review. No strategy, workflow, data, broker, deployment, order, model or financial backtest changes. **Not an M20 PIT admission.**

## Source and PR provenance (direct connector read this cycle)
- Branch search finds `index-alert-research-v1`, `index-alert-position-regen-fix-v1`, and `indexalert-independent-audit-20261104-0222kst`. Branch-search response does not expose commit SHA; exact live branch HEADs **NOT VERIFIED**. README.md path fetch failed; not evidence of missing branch.
- Draft, OPEN, unmerged PRs: [#412](https://github.com/kims34/openpilot-opkr/pull/412) HEAD `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [#413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [#414](https://github.com/kims34/openpilot-opkr/pull/414) `18c5418d9684d1717df58261ea27f28e514385b2`; [#418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`, [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`.
- Direct fetched gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; it explicitly preserves M20 no-go. Exact PR head SHA is **not** automatically a content SHA-256.
- KRX #422/#423 compare *candidate* historical day sets, not proof that official private stored exact day sets were independently reconciled.

## Direct Actions jobs (2026-11-04)
- [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417): 6/6 SUCCESS; [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223): 6/6 SUCCESS; [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311): 6/6 SUCCESS.
- [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): 1/1 SUCCESS; [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): 2/2 SUCCESS.
- [41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296): auto-anchor FAILURE; validation SKIPPED. Chronology anchor **FAIL/BLOCKED**.
- 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic cases and serial 2.9656s vs concurrent 2.6209s (regression-phase 1.1315x) are **prior reported results, not independently recomputed this cycle**. Full CI wall time and official PIT backtest speed **NOT VERIFIED**.

## Direct Railway production evidence
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`. KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS (2026-10-12 13:07 UTC), deployed commit `1e6367d2863a86c3470da13d81a955d277eba485`; PIT rebuild `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS; runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS.
- Query 2026-11-04 13:00–14:30 KST: KRX worker deploy log **0 entries**, PIT rebuild deploy log **0 entries**. Runtime returned 101 entries (requested limit 100, service-side response) through 14:26 KST; Investing USD/KRW HTTP errors followed by Yahoo fallback and a probability-audit 3.2 safe fallback log. These are operational observations only, not PIT or investment validation.
- Prior private KRX 2017–2022 1,565/1,565 weekday original-pair storage hash integrity **historical PASS, not rehashed this cycle**; 90 ambiguous dates, 12,003 zero-activity records and 27 OHLC concerns remain excluded from tradability approval.

## Independent gate verdict
- OpenDART original filing/first public available-at, 2021/2022 initial consolidated standalone three-month operating profit and amendment/period lineage: **NOT VERIFIED, fail-closed**. 15 candidate row signatures and successful shape CI do not prove semantic values or timestamps.
- Historical corp/security mapping; KRX official calendar/status/corporate actions, fill feasibility, costs/taxes: **NOT VERIFIED, fail-closed**.
- Frozen H5/consumed Holdout and Dynamic cannot be re-used as independent validation. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and all cost/tax/risk/promotion thresholds unchanged.
- Annual after-cost-and-tax risk-adjusted return, NetEV, PF, CAGR, MDD, ES95/99, concentration and time robustness: **NOT EVALUABLE; M20 NO-GO**. No M20 economic run.
- Offline-only software CI: **limited PASS**; actual official backtest acceleration **NOT VERIFIED**. Cache must fail closed on approved independent source/data/code/Frozen/runtime/approval evidence SHA-256 equality. Parallelize only independent read-only postprocessing; never dependent refitting/capital transitions.
- `ORDERING=false`; no trading, funding, credential changes, Champion promotion, PR merge, automatic merge, workflow edit or deployment.

## Next safe actions
1. Source specialist: independently pin first-filed source and available-at/period/amendment lineage; resolve failed chronology anchor.
2. KRX specialist: compare authenticated private exact day sets to official historical calendar, market status, corporate actions, security mapping, fills and tax/cost constraints; do not infer PASS from candidate comparators.
3. Runtime specialist: inspect full CI logs/artifact SHA and measure true wall-clock only with synthetic offline tests; do not launch official M20 or alter frozen protocol.
4. After all independent source/PIT/tradability gates PASS, seek separate express authority for a single preregistered M20 economic evaluation.
