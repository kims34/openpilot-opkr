# IndexAlert independent read-only profitability gate — 2026-10-14 UTC

Scope: audit-only documentation on isolated Draft PR #414 branch. This document does not admit source PIT, enable M20, alter Frozen H5/M20, use Holdout, authorize trading, or merge/deploy.

## GitHub evidence at audit
- Research base ref `index-alert-research-v1`, PR #414 base SHA `3b8b7830612a6284d7c7a60628cb527cb741627a` (this is the PR base, **not** an independently established live branch HEAD). PR #414 Draft HEAD `7ab7b3a22cbfc4c8e1c5c147f6f19add02ee5348`, open/unmerged.
- OpenDART Draft PR #412 HEAD `87f905844cd47fe8d725547822c16ae0947f227e`, open/unmerged. Actual Actions #38528346741 two jobs PASS (offline and first-original source diagnostics). 1,570 SGML tables, 15 operating-row label candidates, zero exact CFS title and zero full 2022 or 2021 July–September period window matches. Original financial fact, first public available-at and revision lineage **NOT VERIFIED**. Source ZIP integrity is not PIT admission. Prior original XBRL 014; modern normalized source returned fail-closed 013/014 aggregate code.
- KRX PR #403 HEAD `7f7f4bf3e6baa645179003ff21a6a0bfc4516b11`, PR #404 HEAD `1aef2de445b05883353a1d668acd89b194abbeab`. Both source capture/audit work, not tradeability/PIT approval.
- Railway project IndexAlert production: staged changes NONE at audit. KRX worker latest deploy SUCCESS `16c93d7c-7cd0-4d84-a327-298d2805376c`. Read-only runtime log `INDEXALERT_MISSING_2017_2022_INTEGRITY_FINAL` 2026-10-12 13:08:31Z: 1,565/1,565 weekday source pairs storage/hash integrity PASS, aggregate fingerprint SHA-256 `e2503a3bc623d4386e5783ec19272916fe6abba9bc191c14040d2c0831c7f01a`; 90 unresolved calendar/source gap days. `official_trading_status_verified=false`, `corporate_action_paths_verified=false`, `ordering=DISABLED`.
- Prospective PIT rebuild runtime: repeated `COMMON_OHLC_NONPOSITIVE` fail-closed. A successful deployment does not mean admitted source or live permission.

## Independent gate verdict (do not confuse code CI PASS with economic PASS)
- Original source-byte SHA / storage completeness: PASS for the narrowly pinned DART archive and KRX private 2017–2022 weekday pairs; does not prove all necessary accounting cells or official trading days.
- Earliest original public available-at timestamp and 2022/2021 standalone 3-month consolidated operating-profit cell binding: NOT VERIFIED.
- Full original/corrected financial-cell lineage and historical issuer-to-security as-of mapping: NOT VERIFIED.
- KRX official calendar, trading halt/delist status, corporate actions, price validity and executable fills: NOT VERIFIED.
- Cost/tax/true fills, after-cost NetEV, Profit Factor, CAGR, MDD, ES95/99, return concentration, temporal robustness: NOT VERIFIED (no M20 economic run authorized).
- M20 feature PIT admission: FAIL-CLOSED / NO_GO. M20 performance run: BLOCKED. No independent Holdout reuse, H5 re-fit, Dynamic retuning, Champion/Top3 promotion, Tiny Live, order, funds, credential/permissions or production deployment.

## Next nonduplicative handoffs
1. PR #412 owner: official first-edition CFS income-statement 2022/2021 July–September cell and first-publication proof; no more proximity heuristics as surrogate evidence.
2. KRX owner: authoritative day-by-day exchange calendar and security halt/delist/corporate-action identities, with separate provenance and as-of timestamp proof; quarantine invalid OHLC rows without assuming they are tradable.
3. This integration gate: read-only recheck source SHA/CI/runtime evidence only after owner-provided new proofs. Maintain Frozen H5/M20, WF504/126/126, PIT/Holdout/Champion/Top3/NO_TRADE, and ORDERING=false.

References:
- https://github.com/kims34/openpilot-opkr/pull/414
- https://github.com/kims34/openpilot-opkr/pull/412
- https://github.com/kims34/openpilot-opkr/actions/runs/38528346741
- https://github.com/kims34/openpilot-opkr/pull/404
- https://github.com/kims34/openpilot-opkr/pull/403
