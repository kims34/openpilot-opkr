# IndexAlert isolated read-only gate — 2026-10-25 20:24 KST

Scope: integration/economic admission and separate offline execution optimization audit only. This note is not PIT admission, financial performance approval, order permission, or a specialist code change. The previous isolated audit is commit `c99cb0e9fbfe764db955f00b2358ffbb872fd2c5` (19:51 KST). **No newly admissible market/economic evidence in this cycle.**

## Freshly queried Git refs (GitHub connector, read-only)
- Research `index-alert-research-v1`: **`3b8b7830612a6284d7c7a60628cb527cb741627a`**; GitHub compare against that SHA returned `identical`, ahead=0, behind=0.
- Development `index-alert-position-regen-fix-v1`: **`1e6367d2863a86c3470da13d81a955d277eba485`**; compare returned `identical`, ahead=0, behind=0.
- Integration Draft [#414](https://github.com/kims34/openpilot-opkr/pull/414) pre-note HEAD **`c99cb0e9fbfe764db955f00b2358ffbb872fd2c5`**, base research SHA above; existing gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob **`984c933651f39f1ee9e26a1d7ac3893aaa5335be`**. Latest prior HEAD commit changed only a dated isolated audit document.
- OpenDART Draft [#412](https://github.com/kims34/openpilot-opkr/pull/412): **`e82b26e2431ea15a42888f073a4b0b72a2e11ef6`**.
- Runtime Draft [#413](https://github.com/kims34/openpilot-opkr/pull/413): **`f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`**.
- Independent one-runner Draft [#418](https://github.com/kims34/openpilot-opkr/pull/418): **`2f98401cc50a6c6a25808a98516efd5bf0c944ee`**; based on #413, not directly on research.
- KRX [#420](https://github.com/kims34/openpilot-opkr/pull/420): **`fab3cbbd63a951a4e081f9e7f08c1391ca308581`**; [#422](https://github.com/kims34/openpilot-opkr/pull/422): **`c14857620973531013799e44625d43080904fd5f`**; [#423](https://github.com/kims34/openpilot-opkr/pull/423): **`0e38004363cac9fc4475556b3a1c445de9af407f`**. Earlier #404 closed, not merged.

## Independently re-read CI job results and selected raw job logs
- [#413 Actions 38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): **6/6 SUCCESS**. Exact-parity job `115670744341` raw log shows fixed 34-case identity/outcome SHA-256 **`5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`**, `actual_backtest_speedup_measured=false`, `ci_end_to_end_speedup_measured=false`, `admissible_profitability_generated=false`, `ordering=false`. PASS **offline parity only**; not a full-backtest speed or profitability PASS.
- [#418 Actions 39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395`: **FAIL**. Raw log exact `SourceDriftError`: `research_v1_runtime_manifest.py` archived expected Git blob **`108f66714602a1bd3ae42c34dcca7c16e38f460b`**, observed candidate **`e0055c66c59398fd4a1158077446d886b54c4e37`**. This is a proven code-source identity mismatch/fail-closed, **not** proof of financial source corruption. Same log says 22 distribution versions checked but exact wheel hashes **false**; whole transitive/native environment remains NOT VERIFIED. Do not re-pin the archived baseline, merge or authorize cache from this.
- [KRX Actions 39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438): synthetic-no-provider job `119612852155` SUCCESS. Raw test names explicitly block historical 2021/2022 calendar extrapolation and confusing zero rows with exchange closure. This is **offline policy behavior only**; 1,565/1,565 stored original weekday pairs remain prior *storage-integrity* PASS, while 90 market-day gaps, 27 invalid OHLC, 12,003 zero-activity samples and historical official tradability/corporate actions/fills are NOT VERIFIED or vetoed.
- [OpenDART official Actions 39721626218](https://github.com/kims34/openpilot-opkr/actions/runs/39721626218): **2/2 SUCCESS**, official job `119636230778` raw log explicitly asserts bounded 2022 original-to-2026-10-21 index continuity, one corrected 2022 Q3 edition, zero added attachments; uploaded artifact ID **`12401173549`**, ZIP SHA-256 **`8deb40bd1fa9714277346d052f346dd570894bc5a356d63fcdd5580ef4d8b4d2`**. This is *issuer index inventory* only, not first-original 2022/2021 CFS standalone 3-month profit, accounting period/sign/unit, exact public available-at, immutable vintage financial-cell lineage or issuer/security PIT. Later Oct22 read-only narrow census [39884243351](https://github.com/kims34/openpilot-opkr/actions/runs/39884243351) remains prior bounded result, not a new financial fact.
- Prior [Watchdog 40167777488](https://github.com/kims34/openpilot-opkr/actions/runs/40167777488) SUCCESS only attests CI-side `M20 PIT NOT ATTESTED; orders DISABLED; Holdout NOT AUTHORIZED`, not Railway live order configuration. Prior prospective chronology [39972035700](https://github.com/kims34/openpilot-opkr/actions/runs/39972035700) HTTP 404 and skipped dependent validation remain unresolved. Neither was rerun or bypassed.

## Railway access boundary
A fresh **read-only `list_projects` attempt** returned `User input required but current turn is running in a non-interactive mode`. No project ID could be resolved for a supported direct `list_deployments` / `get_logs` call. No authentication bypass or alternate endpoint probing. Current Railway deployment SHA, log state, actual `ORDERING` and broker permissions are **NOT VERIFIED**. Interactive Railway connector authorization by the account owner is required for future direct read-only attestation; no authorization/permission change attempted here.

## Gate matrix and no-go
| Independent evidence gate | Verdict |
| --- | --- |
| Git ref and CI metadata / fixed 34-case offline parity | **PASS (limited)** |
| Original OpenDART 2022 first ZIP SHA and bounded amendment-index inventory | **PASS (historical source-only)**; source bytes not freshly downloaded this cycle |
| First original 2022/2021 standalone Q3 3-month CFS profit, period, sign, unit, correction financial-cell lineage, exact first-public available-at | **NOT VERIFIED** |
| Historical issuer/security as-of identity; KRX official market sessions, halts, delisting, CA, tradability and realistic fills | **NOT VERIFIED / fail-closed** |
| #418 archived code SHA parity | **FAIL**; exact wheel/native transitive integrity **NOT VERIFIED** |
| Full CI / actual admitted-data H5/M20 backtest acceleration | **NOT VERIFIED** |
| Independently attested cost/slippage/tax and after-tax NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness | **NOT VERIFIED** |
| Railway live state and prospective chronology anchor | **NOT VERIFIED / chronology historical run FAIL** |
| M20 PIT admission and M20 profitability execution | **NO-GO / PROHIBITED** |

Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV, independent consumed Holdout, Champion/Top3/NO_TRADE and all original cost/tax/risk/promotion criteria. `ORDERING=false` is mandatory; **actual live configuration unverified**. Cache only if independently approved source/data/code/Frozen/runtime/evidence SHA-256 all match, fail-closed; parallelize independent read-only postprocessing only, never dependent retraining or capital transitions. No M20 return/alpha search, no Holdout reuse, no strategy parameter modification, real orders, funds, accounts/credentials/permissions, deployment, PR merge or Champion promotion.

Next evidence must come from *specialist owners* (OpenDART original authoritative financial facts and historical public chronology; KRX official private-original market identity/tradability/CA; #418 complete source/dependency identity; Railway authorized read-only operator incident triage). No duplicate specialist code edits or new economic trials in this integration run.
