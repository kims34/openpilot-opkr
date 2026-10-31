# IndexAlert independent profitability gate — 2026-10-30 15:47 KST

Scope: isolated documentation-only evidence receipt. Direct read-only GitHub branch/PR/Actions and Railway production checks. No private source bytes or original OpenDART ZIP downloaded/rehashed; no historical market replay, M20 economic test, Holdout access, broker actions, policy change, deployment, merge, permission or funding change.

## Fresh exact references
- Research `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`; KRX specialist `indexalert-krx-pit-source-audit-20261013` HEAD `073d2d49e95f69fb10b943b93e51bb179fb3c698`. All unchanged.
- PR #412 head `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` and #414 pre-receipt head `be75e9a6025777d3720609c2747adf52f17d9eaf` remain open, Draft, unmerged. Related specialist PR #416/#418/#420/#422/#423 also Draft/unmerged.
- GitHub Actions latest inventory total 4,622. [Watchdog #40988735313](https://github.com/kims34/openpilot-opkr/actions/runs/40988735313) job `123845746566` success, 4 watchdog + 31 governance tests pass; explicit `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. [Chronology Anchor #40914179246](https://github.com/kims34/openpilot-opkr/actions/runs/40914179246) job `123589876652` failed HTTP 404 for `/anchor/latest`; downstream validation skipped. No immutable chronology admission.
- Latest peer independent runtime audit at 15:25 KST on same PR already covers PR #418 archived manifest Git blob mismatch and limited candidate source proof; do not duplicate optimizer or KRX specialist work. Archived pin `108f66714602a1bd3ae42c34dcca7c16e38f460b` vs base/merge `e0055c66c59398fd4a1158077446d886b54c4e37` remains not independently resolved or approved for cache/merge.

## Original source/PIT/tradability gate
- Historical official Actions log receipts (not fresh independent ZIP-byte rehash): first-filed 2021 Q3 OpenDART SHA256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625` and 2022 Q3 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`. Strict standalone 3-month consolidated operating-profit fact, public available-at, corrected edition lineage, issuer/security mapping remain NOT VERIFIED. Candidate label rows are not PIT facts.
- Prior 2017–2022 private KRX weekday-pair SHA integrity 1565/1565 is a historical receipt, not a fresh byte-level rehash, official session or security-day trading permission. 90 uncertain sessions and separate 27 prospective nonpositive common-stock OHLC cases remain quarantined. Historical halts, delistings, corporate actions, lot/volume/liquidity, actual executable fills, brokerage/spread/slippage/impact/sell taxes and 2x cost stress NOT VERIFIED.
- No authorized frozen PIT-tradable ledger; therefore after-tax NetEV/PF/CAGR/MDD/ES95/ES99 and robustness NOT EVALUABLE, not zero and not proof of alpha.

## Railway production direct observations
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT service `indexalert-pit-rebuild` SUCCESS, 1 running/0 crashed. Returned logs through 2026-10-29 14:46 UTC (23:46 KST) show `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27/803 rows, `session_manifest_sha256=null`, independent source/chronology/model admissions false and `ordering=DISABLED`. No later evidence in returned sample; do not infer outage from observation gap.
- Kiwoom REAL read-only service deployment SUCCESS but replica 0 running/1 crashed. 2026-10-29 06:22 UTC structured log: token/login `8050`, `TOKEN_OK=false`, `WS_CONNECTED=false`, `TYPE00_EVENT_COUNT=0`, real orders false and ordering disabled. Dashboard label 'Online' is not proof of a healthy replica.
- Historical KRX worker returned zero fresh deploy logs. Environment has staged patch ID `e113dacb-6705-4416-9997-dc694539d382` with zero exposed changes; do not accept/deploy.

## Decision
**M20 profitability execution NO-GO.** Maintain Frozen H5, consumed Holdout isolation, Champion/Top3/NO_TRADE, preregistered M20 horizon/purge/WF/CPCV, and ORDERING=false. No actual order, capital, permission, deployment, merge, Champion promotion or source-owner/optimization branch edits. Await independently admissible original DART/KRX provenance, chronology, security-day tradability and cost/tax receipts before a separately approved single frozen M20 evaluation. No new material approval or blocker class identified in this audit.
