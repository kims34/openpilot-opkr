# IndexAlert independent read-only profitability and isolated-runtime gate — 2026-10-25 21:23 KST

**Scope:** This is a non-admitting, read-only evidence review of two independent workstreams. No source acquisition, performance/backtest run, strategy/model exploration, market data export, deployment, merge, account/broker permission, order, or Champion action. It supplements the previous 20:46 KST audit, without editing specialist code or workflows.

## GitHub exact refs, freshly read
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Integration Draft PR #414 pre-note HEAD: `929daba33c29dae5c85602cec6958e192ffdb0e9`; gate document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` inspected without modification.
- OpenDART Draft PR #412: `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`.
- Runtime Draft PR #413: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; dependent one-runner Draft PR #418: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft PR #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. Their offline source-calendar comparators are NOT execution on the protected private Railway archive; #404 historically merged, not a current admission.

## Latest independent CI evidence
- Newest [hourly proof Watchdog run #40188482673](https://github.com/kims34/openpilot-opkr/actions/runs/40188482673) at 2026-10-25 11:20:54–11:21:08 UTC: SUCCESS, job `121154222723`. Raw log: 31/31 research-governance tests PASS; `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Flags-only artifact `12596892663`, ZIP SHA-256 `a08b8ada6653856bf9ce825e2da1a7d48c1cdbdcc9cd7abf6a256abd07dc1bb2` independently agrees between job log and GitHub artifact metadata. This is CI evidence only; **not proof of Railway live ORDERING**.
- [#413 offline parity #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) at exact #413 HEAD: six jobs SUCCESS. Reopened serial/parity job logs; immutable 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, `actual_backtest_speedup_measured=false`, `ci_end_to_end_speedup_measured=false`, `ordering=false`. No production/market speedup claim.
- [#418 pinned parallel #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) at exact #418 HEAD: FAIL in job `117628139395`, `research_v1_runtime_manifest.py` original archived Git blob expected `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Preserve fail-closed; do not re-pin. Separate [candidate audit #39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) SUCCESS for non-admitting code-only check, explicitly `all_transitive_imports_pinned=false`, `candidate_approved_for_merge=false`, no actual backtest speed measurement.
- [#412 original viewer offline guard #39884427765](https://github.com/kims34/openpilot-opkr/actions/runs/39884427765) SUCCESS, but synthetic/no-network only. Existing [chronology anchor #39972035700](https://github.com/kims34/openpilot-opkr/actions/runs/39972035700) remains FAIL with HTTP 404 and downstream validation skipped. No new first-public timestamp attestation.
- KRX #420/#422/#423 document and PR source checked. The original private day-set exact comparisons for 2021/2022 have **not** been executed on the protected volume; CI is synthetic only. Earlier KRX 2017–2022 1,565/1,565 day/master raw-pair SHA PASS remains prior storage-only evidence, not a new re-read.

## Railway read boundary
Fresh authenticated read-only `list_projects` was attempted once and returned `User input required but current turn is running in a non-interactive mode`. No workaround or alternate privileged endpoint attempted. Therefore actual latest Railway deployment/logs, source PIT, and live `ORDERING` flag are **NOT VERIFIED**. Required policy remains `ORDERING=false`; no action to change it.

## Decision matrix (independent admission)
| Gate | Verdict | Boundary |
| --- | --- | --- |
| Exact GitHub branch/PR HEAD and selected raw Actions/log/artifact digests | PASS (read-only metadata and limited CI evidence) | Does not admit market data |
| 2017–2022 KRX private raw-pair storage SHA | PRIOR PASS, NOT RECHECKED | No private volume access this run |
| 90 historical calendar/source gaps, 27 nonpositive-OHLC cases, official trading status/CA/halts/delists/fills | NOT VERIFIED / FAIL-CLOSED | KRX specialist source admission required |
| First-original OpenDART 2022 and 2021 Q3 standalone 3-month CFS operating-income values, unit/sign, original/correction lineage, exact first public available-at | NOT VERIFIED | Original edition semantic and chronology proof missing |
| Historical issuer/security PIT mapping | NOT VERIFIED | Must independently bind at historical dates |
| Official fees/slippage/taxes and after-tax NetEV, PF, CAGR, MDD, ES95/ES99, concentration, temporal robustness | NOT VERIFIED | No economic run permitted |
| #413 34-case offline parity | PASS limited synthetic | No full CI/H5/M20 speedup proven |
| #418 original immutable source identity | FAIL | Exact blob mismatch; candidate audit not admission |
| Complete transitive runtime/wheel/native dependency SHA | NOT VERIFIED | No cache/merge authority |
| Railway live deployment/logs/ORDERING | NOT VERIFIED | Interactive authentication required |
| M20 PIT admission and profitability execution | **NO-GO / PROHIBITED** | No authorized original PIT/tradability chain |

## Next non-overlapping evidence
Source owners should independently attest first-original CFS cell/first-publication chronology and official KRX per-date/per-security status/CA/fillability, including original private 2021/2022 calendar exact-set comparisons only with separate authorization. Runtime owner should prove full immutable dependency closure and whole-CI timing, without re-pinning archived identities. Integration work should only incorporate new independently verifiable source SHA, run IDs, and logs.

Keep Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV, consumed sealed Holdout, Champion/Top3/NO_TRADE, costs/taxes/risk/promotion criteria immutable; `ORDERING=false`. Cache fail-closed unless independent source/data/code/Frozen-policy/runtime/approval-evidence SHA-256 match; only independent read-only postprocessing may parallelize. No M20 profitability, official market performance experiment, Holdout reuse, orders, funds, credentials, permissions, deployment, Draft PR merge or Champion promotion.
