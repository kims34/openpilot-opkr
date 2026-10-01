# IndexAlert Kiwoom Demo Connectivity Evidence

Updated: 2026-10-02 KST
Branch: `index-alert-research-v1-kiwoom-demo-connectivity`
Evidence class: **DEMO / READ-ONLY CONNECTIVITY ONLY**

## Observed result

A user-operated local PowerShell smoke test against the Kiwoom mock REST host completed all four read-only stages successfully:

- `TOKEN_OK` — OAuth client-credentials token issuance succeeded against the demo host;
- `ACCOUNT_OK` — demo account-number query succeeded;
- `BALANCE_OK` — demo account evaluation/balance query succeeded;
- `FILLS_OK` — demo fill/order-history query succeeded.

The smoke test targeted `https://mockapi.kiwoom.com` only and used the currently reviewed official Kiwoom REST schema:

- token: `POST /oauth2/token`;
- account-number query: `ka00001`, `/api/dostk/acnt`;
- account evaluation/balance: `kt00018`, `/api/dostk/acnt`;
- filled-order query: `ka10076`, `/api/dostk/acnt`.

No order-create, amend, cancel, real-account, Tiny Live, Limited Live or LIVE endpoint was invoked by this smoke test.

## Privacy / secret handling

The retained project evidence intentionally excludes:

- App Key / App Secret;
- access token;
- full account number;
- balance amounts;
- raw broker response payloads.

Only the four stage outcomes above are recorded in this document. The credential material remains outside the repository and is not project evidence.

## What this proves

This result proves only that, in the observed user-operated demo session, Kiwoom demo authentication and the three reviewed read-only account APIs were reachable and returned responses sufficient for the smoke test to continue.

It is valid plumbing/readiness evidence for the demo integration path.

## What this does **not** prove

This result does **not** prove any of the following:

- genuine real-account broker provenance;
- real-market fill quality, latency, partial-fill, no-fill or slippage behavior;
- exact status-event economics;
- execution-sufficiency protocol satisfaction;
- KRX source-gate closure;
- model promotion readiness;
- sealed-holdout authorization;
- live-trading authorization.

Therefore current project state remains fail-closed:

- `genuine_live_provenance_verified=false`;
- `live_empirical_execution_evidence_ready=false`;
- `empirical_execution_sufficiency_assessed=false`;
- `empirical_execution_blocker_closed=false`;
- `promotion_ready=false`;
- `sealed_holdout_authorized=false`;
- `live_trading_authorized=false`.

## Next allowed engineering work

The next permitted Kiwoom work remains limited to demo/read-only integration, secret-safe configuration, reconciliation plumbing, offline broker-native mapping, and fail-closed tests. Any move to real-account requests or order-capable methods requires a separate reviewed gate change under `INDEXALERT_KIWOOM_REST_READINESS_CONTRACT.md` and the higher-order execution/provenance contracts.
