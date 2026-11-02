# IndexAlert independent profitability / isolated runtime audit — 2026-11-02 16:30 KST

**Scope:** read-only evidence refresh, no financial backtest, no official new source acquisition, no source PIT admission, no order/merge/deploy/workflow edit. This independent audit branch was created from prior audit commit `e866d4eb6c671c397deca20cf37398fc19ba894f`. Existing PR #412/#413/#414/#418 and other owners' code are untouched.

## Exact fresh GitHub source refs

GitHub REST branch GETs (2026-11-02 ~16:30 KST):
- research `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`;
- development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`;
- KRX `indexalert-krx-pit-source-audit-20261013` HEAD `073d2d49e95f69fb10b943b93e51bb179fb3c698`.

Direct PR metadata GETs:
- #412 DART `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` (Draft);
- #413 isolated runtime `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` (Draft);
- #414 orchestration `86c490be6407067224a1124319ab415f33965bf7` (Draft, updated 2026-11-02T06:45:40Z);
- #416 investor flow `053de553646fc4765d2616544ca1e8d6bbdde35f` (Draft);
- #418 single runner `2f98401cc50a6c6a25808a98516efd5bf0c944ee` (Draft);
- #420 KRX session review `fab3cbbd63a951a4e081f9e7f08c1391ca308581`;
- #422 2021 calendar `c14857620973531013799e44625d43080904fd5f`;
- #423 2022 calendar `0e38004363cac9fc4475556b3a1c445de9af407f`.
- #404 KRX original pairs `1aef2de445b05883353a1d668acd89b194abbeab` (historical owner track).
- #414 immutable core gate document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be` (fetched from #414 head).

## Independently read original CI job evidence

- [Latest Watchdog #41368406818](https://github.com/kims34/openpilot-opkr/actions/runs/41368406818), job `125033414398`: **SUCCESS**, 2026-11-02T00:40Z; original log explicitly: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This is software governance, **not** official market/source approval.
- [#413 Actions #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): six of six jobs SUCCESS; parity job `115670744341` original log `RUNTIME_OPT_PARITY`: `cases=34`, digest SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, `test_outcomes_identical=true`, serial 1.7650 sec vs longest parallel 2.7079 sec, test-phase speed ratio **0.652x**. **PASS limited to frozen offline equality, FAIL as demonstrated speedup on this run**, actual backtest and whole CI speedup **NOT VERIFIED**.
- [#418 original offline one-runner #38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): one job SUCCESS, original job `115373285730` shows 34-case same digest, serial 2.9656 sec, parallel 2.6209 sec, **1.1315x test-phase**; official backtest and end-to-end CI not measured.
- [#418 later run #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395`: **FAIL** with `SourceDriftError: archived blob mismatch: research_v1_runtime_manifest.py expected=108f66714602a1bd3ae42c34dcca7c16e38f460b observed=e0055c66c59398fd4a1158077446d886b54c4e37`. Archived provenance gate stays **FAIL-CLOSED**; do not repair by silently replacing expected digest. Full archived wheels/OS dependency identities are also unverified.
- [OpenDART #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742), official job `115372636726`: SUCCESS for original-vs-corrected SGML candidate-row shape; 15 original and 15 amended candidate rows, same numeric-adjacent signature multiset, but all explicit `original_cfs_q3_2022_2021_three_month_profit_verified`, `historical_publication_instant_pit_verified`, `full_correction_lineage_verified`, `historical_corp_security_mapping_verified`, `m20_performance_run_authorized` are **false**.
- [Anchor fetch #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151), job `124184971844`: FAILURE, final `urllib.error.HTTPError: HTTP Error 404: Not Found`; 20 attempted proxy requests for `GET /anchor/latest` are 404 in Railway HTTP evidence. No response-body/private anchor file proof; **cannot conclusively attribute cause**.

## Railway production evidence (read-only)

Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. `describe_environment` returned `staged=null`, while `environment_status` returned pending `patch:e113dacb-6705-4416-9997-dc694539d382` (staged, empty changes): **status-query inconsistency, do not deploy/accept patch**.

- `indexalert-pit-rebuild` service `225f2279-d728-4e1a-a3f3-2447ff0f9dc1`, latest SUCCESS deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, deployed from `e57054ecdb3e734ced3c9a981b887d9b5fc60f97`; replica 1/1 running.
- Latest returned PIT runtime log `2026-11-01T14:46:22.425196674Z` (= 2026-11-01 23:46:22 KST), about 16h44m before this audit. `status=FAIL_CLOSED`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, common stock 803, nonpositive OHLC 27, `source_failure_session=2026-09-28`, `session_manifest_sha256=null`, `fresh_alpha_observation_admitted=false`, `independent_source_admission_verified=false`, `ordering=DISABLED`, all order/funds/permission authority false. Log gap is **not** by itself proof of outage; one replica still running.
- Railway HTTP stream includes 20 `GET /anchor/latest` 404s from 2026-10-29 and 2026-10-30; latest `2026-10-30T17:13:23.750935990Z`. Request path exists in previously reviewed deployed handler code and can return 404 if no valid anchor, but actual response body and private anchor inventory remain **NOT VERIFIED**. Do not infer exact cause from 404 alone.
- `indexalert-runtime` deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, latest returned runtime logs 2026-11-02T07:30:44Z. This is a separate index/FX notification runtime, **not** proof of PIT or market profitability.
- `indexalert-kiwoom-real-readonly` deployment `a77fb922-b679-4d88-92c4-03054ec579cd` marked SUCCESS/online but health reports 0 running, 1 crashed; original last 2026-10-29 log `TOKEN_OR_LOGIN_AUTH`, detail 8050, `ORDERING=DISABLED`. **Status inconsistency / auth unresolved**, do not change account permissions.

## Gate-by-gate decision

| Independent gate | Decision | Reason |
|---|---|---|
| 2017–2022 private KRX 1,565/1,565 weekday pair persisted integrity | **PASS, prior pinned scope only** | Existing verified private receipt/SHA evidence, not a new full private-volume reread |
| Official calendar/session, listing/delisting, corporate actions, execution/lot/tax/cost | **NOT VERIFIED / FAIL-CLOSED** | Private pairs and 90-day/zero-activity classification are not authoritative tradeable state |
| 2022/2021 first-filed original SGML byte/candidate-row identity | **PASS, limited source-shape** | 15 matching candidate-row signatures only |
| Exact first-filed consolidated 3-month operating profit, period and corrections, public available-at, issuer/security history | **NOT VERIFIED / FAIL-CLOSED** | Semantic and historical time-lineage unproved |
| H5/0-N consumed Holdout and Dynamic reuse | **NOT AUTHORIZED** | No retrospective tuning, no new independent reuse |
| #413 34-case offline identity | **PASS, limited** | Pinned SHA-256, no demonstrated runtime speed gain |
| #418 archived manifest provenance | **FAIL-CLOSED** | Original archived SHA mismatch |
| #418 actual full CI / official backtest acceleration | **NOT VERIFIED** | Only offline test subprocess timing |
| M20 horizon20/purge20, WF504/126/126, frozen policy | **PRESERVE** | No mutation |
| M20 after-fee/tax NetEV, PF, CAGR, MDD, ES95/99, concentration, robustness, annual risk-adjusted net profit | **NOT EVALUABLE / NO-GO** | Official source/PIT/tradeability gates blocked |
| Live orders, money, account authority, Champion promotion | **NOT AUTHORIZED** | Explicit separate approval required; `ORDERING=false` |

## Next safe owner-specific actions

1. DART owner: independently bind exact first-filed CFS 3-month facts, period and original-vs-correction lineage, publication timestamp, historical issuer/security IDs to immutable official evidence SHA. Never backfill with later revisions.
2. KRX owner: independently bind official historical trading session, halt/delist/corporate-action, tradeability and realistic fee/tax/lot execution evidence to immutable original SHA; keep 90 uncertain days and 27 suspect OHLC cases vetoed.
3. Prospective owner: inspect **actual HTTP 404 response body** and protected anchor-file inventory through a sanctioned read-only path; distinguish absent artifact vs invalid session vs code response; do not mutate source or grant PIT.
4. Runtime optimization owner: resolve #418 archived manifest provenance with exact original source lineage and adversarial guard equivalence, not hash substitution; only then re-measure offline parity and whole CI, keeping dependent capital transitions sequential and caches SHA-256 fail-closed.
5. Total coordinator: after all independent source and trading gates PASS, seek separate explicit authorization for one frozen M20 economic evaluation. Do not use failed H5 Holdout as a fresh independent test.

**No financial performance experiment, new model search, source PIT admission, holdout access, merge, deployment, workflow change, account/permission modification, or order was performed in this audit.**
