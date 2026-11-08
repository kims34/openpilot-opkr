# IndexAlert independent profitability and offline optimization audit — 2026-11-09 01:24 KST

Scope: read-only GitHub and Railway evidence; no live trading, economic M20 run, workflow edits, deployments, merges, or Champion promotion. This is an evidence ledger, not a source approval.

## GitHub PR HEADs verified directly this run
- #412 OpenDART OPEN/DRAFT head bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- #413 offline optimization OPEN/DRAFT head f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- #414 profitability gate OPEN/DRAFT head 18c5418d9684d1717df58261ea27f28e514385b2; docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md blob 984c933651f39f1ee9e26a1d7ac3893aaa5335be
- #418 single runner OPEN/DRAFT head 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- KRX #420 OPEN/DRAFT fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 OPEN/DRAFT c14857620973531013799e44625d43080904fd5f; #423 OPEN/DRAFT 0e38004363cac9fc4475556b3a1c445de9af407f.
- Research branch index-alert-research-v1 and development index-alert-position-regen-fix-v1 exist; exact branch HEAD not independently obtained this run. Prior reported HEADs df474df348f22aa38b1dedaa59fcff66e548b406 and 1e6367d2863a86c3470da13d81a955d277eba485 are historical anchors, NOT VERIFIED as current HEAD.
- Independent audit branch indexalert-independent-audit-20261108-1921kst exists.

## GitHub Actions jobs directly re-read
- 38381997417: 6/6 success; 38382214223: 6/6 success; 38419111311: 6/6 success; 38419649711: 1/1 success; 38419439742: 2/2 success.
- Chronology anchor 41515392296: auto-anchor FAILURE; validation SKIPPED. This is a blocking FAIL, not a source PIT PASS.
- Historical 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and 2.9656s vs 2.6209s are supplied prior evidence, not rehashed or rebenchmarked this run. Full CI / real official backtest acceleration NOT VERIFIED.

## Railway production direct read
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS; replicas running 1/1.
- KRX historical worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS; 0/1 running (noncontinuous worker); historical 1565/1565 stored-pair integrity remains prior PASS only.
- Runtime deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS; replicas 1/1.
- Real readonly deployment a77fb922-b679-4d88-92c4-03054ec579cd reports online/SUCCESS yet running 0, crashed 1 of 1: operational mismatch, NOT healthy.
- db-query-readonly offline, critical 1; backend offline warning 4; push offline warning 1.
- pendingWork includes staged empty changes patch:e113dacb-6705-4416-9997-dc694539d382 (started 2026-10-29T06:20:53Z). Do not accept/deploy or mutate.
- Deploy log window 2026-11-08T15:00:00Z to 16:25:00Z: PIT 0 entries, KRX 0, real readonly 0; runtime 101 entries, index/FX quotes, not a backtest approval. Absence of logs does not prove service health or source correctness.
- Prior COMMON_OHLC_NONPOSITIVE 27/803 on 2026-09-28 session is a historical blocker; not independently re-observed in this window.

## Independent gate disposition
PASS (limited): previously documented 1565/1565 weekday pair storage integrity, offline CI job outcomes. FAIL: chronology anchor action and readonly replica health; source/market gates remain fail-closed. NOT VERIFIED: official original-filing available-at/PIT; 2021/2022 initial 3-month consolidated operating profit period/correction lineage; historical corp/security identity; official KRX market calendar/tradability/corporate actions/execution; fees/taxes; net annual risk-adjusted NetEV/PF/CAGR/MDD/ES95/99, return concentration, regime robustness; full-run speedup.
M20 NO-GO; ORDERING=false. H5 consumed holdout and dynamic retrospective tuning must not be reused. Frozen H5 and M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE and risk/cost/approval gates unchanged.
Cache only with independently approved source/data/code/Frozen/runtime/approval evidence SHA-256; fail closed. Parallelize only independent read-only postprocessing, not retraining or capital transitions.

Next: obtain exact branch HEAD by independent commit ref method; owner teams to resolve original-filing chronology, exact Q3 lineage, KRX official tradability and 27 veto rows, and readonly replica failure. Re-check evidence without altering shared code. No market-performance run until independently approved.
