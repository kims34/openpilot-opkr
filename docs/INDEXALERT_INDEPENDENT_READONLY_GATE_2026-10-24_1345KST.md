# IndexAlert independent read-only gate — 2026-10-24 13:45 KST

Scope: independent orchestration audit only. No source-PIT admission, market economic test, H5/consumed Holdout reuse, Champion change, live orders, account changes, deployment, workflow modification, PR merge, or other workstream code edits.

## GitHub exact refs and provenance

Read directly from GitHub API at this run:
- research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- integration Draft PR #414 pre-write HEAD: `f8b2de93e43cc7b93d7eb19a8172c87561854dcd`; integration gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` Git blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be` (not SHA-256).
- OpenDART Draft PR #412: `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`
- optimization Draft PR #413: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`
- downstream single-runner Draft PR #418: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`
- KRX Draft #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All remained draft/open/unmerged.

## Actual CI evidence inspected

- [Watchdog #40045981668](https://github.com/kims34/openpilot-opkr/actions/runs/40045981668) completed SUCCESS, job `120727693995`. Raw log: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This attests to the GitHub read-only watchdog policy, not current Railway production configuration.
- [Prospective chronology anchor #39972035700](https://github.com/kims34/openpilot-opkr/actions/runs/39972035700) FAILURE, job `120476944660`: request to `/anchor/latest` returned HTTP 404; chronology branch check, hash-only record creation and append SKIPPED; validation job SKIPPED; no artifact reported. The endpoint's root cause is not established and no chronology or PIT approval may be inferred. This is consistent with previously known source-chronology blockers.
- [OpenDART #39884492812](https://github.com/kims34/openpilot-opkr/actions/runs/39884492812) 2/2 offline source-boundary and digest tests SUCCESS. These are synthetic/original-payload software checks, not first-public original financial semantics.
- [OpenDART #39884243351](https://github.com/kims34/openpilot-opkr/actions/runs/39884243351) bounded official index receipt success on Oct 22, previously reviewed. Do not infer earliest original filing, amendment lineage or available-at from a later bounded index.
- KRX Draft #420/#422/#423 are offline gates only. Historic 1,565/1,565 weekday private-pair SHA storage-integrity PASS is a prior reported narrow result; independent private-source byte rehash, exact official calendar, per-security as-of status, corporate actions, fills, and 27 nonpositive-OHLC security exclusions remain NOT VERIFIED.
- Optimization #413 historical 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` refers to frozen synthetic test identity, not official returns. #418 archived original-source SHA gate FAIL CLOSED; limited candidate-only pass cannot establish transitive import/wheel/native closure, production CI acceleration, or merge eligibility.

## Independent decisions

**PASS (limited):** GitHub branch/PR identity reads; latest watchdog policy/offline CI; narrow previously reported source-storage and bounded-index checks within their stated scopes.

**FAIL CLOSED:** #418 original archive SHA mismatch; latest prospective chronology anchor HTTP 404 with downstream jobs skipped. Neither may be bypassed.

**NOT VERIFIED:** 2022 and 2021 first-filed July–September three-month consolidated operating-profit values with period/unit/sign, exact first public available-at and full correction lineage; historical issuer-to-security PIT mapping; official KRX market/security tradability and corporate actions; realistic fill, commissions, tax and slippage; independently validated after-tax NetEV, PF, CAGR, MDD, ES95/ES99, concentration, date-cluster and WF robustness. Therefore M20 economic run NO-GO.

**Railway:** read-only list_projects call blocked with `User input required but current turn is running in a non-interactive mode.` No current production deploy/log/ORDERING attestation; no interactive auth, token or permission changes attempted.

Preserve Frozen H5, M20 horizon20/purge20 and WF504/126/126, PIT/label/Purged/CPCV, sealed Holdout, Champion/Top3/NO_TRADE, all original cost/tax/NetEV/fill/risk/promotion gates. Require `ORDERING=false`. Do not parallelize dependent retraining/capital transition; any cache requires independent approved original source/data/code/frozen policy/runtime/evidence SHA-256 match and fail-closed rejection.

Next bounded evidence: OpenDART original CFS 3-month cell plus first-public clock and amendment chain; KRX actual official as-of trade-state and corporate-action source reconciled to private raw-pair SHA; #418 immutable dependency closure and total CI wall-time without baseline rewrite; Railway read-only operational attestation only after normal interactive authorization. No writes outside this isolated document.
