# IndexAlert independent profitability evidence checkpoint — 2026-10-31 16:49 KST

This is an isolated documentation-only audit. It is **not** a source/PIT/tradability/holdout/performance/trading approval. No other specialist branches, runtime services, trading controls, or research protocol were changed.

## Direct read-only evidence

- GitHub branch HEADs: research `index-alert-research-v1` = `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1` = `1e6367d2863a86c3470da13d81a955d277eba485`; KRX specialist `indexalert-krx-pit-source-audit-20261013` = `073d2d49e95f69fb10b943b93e51bb179fb3c698`. All three were resolved directly via GitHub commit reads, unchanged from prior checkpoint.
- PR #412 head `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`, PR #414 head before this audit `40c137794558dcd660c5e19cdd25ad9adfd91ff7`, KRX PR #420/#422/#423 and related #416/#418/#424: Draft, open, unmerged at read time. No PR merge or promotion.
- Latest repository Actions run from GitHub's run collection: [read-only watchdog #41178674319](https://github.com/kims34/openpilot-opkr/actions/runs/41178674319), completed SUCCESS at 2026-10-31 06:58:04 UTC (15:58:04 KST). Actual job 124471405513 log: 31/31 offline governance tests pass, `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This is a governance test only, **not** source/PIT/economic admission.
- [Chronology Anchor #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151) failed: repeated `/anchor/latest` HTTP 404 at 2026-10-30 17:13 UTC, downstream chronology/validation skipped. No new successful anchor run in the latest 30-run repository collection.
- [OpenDART official source run #38380988990](https://github.com/kims34/openpilot-opkr/actions/runs/38380988990), job 115241142185: first-filed 2022 Q3 document ZIP received, CRC/bounded read passed, 1 legacy SGML entry, 1,570 tables and 15 operating-row shapes; **0 exact 2021 or 2022 Q3 three-month matches** and **0 verified consolidated three-month operating-profit facts**. Existing source-reported 2022 original ZIP SHA256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` is a prior receipt, **not** an independent raw-byte rehash in this run. Artifact ZIP digest must not be substituted for source ZIP SHA.
- Railway production: `indexalert-pit-rebuild` service deploy SUCCESS since 2026-10-10, configured for one SFO replica. Last returned runtime log 2026-10-30 14:46:37 UTC: `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27 nonpositive OHLC rows among 803 common-stock rows, all independent source/model/chronology admission flags false, `ordering=DISABLED`, real orders false. Configured replica count is **not** proof of live instance count; status endpoint returned `numReplicas=null`.
- Railway `indexalert-kiwoom-real-readonly`: latest deployment SUCCESS 2026-10-29 06:21 UTC; returned deploy log contains only container start, no new authenticated broker success. `indexalert-krx-historical-worker` current deploy SUCCESS from 2026-10-12, no new deploy log entries returned. Earlier private six-year raw SHA receipts show 1,565/1,565 pairs; 90 uncertain historical sessions and 27 separate prospective OHLC anomalies remain unadmitted.
- Railway `get_status` returned `stagedChanges=null` while `pendingWork` listed a staged empty-change patch `e113dacb-6705-4416-9997-dc694539d382`; `get_staged_changes` returned null. Treat as inconsistent metadata, not as a new deployment or approval. No attempt to commit or resolve staged changes.

## Independent admission verdict (all economic gates fail closed)

| Gate | Direct conclusion |
| --- | --- |
| Source SHA | Existing KRX receipts and OpenDART source digest observed, but **no independent 2022 raw ZIP byte rehash** or independent full cross-source chain in this run |
| PIT | Original 2022 Q3 consolidated three-month fact binding, first publication instant, amendment lineage, historical issuer/security mapping and observation-at not approved |
| Historical market/tradability | 90 uncertain sessions, security-specific halts/delistings/corporate actions, price-path and executable order-book fills not approved; 27 bad prospective OHLC remain quarantined |
| Costs/taxes | Side-specific commission, spread/slippage, queue/depth/partial fills, product- and jurisdiction-specific transaction tax and turnover costs not independently attested |
| NetEV/PF/CAGR/MDD/ES95/ES99 | **NOT ESTIMABLE / NOT VERIFIED** from approved independent executable data; do not replace missing evidence with zeros, simulated profits, or stale H5/0–N results |
| M20 profitability | **NO-GO** until original source/PIT, tradability and cost/tax/fill evidence pass independent gate, then frozen preregistered one-shot evaluation is separately authorized |

Frozen/Holdout/Champion/Top3 preserved. `ORDERING=false` / runtime `ordering=DISABLED`. No M20 profitability run, no sealed Holdout reuse, no orders, funds movement, permission changes, Railway deployment, PR merge or Champion promotion. This document grants no future authority.

## Required external specialist evidence before reconsideration

OpenDART owner: independently pinned original source bytes + exact CFS Q3 three-month facts and publication/amendment lineage. KRX owner: official calendar reconciliation, security/day tradability and corporate-action PIT evidence. Economics owner: precommitted fee, tax, slippage and fill assumptions with stress and capacity checks. Only after all gates pass, request separate explicit approval for the frozen M20 test; never infer authorization from this audit.
