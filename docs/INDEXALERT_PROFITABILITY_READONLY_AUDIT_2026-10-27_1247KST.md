# IndexAlert independent profitability gate — read-only evidence audit
Observed at 2026-10-27 12:47 KST. This is a source/CI-only adjudication, not PIT approval, an economic backtest, an execution authorisation, or a production configuration attestation. No source data, identifiers, amounts, credentials, account details or market orders are included.

## Exact GitHub refs and isolation
- Repository: kims34/openpilot-opkr
- Research index-alert-research-v1: `3b8b7830612a6284d7c7a60628cb527cb741627a` (PR #412/#413/#414 base SHA)
- Development index-alert-position-regen-fix-v1: `1e6367d2863a86c3470da13d81a955d277eba485` (PR #420 base SHA)
- Draft, open, unmerged PRs: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `2bda0b5e3dc7cc33fd3ad3e525ee9fe717ed9c33` (pre-audit HEAD); #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- The integration gate is located on the #414 head branch, not the research base; blob SHA at read: `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. No edits to that shared file or specialist branches.

## Independent PASS / FAIL / NOT VERIFIED
| Gate | Verdict | Independent source |
|---|---|---|
| 2021 first-original OpenDART archive identity | PASS for source identity only | Actions #40262558066, official source job #121379096007: ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`; artifact ZIP SHA-256 `3fe75e2af23f508d3c518a14e98732a399eb0daeca46cccd7b3191b1e2e4777b` |
| 2021 first-original connected 3-month operating-income meaning | NOT VERIFIED | 13 operating-label candidate tables, zero with Q3 period in same table; first public instant false, 2021/2022 original comparative amounts false |
| 2022 first-original vs corrected archive identity | PASS only within previously pinned official original/correction archive evidence; NOT VERIFIED as economic input | PR #412 / integration gate; original and corrected edition identity does not establish account meaning or available-at |
| 2022 and 2021 first-original 3-month CFS earnings, corrections, available-at/PIT, historical issuer/security map | NOT VERIFIED | PR #412 and official 2021 job; exact period/statement/sign/unit/chronology not independently bound |
| KRX 2017–2022 private storage pair hash completeness | Historical PASS, not re-attested from Railway in this run | Earlier recorded 1565/1565 weekday pair integrity, 90 unresolved calendar/source-gap days, 12003 zero-activity rows excluded |
| Official KRX session state, historical tradability, corporate actions, fills, costs and taxes | NOT VERIFIED | #423 Actions #39714207925 job #119612335677: 32 synthetic tests PASS, explicitly `DRY_RUN_NO_PRIVATE_STORAGE_READ`; no real private provider admission |
| Chronology anchor | FAIL | Actions #40360864884 job #121705590170: HTTP 404 on /anchor/latest; no public chronology attestation |
| Safety-only Watchdog | PASS only as offline governance | Actions #40436115571 job #121965063367, artifact ZIP SHA-256 `3ea4af4d7f8dfe080b191901e6fcba21425d82cd24e57e48c8ef0eeb0d9ca7c5`: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED` |
| #413 optimization parity | PASS fixed 34-case output identity, FAIL to demonstrate speed gain | Actions #38508247773 6/6 jobs, 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`; 1.765s serial vs 2.7079s parallel-longest, ratio 0.652 |
| #418 independent runner | PASS limited synthetic CI; FAIL strict archive source-identity guard; full CI/real backtest speed NOT VERIFIED | Actions #39111405562 succeeds; #39111405478 fails: `research_v1_runtime_manifest.py` expected Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37` |
| NetEV/PF/CAGR/MDD/ES95/ES99, after-tax annual risk-adjusted returns, concentration and time robustness | NOT VERIFIED / NO-GO | Official PIT and tradability prerequisite gates remain unapproved; **no M20 financial run was performed** |
| Railway latest deployment, runtime logs, actual ORDERING variable | NOT VERIFIED | Read-only Railway project enumeration required interactive authentication; blocked in non-interactive context. No workaround attempted. CI `orders: DISABLED` is not a production environment-variable attestation. |

## Frozen governance and next permissible actions
- Preserve frozen H5; M20 horizon20/purge20; WF504/126/126; PIT, label, Purged/CPCV, independent Holdout, Champion, Top3, NO_TRADE and unchanged transaction cost, tax, execution, risk and promotion rules.
- No holdout reuse, Dynamic after-the-fact adjustment, economic performance run, market-source inference from synthetic tests, Champion promotion, orders, funds, credentials/permissions, deployment, workflow changes, or PR merges.
- Require independent first-original edition semantic and publication-time source attestation from the OpenDART owner; official KRX session/trading/CA/fill source attestation from KRX owner; resolve /anchor/latest 404 through authorised owners; and authenticated read-only Railway production deployment/log/config evidence. Until then **M20 NO-GO** and policy requirement `ORDERING=false` remain.
- Optimization only offline synthetic and fail-closed cache identity checks; parallelize read-only independent post-processing only; never dependent retraining/capital transitions. No specialist code modified.
