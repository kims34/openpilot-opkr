# IndexAlert independent profitability gate — 2026-10-31 10:42 KST

Scope: independent read-only GitHub/Railway metadata, Actions and bounded runtime log review. No source ingestion, private source-byte read, M20 profitability replay, Holdout access, execution, permissions, funds, deployment, merge, or Champion promotion. This file is the sole permitted isolated documentation write.

## Independently observed GitHub state

- Research `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`, development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`, KRX source owner `indexalert-krx-pit-source-audit-20261013` HEAD `073d2d49e95f69fb10b943b93e51bb179fb3c698`. GitHub compare with each known pinned SHA returned `identical`, ahead=0, behind=0.
- PR #412 (DART), #413/#418 (runtime), #414 (independent integration), #416 (investor flow), #420/#422/#423 (KRX), #424 (ETF opening) all open Draft and unmerged. PR #414 pre-write HEAD `cb3a9ca92015db278f6f1a230f8f8fa3642be5ae`.
- Latest repository Actions run [Watchdog #41151825793](https://github.com/kims34/openpilot-opkr/actions/runs/41151825793), completed 2026-10-31 09:45:03 KST SUCCESS. Actual job #124389856589 log confirms governance regressions and `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. SUCCESS is not source, profitability or order authority.
- [Chronology Anchor #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151), job #124184971844 FAILED with HTTP 404 for `/anchor/latest`; downstream immutable chronology/validation skipped. This is a previously known unresolved blocker, not a new approval.
- [2022 OpenDART official first-document run #38380988990](https://github.com/kims34/openpilot-opkr/actions/runs/38380988990), job #115241142185: ZIP received, CRC and bounded read completed, 1,570 source tables, 15 operating-profit row shapes. Strict 2022 Q3 three-month window matches=0 and strict CFS statement binding=false. `historical_publication_instant_pit_verified=false`, `historical_correction_lineage_complete=false`, `historical_security_corp_mapping_verified=false`, `m20_feature_pit_admitted=false`. The official Actions summary is source-layout diagnostic only. Original ZIP bytes were not independently rehashed here. An Actions artifact ZIP digest is not an original filing ZIP digest.

## Independently observed Railway state

- Production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`; PIT service `indexalert-pit-rebuild` deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS and 1/1 running replicas. Latest returned prospective runtime log 2026-10-30 23:46:37 KST (UTC 14:46:37), `COMMON_OHLC_NONPOSITIVE`, source/chronology/model approvals false, `ordering=DISABLED`; 803 common-stock rows with 27 nonpositive OHLC observations per prior observed payload. No fresher runtime log returned.
- Kiwoom REAL read-only service `indexalert-kiwoom-real-readonly` deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS, but replica status 0 running / 1 crashed; only startup log lines on 2026-10-29, no new broker authentication proof. SUCCESS deployment is not service-health or trading proof.
- KRX historical worker returns no new runtime entries; existing 90 uncertain historical sessions and 27 prospective invalid OHLC remain unresolved and are distinct categories.
- Railway `describe_environment` and `get_staged_changes` report no staged patch; `environment_status` still exposes an older `pendingWork` patch ID `e113dacb-6705-4416-9997-dc694539d382` with empty changes. This read-path inconsistency is not a verified live config mutation; no changes were made.

## Independent fail-closed gate

| Gate | Status | Missing proof |
| --- | --- | --- |
| Original byte SHA / provenance | NOT ATTESTED | Independent byte-level rehash and complete original issuer/vintage lineage |
| PIT / chronology | BLOCKED | Exact 3-month consolidated operating profit, first-publication timestamps, corrections, historical security mapping and independent chronology |
| Historical tradability | BLOCKED | Resolution of 90 KRX sessions; historical membership, halts, price/volume, market-cap timing and fill constraints |
| Prospective OHLC | BLOCKED | 27 nonpositive common-stock OHLC rows quarantined; source fail-closed |
| Cost / tax | BLOCKED | Verified commission, tax, spread, slippage, impact, partial fills and executable after-tax trade ledger |
| NetEV / PF / CAGR / MDD / ES95 / ES99 | NOT COMPUTED | Cannot execute/validate M20 without upstream admission |

**Decision: M20 profitability NO-GO.** Frozen, Holdout, Champion and Top3 unchanged; `ORDERING=false` (runtime `DISABLED`). No real orders, funds, authority changes, deployment, PR merge, or Champion promotion. Other specialist workstreams were not modified. Only this isolated Markdown record was eligible for a single write attempt; if denied, do not retry or bypass.
