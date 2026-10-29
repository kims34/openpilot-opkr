# IndexAlert independent profitability source gate — 2026-10-29 11:46 KST

**Decision: M20 profitability NO-GO.** Read-only audit; no backtest execution, Holdout access, data/source capture, code/strategy change, production action, live orders, capital, credentials, deploy, merge, or Champion promotion. This document is an isolated evidence receipt, not an admission authority. Do not duplicate the KRX/OpenDART/flow/runtime specialist workstreams.

## Current repository/PR evidence (fresh GitHub connector reads)
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX specialist `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- PR #412, #413, #414, #416, #418, #420, #422, #423: OPEN/DRAFT/UNMERGED. PR #414 pre-write head `72f752db1f13db314cf73760f6775af777e44820`; research base remains pinned. Last independent audit 10:49 KST was read; no duplicated implementation or KRX specialist edits.

## Independent action-log checks
- [Hourly proof watchdog #40785611286](https://github.com/kims34/openpilot-opkr/actions/runs/40785611286), job `123157909379`: 4 safety + 31 governance tests PASS. Exact log status: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Test success is not a source approval.
- [Chronology Anchor #40726273259](https://github.com/kims34/openpilot-opkr/actions/runs/40726273259), job `122950285352`: public `/anchor/latest` HTTP 404; anchor fetch failed and validation skipped. Pre-existing blocker, not a newly accepted chronology.
- [2021 original OpenDART #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), job `121379096007`: original-document ZIP SHA-256 logged as `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`; 1,728 table shapes, 13 operating-label candidates. Same-table standalone Q3 3-month CFS cell, original availability instant, corrections, issuer/security mapping NOT VERIFIED.
- [2022 original OpenDART #38392847048](https://github.com/kims34/openpilot-opkr/actions/runs/38392847048), job `115280695115`: document ZIP SHA-256 logged as `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`; 2021/2022 Q3 period-to-profit binding, correction lineage, as-of time and full PIT panel NOT VERIFIED. Original ZIP bytes were **not** independently re-downloaded or rehashed this run; the GitHub artifact ZIP digests are different objects and must not be conflated.
- [KRX offline gate #39721289545](https://github.com/kims34/openpilot-opkr/actions/runs/39721289545), job `119635081965`: 164 synthetic/offline tests PASS, not official historical per-security tradability. Historical private storage receipts, 2021 13 / 2022 14 exact source-empty day sets, 90 uncertain sessions, 27 bad/nonpositive OHLC, calendar-as-of, corporate actions and executable fills remain NOT ADMITTED.
- [Cost regression #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773), job `115670591137`: 9 tests and 10 subtests PASS; `profitability_evaluated=false`. This is not proof of actual commission, taxes, spread, slippage, borrow, impact, partial fills or lot/price constraints.
- [Archived runtime source gate #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395`: FAIL-CLOSED `research_v1_runtime_manifest.py` Git blob mismatch, expected `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. No immutable code/source/runtime-to-PnL closure.
- [ETF offline #40800378513](https://github.com/kims34/openpilot-opkr/actions/runs/40800378513) successful but separate scope, not M20 admission. A repository-wide latest Actions inventory was **not independently established in this run**; do not claim this is the absolute latest.

## Railway access and economics gate
- One read-only Railway `list_projects({})` call returned `User input required but current turn is running in a non-interactive mode.` Stopped without retry, alternate authentication or bypass. Runtime deployment logs, effective production `ORDERING` variable, deployed SHA and current operational state were **not verified**. Mandatory policy remains `ORDERING=false`; do not assert observed production value.
- **NetEV / PF / CAGR / MDD / ES95 / ES99 after fees and taxes: NOT COMPUTABLE / NOT VERIFIED.** Required immutable PIT original financial panel, historical tradability and source dates, independent raw SHA chain, runtime closure, executable cost/tax/fill model and sealed out-of-sample protocol are absent. No invented numerical performance, no M20 replay.

## Controls and escalation
Keep Frozen H5/M20 prereg, sealed Holdout, Champion/Top3 and no rank-4 backfill; ORDERING=false, no orders/funds/permissions/deploy/merge/Champion promotion. Source-owner original PIT admission and independent executable economics evidence are prerequisites. Compared with the 10:49 KST independent receipt, no material new original approval or newly established critical blocker; no routine notification.
