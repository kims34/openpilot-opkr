# IndexAlert independent profitability audit — 2026-11-02 15:44 KST

Scope: independent read-only verification of selected GitHub refs/PRs/Actions and Railway logs; this Markdown is the sole permitted isolated write. No model/data/strategy/workflow/runtime changes. No M20 replay or Holdout access.

## Ref and PR state
- Research `index-alert-research-v1` = `3b8b7830612a6284d7c7a60628cb527cb741627a`; compare with pinned SHA identical (ahead 0/behind 0).
- Development `index-alert-position-regen-fix-v1` = `1e6367d2863a86c3470da13d81a955d277eba485`; identical.
- KRX source-audit `indexalert-krx-pit-source-audit-20261013` = `073d2d49e95f69fb10b943b93e51bb179fb3c698`; identical.
- PR #414 head before this document `bb5bf842675a76829b2140fdf0ebad96a669faba`; PR #412 head `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`. KRX PRs #420/#422/#423 heads `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, `c14857620973531013799e44625d43080904fd5f`, `0e38004363cac9fc4475556b3a1c445de9af407f`. All five Draft/open/unmerged. The isolated audit file is not source approval.
- Selected Actions #41368406818 job 125033414398 completed successfully 2026-11-02 09:40 KST; 31 research-governance tests pass, `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This is a selected run, not a proven repository-wide latest Actions inventory.
- Chronology Anchor Actions #41091128151 auto-anchor job 124184971844 failed with HTTP 404; validation skipped.

## Original source/PIT
- Original official OpenDART 2022 fixed slot-5 Actions #38380988990 job 115241142185: source ZIP received; CRC/bounded-read completed; 1 SGML-like entry, 1,570 tables, 15 operating-profit row shapes, zero exact 2022/2021 Q3 three-month window matches. `original_q3_cfs_three_month_profit_bound=false`; original issuer financial fact, original publication instant, full correction lineage, historical issuer-security map and feature PIT remain unverified. Prior recorded archive digest must not be confused with a fresh independent rehash: **no original raw ZIP bytes rehashed in this run**.
- KRX PR #420 reports historical stored integrity for 1,565 weekday daily/master pairs, but 90 uncertain session classifications remain unresolved; 27 nonpositive common-stock OHLC rows quarantined. #422/#423 contain offline exact-day candidate comparators only; no authorized real private day-set audit or official historical tradability/PIT admission was performed in this run.
- Historical tradability, execution feasibility, spread, slippage, commission, market impact, taxes, and security/corporate-action lineage are not independently approved. Therefore no defensible after-tax NetEV/PF/CAGR/MDD/ES95/ES99 calculation or M20 profitability run.

## Railway (read-only)
- Production PIT service `indexalert-pit-rebuild`: most recent returned deploy log 2026-11-01 14:46:22 UTC: `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27 nonpositive OHLC / 803 common-stock rows, `independent_source_admission_verified=false`, `ordering=DISABLED`, no live orders.
- `indexalert-kiwoom-real-readonly` deploy 2026-10-29: TOKEN_OR_LOGIN_AUTH, detail 8050; `TOKEN_OK=false`, `WS_CONNECTED=false`, `TYPE00_REG_ACK_OK=false`, orders disabled. Environment status reports SUCCESS/online but 0 running and 1 crashed replica; treat as unavailable, not healthy.
- Railway status shows a staged environment patch from 2026-10-29; no commit/apply action taken. KRX worker has a volume but no new returned deploy log entries in this check; no private volume read.
- No fresh independent source approval, no approved economic inputs, no change to frozen evaluation authority.

## Decision
**M20 NO-GO.** Preserve Frozen/Holdout/Champion/Top3, no Champion promotion, `ORDERING=false` (runtime `DISABLED`). No trading, funding, permissions, deployment, merge, backtest replay or duplicate specialist work. Reassess only upon new independently verifiable first-filed source/PIT and exchange/tradability evidence, then explicit cost/tax model approval. 
