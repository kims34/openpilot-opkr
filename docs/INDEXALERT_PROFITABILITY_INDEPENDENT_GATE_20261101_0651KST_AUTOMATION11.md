# IndexAlert independent profitability audit — 2026-11-01 06:51 KST

Decision: **M20 NO-GO / FAIL-CLOSED**. Independent read-only evidence audit; this single Markdown file is the only authorized write attempt. This note does not approve any original source, PIT feature, strategy, Holdout, order, deployment, permission or model promotion.

## Current independently fetched references
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a` (unchanged).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (unchanged).
- KRX audit `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698` (unchanged).
- Draft PR #414 head `0d3f37eddfa8973b82fff4f26651a2c51127c656` before this isolated documentation write. Draft PR #412 head `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; KRX Draft #420/#422/#423 heads `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, `c14857620973531013799e44625d43080904fd5f`, `0e38004363cac9fc4475556b3a1c445de9af407f`. All open/unmerged at read time.
- Latest listed Watchdog Actions #41229825403 (2026-10-31 18:31 UTC) successful; actual job log: four watchdog tests and 31 research governance tests passed, `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. CI success does **not** authorize M20.
- Chronology Anchor Actions #41091128151: `/anchor/latest` HTTP 404, anchor fetch failed, validation skipped. No independently verified immutable chronology admission.
- Official OpenDART 2022 first-filing Actions #38380988990, actual source-only job log: first-document ZIP received, CRC/bounded read true, 1,570 tables and 15 operating-profit row *shapes*, but exact 2021/2022 Q3 window matches zero, standalone consolidated three-month profit unverified. No earnings fact, historical available-at or corrected-edition lineage approval.
- Prior reported 2022 first-document ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` is a **recorded receipt only** in this run; the original ZIP bytes were not available for independent SHA-256 recomputation. An Actions-upload artifact ZIP digest is a different object and cannot substitute for source-byte verification.
- KRX historical 2017–2022 raw pair SHA audit previously reported 1,565/1,565 stored weekday pairs with no invalid stored pairs. This is storage integrity, not historical market-calendar, trading-status, corporate-action or fill admission. Ninety historical uncertain sessions remain unresolved. Separately, prospective source session 2026-09-28 has 27 nonpositive OHLC common-stock rows (among 803); these are distinct populations.
- Railway production PIT service: latest returned log `2026-10-31T14:46:01.190084194Z` (23:46:01 KST), session `2026-10-31`, source failure session `2026-09-28`, `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, independent source/model/chronology flags false, `session_manifest_sha256=null`, `ordering=DISABLED`, live orders/funds/permission change false.
- Railway Kiwoom REAL read-only: deployment reports SUCCESS but health replica counters show running 0 / crashed 1, no new authentication success in returned runtime logs. `describe_environment` and `get_staged_changes` show no staged patch, while `environment_status` reports an older pending patch `e113dacb-6705-4416-9997-dc694539d382`; this inconsistent status was not applied or modified.

## Independent economic gate
- Original source bytes and SHA: **not independently attested**.
- First-published edition/available-at, corrected-document lineage, PIT issuer/security mapping: **not admitted**.
- Historical exchange calendar, suspension/listing, corporate actions, price/volume validity and executable tradability: **not admitted**.
- Commission, spread, slippage, partial fills, turnover, capital/lot feasibility, transaction taxes and net execution ledger: **not independently validated**.
- After-tax NetEV, PF, CAGR, MDD, ES95 and ES99: **not computable as approved PIT results**. No M20 performance run was started and no substitute/synthetic profitability was asserted.

## Unchanged controls
`M20 performance_run_authorized=false`; Frozen/Holdout/Champion/Top3 and preregistered evaluation rules unchanged. `ORDERING=false` / runtime `ordering=DISABLED`. No live orders, funds, credential/permission changes, deployment, PR merge, Champion promotion, or duplicate specialist-source modification. Source/PIT approval must precede any one-time preregistered M20 performance test; the isolated audit does not supply that approval.

Evidence:
- https://github.com/kims34/openpilot-opkr/pull/414
- https://github.com/kims34/openpilot-opkr/pull/412
- https://github.com/kims34/openpilot-opkr/pull/420
- https://github.com/kims34/openpilot-opkr/pull/422
- https://github.com/kims34/openpilot-opkr/pull/423
- https://github.com/kims34/openpilot-opkr/actions/runs/41229825403
- https://github.com/kims34/openpilot-opkr/actions/runs/41091128151
- https://github.com/kims34/openpilot-opkr/actions/runs/38380988990
