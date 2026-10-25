# IndexAlert isolated read-only verification — 2026-10-25 20:46 KST

**Scope:** independent integration gate, not an original-market-data attestation, PIT approval, M20 performance run, optimization benchmark, order authority, or specialist code change. This note supplements the 20:24 KST audit at PR #414 HEAD `20b543ff78f8b03fcd9087244c3fd2ac50ca65f0`. No changes to specialist-owned code, workflow, or branch.

## Directly checked immutable refs (GitHub connector)
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (resolved through commit fetch).
- Draft PR #414 before this note `20b543ff78f8b03fcd9087244c3fd2ac50ca65f0`, existing gate doc Git blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; #412 `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. **Historical record correction:** PR #404 is CLOSED **MERGED** at `2026-10-12T12:46:24Z` (direct GitHub PR metadata); previous 20:24 audit said closed/not merged. This historical merge is not permission for any present Draft merge or PIT/financial admission.

## Newly re-opened actual CI jobs and raw logs (limited scope)
- [Watchdog run 40167777488](https://github.com/kims34/openpilot-opkr/actions/runs/40167777488), job `121092240087`: SUCCESS; actual log explicitly prints `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Artifact ZIP SHA-256 printed `c0f90b91564348a8c958edab0ffcc958f5dcc7004e01a9aa2b89ae9935dd8b8b`. CI-side only; live Railway settings NOT VERIFIED.
- [Prospective chronology run 39972035700](https://github.com/kims34/openpilot-opkr/actions/runs/39972035700), job `120476944660`: FAIL with HTTP 404 on anchor fetch, validation job `120476947705` SKIPPED. No chronology/PIT proof from that run. No retries or endpoint probing.
- [OpenDART original-receipt offline guard run 39884427765](https://github.com/kims34/openpilot-opkr/actions/runs/39884427765), job `120189157379`: SUCCESS for synthetic/no-network checks; raw log retains `m20_feature_pit_admitted=False`, `m20_performance_run_authorized=False`, `ordering=DISABLED`. No first-original standalone 2022/2021 Q3 CFS cell or precise public available-at attested.
- [KRX run 39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438), job `119612852155`: SUCCESS for no-provider synthetic checks; explicit tests reject inference of historical exchange closures from zero activity and reject wrong market/status labels. Not a direct Railway private-source or official per-security trading-state comparison.
- [#418 run 39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395`: FAILURE persists (archived source identity mismatch from previous independently reviewed raw log); no re-pin, cache admission, merge or actual backtest speed claim.
- #413 original 34-case pinned SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` remains prior limited offline parity evidence, not economic or full-CI speed evidence. No new market/strategy experiment.

## Railway read boundary
Fresh read-only `list_projects` returned `User input required but current turn is running in a non-interactive mode`. Project IDs and latest deployment/runtime logs unavailable. No alternate endpoint, authentication workaround, deployment, credentials or permission change. **Actual production ORDERING setting NOT VERIFIED**; required policy `ORDERING=false` unchanged.

## Gate verdict
| Gate | Verdict |
|---|---|
| Exact GitHub PR refs and selected CI job statuses/logs | PASS (limited metadata/log read) |
| Historical 2017–2022 stored original day/master SHA | Prior storage-only PASS; original private bytes not re-read this cycle |
| Original first-filing CFS standalone 2022/2021 Q3 earnings, period/sign/unit/correction lineage, exact public available-at | NOT VERIFIED |
| Historical issuer/security PIT mapping, official KRX cash-market calendar, halts/delist/corporate actions, executable fills | NOT VERIFIED / FAIL-CLOSED |
| Cost/slippage/tax source attestation, after-tax NetEV/PF/CAGR/MDD/ES95/99, concentration, temporal robustness | NOT VERIFIED |
| #418 archived implementation SHA equivalence | FAIL; complete wheel/native dependency integrity and real speedup NOT VERIFIED |
| Prospective chronology anchor 39972035700 | FAIL (HTTP 404), downstream validation SKIPPED |
| Railway live deployment, logs, ORDERING flag | NOT VERIFIED (interactive connector authorization required) |
| M20 PIT admission and M20 economic run | NO-GO; run PROHIBITED |

Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV, sealed consumed Holdout, Champion, Top3/NO_TRADE, fixed costs/tax/risk/promotion gates, and `ORDERING=false`. Cache is fail-closed unless independently approved source/data/code/policy/runtime/evidence SHA-256 match; only independent read-only postprocessing may be parallelized. No new market returns, model search, H5/Holdout reuse, live orders, funds, credentials, permissions, deployment, PR merge or Champion promotion.

**Next admissible evidence:** specialist-provided first-original OpenDART CFS cells and public chronology, official private KRX per-session/per-security identity/tradability/CA proof, full #418 immutable implementation/dependency lineage, and authorized read-only Railway attestation. Avoid overlapping specialist code work.
