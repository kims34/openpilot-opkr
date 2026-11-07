# IndexAlert independent profit/runtime audit — 2026-11-07 17:21 KST

Scope: read-only GitHub and Railway review; no economic run, no deployment, no merge, no ordering or policy changes. This document is isolated from PR #412/#413/#414/#418 and KRX owners.

## GitHub evidence
- Research branch HEAD df474df348f22aa38b1dedaa59fcff66e548b406 (fetch_commit branch ref); development HEAD 1e6367d2863a86c3470da13d81a955d277eba485.
- PR #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f. All OPEN/Draft/unmerged at inspection.
- Action 38419439742 2/2 success (OpenDART candidate diff); 38419649711 1/1 success (offline one runner); 38498552499 6/6 success (isolated optimization); 41515392296 auto-anchor failure, validation skipped. Job conclusions fetched directly. Historical 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 is previously reported, NOT independently rehashed in this run.
- PR #414 integration-gate file current blob SHA NOT VERIFIED this run: fetch_file failed. Earlier reported 984c933651f39f1ee9e26a1d7ac3893aaa5335be is prior evidence only.

## Railway production evidence
- Project d1c1a050-b7d6-41ce-b300-13c20f82a20a. describe_environment: staged=null; get_status: stagedChanges=null BUT pendingWork contains empty staged patch e113dacb-6705-4416-9997-dc694539d382, started 2026-10-29T06:20:53Z. Treat discrepancy as NOT VERIFIED, do not apply.
- Latest deployment status: indexalert-runtime SUCCESS, PIT rebuild SUCCESS, KRX historical worker SUCCESS, kiwoom real readonly SUCCESS; backend and push FAILED (old deployments from 2026-09-23). Deployment status is NOT a live replica health proof. Runtime/PIT/KRX/real-readonly configured replica count 1, not actual running count.
- Log window from 2026-11-07 06:00Z: PIT, KRX, real-readonly no deploy logs; runtime has 08:21Z Investing.com USD/KRW HTTPError then Yahoo fallback, and EWY extended-session unavailable. Existing OHLC 27 anomalies, 90 uncertain sessions and 12003 zero-activity exclusions are not cleared by empty logs.

## Gate verdict
PASS only for named offline CI job conclusions and historical reported private storage-pair integrity (1565/1565, prior evidence; no new rehash).
FAIL: chronology auto-anchor job. NOT VERIFIED: original-filing/public available-at/PIT, 2021/2022 original 3-month consolidated operating profit and correction lineage, historical issuer/ticker mapping, official KRX sessions/corporate actions/fillability, all after-cost/tax NetEV/PF/CAGR/MDD/ES95/99/concentration/regime robustness, and actual full-backtest acceleration. NO-GO M20 and ORDERING=false. Frozen H5, M20 horizon20/purge20, WF504/126/126, independent holdout, Champion/Top3/NO_TRADE and all cost/risk/promotion policies unchanged. H5 spent holdout not reusable.

## Next read-only steps
1. Inspect chronology anchor failed job logs and reconcile exact public-available-at source SHA and routing before any PIT approval.
2. Independently compare official KRX session/corporate-action evidence and historical issuer mapping against immutable originals.
3. Obtain replica/health evidence distinct from deployment SUCCESS, inspect readonly crash cause and pending patch discrepancy without applying changes.
4. For optimization, keep fail-closed SHA-256 evidence-key caching and parallelize only independent read-only postprocessing; do not parallelize dependent refits/capital transitions. Offline synthetic safety tests only until source PIT approval.
