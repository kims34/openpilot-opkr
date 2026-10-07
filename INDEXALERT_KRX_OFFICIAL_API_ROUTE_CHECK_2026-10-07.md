# Official API route check — 2026-10-07

Read-only public documentation inspection; no credential request, API call, purchase, licence acceptance, source admission or policy change.

| Needed data | Inspected official route | Actual finding | Remaining distinction |
|---|---|---|---|
| KOSPI daily trading / security basics | KRX OpenAPI service list and exact service pages | Both named APIs are listed with2010-01-04 history; existing project connectivity is exact-service evidence | Source coverage/availability/current service approval still require existing scoped evidence. |
| Halt / cleanup / delisting history | KRX OpenAPI current published stock service list | No dedicated history API appears in the inspected published list | This scoped catalog absence is not proof no other official product exists. Current basics/daily trades cannot stand in for event history. |
| Investor-by-security trades | Same KRX catalog; Koscom provider's v3/v2 docs | KRX inspected catalog has no named investor-by-security service; Koscom documents investor endpoint as a separate provider/licensed route | Different licence/credentials and unverified historical coverage/PIT; not an already approved replacement. |
| Current trading halt / cleanup state | Koscom official stock master docs | haltYn / arrantrdYn fields described | Current flags do not establish complete historical events or delisting outcomes. |

Sources:
- https://openapi.krx.co.kr/contents/OPP/INFO/service/OPPINFO004.cmd
- https://openapi.krx.co.kr/contents/OPP/USES/service/OPPUSES002_S2.cmd?BO_ID=JvJFzlAENzZlPBDNGAWC
- https://openapi.krx.co.kr/contents/OPP/USES/service/OPPUSES002_S2.cmd?BO_ID=PiwgMdTwmsenXhmqqxuj
- https://koscom.gitbook.io/open-api/api/marketv3
- https://github.com/devkoscom/openapi/blob/master/api/market/stocks/README.md

Koscom current v3 docs say processing/accumulation, including development-support quotes, requires a quote licence/contract and warn sandbox data may not match actual quotes. Older v2 schema demonstrates candidate field meanings only; use current v3 contract before any integration. No expense/account setup is requested or authorized here.

Code correction paired with this check: retain historicalv3 JSON/hashes and integrity validation, but return current unrestricted web automation/history rights false following the contradictory original email and owner confirmation of no matching permission. Historical acquisition preflight therefore remains blocked even with exact prior execution consent and safe private storage. This correction does not affect the separately approved KRX OpenAPI adapter or globally prohibit internal-research storage/analysis.

Validation: direct stdlib assertion of actual committed evidence -> rights=false -> fully configured preflight denied with KRX_FULL_HISTORY_RIGHTS and no network request. Local pytest package unavailable; isolated pytest8.4.2 GitHub check validates existing evidence/preflight regression suite. Runtime and historical pinned worker images were not redeployed; source correction applies to this branch and future builds, not falsely claimed as applied to every deployed snapshot.
