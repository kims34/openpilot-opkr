# IndexAlert independent profitability admission gate — 2026-10-26 13:44 KST

Scope: integration-only read of authenticated GitHub branch/PR/Actions state; no market return run, provider source collection, optimisation experiment, policy mutation, workflow change, deployment, broker operation or merge. This receipt deliberately adds no new source admission. Prior integration receipt: `docs/INDEXALERT_INDEPENDENT_READONLY_GATE_2026-10-26_1316KST.md` (blob `2ecacfa440f71b3865ea07ac95e5f13665957bc8`).

## Pinned HEADs from GitHub REST/PR metadata

- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Integration Draft #414: `ed8b69deaaa6c006b632572722f3cecf0cf81a2c` **before** this receipt; existing integration-gate file blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- Offline runtime Draft #413: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- Isolated one-runner Draft #418: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- OpenDART Draft #412: `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`.
- KRX Draft #420: `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; private 2021 comparator Draft #422: `c14857620973531013799e44625d43080904fd5f`; 2022 comparator Draft #423: `0e38004363cac9fc4475556b3a1c445de9af407f`; historical SHA audit PR #404: `1aef2de445b05883353a1d668acd89b194abbeab`. Draft PRs remain unmerged. Do not conflate #404 non-draft with admission/production approval.

## Independently read current CI evidence and limits

- Official 2021 Q3 first-filed source [run 40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), **job 121379096007**: actual logged source ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, 1 SGML, 1,728 tables, 13 operating-label candidates, **0** same-table exact 2021 Q3/standalone 3-month semantic matches. The job asserted first original archive identity but `original_2021_q3_three_month_cfs_profit_cell_verified=false`, `first_2022_q3_report_2021_comparator_cell_verified=false`, `2021_first_publication_instant_verified=false`, `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, `ordering=DISABLED`. The separately uploaded **900-byte workflow artifact ZIP** ID `12625042488` has GitHub artifact digest `sha256:3fe75e2af23f508d3c518a14e98732a399eb0daeca46cccd7b3191b1e2e4777b` (confirmed by API metadata and job log). **Artifact ZIP digest != official first-filed source ZIP digest**; they identify different objects. Neither artifact digest nor log assertion is an independent second download/hash of the private raw source.
- Newest first-original viewer TOC synthetic-only [run 40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758), job `121379780273`, SUCCESS. No official original CFS financial cell or public-available-at proof; synthetic guard checks are not market PIT. Companion viewer synthetic [run 40263181687](https://github.com/kims34/openpilot-opkr/actions/runs/40263181687) SUCCESS.
- KRX [#420 run 39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438), [#422 run 39001836000](https://github.com/kims34/openpilot-opkr/actions/runs/39001836000), [#423 run 39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925): CI SUCCESS on **synthetic offline controls**; protected original 2021 13-day / 2022 14-day exact-set comparisons **not executed**, and official exchange session, issuer/security status, corporate actions and fillability not independently established. Previously reported 1,565/1,565 private weekday day/master source pairs = storage integrity only; 90 unknown sessions and 27 nonpositive OHLC cases remain quarantined.
- Runtime #413 [run 38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) 34 fixed synthetic regression digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` remains limited PASS; parallel 2.7079s vs serial 1.7650s = 0.652x (slower) in this regression phase, not a financial speed-up. #418 [run 39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) archived source identity FAIL CLOSED; expected Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`; full transitive/wheel/native runtime provenance and end-to-end CI speed-up NOT VERIFIED. No cache approval or re-pinning.
- Railway **read-only** `list_projects` returned `User input required but current turn is running in a non-interactive mode.` Stop; no retry or authentication workaround. Latest Railway deploy/logs and actual running `ORDERING=false` **NOT VERIFIED** (the CI/source flags above do not attest live Railway settings).

## Admission matrix (PASS / FAIL / NOT VERIFIED)

| Required independent evidence | Verdict |
| --- | --- |
| 2021 first original source ZIP hash receipt | PASS (limited CI source identity only; no independent second raw-byte replay) |
| 2022 first original source ZIP / full 2021 and 2022 amendment chronology | historical receipt only / NOT VERIFIED this run |
| First-public available-at, original 2022 and 2021 July–September 3-month CFS operating-income semantics, unit/sign, corrected-vintage lineage | NOT VERIFIED |
| Historical issuer/security mapping, official KRX calendar/status/halts/delist/corporate actions, capacity/fills | NOT VERIFIED |
| Approved cost/slippage/tax and independent after-tax NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness | NOT VERIFIED / NOT RUN |
| #413 immutable synthetic regression identity | PASS (limited) |
| #418 archived implementation identity | FAIL CLOSED |
| Real H5/M20 full CI/backtest speed-up | NOT VERIFIED |
| Railway current deployment/logs and actual ordering-off | NOT VERIFIED |

**Admission decision: M20 PROFITABILITY NO-GO.** Do not run new official market-return experiments, model search or M20 economic evaluation before first-original PIT and tradability approval. Preserve Frozen H5; M20 horizon20/purge20; WF504/126/126; label/PIT/Purged/CPCV; independent sealed and consumed Holdout; Champion/Top3/NO_TRADE; unchanged cost, tax, NetEV, fill, risk and promotion thresholds. `ORDERING=false` is mandatory, not currently runtime-attested. Only fully source/code/policy/runtime/evidence SHA-256-matched fail-closed caches and read-only independent postprocessing may eventually parallelize; no dependent retraining/capital-transition parallelisation. No H5/Dynamic hindsight tuning or Holdout reuse, orders, funds, keys, account rights, production deploy, workflow changes, PR merges or Champion promotion.

Next owner-specific proofs: #412 original financial-cell plus first-publication time and corrections; KRX owner official historic exact-date/tradeability/corporate action as-of and protected-source reconciliation; #418 owner archive/merged-code/transitive dependency identity and true CI profiling. This integration lane made no specialist code edits.