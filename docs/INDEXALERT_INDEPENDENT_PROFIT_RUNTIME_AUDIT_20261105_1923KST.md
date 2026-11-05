# IndexAlert independent profitability and runtime audit — 2026-11-05 19:23 KST

## Evidence boundary
Read-only GitHub Actions and Railway production inventory/logs. Audit branch based on verified repository default ref `HKG_community` (README default display URL); this is not the research/development HEAD. No model, market profitability, deployment, ordering, or production modifications.

## Newly observed critical blocker
Railway service `indexalert-pit-rebuild`, deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, 2026-11-05T10:15:37.947537478Z: `status=FAIL_CLOSED`, `error_class=KRXProspectiveOpenAPISourceError`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`; 803 common-stock rows, 27 nonpositive OHLC rows, 27 zero-volume/value rows, `session_manifest_sha256=null`, `fresh_alpha_observation_admitted=false`, `independent_source_admission_verified=false`, `ordering=DISABLED`. A private rejected source receipt was saved. This is evidence of fail-closed rejection, NOT evidence of a valid official KRX session. Previous `source_failure_session=2026-09-28` must not be interpreted as current provenance.

## CI evidence
GitHub Actions jobs fetched in this run: [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417) 6/6 PASS; [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223) 6/6 PASS; [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) 6/6 PASS; [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 PASS; [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 PASS. [41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296): auto-anchor FAIL at public hash-only payload retrieval; validation SKIPPED. Earlier 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and 1.1315x regression-phase figure are historical assertions not recomputed this run. Whole-CI and real official backtest speed NOT VERIFIED.

## Production inventory
Railway IndexAlert production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`: PIT rebuild latest deployment SUCCESS 2026-10-10; KRX historical worker latest deployment SUCCESS 2026-10-12, but no new worker logs after 09:00 UTC in this query. Runtime latest deployment SUCCESS 2026-10-05; 10:22 UTC logs show Yahoo USD/KRW fallback after Investing HTTP error and market-display data; these are NOT official PIT approval. Backend and Push latest deployment FAILED. Environment staged=null.

## Gate verdicts
- Official original-filing and public available-at PIT: NOT VERIFIED.
- 2021/2022 first three-month consolidated operating profit and correction lineage: NOT VERIFIED.
- Historical issuer/security mappings: NOT VERIFIED.
- KRX official trading calendar/status/corporate actions/executability: NOT VERIFIED; current prospective session source rejection FAIL_CLOSED (safety PASS, source admission FAIL).
- Costs/taxes, NetEV/PF/CAGR/MDD/ES95/99, concentration and temporal robustness: NOT VERIFIED.
- H5 Frozen/Holdout independence and M20 horizon20/purge20 WF504/126/126: unchanged, no run.
- M20 profitability: NOT EVALUABLE / NO-GO.
- Optimization offline CI: PASS only for observed jobs; immutable suite SHA, benchmark scope and full CI speed NOT VERIFIED this run.

## Safe next steps
Independently reconcile 27 nonpositive OHLC observations with official KRX calendar, suspension and corporate-action lineage using private receipts without admitting them into alpha. Validate original filing chronology and corrections with independent source SHA. Recheck research/development exact HEAD and PR #412/#413/#414/#418 plus KRX PR heads using authenticated read APIs before making any cross-branch claim. Keep cached evidence fail-closed, ORDERING disabled, no M20 economics or market backtest, no workflow changes/merges/deployments/trades.
