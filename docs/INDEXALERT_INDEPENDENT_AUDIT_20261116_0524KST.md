# IndexAlert independent audit — 2026-11-16 05:24 KST

## Scope and provenance
Read-only connector checks of GitHub Actions jobs 38381997417, 38382214223, 38419111311, 38419439742, 38419649711, 38486028854 and Railway IndexAlert production. No official market-return run, orders, deployment, merge, workflow edit, or model search. This document is an independent audit note, not PIT approval.

## CI status
- PASS (offline software only): 38381997417 6/6; 38382214223 6/6; 38419111311 6/6; 38419439742 2/2; 38419649711 1/1.
- FAIL: 38486028854 job 115599778959; original regression-source blob identity gate fails before archived-case or four-suite regression execution. Prior recorded expected SHA-1 108f66714602a1bd3ae42c34dcca7c16e38f460b vs observed e428789e2e97ca7be3a4482e0df23b483a1ad69d. No waiver.
- NOT VERIFIED: independently recomputed immutable 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 in this run; whole-CI or real backtest speed-up. Previous isolated 2.9656s serial vs 2.6209s concurrent is not full-run acceleration.

## Railway production evidence
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS; no deploy logs returned since 2026-11-15T18:20Z.
- KRX historical worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS; no deploy logs returned in same interval. Deployed commit 1e6367d2863a86c3470da13d81a955d277eba485 from index-alert-position-regen-fix-v1 is historical deployment SHA, NOT verified current branch HEAD.
- Runtime deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS. At 2026-11-15T20:22Z logs show Investing USD/KRW HTTP failure and Yahoo fallback, not a PIT certification.
- Previous observed prospective KRX OHLC invalid 27/803 and FAIL_CLOSED remain unresolved; zero logs is not recovery evidence. Staged patch resolution NOT VERIFIED.

## Independent profitability gate
NOT VERIFIED: original-filing public available-at/PIT, 2021/2022 first-three-month consolidated operating-profit period/correction lineage, historical issuer/security mapping, official KRX market calendar/status/corporate actions/executability, fees/taxes, net EV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness, independent holdout. The 15 SGML candidate rows from 38419439742 do not authorize original semantic/temporal interpretation. Private 1565/1565 weekday-pair hash integrity does not authorize official session/tradability claims.

## Frozen policy / next safe work
M20 NO-GO, ORDERING=false, H5 holdout consumed; horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/Champion/Top3/NO_TRADE frozen. Keep source/model/temporal approvals false. Only synthetic offline software and fail-closed tests until independent original-filing PIT and KRX official state evidence pass. Cache only when all approved source/data/code/policy/runtime/evidence SHA-256 match; parallelize read-only postprocessing only. Next: obtain independently hash-bound KRX 27 invalid rows and official session status, DART filing timestamps/lineage, and diagnose #418 SHA mismatch without weakening gate. Research HEAD, development current HEAD, PR #412/#413/#414/#418/#420/#422/#423 exact current HEAD/draft status: NOT VERIFIED in this run (GitHub issue search returned no results; direct file reads 404). No authority changes.
