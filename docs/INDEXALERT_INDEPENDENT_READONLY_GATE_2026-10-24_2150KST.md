# IndexAlert independent read-only gate — 2026-10-24 21:50 KST

Scope: orchestration-only audit; no trading, no PIT admission, no M20 economic run, no official market replay, no Holdout reuse, no specialist code edits, no deployment or merge. Read-only GitHub connector evidence plus attempted read-only Railway access.

## Live GitHub references (fetched in this run)
- research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a` (fetch_commit ref)
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (fetch_commit ref)
- PR #414 (Draft/open) integration HEAD **before this audit** `2b496058994cee20bed532e9780ec91ab04d6132`; source gate document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` Git blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- PR #412 (Draft/open) OpenDART HEAD `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`.
- KRX #420 / #422 / #423 (Draft/open): `fab3cbbd63a951a4e081f9e7f08c1391ca308581` / `c14857620973531013799e44625d43080904fd5f` / `0e38004363cac9fc4475556b3a1c445de9af407f`. #404 is closed; not evidence of independent source admission.
- Offline runtime #413 / #418 (Draft/open): `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` / `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.

## Independently inspected CI logs, limited to their exact claims
- Watchdog [run 40031477539](https://github.com/kims34/openpilot-opkr/actions/runs/40031477539), job `120680506053`: SUCCESS, logged `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Uploaded ZIP digest reported by GitHub Actions: SHA-256 `2e9c77a946db71f44011b2390d0b4e6b19917249d9f014991ea956a12b8c9de8`, artifact `12535331611`. Digest is **Action-attested only**; ZIP not independently downloaded and rehashed. Job flags are **not** live Railway environment verification.
- OpenDART [run 39884243351](https://github.com/kims34/openpilot-opkr/actions/runs/39884243351), official-source job `120188625190`: SUCCESS; narrow 2026-10-22 census did not establish original 2022/2021 CFS standalone three-month operating-profit cells or exact first-public instant. Uploader-attested artifact SHA-256 `02e829d3a5fdde8754f649431363c74221eb192b78b8237c911f74b54325820c`. [Runs 39884427765](https://github.com/kims34/openpilot-opkr/actions/runs/39884427765) and [39884427805](https://github.com/kims34/openpilot-opkr/actions/runs/39884427805) are synthetic/offline source guard PASS, not original-filing semantic PIT proof.
- KRX [run 39721289545](https://github.com/kims34/openpilot-opkr/actions/runs/39721289545), job `119635081965`: SUCCESS on metadata/offline XLSX/holiday and fail-closed tests, not private original official date/state/corporate-action/fillability reconciliation.
- Runtime #418 [run 39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395`: FAIL on immutable archived regression-source identity; archived CI environment versions match, but wheel file hashes and native dependency identity remain unverified. Runtime #413 [run 38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): six jobs SUCCESS; regression-phase parity is not proof of end-to-end official backtest acceleration.

## Independent admission matrix
| Gate | Verdict | Reason |
|---|---|---|
| Git branch and PR HEAD identity | PASS (metadata only) | Connector returned immutable commit SHAs above; not source-byte rehash |
| CI safety assertions / synthetic tests | PASS (narrow only) | Named successful jobs and log lines |
| OpenDART first-original CFS 2022 and 2021 3-month operating profit, exact public available-at, correction lineage | NOT VERIFIED | Original-edition account semantics and timestamps not independently proven |
| Historical issuer-security PIT mapping | NOT VERIFIED | No independently authenticated point-in-time map |
| KRX official trading day/state, delisting/halts/corporate actions, fillability | NOT VERIFIED | Offline source-shape tests are not official per-day reconciliation; prior 90 uncertain sessions and 27 bad OHLC remain blocked |
| Realistic costs, commissions, taxes, slippage | NOT VERIFIED | No admitted execution/cost source panel |
| NetEV/PF/CAGR/MDD/ES95/99, return concentration, temporal robustness | NOT VERIFIED / NOT EVALUABLE | No admitted source, M20 economic run prohibited |
| #418 archived-source identity | FAIL (existing CI) | Fail-closed SHA gate |
| Production Railway deployment/logs and actual ORDERING | NOT VERIFIED | `list_projects` returned `User input required but current turn is running in a non-interactive mode.` |

## Decision / next admissible work
**M20 PIT NO-GO; M20 profitability RUN NO-GO.** Preserve Frozen H5, horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV, independent sealed Holdout, Champion, Top3/NO_TRADE, all cost/tax/risk and promotion gates. Require `ORDERING=false`; no claim that Railway production value was checked. OpenDART specialist owns original first-public/CFS lineage; KRX specialist owns official as-of tradability/corporate-action reconciliation; runtime specialist owns archived-source and transitive environment identity. This audit does not duplicate their tests. Railway requires interactive connection authorisation before operational attestation. No workflow/security workaround, model exploration, live order, funds, account access change, deployment, merge, or promotion.
