# IndexAlert M20 — Official 2022 first-filed OpenDART source handoff (2026-10-13)

**Evidence classification:** `FIRST_FILED_2022_DOCUMENT_PROVENANCE_ONLY_NOT_PIT`.
**Downstream admission decision:** `NO_GO_SOURCE_INCOMPLETE`.
This report contains *verified source metadata only*; it does **not** contain, infer, repair or admit original financial values or a performance claim.

## Reproducible official proof

- Repository: `kims34/openpilot-opkr`.
- Isolated branch: `indexalert-m20-opendart-original-proof-20261013`, forked from `index-alert-research-v1` commit `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Official read-only Actions run: https://github.com/kims34/openpilot-opkr/actions/runs/38381866190
- Offline security/lineage tests: **SUCCESS**; official read-only original proof: **SUCCESS**.
- Evidence artifact ID `11804485794` (`indexalert-m20-opendart-2022-original-source-proof`; retention 7 days); archive digest `sha256:3ffe9b379896175c68bc38dd6cf411fe33de85f216cd221db58cdf786bac5788`.
- The **original official first-filed document ZIP** SHA-256 fingerprint: `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`. SHA is a non-reversible source integrity fingerprint, **not** a fact table or issuer ID.
- Fixed ex-ante source sample slot **5**, original 2022 Q3 report. No issuer substitution.
- OpenDART's existing registered GitHub Actions secret was available (`credential_present=true`) but **not logged or stored**.
- The complete **bounded initial filing-index page** was validated and the **first submitted report's date and receipt binding** verified. The same-period subsequent version count **inside that initial search window** was **0**. This does **not** establish that later historical correction filings never occurred.
- Exactly three pre-existing approved official endpoints were used: `corpCode.xml`, `list.json`, `document.xml`.
- ZIP integrity verified; one structured markup source, of legacy **SGML/HTML** form rather than standardized original financial XBRL; no financial values persisted.
- The independent earlier original layout scan: [run #38380988990](https://github.com/kims34/openpilot-opkr/actions/runs/38380988990), 1,570 tables; 15 apparent operating-income row **shapes**, 12 with four numeric-looking peer cells; **zero** authoritative 2022/2021 July–September period-table bindings or CFS standalone-quarter facts. Treat all shape counts as **non-factual**.
- The original 2022 standardized financial XBRL route had reported provider status `014` / file not found; `document.xml` is a different source type, not a substitute for a validated XBRL fact.

## Remaining hard blockers — no data correction, backfill or experiment

1. Exact first-filed **2022 Q3 three-month standalone consolidated operating-profit value** and **2021 Q3 comparable value** are not verified in original statement context; SGML proximity and apparent numbers cannot be substituted.
2. Full subsequent correction-filing lineage and exact **public release timestamp** remain unverified. A receipt *date* is not a PIT available-at instant.
3. Historical corp/security identity and historical tradability/capitalisation coverage, complete intended cross-sectional history, and actual costed KRX return paths remain unverified.
4. Original XBRL 2022 `014` is unresolved as a standardized source gap; no implied accounting-field aliasing or latest-API backfill allowed.

## Immutable guardrails and handoff contract

- `is_standardized_financial_xbrl=false`
- `original_cfs_q3_three_month_operating_profit_verified=false`
- `original_q3_qminus4_comparability_verified=false`
- `historical_publication_instant_pit_verified=false`
- `full_correction_lineage_verified=false`
- `m20_feature_pit_admitted=false`
- `m20_performance_run_authorized=false`
- `independent_holdout_authorized=false`
- `champion_change_authorized=false`
- `real_orders_authorized=false`, `funds_movement_authorized=false`, `permissions_change_authorized=false`
- `ORDERING=DISABLED`; no broker API/network use, no live trading or capital movement.

**For the separate M20 profitability Work:** this file and the run are **source-gap/provenance evidence only**. Do not pass source-shape rows or the ZIP digest as an M20 feature, label, price or alpha result. Performance remains `NOT_EVALUABLE_NEW_EVIDENCE_REQUIRED` until every original-data and PIT gate has independent affirmative evidence. Frozen/H5 and the preregistered M20 experiment/Champion/holdout remain untouched.


## 2026-10-13 continuation — original ZIP fingerprint fail-closed regression

- Change commits: `7e3605036488e9c8805a3b176543613e9e2e5054` (source SHA-256 gate), `71586fac66c4ce945685c6e26cbfeacfa09984ab` (positive and negative regression cases), `d976330498991c59d2571c043e1e09528bbdc0c8` (official CI SHA assertion).
- [Latest completed real official run #38392847048](https://github.com/kims34/openpilot-opkr/actions/runs/38392847048), head `d976330498991c59d2571c043e1e09528bbdc0c8`: **offline-security-and-lineage SUCCESS** and **official-original-read-only SUCCESS**.
- The original 2022 slot-5 document ZIP SHA-256 matched the previously audited `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`. The prior digest is now pinned and checked **before** SGML layout inspection; any changed ZIP is `SOURCE_GAP_FAIL_CLOSED / ORIGINAL_DOCUMENT_SHA256_DRIFT` without recording the altered hash, financial contents or admitting M20 PIT.
- New regression explicitly proves that a mismatched response skips layout, rejects M20/holdout/orders and does not expose provider keys; fixed expected hash is independently asserted by offline tests and official CI.
- Latest actual evidence artifact ID `11811306026`, `indexalert-m20-opendart-2022-original-source-proof`, ZIP artifact digest `sha256:2738ccf8f1794d9975a384671d96822c4b003040c151c2f382030c53ce1ec1d8` (7-day retention). This archive is a **flags-only report**, not the OpenDART document ZIP.
- Continuing source gate: the source remains **non-XBRL SGML**; neither 2022 nor 2021 three-month original CFS operating-profit fact is bound to a validated statement/window. Original XBRL provider `014`, entire correction history, intraday publication instant and historical issuer/security PIT remain unresolved. No M20 performance or live admission.
