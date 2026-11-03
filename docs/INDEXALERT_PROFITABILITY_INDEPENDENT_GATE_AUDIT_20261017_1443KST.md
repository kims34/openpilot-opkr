# IndexAlert independent profitability gate — 2026-10-17 14:43 KST

Scope: read-only independent integration audit. No source approval, market replay, performance run, order, deploy, permission change, PR merge, or Champion change. Other owners retain their own PR/code and tests.

## Pinned repository evidence

- Research base `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a` (observed base SHA of PR #412/#414).
- Development base `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (observed base SHA of KRX PR #420).
- Draft PR #414 integration document HEAD `7baa57b6ba780870751aaa3aabf89485865cfa8d`; Draft PR #412 source HEAD `dcb4a6d30c47fd84a4e7667453af5bd5a6bcf1d0`; Draft KRX PR #420 HEAD `588bc296eafa58525954f691a763ff6eb413f053`. All unmerged when read.
- Prior isolation only: Draft #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`, Draft #418 `c9b125ff5d3d080848dd9ab1f23a8755af4faaa9`. No change or performance experiment in this audit.

## Newly cross-checked official-source artifact lineage (read-only)

- OpenDART #412's four historical official source-only artifacts from Actions `38706084440`, `38708786002`, `38731230183`, `38822004271` were rechecked by actual GitHub Actions `39001867286`, both jobs SUCCESS. The verification job log checked run IDs, original HEAD and artifact metadata, and SHA-256 digests; published counts-only gate artifact `12088933161` has SHA-256 `0c6e175b48473b9e8067b9e88691b49c6bc1a577dfcf3228a296b7b07aab065e` (retention expiry 2026-10-24). Four original-viewer financial sections, 329 tables, two operating-profit label candidate tables; zero complete 2022/2021 July–September windows and zero candidate header contexts containing both quarter terms. Source-artifact identity/consistency PASS, exact first-edition 2022/2021 three-month consolidated operating-profit cells, original publication available-at and amendment-vintage PIT NOT VERIFIED. Original standardized XBRL 014 is not repaired by viewer probes.
- KRX #420 2021 official calendar contemporaneous evidence identifies 10 planned weekday closures and 3 later-added closures; private Railway 2021 annual source records 261/261 stored weekday pairs, 13 source-empty/unknown calendar days, snapshot SHA-256 `362716e7bb5e025a9dcd39207b1ee095d97c633b8ca907722c766edf799ec2a1`. **Equal count 13 does not establish equality of exact dates**. The isolated exact-date comparison code and adversarial tests passed GitHub Actions `39001870209` (52 synthetic tests) and `39001870246` (six synthetic tests). The candidate has NOT read actual private day lists and is NOT a source PIT admission; running against the private Railway volume requires separate explicit authorization and no deployment/operation was performed.
- Railway IndexAlert production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`: staged patch NULL, zero staged changes. KRX historical worker latest successful deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` (2026-10-12, source commit `1e6367d2863a86c3470da13d81a955d277eba485`), logs confirm 2017–2022 **1,565/1,565** stored weekday source-pair integrity and **90** unknown official calendar/source-gap days. The prospective PIT runtime continues FAIL_CLOSED on 27 nonpositive-OHLC common-stock rows; it is a separate 2026 observation, not part of the 90 historical calendar exceptions.

## Independent admission verdict

| Gate | Verdict | Scope |
|---|---|---|
| OpenDART historical first-filed ZIP / four pinned source evidence identities | PASS (identity and consistency only) | Not a verified original financial fact |
| Exact 2022/2021 first-edition three-month consolidated operating profit, public available-at, full correction lineage | NOT VERIFIED | No M20 features |
| Issuer/security historical mapping | NOT VERIFIED | No look-ahead-universe permission |
| KRX raw 2017–2022 pair storage integrity | PASS (storage SHA receipts only) | 1,565/1,565 |
| Exact official market calendar, per-security suspension/delisting, corporate actions, fillability | NOT VERIFIED | 90 unknown historic days, 27 separately quarantined 2026 rows |
| Realistic commissions/slippage/market impact/taxes and after-tax NetEV, PF, CAGR, MDD, ES95/99, concentration and temporal robustness | NOT VERIFIED | No economic backtest run authorized |
| M20 PIT admission and economic evaluation | BLOCKED | No performance execution |
| Frozen H5/M20, WF504/126/126, horizon20/purge20, Purged/CPCV, Holdout, Champion, Top3, NO_TRADE | UNCHANGED | No tuning, no holdout reuse |
| Real orders, funds, broker/account permissions, deploy, merges, promotion | DISABLED | `ORDERING=false` |

Next source-only gates are owner-authenticated original DART numeric period/available-at/lineage evidence and private exact KRX date/security source-vintage reconciliation with separate explicit authorization; do not substitute synthetic CI for official source proof. No changes to other owners' documents or code.
