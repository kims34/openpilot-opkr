# IndexAlert independent profitability/source and isolated runtime gate — 2026-10-26 01:18 KST

**Scope:** Fresh read-only GitHub refs, Actions jobs/logs, artifacts and source-governance review. No market-data download, model search, backtest, Holdout, order, funds, permissions, deploy, merge, workflow or policy changes. Railway read-only `list_projects` was attempted and returned `User input required but current turn is running in a non-interactive mode`; NO Railway deployment, logs, source volume, current `ORDERING` or live permissions were inspected. Do not reuse historic Railway data as fresh proof.

## Exact directly fetched GitHub refs

- Research `index-alert-research-v1` HEAD: `3b8b7830612a6284d7c7a60628cb527cb741627a` (GitHub git/ref).
- Development `index-alert-position-regen-fix-v1` HEAD: `1e6367d2863a86c3470da13d81a955d277eba485` (GitHub git/ref).
- Integration Draft [PR #414](https://github.com/kims34/openpilot-opkr/pull/414): pre-document HEAD `73bb25f904d6af1c414afb6fb61658d6686d926e`; `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- OpenDART Draft [PR #412](https://github.com/kims34/openpilot-opkr/pull/412): `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`.
- Offline optimization Draft [PR #413](https://github.com/kims34/openpilot-opkr/pull/413): `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- Dependent single-runner Draft [PR #418](https://github.com/kims34/openpilot-opkr/pull/418): `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX exception Draft [PR #420](https://github.com/kims34/openpilot-opkr/pull/420): `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; 2021 comparator Draft [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`; 2022 comparator Draft [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`. KRX source-integrity [#404](https://github.com/kims34/openpilot-opkr/pull/404) `1aef2de445b05883353a1d668acd89b194abbeab`.

## Independently inspected Actions and exact limited meaning

1. **New latest watchdog evidence:** [Actions #40210551585](https://github.com/kims34/openpilot-opkr/actions/runs/40210551585), created 2026-10-25T16:12:13Z (2026-10-26 01:12 KST), job `121220651879` SUCCESS. Actual log: 4/4 watchdog tests and 31/31 offline governance tests PASS; `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Uploaded artifact `12605301589` SHA256 `38543256b6531cbc51c8da390914920684f119d04e01bc9206f1db29978d469c` matches actual upload log and artifact metadata. **Limited PASS:** ZIP metadata/log digest, governance checks; NOT actual Railway runtime, original KRX/DART SHA or PIT.
2. **OpenDART:** [#39884427765](https://github.com/kims34/openpilot-opkr/actions/runs/39884427765), job `120189157379` SUCCESS, actual log 12 synthetic no-network original-receipt tests PASS. Does not establish first-edition 2022/2021 consolidated July–September three-month operating-profit cells, as-of publication instant or full amendment lineage. Historic original ZIP SHA `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` and amendment ZIP SHA `606be9d03928808f0a2a05f052444587bd2457bdef7a47a8f4bff3d2ea098a30` were not re-downloaded here; 15 SGML candidate rows do not prove semantics.
3. **KRX:** [#39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) job `119612852155` SUCCESS (offline exception); [#39001836000](https://github.com/kims34/openpilot-opkr/actions/runs/39001836000) job `117306218697` SUCCESS (2021 synthetic candidate); [#39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) job `119612335677` SUCCESS, actual log 32 synthetic tests and `DRY_RUN_NO_PRIVATE_STORAGE_READ` assertion. These DO NOT prove private volume exact sets or official exchange sessions. Historic Railway 2017–2022 1,565/1,565 SHA storage pairs are limited historic integrity PASS only, not independently re-read. Unresolved 90 day/session classifications, 27 bad OHLC and zero-activity 12,003 remain excluded from tradable admission.
4. **Optimization #413:** [#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) six jobs SUCCESS. Actual parity job `115670744341` confirms 34 immutable regression identities and case digest SHA256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, and explicitly `actual_backtest_speedup_measured=false`, `ci_end_to_end_speedup_measured=false`, `admissible_profitability_generated=false`. Historic serial 1.7650s vs longest parallel 2.7079s indicates no improvement in that test phase; no full CI or official-market speedup proof.
5. **Independent #418:** [#39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) job `117628139395` FAIL. Actual log `SourceDriftError: archived blob mismatch: research_v1_runtime_manifest.py expected=108f66714602a1bd3ae42c34dcca7c16e38f460b observed=e0055c66c59398fd4a1158077446d886b54c4e37`. Do not re-pin or bypass; source change requires independent approved candidate-tree, dependency and runtime provenance. Separate one-runner probe #39111405562 SUCCESS is limited synthetic/offline CI, not a pass of the failed immutable-source gate.
6. **Chronology:** [#39972035700](https://github.com/kims34/openpilot-opkr/actions/runs/39972035700) auto-anchor FAIL, validation SKIPPED; no uninterrupted prospective chronology assertion.

## PASS / FAIL / NOT VERIFIED (fail closed)

| Gate | Verdict | Exact boundary |
|---|---|---|
| GitHub branch/PR refs and new watchdog artifact log/metadata SHA | **PASS, limited** | Source code refs and 940-byte ZIP upload only |
| Offline synthetic DART, KRX, #413 parity | **PASS, limited** | Synthetic checks cannot admit official source PIT or profit |
| #418 immutable archived blob equality | **FAIL** | Expected/observed blob mismatch above; no cache approval |
| Official first-original DART 2022/2021 Q3 3-month CFS profit; exact public available-at; corrections | **NOT VERIFIED** | No authoritative semantic and temporal PIT |
| Historic issuer/security mapping, KRX official market calendar/status/corporate actions and fills | **NOT VERIFIED** | No official security/date tradability lineage |
| Commission, slippage, taxes, real fill feasibility; after-tax annual risk-adjusted NetEV/PF/CAGR/MDD/ES95/ES99; return concentration and temporal robustness | **NOT VERIFIED / NOT RUN** | M20 economic evaluation prohibited before source admission |
| #413/#418 complete CI or real-backtest acceleration; full wheel/native runtime/evidence SHA chain | **NOT VERIFIED** | CI regression parity is not full environment equivalence |
| Railway latest deploy/log, private source bytes, actual production ordering flag | **NOT VERIFIED / AUTH BLOCKED** | Noninteractive user-input requirement; no workaround |

## Required next evidence and immutable boundaries

- OpenDART specialist: verify exact first-submitted edition, 2022 and 2021 Q3 consolidated standalone 3-month operating-profit values/period/unit/sign, publication time and amendment lineage without amended-value backfill.
- KRX specialist: compare exact private raw SHA/holiday candidate sets against official historic calendar, security status, issuer mapping and corporate actions; keep unresolved zero-activity/invalid OHLC blocked. Independent source, fill, fee and tax proof needed.
- Runtime specialist: keep original immutable 34-case digest, fail-closed source/code/data/Frozen-policy/runtime/evidence SHA256; no cache reuse unless ALL independently admitted. Parallelize only independent read-only postprocessing; never dependent training or capital transitions.
- Integration: **M20 PROFITABILITY NO-GO**. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV, independent Holdout, Champion/Top3/NO_TRADE and original cost/risk/promotion gates unchanged. Consumed H5 Holdout and post-hoc Dynamic results are not independent evidence. `ORDERING=false` is required but not attested live. No official market returns, new performance experiments, tuning, trading, funds, credentials, permission changes, deployment, PR merges or Champion promotion.
- Railway: only a legitimate interactive authorization can unblock read-only production verification; unattended access must not bypass the challenge.

This isolated documentation-only record does not grant any authority or assert a new economic PASS.
