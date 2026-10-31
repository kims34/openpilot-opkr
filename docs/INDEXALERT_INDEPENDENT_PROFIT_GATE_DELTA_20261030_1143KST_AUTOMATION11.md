# IndexAlert independent profitability gate — 2026-10-30 11:43 KST

## Allowed scope and provenance
This run read GitHub branch/PR/Actions metadata and job logs plus Railway production service state and deploy logs. No original ZIP bytes or protected private Railway volume were accessed, no official-source network requests were newly launched, no M20 profitability/holdout/strategy tests were executed, and no specialist branch or implementation file was changed. This is a single isolated Markdown-only audit note.

## GitHub branch and PR snapshots (direct REST)
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a` (unchanged).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (unchanged).
- KRX specialist `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698` (unchanged).
- Draft/open/unmerged: #412 `bf3d951`; #414 pre-note `520830f`; #416 `053de553`; #418 `2f98401`; #420 `fab3cbb`; #422 `c148576`; #423 `0e38004`. ETF #424 is separate offline/watch-only research, not M20 admission.
- Actions total_count 4622. New [read-only Watchdog #40988735313](https://github.com/kims34/openpilot-opkr/actions/runs/40988735313), created 2026-10-30T01:56:09Z, completed success. Job `readonly-proof-audit` 123845746566: four watchdog and 31 governance tests passed, and explicitly reports `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Passing safety checks are not original-data, financial-performance, or production authority.
- [Chronology Anchor #40914179246](https://github.com/kims34/openpilot-opkr/actions/runs/40914179246) remains failed: source payload fetch failed and chronology record/validation steps skipped. No new independently attested available-at clock.

## Independent original-source SHA, PIT and economics gates
- Prior first-2022 Q3 original ZIP SHA256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` (15 operating-profit label candidates) and first-2021 Q3 original ZIP SHA256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625` (13 candidates) are **existing official Actions log attestations**, not newly independently recomputed SHA from original ZIP bytes. Both have zero strictly bound standalone 3-month CFS facts. Exact amount, unit, sign, financial statement context, first publication timestamp, original/correction vintage lineage and historical issuer-security identity remain unapproved.
- Historical KRX 90 uncertain sessions and prospective common-stock 27 nonpositive OHLC rows remain unresolved; exact market calendar, suspensions, corporate actions, liquidity, fill feasibility and security-level PIT are unapproved. Private original data cannot be replaced by synthetic offline comparison.
- No approved executable price/volume, bid-ask spread, fees, slippage, market impact or actual tax/fill ledger. **After-tax NetEV, PF, CAGR, MDD, ES95, ES99: NOT EVALUABLE**, not zero and not evidence of profit. The prior runtime manifest blob SHA mismatch is not independently resolved.

## Railway production direct reads
- Production `indexalert-pit-rebuild` has 1 running / 0 crashed replica and deployment SUCCESS. Latest returned deploy log is 2026-10-29T14:46:05Z (23:46:05 KST in this bounded query), `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27 of 803 common-stock OHLC rows nonpositive, `session_manifest_sha256=null`, independent source/chronology/model flags false, funds/orders/permissions false, `ordering=DISABLED`. No newer PIT log returned in this query; observation gap does not prove service outage.
- `indexalert-kiwoom-real-readonly` deployment SUCCESS but replica status running=0/crashed=1. Latest observed 2026-10-29T06:22:02Z structured attributes: `TOKEN_OR_LOGIN_AUTH`, code 8050, `TOKEN_OK=false`, `WS_CONNECTED=false`, `TYPE00_EVENT_COUNT=0`, `ORDERING=DISABLED`, `REAL_ORDERS_AUTHORIZED=false`. No new authenticated broker proof.
- KRX historical worker returned zero recent deploy log entries. Production has an existing staged empty patch; no patch was accepted or deployed. Runtime service log data was not interpreted as financial strategy evidence.

## Decision / hard stop
**M20 profitability execution NO-GO.** Original SHA/PIT/tradability/cost-tax evidence is not independently admitted. Preserve Frozen/Holdout/Champion/Top3, preregistration and `ORDERING=false`; no orders, funds, permission changes, deployment, PR merge, promotion or specialist overlap. Recheck only if source provenance, PIT chronology, security-level executable tradability, cost/tax proof, or major new blocker changes.
