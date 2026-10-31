# IndexAlert independent profitability gate — 2026-10-31 09:46 KST

Scope: independent, metadata/log-only inspection. This is a documentation-only record; no M20 backtest, source collection, Holdout access, order, deployment, permissions, merge or Champion action.

## Fresh read-only evidence

- GitHub branch API: research `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`; KRX owner `indexalert-krx-pit-source-audit-20261013` HEAD `073d2d49e95f69fb10b943b93e51bb179fb3c698`. These match prior inspected values.
- PR #412 (OpenDART), #414 (profitability integration), #416 (investor flow), #418 (runtime optimization), #420 (KRX gap), #422 (2021 calendar), #423 (2022 calendar), #424 (ETF opening) all remain open Draft and unmerged; PR #413 runtime optimization likewise Draft/unmerged. #414 head before this documentation-only write: `88e4ef8c4e38534ab2de7161fce86a54bd25e2fb`.
- New GitHub Actions Watchdog run [#41151825793](https://github.com/kims34/openpilot-opkr/actions/runs/41151825793), completed 2026-10-31 09:45:03 KST with success; job #124389856589 passed offline governance and explicitly logged: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This is a safety-regression pass, **not** an M20 source or profitability admission.
- Chronology Anchor [#41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151) failed on public prospective payload HTTP 404; downstream immutable chronology and validation steps were skipped. No independent chronology proof.
- Original OpenDART 2022 first-document [run #38380988990](https://github.com/kims34/openpilot-opkr/actions/runs/38380988990), job #115241142185: official ZIP received, CRC/bounded read passed, 1,570 tables and 15 candidate operating-profit row shapes. However `original_q3_cfs_three_month_profit_bound=false`, `original_statement_binding_verified=false`, `historical_publication_instant_pit_verified=false`, `historical_correction_lineage_complete=false`, `m20_feature_pit_admitted=false`. Original ZIP byte-level SHA-256 **was not independently recomputed during this audit**; previously logged digests must not be conflated with independent verification.
- Railway `indexalert-pit-rebuild` current deployment #8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 status SUCCESS (deployment health does not equal data admission). Latest returned runtime log: 2026-10-30 23:46:37 KST, `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, common-stock rows 803, nonpositive OHLC rows 27, source failure session 2026-09-28, source/chronology/model admission all false, `ordering=DISABLED`, `real_orders_authorized=false`, `session_manifest_sha256=null`. No fresher runtime log returned.
- Railway Kiwoom REAL read-only-run service latest deployment status SUCCESS, but no runtime logs returned in this check; no new verified broker auth evidence. KRX historical worker deployment SUCCESS, but no new runtime log returned. No staged changes reported by describe-service for these three services. No configuration change attempted.

## Independent admission matrix (fail-closed)

1. **Original SHA/provenance**: official 2022 ZIP receipt and integrity logged; independent original-byte rehash not completed. Full 2021/2022 issuer-first-submission linkage, exact financial semantics and corrections not independently accepted.
2. **PIT**: first public availability timestamp, 3-month consolidated operating profit, correction lineage, issuer/security historical mapping, and independent chronology not approved. **BLOCKED**.
3. **Tradability**: prior KRX private six-year receipt audit does not close 90 unresolved historical session classifications; 27 prospective nonpositive-OHLC cases remain excluded. Historical membership, price/volume validity, halts, market-cap timing and executable fill assumptions not independently certified. **BLOCKED**.
4. **Costs/tax**: explicit contemporaneous commission, exchange fees, taxes, slippage, spreads, partial fills, impact and price-limit constraints lack an approved, executable trade ledger. **BLOCKED**.
5. **NetEV, PF, CAGR, MDD, ES95/ES99**: **NOT COMPUTED/NOT ADMISSIBLE**, because source/PIT/tradability/cost admission is false; do not infer numerical results from synthetic regressions, deployment SUCCESS or flags-only tests.

## Guardrails

**M20 profitability run: NO-GO.** Frozen, Holdout, Champion and Top3 remain unchanged. `ORDERING=false` / runtime `DISABLED`. No real trades, funds, permissions, deployments, PR merge, Champion promotion or other workstream edits. Independent audit only; do not repeat KRX, OpenDART or runtime specialist tasks. The only allowed mutation in this run is creation of this single isolated Markdown audit file on the existing Draft #414 branch; if blocked, no bypass or retry.
