# IndexAlert independent profitability gate — 2026-10-31 14:47 KST

Read-only independent evidence checkpoint. This document alone grants no source, PIT, trading, performance, holdout, or deployment authority. All other specialist workstreams and code are unchanged.

## Immutable observed refs
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a` (same-ref GitHub compare, identical).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (identical).
- KRX specialist `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698` (identical).
- Draft/unmerged PR #412 head `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #414 head at read `2f40106a6d0955302a25677491679caa000b7481`. KRX #420/#422/#423 and related #416/#418/#424 also Draft/unmerged.
- GitHub Actions latest repository run observed at this read: read-only watchdog #41151825793 completed SUCCESS 2026-10-31 00:45:03 UTC. Its job log explicitly says `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. A green watchdog is not source admission.
- Prospective chronology anchor #41091128151 FAILED (2026-10-30 17:13 UTC): `/anchor/latest` HTTP 404, downstream record creation and validation skipped.
- Official OpenDART first-filed 2022 Q3 document #38380988990, job 115241142185: original ZIP received, CRC/bounded read complete, 1,570 source tables, 15 operating-profit row shapes, zero exact 2021/2022 Q3 three-month window matches; no verified standalone consolidated 3-month operating profit. Original raw ZIP independent SHA-256 recomputation and first-publication/correction lineage still not attested. An Actions artifact ZIP digest is not the original document byte digest.
- Railway production `indexalert-pit-rebuild` latest returned runtime log 2026-10-30 14:46:37 UTC: `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27 nonpositive OHLC rows / 803 common-stock rows, independent source/model/chronology flags false, `ordering=DISABLED`, live orders false. No later runtime log returned. Railway `indexalert-kiwoom-real-readonly` returned only container start 2026-10-29 06:22 UTC, no new authenticated broker success.
- Railway `get_status` reported stagedChanges null but also a stale-looking pendingWork staged patch `e113dacb-6705-4416-9997-dc694539d382` with empty changes; `get_staged_changes` reported null. This inconsistent read is not evidence of a new deployment; no changes made.

## Independent gate verdict
- Raw source SHA: official source-level logs and private KRX receipts exist, but original OpenDART ZIP bytes have **not** been independently rehashed here; no independent admission.
- PIT: first-publication instant, correction lineage, 2021/2022 exact quarter context, historical issuer/security mappings and point-in-time availability unapproved.
- KRX/tradability: six-year raw integrity receipts do not resolve 90 uncertain historic sessions or 27 prospective nonpositive OHLC cases; orderable universe, historical limit/halts and execution price path remain unapproved.
- Costs/taxes: actual side-specific fees, tax jurisdiction/product treatment, slippage, spread, depth, queue/fill constraints and portfolio turnover remain unproven.
- NetEV, PF, CAGR, MDD, ES95 and ES99: **NOT ESTIMABLE / NOT ADMITTED** on approved independent data; do not fill with hypothetical or zero returns.
- M20 profitability run: **NO-GO**. Frozen/Holdout/Champion/Top3 untouched; `ORDERING=false` / `ordering=DISABLED`; no orders, funds, permissions, deployments, PR merges or Champion promotion.

## Reopen only upon
Independent raw-byte SHA + first-filed quarter binding + chronology/correction lineage; historical security/calendar and tradability attestation; cost/tax/fill schedule; pre-registered frozen out-of-sample evaluation authorization. Do not infer any approval from tests, deployment SUCCESS, or an audit document.
