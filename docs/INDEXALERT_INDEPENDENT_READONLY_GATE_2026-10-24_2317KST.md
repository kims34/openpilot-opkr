# IndexAlert independent integration gate — 2026-10-24 23:17 KST

## Scope and source-of-truth
Read-only GitHub connector checks only. Railway list_projects read-only call was attempted and returned `User input required but current turn is running in a non-interactive mode.` No production log, deployment or actual ORDERING state is claimed. No market data, backtest, new model test, protected Holdout, account, permission, deployment or orders accessed.

### Git refs (GitHub API)
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Integration Draft PR #414 pre-write: `85d0bd8023760e9599f78625e3da7248edad732d`; unchanged integration gate blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- OpenDART Draft PR #412: `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`.
- KRX Draft PR #420/#422/#423: `fab3cbbd63a951a4e081f9e7f08c1391ca308581` / `c14857620973531013799e44625d43080904fd5f` / `0e38004363cac9fc4475556b3a1c445de9af407f`.
- Runtime Draft PR #413: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; independent runner Draft PR #418: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`. All above PRs remain Draft and unmerged in this read.

## Independently checked additional implementation divergence
GitHub compare of PR #418's pinned parent `ca6c5d915d2c0e018f4aa9f82b4488038c16f8d3` against current PR #413 head `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` reports **18 commits ahead, 0 behind** and exactly four changed paths: runtime manifest, runtime one-runner, runtime CI integrity tests, and engineering ledger. This confirms #418's PR base is **not the current #413 HEAD**, not that any branch is safe to merge. No specialist changes made.

Independently fetched actual Git blobs:
- #418 `research_v1_runtime_manifest.py` blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`; receipt check rejects only literal True for two authorization fields, so missing or nonboolean values do not prove explicit denial.
- #413 `research_v1_runtime_manifest.py` blob `e0055c66c59398fd4a1158077446d886b54c4e37`; explicitly requires both `holdout_access_authorized` and `live_orders_authorized` to be literal False and guards additional optional aliases. This is an offline metadata guard, **not** a live broker permission attestation.
- #418 archived source gate blob `92cd52a4226fe7e1b58316e298e9d862178c12f1` pins the former manifest blob and immutable 34-case SHA256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`.
- #418 archived environment gate blob `9a7af4ec2f3742448962f76ab4e8fadf8521c9ff` explicitly does **not** verify wheel byte hashes or OS/native identity.

## CI evidence directly fetched
- [#413 offline parity run #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773), job `115670744341`: 34/34 same case outcomes, fixed SHA256 above; serial 1.7650s versus parallel 2.7079s (ratio 0.652x, slower). Artifact digests checked by the GitHub job downloader, **not independently downloaded and locally rehashed here**. Whole-CI and official-market backtest acceleration NOT VERIFIED.
- [#418 archived pinned run #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395`: actual `SourceDriftError` expected manifest Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. **FAIL CLOSED**, not evidence of KRX/DART data corruption. Environment job attests 22 package versions, not exact wheels/native graph.
- [#412 current head run #39884427765](https://github.com/kims34/openpilot-opkr/actions/runs/39884427765) offline-only success. No initial-filing 2022/2021 CFS operating-income cell/period/public available-at proof.
- [KRX #420 current head run #39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) and [#423 run #39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) offline-only success. They do not independently rehash private Railway original bytes or prove official security/day tradability.

## Independent admission verdict
| Gate | Verdict |
|---|---|
| Git refs / Draft states and direct source blob identity | PASS (metadata/source identity only) |
| #413 34-case offline parity | PASS (test identity only); negative measured timing |
| #418 archived source identity | FAIL (actual GitHub Actions) |
| #418 wheel/native/transitive runtime closure | NOT VERIFIED |
| OpenDART original 2022/2021 3-month consolidated operating-profit period, corrections, exact public available-at/PIT | NOT VERIFIED |
| Historical company-to-security mapping | NOT VERIFIED |
| KRX official exchange sessions, security status, corporate actions, actual fills | NOT VERIFIED; retain prior 90 unresolved session gaps and 27 OHLC quarantines |
| Brokerage fees/tax/slippage/impact, NetEV/PF/CAGR/MDD/ES95/99, concentration/time-slice robustness | NOT EVALUABLE / NOT VERIFIED (no approved PIT data or M20 economic run) |
| Railway live deployment, live ORDERING | NOT VERIFIED (interactive authorization blocker) |

**M20 source admission NO-GO; M20 profitability RUN NO-GO.** Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, label/PIT/Purged/CPCV, sealed Holdout, Champion/Top3/NO_TRADE, all cost/tax/risk/promotion thresholds. Require `ORDERING=false` but do not assert actual production value. No Holdout reuse, source re-pin, caching across unapproved data, parallel dependent training/capital transitions, strategy exploration, new market performance runs, orders, funds, credentials, permissions, deployment, PR merge or Champion promotion.

Next independent evidence: OpenDART owner original exact first-public CFS cell/period and correction vintage; KRX owner official per-session/per-security source and private archive; runtime owner explicit changed-source dependency/wheel/native closure with non-admitting offline controls; Railway owner interactive authorization for read-only operational logs. No duplicate specialist code edits.
