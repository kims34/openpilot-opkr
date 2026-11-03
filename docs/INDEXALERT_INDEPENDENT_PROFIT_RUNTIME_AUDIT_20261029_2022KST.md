# IndexAlert independent profitability / isolated runtime audit — 2026-10-29 20:22 KST

> Read-only evidence review. This file is **not** source PIT approval, performance authorization, trading permission, deployment approval, or a new model experiment. All recorded SHAs are source/commit or prior-evidence fingerprints; no official raw files were newly rehashed. Do not merge this Draft PR automatically.

## Scope and pinned GitHub heads at this review

Repository: `kims34/openpilot-opkr`.

| Source | Exact HEAD SHA | Review |
| --- | --- | --- |
| Research `index-alert-research-v1` | `3b8b7830612a6284d7c7a60628cb527cb741627a` | frozen research; unchanged |
| Development `index-alert-position-regen-fix-v1` | `1e6367d2863a86c3470da13d81a955d277eba485` | no runtime changes |
| OpenDART Draft PR #412 | `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` | first-filing semantics/PIT not admitted |
| Runtime Draft PR #413 | `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` | offline parity only |
| Integration Draft PR #414 | `473b2ba3e2f22840443a27948485a6e35b275960` (pre-document write) | integration evidence, not M20 admission |
| Investor flow Draft PR #416 | `053de553646fc4765d2616544ca1e8d6bbdde35f` | separate specialist; no source admission |
| One-runner Draft PR #418 | `2f98401cc50a6c6a25808a98516efd5bf0c944ee` | independent offline-only experiment |
| KRX Draft PR #420 | `fab3cbbd63a951a4e081f9e7f08c1391ca308581` | synthetic calendar/exception guard |
| KRX Draft PR #422 | `c14857620973531013799e44625d43080904fd5f` | synthetic 2021 comparison |
| KRX Draft PR #423 | `0e38004363cac9fc4475556b3a1c445de9af407f` | synthetic 2022 comparison |

All listed PRs remain **open Draft**, not merged. #418 reported base snapshot SHA `ca6c5d915d2c0e018f4aa9f82b4488038c16f8d3`, whereas current #413 head is `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; do not treat the earlier base snapshot as the current branch tree or silently re-pin the archived source evidence. #414 pre-write HEAD must be distinguished from this audit commit.

## GitHub Actions and source evidence reviewed

- [OpenDART #412 Actions 40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758) and [40263181687](https://github.com/kims34/openpilot-opkr/actions/runs/40263181687) completed SUCCESS for offline source-shape/edition guards. Previously recorded official [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) original/correction SGML operating-profit *candidate* rows and adjacent numeric signatures 15/15 agree, but do not prove the 2022/2021 original 3-month **consolidated** operating-profit cells, period/sign/units, amendment lineage, earliest public available-at, or issuer/security historical mapping. Previously recorded 2022 original ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` and correction `606be9d03928808f0a2a05f052444587bd2457bdef7a47a8f4bff3d2ea098a30` were **not newly rehashed**.
- KRX [#420 Actions 39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438), [#422 39001836000](https://github.com/kims34/openpilot-opkr/actions/runs/39001836000), [#423 39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) are completed SUCCESS in synthetic/offline scope only. Prior Railway historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c` 2017–2022 private stored 1,565/1,565 weekday daily/master pairs integrity PASS is *previous evidence*, not a fresh private SHA rehash; 90 calendar/source gaps, 12,003 zero-activity samples and official per-security status/halts/delistings/corporate actions/fillability are NOT VERIFIED.
- [#413 Actions 38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) six jobs SUCCESS, exact-parity job `115670744341` re-read: immutable 34-case identity/outcome SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` PASS. Offline parity does not prove faster end-to-end CI or official backtest.
- [#418 one-runner Actions 39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562), job `117628139856` SUCCESS. Re-read logs: 34-case digest matches, synthetic safety tests pass; prior 2.3911 s serial vs 2.0755 s parallel is **test-phase only** (about 1.1521x), both-mode validation wall 4.4674 s, full CI/official M20 speed NOT VERIFIED. Artifact ZIP SHA-256 from Action log: `0a07b46bdc93081b1783a89c1b5b3a1128d06cb86941028c936035c0c6713131`.
- [#418 merged-context Actions 39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395` FAILED before regression with `SourceDriftError`: `research_v1_runtime_manifest.py` archived expected Git blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Direct file reads at current #413/#418 branches confirmed those blob SHAs. The #413 implementation explicitly rejects missing/non-boolean holdout/live authority fields and follows no symlinks; #418's stale version only rejects literal `True` and has weaker local file-open handling. This is a **semantic safety difference**, not a harmless hash-only change. Do not change the pinned digest to force PASS. **Cache FAIL-CLOSED**; no economic reuse.
- Other specialist [#416 Actions 40262192831](https://github.com/kims34/openpilot-opkr/actions/runs/40262192831) completed SUCCESS for isolated source-boundary checks, not market or M20 admission.

## Railway production read-only evidence (2026-10-29)

Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. `describe_environment` returned **staged=null** and no service marked with staged changes. No environment mutation, credential access, deployment or order was attempted.

Latest Kiwoom real-readonly deployment `a77fb922-b679-4d88-92c4-03054ec579cd` created 2026-10-29 06:21:36 UTC (15:21 KST), SUCCESS, source commit `85bb6fd10bcc9ff2b14abe1c774f0d99f8eb84ab`; deploy log contains two startup lines and does not attest active process health or trading authority.

Fresh prospective `indexalert-pit-rebuild` deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` service log observed **through 2026-10-29 11:15:51 UTC (20:15:51 KST)**. Latest session `2026-10-29` still has `error_reason_code=COMMON_OHLC_NONPOSITIVE`, 27 nonpositive/zero-volume-value common-stock rows of 803, `independent_source_admission_verified=false`, `fresh_alpha_observation_admitted=false`, `ordering=DISABLED`, `live_order_authorized=false`, `real_orders_authorized=false`, `funds_movement_authorized=false`, `permission_change_authorized=false`. This is one service's logged flags, not a verified environment-wide ORDERING setting. Historical worker service latest deployment is SUCCESS but the queried recent service log window returned no historical raw-audit lines; do not claim fresh revalidation.

## Independent verdict and next strictly isolated actions

**PASS, limited:** previously evidenced raw-file/storage SHA integrity and immutable 34-case offline test parity; latest observed no-order service flags. **FAIL / FAIL-CLOSED:** merged-context #418 archived source SHA gate; 2026-10-29 prospective common-stock nonpositive OHLC admission; cache and market-input admission remain blocked. **NOT VERIFIED:** 2022/2021 first-filed connected three-month operating income, strict original public available-at/PIT and correction lineage, issuer/security as-of mapping, official historical KRX sessions/trading state/corporate actions/fillability/costs/tax, label/Purged/CPCV and fresh independent Holdout, actual whole-CI and economic backtest acceleration. **NOT EVALUABLE:** frozen M20 after-tax NetEV/PF/CAGR/MDD/ES95/99, annual risk-adjusted net profitability, concentration and temporal robustness. **M20 performance NO-GO**.

Next: OpenDART specialist must attest original 2022/2021 three-month CFS semantics and exact public timestamps without backfill; KRX specialist must independently resolve official calendar/status/corporate actions and 27 invalid OHLC; runtime specialist must reconcile merged-tree permission/source semantics and dependency lock before any cache use, with synthetic/offline-only whole-CI measurement. Integration may admit one frozen M20 evaluation **only after all independent official PIT/market/execution/cost gates PASS** and separate authorization. No H5 consumed Holdout reuse, Dynamic post-hoc tuning, new profitability runs or model search. Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, Champion/Top3/NO_TRADE and tax/cost/risk thresholds. `ORDERING=false` policy, no orders/funds/credentials/Champion promotion, no PR merges or Railway deployments.
