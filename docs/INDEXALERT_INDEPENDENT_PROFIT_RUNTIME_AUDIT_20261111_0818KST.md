# IndexAlert independent evidence gate — 2026-11-11 08:18 KST

Read-only snapshot, not permission to trade, deploy, merge, tune or run M20. Source references are exact URLs; reported historical fingerprints are not independently recomputed in this run.

## GitHub immutable refs

- Research `index-alert-research-v1` HEAD `df474df348f22aa38b1dedaa59fcff66e548b406`.
- Development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`.
- Draft/open/unmerged PR HEADs: [#412](https://github.com/kims34/openpilot-opkr/pull/412) `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [#413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [#414](https://github.com/kims34/openpilot-opkr/pull/414) `18c5418d9684d1717df58261ea27f28e514385b2`; [#418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`, [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`.
- [#414 gate document](https://github.com/kims34/openpilot-opkr/blob/18c5418d9684d1717df58261ea27f28e514385b2/docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md) read from PR HEAD. Prior independently observed blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; not independently rehashed in this run.

## GitHub Actions — current API result

| Run | HEAD SHA | jobs | verdict |
| --- | --- | --- | --- |
| [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417) | `55e7fe2b3fe322e39f817914ff1ed5b589bbe0da` | 6/6 success | PASS offline CI only |
| [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223) | `05d73661bcc879fe0dd66ffcea5fe1f5ee6fbd56` | 6/6 success | PASS offline CI only |
| [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) | `b22e4f39517c2bc38e173e63e8fd52f29a535dad` | 6/6 success | PASS offline CI only |
| [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) | `8f363b8683d34a48754916b34810a5a8bb958896` | 1/1 success | PASS offline CI only |
| [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) | `39af5b0043e122bc0e42935d8813759ff6c1a6e7` | 2/2 success | PASS job completion, source semantics NOT VERIFIED |
| [38498552499](https://github.com/kims34/openpilot-opkr/actions/runs/38498552499) | `bfe1be1b1f3edad94d064d21203c0b13f663c129` | 6/6 success | PASS offline CI only |

Previously reported 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic cases, and 21 integrity cases were **not rehashed or replayed** in this snapshot. Previously reported serial/parallel timings are phase-specific, not proof of end-to-end acceleration. No new benchmarking performed.

## Railway IndexAlert production — current environment status

Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.

- PIT rebuild: SUCCESS deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, running 1/1; Runtime: SUCCESS `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`, running 1/1. This does not prove PIT approval or safe trading.
- KRX worker: SUCCESS deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, replica running 0/crashed 0/total 1: **NOT VERIFIED** operational activity.
- Kiwoom real read-only: SUCCESS deployment `a77fb922-b679-4d88-92c4-03054ec579cd` but replica running 0/crashed 1/total 1: **FAIL runtime replica health**, despite service display state online.
- Backend, Push, db-query-readonly offline; db-query-readonly 1 critical notification.
- One pre-existing staged patch `e113dacb-6705-4416-9997-dc694539d382` has **zero changes**; not committed.
- Requested deploy-log window 2026-11-11 00:00Z to query time: PIT, KRX, Runtime, Kiwoom each **0 returned entries**. Absence of logs is not proof of health.

## Independent source/PIT/economics gate

| Criterion | Decision | Explanation |
| --- | --- | --- |
| 2017–2022 KRX weekday raw-pair storage | Historical scoped PASS only | Prior 1,565/1,565 stored pair SHA integrity; not independently rehashed now |
| KRX official sessions, trading status, corporate actions, fills, tax/costs | NOT VERIFIED — FAIL CLOSED | 90-day uncertain calendar, 12,003 zero-activity rows and 27 abnormal OHLC remain vetoed; storage integrity is not tradability |
| OpenDART original-filing bytes and candidate row signature | Historical scoped PASS only | 2022 SGML 15 candidate rows, adjacent signatures; not proof of period/meaning |
| 2021/2022 original 3-month consolidated operating income, correction lineage and exact public available-at | NOT VERIFIED — FAIL CLOSED | No complete original period/filing-time and correction-chain approval |
| Historical corp/security mapping, label PIT | NOT VERIFIED — FAIL CLOSED | No independent complete provenance approval |
| NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness net of taxes and costs | NOT VERIFIED — NO RUN | Official M20 economic run prohibited pending source and market PIT |
| Optimization software offline CI | PASS in tested scope | Jobs above successful; 34-case SHA not recomputed here |
| Entire CI / official backtest speedup | NOT VERIFIED | Parallel regression phases can be slower; no sanctioned economic benchmark |

## Frozen execution policy and next permitted steps

Keep Frozen H5 and spent holdout sealed; M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE and all cost, tax, execution, risk and promotion thresholds unchanged. `ORDERING=false` required; actual environment variable value not independently inspected this run. No trading, transfers, credential/account changes, Champion promotion, deployment, merge or workflow modification.

Optimization remains isolated offline-only: cache only with matching independently approved source, data, calculation, Frozen protocol, runtime and approval evidence SHA-256, fail-closed; parallelize independent read-only postprocessing only. No dependent retraining/capital-transition parallelism, no performance search. Next gate: independent original-file PIT and KRX tradability provenance, then one pre-registered authorized economic evaluation; verify CI wall-clock independently without changing frozen logic. No blocked write bypass attempted.
