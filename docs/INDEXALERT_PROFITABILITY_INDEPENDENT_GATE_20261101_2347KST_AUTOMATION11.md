# IndexAlert independent profitability evidence gate — 2026-11-01 23:47 KST

Documentation-only independent review; **not a PIT admission, M20 performance authorization, broker permission or production change**. No source fetch beyond existing read-only GitHub/Railway connectors, no real backtest, no trading, no Frozen/Holdout/Champion/Top3 change. Avoid overlapping KRX/OpenDART specialist tasks.

## Live GitHub refs / PRs
- Research `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`; KRX `indexalert-krx-pit-source-audit-20261013` HEAD `073d2d49e95f69fb10b943b93e51bb179fb3c698`. Independently queried GitHub branch REST API this run; unchanged.
- PR #414 head before this documentation-only write `320ba0ba9769c113b00b3e041bd4de0930f5bd8a`. PR #412/#420/#422/#423 remain open, Draft, unmerged.
- Latest repository-wide GitHub Actions listing (2026-11-01 23:47 KST) shows watchdog run [#41292056320](https://github.com/kims34/openpilot-opkr/actions/runs/41292056320), 2026-11-01 09:11:52Z, SUCCESS. Job `124805130699` actual log: 31 governance tests PASS, `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Scheduled watchdog is on `HKG_community`; do not infer branch-specific M20 proof.
- Chronology Anchor [#41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151) failed 2026-10-30 source fetch HTTP 404; validation job skipped. No independent chronology admission.

## Official original source / PIT separation
- OpenDART 2022 first-filed Q3 ZIP **recorded** SHA256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`; later correction ZIP `606be9d03928808f0a2a05f052444587bd2457bdef7a47a8f4bff3d2ea098a30`. These are source-only evidence in PR #412 and official CI, not newly rehashed original ZIP bytes in this audit. 15 candidate operating rows, zero strictly bound 2022 Q3 consolidated standalone three-month operating profit facts. Original/correction row candidate equality does not establish CFS semantics.
- 2021 first-filed Q3 ZIP recorded SHA256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`; no permission to substitute a 2021 filing for 2022 report's 2021 comparison.
- Missing first-vintage exact 2022/2021 standalone CFS facts (period, unit, scale, sign), first public available-at, complete amendment lineage and historical issuer/security mapping. Original XBRL official `014` missing. No M20 PIT admission.
- KRX specialist PR #420: 1,565 daily/master SHA-pair receipts stored/integrity PASS, 90 uncertain historical sessions, 27 prospective nonpositive OHLC cases. PR #422/#423 calendar comparators remain offline candidates, not verified historical market sessions, securities' tradability, liquidity, corporate actions, or fills. No private exact-set read performed here.

## Railway actual read-only observation
- Production `indexalert-pit-rebuild` last returned runtime log `2026-11-01T14:46:22.425Z` (23:46:22 KST): `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27 nonpositive rows, `independent_source_admission_verified=false`, `independent_chronology_admission_verified=false`, `real_orders_authorized=false`, `funds_movement_authorized=false`, `ordering=DISABLED`.
- `indexalert-kiwoom-real-readonly` deployment `a77fb922-b679-4d88-92c4-03054ec579cd` displays SUCCESS but environment health reports 0 running/1 crashed replicas; not evidence of broker auth/WS success.
- Environment status reports pending patch `e113dacb-6705-4416-9997-dc694539d382` while get-staged-changes and describe-environment both report `staged=null`; read-view inconsistency remains. No deploy/patch action attempted.

## Independent economics admission
- Historical stock/day tradeability, calendar, suspensions, limit bands, lot sizes, corporate actions, liquidity, realistic fill, price/volume validity and as-of PIT are unapproved.
- Timestamped venue-specific fees, spread, slippage/impact, market taxes, turnover and conservative 2x-cost sensitivity are unapproved.
- Therefore post-cost/post-tax **Net EV, PF, CAGR, MDD, ES95, ES99 are NOT ESTIMABLE** from approved evidence. No synthetic point estimates, no M20 backtest or Holdout reuse.
- **M20 GO/NO-GO = NO-GO**; Frozen/Holdout/Champion/Top3 intact, `ORDERING=false`/`DISABLED`. No real trades, funding, account/permission changes, deployment, PR merge or Champion promotion.

Evidence: https://github.com/kims34/openpilot-opkr/pull/414 ; https://github.com/kims34/openpilot-opkr/pull/412 ; https://github.com/kims34/openpilot-opkr/pull/420 ; https://github.com/kims34/openpilot-opkr/pull/422 ; https://github.com/kims34/openpilot-opkr/pull/423 .
