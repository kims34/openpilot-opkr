# IndexAlert independent profitability gate — 2026-10-31 23:43 KST

**Audit scope:** Read-only GitHub branch/PR/Actions and Railway production evidence, independent *admission* review, not an M20 backtest. This isolated Markdown record is the sole authorized write attempt. No other workstream source capture, specialist code, private volume access, trading, deployment, configuration, permissions, funds, PR merge, Holdout or Champion action.

## Immutable refs and PR gates

- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX source specialist `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- OpenDART PR [#412](https://github.com/kims34/openpilot-opkr/pull/412): `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`. Integration PR [#414](https://github.com/kims34/openpilot-opkr/pull/414) pre-audit: `697ae153336b2576298b73325461472a898450dc`. KRX PR [#420](https://github.com/kims34/openpilot-opkr/pull/420): `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; [#422](https://github.com/kims34/openpilot-opkr/pull/422): `c14857620973531013799e44625d43080904fd5f`; [#423](https://github.com/kims34/openpilot-opkr/pull/423): `0e38004363cac9fc4475556b3a1c445de9af407f`. All open, Draft, unmerged.
- Latest [Watchdog #41206386585](https://github.com/kims34/openpilot-opkr/actions/runs/41206386585), 2026-10-31 22:37 KST: 31/31 offline governance tests pass; actual log states `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. **No performance or source certification follows from synthetic CI.**
- [Chronology Anchor #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151): actual job failed HTTP 404 at public hash-only anchor fetch, downstream append/validation skipped; not an accepted PIT chronology.

## Original source SHA and PIT admission — still NO-GO

- Official 2021 first-filed Q3 read-only [#40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066): offline and official jobs both SUCCESS. Original document ZIP digest asserted by actual log: `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`; one SGML, 1,728 table shapes, 13 operating-label candidates, **zero exact three-month period binding**.
- Official 2022 first-filed Q3 [#38380988990](https://github.com/kims34/openpilot-opkr/actions/runs/38380988990) and checksum-pinned repeat [#38392847048](https://github.com/kims34/openpilot-opkr/actions/runs/38392847048): original document ZIP digest `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`; one SGML, 1,570 table shapes, 15 operating-label candidates, **zero authenticated 2022 and 2021 comparator standalone Q3 CFS operating-profit cells**. Original standardized XBRL `014` source gap persists.
- These are **logged source SHA claims with official repeat verification**, not an independent third-party rehash: the original ZIP binary bytes were unavailable to this audit; the downloadable Actions flags-only artifact ZIP digest is a different object. Therefore independent raw-byte SHA approval **false**.
- First as-published time, full corrections/withdrawals, 2022-first-original 2021 comparative cell, exact standalone quarterly CFS account/unit/sign, historical issuer/security identity, full universe and decision-time availability are not attested. `m20_feature_pit_admitted=false`.

## Market calendar, tradability and economics

- Historical 2017–2022 private KRX SHA receipts alone do not resolve **90 uncertain exchange-calendar/source-gap sessions**. KRX #420 synthetic tests (actual [#39714240902](https://github.com/kims34/openpilot-opkr/actions/runs/39714240902): 39+25+8 = 72 tests PASS) and #422/#423 offline candidate comparators do **not** read or certify the private 2021/2022 exact-day sets or original market calendar.
- Separately, prospective 2026-09-28 session had **27 nonpositive common-stock OHLC rows of 803**; it is not part of the historical 90-day set. No independent security/day status, halt/limit/volume/turnover, corporate-action adjusted price, execution clock, order book or fill attestation.
- Commissions, historical transaction tax by product/date, bid/ask spread, slippage, impact, latency, partial fills, capacity and portfolio turnover are not independently tied to an admitted decision-time trade ledger. **After-tax NetEV, PF, CAGR, MDD, ES95 and ES99 remain NOT EVALUABLE**. No estimated performance substituted for source proof.

## Railway production read-only observation

- `indexalert-pit-rebuild` latest returned log at **2026-10-31 23:30:55 KST** (`2026-10-31T14:30:55.001Z`): `COMMON_OHLC_NONPOSITIVE`, `source_failure_session=2026-09-28`, 27 bad rows / 803 common-stock rows, source/chronology/model independent admissions false, live order false, `ordering=DISABLED`. Service shows 1 running, 0 crashed replica. No new accepted source.
- `indexalert-kiwoom-real-readonly` deployment shows SUCCESS, but replica status **running=0, crashed=1**; current runtime log contains no fresh successful authenticated broker session. Do not infer broker readiness from deployment label.
- `environment_status` shows one staged-patch pendingWork reference with empty changes; `get_staged_changes` and `describe_environment` show **staged=null**. These read views conflict; no attempt was made to resolve by mutation, and no live deployment was changed.

## Final authority gate

**M20 performance execution = NO-GO**, until independently accepted original ZIP bytes, first-available PIT and corrections, exact historical tradability, and cost/tax/market-impact ledger exist and the separate prerequisite approval is recorded. Preserve Frozen, preregistered WF/CPCV, sealed Holdout, Champion, Top3, `ORDERING=false` / runtime `DISABLED`. No source/CI, model, trading, capital, permissions, Railway deploy, PR merge or Champion promotion. No newly approved evidence or new critical blocker beyond the already-known unresolved source and runtime failures. Continue independent read-only audit without duplicating KRX/OpenDART specialist work.
