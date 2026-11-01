# IndexAlert independent profitability gate — 2026-11-01 14:45 KST

Scope: independent read-only review, separate from KRX investor-flow, KRX specialist, backtest optimisation, and trading work. This document alone is an allowed isolated write on Draft PR #414's documentation branch. No M20 run, broker action, deploy, merge, authority grant, Holdout access, Champion promotion, or configuration change.

## Pinned repository observations
- Research base HEAD: `3b8b7830612a6284d7c7a60628cb527cb741627a` (PR #414 and #412 base SHA).
- Development base HEAD: `1e6367d2863a86c3470da13d81a955d277eba485` (PR #420 base SHA).
- PR #414: Draft/open/unmerged; pre-write head `c40a5e4d4e6b02b847084aa371aaca048538a43b`; documentation-only.
- PR #412: Draft/open/unmerged; head `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`.
- KRX PR #420: Draft/open/unmerged; head `fab3cbbd63a951a4e081f9e7f08c1391ca308581`. Dependent #422 head `c14857620973531013799e44625d43080904fd5f`, #423 head `0e38004363cac9fc4475556b3a1c445de9af407f`; both Draft/open/unmerged. Their calendar candidate comparisons do not confer PIT or tradability admission.

## Independent source and chronology checks
- Actions run 41264126871, job 124723240979: successful read-only proof audit; 31 research governance tests pass. Actual log says `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`.
- Chronology Anchor run 41091128151: fetch prospective public hash-only payload failed; downstream anchor and validation skipped. No independent chronology admission.
- OpenDART official original read-only run 38381866190, job 115244084285: 2022 original document receipt and ZIP integrity reported; document SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`; 15 operating-profit table *candidates*, no verified exact 3-month CFS operating-profit fact, no proven 2021/2022 comparable quarter window. This is a logged digest, **not** a new independent rehash of source ZIP bytes in this run. Original publication instant, correction lineage, historical security mapping, full universe and PIT not admitted.
- KRX 2017–2022 historical private source SHA audit remains integrity evidence only; 90 unresolved source-empty/market-calendar sessions and separate 27 nonpositive OHLC common-stock cases remain quarantine. No source/session/tradability admission. No new private raw-source read or rehash was performed.

## Railway observed (read-only)
- Project IndexAlert production. PIT rebuild latest deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` reports SUCCESS, but most recent returned runtime event is **2026-10-31 14:46:01 UTC**: `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, `independent_source_admission_verified=false`, `independent_chronology_admission_verified=false`, `independent_model_admission_verified=false`, `ordering=DISABLED`, `real_orders_authorized=false`. No newer event was returned; deployment SUCCESS is not runtime/source admission.
- Kiwoom REAL read-only latest deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS, but last returned log (2026-10-29 06:22 UTC) reports `DETAIL_CODE=8050`, `TOKEN_OK=false`, `WS_CONNECTED=false`, `TYPE00_REG_ACK_OK=false`, `ORDERING=DISABLED`; no genuine live provenance verified.
- Historical KRX worker latest deployment SUCCESS, but this read returned zero deploy log rows; no inference of new raw-source verification.
- Environment status API returns `stagedChanges=null` while `pendingWork` contains empty staged patch `e113dacb-6705-4416-9997-dc694539d382`; dedicated staged-changes API returns null/empty. Unresolved API inconsistency; no commit/deploy action.

## Economics decision
- SHA provenance: logged digest only, independent raw-byte rehash incomplete.
- PIT: first publication instant, first-filed 3-month consolidated facts, corrections, security/time mapping, chronology, full universe not independently admitted.
- Tradability: unresolved historical sessions, nonpositive OHLC, market cap, executable liquidity/quotes, lot constraints and corporate-action path.
- Costs and taxes: venue/commission, spread, impact/slippage, fill failure, financing/borrow where applicable and tax schedule require PIT-valid trade ledger and independent evidence.
- Therefore after-cost/after-tax NetEV, PF, CAGR, MDD and ES95/ES99 are **not estimable or approvable**; do not substitute synthetic or optimistic values. M20 profitability execution **NO-GO**.
- Preserve Frozen/Holdout/Champion/Top3, ORDERING=false, fail-closed. No user approval requested absent independently verifiable source closure.

References: https://github.com/kims34/openpilot-opkr/pull/414 ; https://github.com/kims34/openpilot-opkr/pull/412 ; https://github.com/kims34/openpilot-opkr/pull/420 ; https://github.com/kims34/openpilot-opkr/pull/422 ; https://github.com/kims34/openpilot-opkr/pull/423 ; https://github.com/kims34/openpilot-opkr/actions/runs/41264126871 ; https://github.com/kims34/openpilot-opkr/actions/runs/41091128151 ; https://github.com/kims34/openpilot-opkr/actions/runs/38381866190 .
