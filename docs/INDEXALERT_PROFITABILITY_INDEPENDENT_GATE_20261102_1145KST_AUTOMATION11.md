# IndexAlert independent M20 profitability gate — 2026-11-02 11:45 KST

**Decision: NO-GO for M20 economic execution.** This is a read-only audit handoff, not source/PIT admission, model testing, economic backtesting, or authorization to use Holdout. NetEV, PF, CAGR, MDD, ES95 and ES99 after costs/tax are **NOT EVALUABLE**, not zero.

## Direct read-only GitHub evidence

- GitHub REST branch GET: research `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`; KRX source specialist `indexalert-krx-pit-source-audit-20261013` HEAD `073d2d49e95f69fb10b943b93e51bb179fb3c698`; exception review `indexalert-krx-session-gap-review-v1-20261015` HEAD `fab3cbbd63a951a4e081f9e7f08c1391ca308581`.
- [Integration PR #414](https://github.com/kims34/openpilot-opkr/pull/414) before this document write HEAD `12d432156573c7bfe9eba62ebe89c8f711d663f2`; [DART PR #412](https://github.com/kims34/openpilot-opkr/pull/412) HEAD `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; KRX PRs [#420](https://github.com/kims34/openpilot-opkr/pull/420), [#422](https://github.com/kims34/openpilot-opkr/pull/422), [#423](https://github.com/kims34/openpilot-opkr/pull/423) are open/Draft/unmerged. Other specialists' branches not modified.
- Repository-wide [Actions latest run #41368406818](https://github.com/kims34/openpilot-opkr/actions/runs/41368406818) at 2026-11-02 00:40:24 UTC completed SUCCESS; actual job `125033414398` log shows 4/4 watchdog and 31/31 governance tests PASS, with `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This is a safe-contract test, **not** official original PIT or economics approval.
- [Chronology Anchor #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151) job `124184971844` failed HTTP 404 on 2026-10-30; downstream validation skipped.

## Independent comparison of existing official-source Actions logs (not a fresh original ZIP byte rehash)

- 2022 first-submitted OpenDART [Actions #38392847048](https://github.com/kims34/openpilot-opkr/actions/runs/38392847048), official job `115280695115`: original ZIP recorded SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, integrity true, 15 candidate operating-profit row shapes; original 2022 and 2021 Q3 exact three-month consolidated operating-profit binding **false**. First publication instant, full amendment lineage and issuer/security PIT **false**.
- 2021 first-submitted OpenDART [Actions #40262532310](https://github.com/kims34/openpilot-opkr/actions/runs/40262532310), official job `121377826016`: original ZIP recorded SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, 1,728 table shapes, 13 candidate operating labels, zero same-table exact Q3 period or three-month matches; 2021 original is not a verified 2022 first-filing 2021 comparator. Full publication/amendment PIT remains false.
- Original vs corrected 2022 [Actions #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742), official job `115372636726`: 15/15 exact-label candidate shapes and 15/15 numeric-peer shapes match, but normalized original CFS operating-profit lineage remains **unverified**. Different source ZIPs/identical candidate shapes do not prove authoritative earnings unchanged.
- The above are authenticated existing job outputs, **not** an independent fresh download and SHA-256 calculation on raw original ZIP bytes. No financial values or exact publication timestamps are admitted.

## KRX market/tradability and Railway production observation

- Existing 2017–2022 KRX private 1,565 daily/master pair SHA integrity PASS is a storage check, not official as-published calendar or tradability PIT. Historical 90 uncertain calendar/source-gap sessions are unresolved. Separate prospective **2026-09-28** 27 nonpositive common-stock OHLC rows remain quarantined; these are different horizons and must not be combined. PR #420/#422/#423 synthetic tests do not authenticate protected originals, per-security tradability, corporate actions, suspensions/delistings, tick/lot/fillability or broker economics.
- Railway IndexAlert production project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`: PIT service `indexalert-pit-rebuild` latest returned log **2026-11-01 14:46:22 UTC** `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27 of 803 common-stock rows, source/model/chronology admissions false, `fresh_alpha_observation_admitted=false`, `ordering=DISABLED`. Do not infer a newer success after the returned log boundary.
- Kiwoom REAL read-only deployment displays SUCCESS but environment health reports 0 running / 1 crashed replica; no healthy live broker authorization follows from deployment metadata. No service restart or deploy performed.
- Railway `describe_environment` and `get_staged_changes` show `staged=null`, while `environment_status.pendingWork` lists `patch:e113dacb-6705-4416-9997-dc694539d382` as staged with empty changes. This is an unresolved read-model discrepancy, **not** permission to apply.

## Independent economic admissibility decision and invariants

- Required before an immutable M20 economic test: authoritative original 2021/2022 first-filing 3-month CFS operating-profit semantics, first-available publication-vintage PIT, complete amendment and issuer/security history, official session/security tradability, corporate actions, precommitted executable fill/quote/lot/tick and partial-fill assumptions, realistic commissions/levies/transaction taxes, slippage, doubled-cost stress and explicit separate M20 admission.
- Until then **no calculation or claims** of after-tax NetEV/PF/CAGR/MDD/ES95/ES99; no backtest replay, no Holdout opening, no leakage into Frozen champion research.
- Preserve H5/M20 Frozen, M20 horizon20/purge20/WF504-126-126, sealed Holdout, Champion/Top3 (no rank-4 backfill), `ORDERING=false`. No live orders, capital, permissions, credentials, deployment, PR merge, or Champion promotion. No duplicate specialist work initiated.

Only this new isolated Markdown evidence note was intended to be written on the integration Draft PR branch; no other mutation authorized.
