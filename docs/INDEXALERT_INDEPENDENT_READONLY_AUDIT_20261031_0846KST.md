# IndexAlert independent profitability audit — 2026-10-31 08:46 KST

Scope: metadata/logs only; documentation-only isolated write. No original source bytes copied, no model/backtest, no deployment, no orders, no PR merge.

## Independently observed repository state
- Research branch `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a` (GitHub branches API).
- Development branch `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX source-audit branch `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- PR #412, #414, #416, #418, #420, #422, #423, #424: all open, Draft, unmerged on direct metadata query. #414 head before this audit write: `b24785b328b098631784f38ff1166cc44a7caf57`.
- GitHub Actions API latest run #41125666590 (2026-10-31 05:45 KST): successful watchdog. Its decoded job log reports 31 passing offline governance tests, `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This is not source or performance admission.
- Chronology run #41091128151: failed. Decoded job log confirms /anchor/latest HTTP 404 after 20 retries; follow-on validation skipped. Not an independently anchored prospective sample.

## Original source / PIT admission
- OpenDART official 2022 first-submitted Q3 document Actions run #38380988990 job #115241142185: original ZIP received, bounded ZIP/CRC read completed, 1 structured document entry, 1,570 tables, 15 operating-profit-shaped rows, zero strictly bound three-month CFS operating-profit facts. The original document layout diagnostic explicitly reports `m20_feature_pit_admitted=false`, original quarterly earnings unverified, original publication instant unverified. This is not an approved financial panel.
- Previously logged 2021/2022 original ZIP SHA-256 claims are *log-record digests only*. Independent rehash of original archive bytes was not performed in this run; SHA-to-original-binary provenance and filing revision chain remain unapproved.
- KRX specialist Draft #420 documents 90 unresolved historical source/session classifications and 27 nonpositive-OHLC prospective rows; dependent Drafts #422/#423 describe exact-calendar candidate checks, not approved actual private historical exact-set re-runs. Historical per-security tradeability and as-of-time PIT are not admitted.
- Do not conflate verified metadata, source fingerprint, source authority, timestamp chronology, security mapping, and executable tradeability.

## Railway read-only state
- Production `indexalert-pit-rebuild`: deployment SUCCESS, 1 running replica; most recent returned runtime log 2026-10-30 23:46:37 KST. `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 803 common-stock rows, 27 nonpositive OHLC, `independent_source_admission_verified=false`, `ordering=DISABLED`.
- `indexalert-kiwoom-real-readonly`: deployment SUCCESS but replica status 0 running / 1 crashed; latest returned deploy log 2026-10-29 15:22 KST only container start, no independently verified REAL authentication.
- Railway environment_status reports pending staged patch ID `e113dacb-6705-4416-9997-dc694539d382`; get_staged_changes reports `staged=null`. Read-model discrepancy; no staged change accepted or modified.

## Economic admission decision
- No approved PIT original-source panel, market calendar and historical tradability, as-of mapping, or executable fill/commission/slippage/tax ledger. No independently authorized frozen M20 return series.
- Therefore after-tax NetEV, PF, CAGR, MDD, ES95 and ES99 are NOT ESTIMABLE, not zero and not validated. No M20 profitability run.
- Preserve Frozen/Holdout/Champion/Top3 and preregistered WF504/126/126/cost/tax constraints unchanged. `ORDERING=false`. No funds, trading, permissions, deployments, merges, Champion promotion.
- Dependency sequence: original-byte rehash and first-publication/correction provenance; exact 3-month CFS fact binding; official KRX exact-session/per-security tradeability and PIT chronology; executable fill/cost/tax audit; only then independent approval for one immutable M20 profitability run.

Evidence links:
- https://github.com/kims34/openpilot-opkr/actions/runs/41125666590
- https://github.com/kims34/openpilot-opkr/actions/runs/41091128151
- https://github.com/kims34/openpilot-opkr/actions/runs/38380988990
- https://github.com/kims34/openpilot-opkr/pull/412
- https://github.com/kims34/openpilot-opkr/pull/414
- https://github.com/kims34/openpilot-opkr/pull/420
- https://github.com/kims34/openpilot-opkr/pull/422
- https://github.com/kims34/openpilot-opkr/pull/423
