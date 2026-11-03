# IndexAlert independent evidence audit — 2026-11-03 17:16 KST

Read-only audit, isolated from PR #412/#413/#414/#418 and other Work. Base commit: ac28f98db3ac605ac2410efbb051549718458019. Branch source is prior isolated audit commit, **not verified as current research/development HEAD**. No market performance run or trading authority.

## Fresh independent checks
- PR #414 gate file fetched at refs/pull/414/head: explicitly retains original-filing PIT and KRX tradability FAIL-CLOSED, M20 run unauthorized, H5 historical holdout consumed. Fetch confirms document existence, not PR HEAD SHA.
- Research index-alert-research-v1 and development index-alert-position-regen-fix-v1: README.md path lookup returned 404; this is **not evidence that branches are absent**. Their current HEADs were NOT VERIFIED in this run.
- GitHub Action 38419111311: jobs queried, six successful jobs (offline synthetic CI); action 38419649711: one successful job, synthetic one-runner comparison. Exact 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 is historical evidence, not independently recomputed this run. Whole-CI or actual backtest speedup NOT VERIFIED. Prior PR #418 archived manifest SHA mismatch remains FAIL-CLOSED pending independent resolution.
- Chronology Action 41515392296: auto-anchor failed at 'Fetch today's public hash-only prospective payload'; validation skipped. Independent chronology admission NOT VERIFIED.
- Railway IndexAlert production: KRX worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, source commit 1e6367d2863a86c3470da13d81a955d277eba485; 1565/1565 weekday pair storage integrity historical PASS only. Official calendar, status, corporate actions, execution and taxes NOT VERIFIED.
- Railway PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, returned runtime logs show 27/803 nonpositive OHLC, session_manifest_sha256=null, FAIL_CLOSED, ORDERING=DISABLED, source_failure_session=2026-09-28. Success of deployment is not source admission.
- Railway Kiwoom REAL readonly deployment a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS; runtime TOKEN_OR_LOGIN_AUTH detail 8050, WS_CONNECTED=false, REAL_ORDERS_AUTHORIZED=false.
- Railway runtime logs contain market proxy quotes, not independent official PIT or model-profitability evidence; do not promote to PASS.

## Gate assessment
- OpenDART 2021/2022 original 3-month consolidated operating profit, exact original-filing public available-at, restatement lineage and historical corp/security map: NOT VERIFIED.
- KRX original-pair private storage integrity: historical PASS (not independently rehashed here). Official tradability, calendar, delistings, actions, costs and taxes: NOT VERIFIED.
- H5 frozen and consumed holdout: NO-GO, no retrospective retuning/reuse.
- M20 horizon20/purge20, WF504/126/126, frozen selection and risk gates: unchanged; performance NOT EVALUABLE / NO-GO. NetEV/PF/CAGR/MDD/ES95/99 and concentration/temporal robustness NOT VERIFIED. No M20 run.
- Optimization: synthetic CI limited PASS; archived manifest mismatch FAIL-CLOSED; full CI/market backtest acceleration NOT VERIFIED. Cache must match approved source/data/code/frozen policy/runtime/evidence SHA-256 and fail closed; parallelize read-only independent postprocessing only.
- ORDERING=false, no merge, deploy, order, fund transfer, permission change, Champion promotion or workflow modification.

## Next
Obtain exact research/development HEAD and current PR/KRX Actions metadata from authoritative refs; independently compare original-filing PIT/lineage and KRX official tradability SHA-bound artifacts; resolve anchor source 404 and archived manifest mismatch in owning isolated Work. Keep M20 blocked until all source gates independently PASS.