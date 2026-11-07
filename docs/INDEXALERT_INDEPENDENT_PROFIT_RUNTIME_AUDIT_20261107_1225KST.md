# IndexAlert independent read-only audit — 2026-11-07 12:25 KST

## Scope and provenance
Repository: kims34/openpilot-opkr. Read-only GitHub PR search, GitHub Actions job evidence, Railway project/service inventory, production environment status and deployment logs. This is an independent audit record only, not source admission, model experimentation, or approval.

Research branch `index-alert-research-v1` and development `index-alert-position-regen-fix-v1`: previous confirmed HEADs `df474df348f22aa38b1dedaa59fcff66e548b406` and `1e6367d2863a86c3470da13d81a955d277eba485`; current HEADs **NOT VERIFIED in this run**. PR #414 previously confirmed HEAD `18c5418d9684d1717df58261ea27f28e514385b2` and document blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; current HEAD **NOT VERIFIED**. GitHub search returned PR #412/#413/#414/#418 and KRX #420/#422/#423, plus #424, but search is not authoritative for draft/merged state; latest exact state **NOT VERIFIED**.

## Fresh evidence
- GitHub Actions #38419439742: offline-row-security-tests and official-safe-candidate-row-diff **2/2 success**. Original SGML meaning/available-at not independently admitted.
- #38419649711: one-runner-offline-comparison **1/1 success**. Prior 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` not freshly recomputed; 2.9656/2.6209=1.1315 regression-phase ratio only; whole-CI and official backtest acceleration NOT VERIFIED.
- #38498552499: serial regression, four parallel component suites, exact parity **6/6 success**. Other historical job IDs and underlying artifacts not independently rehashed in this run.
- Chronology Anchor #41515392296: auto-anchor **FAIL**, validation **SKIPPED**; previous /anchor/latest HTTP 404 cause NOT VERIFIED.
- Railway production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`: PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, running 1/1; KRX historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS but running 0/1 (no crash); runtime deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, running 1/1.
- Kiwoom real-readonly deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS **but replica running 0, crashed 1/1**: runtime health FAIL / deployment metadata PASS. Do not infer authorization or safe broker readiness.
- Pending Railway patch `e113dacb-6705-4416-9997-dc694539d382`: STAGED, changes=[]; status/meaning NOT VERIFIED. Do not accept/deploy.
- PIT/KRX/real-readonly logs from 2026-11-07 10:00 KST onward returned no entries. No evidence of correction of 27 OHLC anomalies or 90 uncertain sessions. Runtime at 12:25 KST logged Investing.com USD/KRW HTTPError and Yahoo fallback, plus KOSPI extended session unavailable; operational source fallback, not official PIT evidence.

## Independent gates
- KRX archived 1565/1565 weekday raw pairs: historical storage-integrity PASS **as previously evidenced**, official session/calendar/status, corporate actions, fillability and actual costs/taxes NOT VERIFIED.
- 2021/2022 original first 3-month CFS operating income, correction lineage and exact public available-at, historical issuer/security mapping: NOT VERIFIED.
- Original filing PIT and full KRX market-source PIT: NOT VERIFIED.
- NetEV, PF, CAGR, MDD, ES95/ES99, concentration, rolling robustness and annual after-tax risk-adjusted return: NOT VERIFIED.
- Offline synthetic CI: PASS at job level only; end-to-end backtest runtime gain: NOT VERIFIED.
- M20 admission: **NO-GO**; H5 failed/consumed holdout and Dynamic results never reused. Frozen H5/M20 horizon20/purge20, WF504/126/126, Purged/CPCV, independent Holdout, Champion/Top3/NO_TRADE and costs/risk policies unchanged. ORDERING=false. No live orders, money movement, credentials, promotion, merge, deploy or source-performance experiment.

## Next allowed work
1. Obtain immutable current branch/PR HEAD and CI artifact SHA and independently compare to frozen source, without touching other Work branches.
2. Trace chronology-anchor 404 against deployed route/commit, read-only; do not patch workflow or Railway without separate approval.
3. Source-owner independent original-filing time/lineage and KRX official calendar/status, OHLC anomalies and archived SHA proof, before M20 admission.
4. Keep isolated cache strictly SHA-256 fail-closed; only independent read-only post-processing parallel, no capital transitions or dependent model training.

Audit evidence URLs: https://github.com/kims34/openpilot-opkr/actions/runs/38419439742 ; https://github.com/kims34/openpilot-opkr/actions/runs/38419649711 ; https://github.com/kims34/openpilot-opkr/actions/runs/38498552499 ; https://github.com/kims34/openpilot-opkr/actions/runs/41515392296 .
