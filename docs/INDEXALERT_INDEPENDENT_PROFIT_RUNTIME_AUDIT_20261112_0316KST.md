# IndexAlert independent audit — 2026-11-12 03:16 KST

Scope: read-only GitHub/Railway evidence; no economic run, strategy modification, deployment, merge, ordering, or promotion. Prior run claims are not treated as fresh proof.

## Exact branch and PR evidence
- research index-alert-research-v1 HEAD df474df348f22aa38b1dedaa59fcff66e548b406 (GitHub compare against pinned SHA: identical, 0 ahead/0 behind).
- development index-alert-position-regen-fix-v1 HEAD 1e6367d2863a86c3470da13d81a955d277eba485 (identical, 0/0).
- PR #412 OPEN draft HEAD bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 OPEN draft HEAD f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 OPEN draft HEAD 18c5418d9684d1717df58261ea27f28e514385b2; #418 OPEN draft HEAD 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 HEAD fab3cbbd63a951a4e081f9e7f08c1391ca308581, #422 HEAD c14857620973531013799e44625d43080904fd5f, #423 HEAD 0e38004363cac9fc4475556b3a1c445de9af407f (all OPEN draft).
- PR #414 integration gate document blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be, fetched from exact PR HEAD; read-only.
- Actions jobs fetched fresh: 38381997417 6/6 success, 38382214223 6/6 success, 38419111311 6/6 success, 38419649711 1/1 success, 38419439742 2/2 success. Job success = CI-only PASS; 34-case identity SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 NOT independently recomputed this run. 13 adversarial and 28 synthetic assertions NOT independently replayed. 2.9656s serial / 2.6209s concurrent = 1.1315x regression-phase only (historical), whole-CI and official backtest speed NOT VERIFIED.

## Railway production
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a. Environment-status fresh read: pit-rebuild 1/1 running (deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5), runtime 1/1 running (eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00), krx-historical-worker 0/1 running (16c93d7c-7cd0-4d84-a327-298d2805376c), kiwoom-real-readonly 0/1 running, 1/1 crashed (a77fb922-b679-4d88-92c4-03054ec579cd): replica runtime FAIL. Backend, push and db-query-readonly offline; db-query-readonly one critical. Staged patch e113dacb-6705-4416-9997-dc694539d382 has empty changes list; left untouched.
Deploy logs read for PIT, KRX, Kiwoom, runtime, window 2026-11-11 17:00–18:20 UTC. PIT/KRX/Kiwoom zero entries in this bounded window; absence is not evidence of healthy service. Runtime USDKRW investing HTTPError -> Yahoo fallback at 18:10 UTC, other market snapshot logs. This does not authorize historical market-data PIT or economic testing.

## Independent gates (strict)
- KRX 2017–2022 1565/1565 private weekday pairs storage integrity: historical PASS only, not rehashed today. Official exchange calendar, trading status, corporate actions, actual execution feasibility, tax/cost: NOT VERIFIED; 90 uncertain days, 12003 zero-activity cases remain vetoed.
- OpenDART first original filing and correction lineage: 15 SGML candidate rows / adjacency evidence is historical shape-only; precise 2021/2022 original consolidated 3-month operating profit, correction chain, public available-at and PIT: NOT VERIFIED / fail-closed.
- historical company/security mapping, PIT labels and purge/CPCV, independent holdout: NOT VERIFIED. H5 failed/consumed holdout and dynamic outputs cannot be retuned or recycled.
- M20 horizon20/purge20, WF504/126/126, Frozen Champion/Top3/NO_TRADE and fees/taxes/risk/advancement policy: unchanged; M20 economic run NO-GO. Post-cost/tax NetEV, PF, CAGR, MDD, ES95/99, concentration, date robustness: NOT VERIFIED (not run).
- Optimization PR #413/#418: offline CI job success PASS, immutable test digest and synthetic assertions NOT independently recomputed, official backtest acceleration NOT VERIFIED. Cache must fail closed unless independent approved source/data/code/Frozen/runtime/approval SHA256 match. Parallelism restricted to read-only independent post-processing, never dependent training/capital transitions.
- ORDERING=false / KIWOOM_ORDERING_ENABLED=false remain required policy; no authority to assert deployed environment-variable values from this read-only status query. No live orders, money movement, credentials/permissions changes, Champion promotion, merge, deployment.

## Next safe step
Independent source owner must establish original-filing exact PIT/lineage and KRX official trading-state evidence with immutable SHA before M20 admission. Optimization owner may independently validate fixed offline test identity and one-runner wall time, without market performance runs. Preserve existing isolated PR owners' code and workflow. No policy changes, no deployment.