# IndexAlert independent profitability/runtime audit — 2026-11-03 13:23 KST

Read-only observations. No PIT source approval, no trading or deployment authority.

## Exact refs
- research index-alert-research-v1 HEAD bba25477b41fcd0a8beca78168abb0009fb5b82c (observed before this document)
- development index-alert-position-regen-fix-v1 HEAD 1e6367d2863a86c3470da13d81a955d277eba485
- PR #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581, #422 c14857620973531013799e44625d43080904fd5f, #423 0e38004363cac9fc4475556b3a1c445de9af407f. All observed open/draft.
- GitHub Actions #38419111311 success HEAD b22e4f39517c2bc38e173e63e8fd52f29a535dad; #38419649711 success HEAD 8f363b8683d34a48754916b34810a5a8bb958896; chronology #41515392296 failure HEAD f17283d9a5f0427c3d5b8a865d39455f92ee2f1d. Historical job-level / fixture SHA claims not freshly independently reproduced.
- Historical 34-case fixed SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34: historical evidence only, not independently rehashed this run.

## Railway read-only
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a. indexalert-pit-rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS; returned runtime records through 2026-11-02 13:46 UTC show 27 nonpositive OHLC / 803 common stock, zero-volume-value 27, session_manifest_sha256 null, COMMON_OHLC_NONPOSITIVE, FAIL_CLOSED, ORDERING=DISABLED, no live order authorization. Runtime deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS; recent HTTP sample has no anchor/latest rows, therefore recovery NOT VERIFIED. Kiwoom REAL readonly deployment a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS but replica 0 running / 1 crashed, contradictory health surface. Staged patch e113dacb-6705-4416-9997-dc694539d382 still present; do not apply.

## Gate decisions
- Original-filing semantic mapping, 2021/2022 first-three-month consolidated operating income, correction lineage, exact public available-at/PIT: NOT VERIFIED.
- Historical company/security mapping, official KRX trading calendar/status/corporate actions, executable fills, tax/cost: NOT VERIFIED. Historical private 1565/1565 weekday pair SHA-storage PASS is limited to storage integrity, not official trading eligibility.
- M20 horizon20/purge20 WF504/126/126 independent holdout and NetEV/PF/CAGR/MDD/ES95/99/concentration/time robustness: NOT EVALUABLE; NO-GO.
- PR #413 synthetic equivalence: historical limited PASS; full CI and actual backtest speed NOT VERIFIED. PR #418 archived manifest mismatch: FAIL-CLOSED; isolated synthetic checks do not override.
- No H5 holdout reuse, no Dynamic post-hoc tuning, no M20 economic run, no model search. Cache only with complete independent source/data/code/Frozen/runtime/approval SHA-256 match; parallelize read-only postprocessing only. ORDERING=false.
- Next: independently recover original filing and availability provenance, KRX status/calendar and corporate action source, anchor response/body/private storage integrity, archived manifest hash chain, then re-audit without changing frozen policy. No merge, deploy, workflow edit, permission change, order, or Champion promotion.
