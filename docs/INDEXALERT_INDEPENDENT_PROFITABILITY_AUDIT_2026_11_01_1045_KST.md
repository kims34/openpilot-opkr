# IndexAlert independent admission check — 2026-11-01 10:45 KST

**Evidence-only isolated note on Draft PR #414.** This is not source/PIT admission, a strategy backtest, a workflow run, a broker authorization or an instruction to deploy. No Holdout read. No order or funds activity.

## Re-read of exact GitHub refs
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX specialist `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- PR #414 before this note: `f3172a08769721f52e6fd14f82fb60b2d1d571d3`; PR #412: `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; KRX PRs #420/#422/#423: `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, `c14857620973531013799e44625d43080904fd5f`, `0e38004363cac9fc4475556b3a1c445de9af407f`. All five PRs open, Draft, unmerged at read time.
- Watchdog Actions #41248232339, job #124676072097, completed success: 31 offline governance tests pass, but actual log states `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Chronology Anchor #41091128151 failed at public hash-only payload fetch; subsequent validation skipped.

## Independent-source SHA and PIT boundary
- Official source-only OpenDART Actions #38381866190, job #115244084285, records 2022 first-filed archive SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, archive integrity true, and 15 operating-row candidates. Those rows are *not* original consolidated 3-month quarterly operating-profit facts.
- Raw ZIP bytes were not supplied to this independent read-only review; **no second independent SHA-256 was calculated**. A logged source SHA is a provenance receipt, not an independently reproduced byte digest.
- First-available intraday timestamp, complete later-correction chronology, 2022/2021 comparable 3-month CFS amounts, historic issuer/security linkage and full point-in-time universe remain unapproved. A date-only disclosure index cannot certify intraday availability.
- KRX 2017–2022 private raw-byte receipts were not independently rehashed in this run. The 90 historic uncertain source/session days and the distinct 2026-09-28 prospective 27 common-stock nonpositive-OHLC rows are unresolved; KRX PR #420/#422/#423 synthetic offline controls are not actual official exchange-calendar or stock-day tradability evidence.

## Fresh Railway read-only observations
- Production project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- Latest returned PIT runtime log remains 2026-10-31 14:46:01 UTC (23:46:01 KST), `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27/803 rejected common-stock OHLC rows, independent source/chronology/model admission all false, `ordering=DISABLED`, live orders and funds false.
- Kiwoom REAL read-only service is marked online/SUCCESS in deployment metadata but replica health reports 0 running, 1 crashed. No new broker-authentication success in the returned logs.
- Environment inventory and get-staged-changes report no staged patch; environment-status separately reports pending staged patch `e113dacb-6705-4416-9997-dc694539d382` with empty changes, started 2026-10-29. Treat as inconsistent read-only metadata; no patch acceptance or deployment.
- Historical KRX worker deployment SUCCESS is not proof of independent private raw SHA, historical PIT or fill availability.

## Trading feasibility, economics and authorization
- No admitted stock/day original trading status, market cap, price-limit, auction, halt, volume, fill-depth, spread, commission, tax, slippage or execution-latency panel. Thus a realistic fill model and a net trade ledger cannot be independently reproduced.
- `NetEV`, `PF`, `CAGR`, `MDD`, `ES95`, `ES99`: **not computable on admissible original trade-level evidence**; no fabricated estimates, zero-filling, synthetic proxy or Holdout peeking.
- **M20 performance NO-GO.** Preserve Frozen/Holdout/Champion/Top3 and `ORDERING=false` (`DISABLED` in live log). No workflow rerun, broker order, money movement, permission change, deployment, merge or promotion.
- No new original approval or major new blocker established. Next independent gates: source-byte rehash, filing/period/correction/PIT binding, stock/day tradeability and executable costs/taxes. Avoid duplicating KRX/DART specialist data capture.

Evidence: https://github.com/kims34/openpilot-opkr/pull/414 ; https://github.com/kims34/openpilot-opkr/pull/412 ; https://github.com/kims34/openpilot-opkr/pull/420 ; https://github.com/kims34/openpilot-opkr/pull/422 ; https://github.com/kims34/openpilot-opkr/pull/423 ; https://github.com/kims34/openpilot-opkr/actions/runs/41248232339 ; https://github.com/kims34/openpilot-opkr/actions/runs/38381866190 ; https://github.com/kims34/openpilot-opkr/actions/runs/41091128151 .
