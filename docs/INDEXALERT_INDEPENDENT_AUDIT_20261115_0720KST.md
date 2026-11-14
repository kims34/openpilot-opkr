# IndexAlert independent read-only audit — 2026-11-15 07:20 KST

Scope: isolated profitability gate and offline-only runtime optimization review. No production write, no market return experiment, no strategy or Frozen policy changes. All findings below derive from fresh connector reads this run, except explicitly labeled historical evidence.

## Current refs
- Research `index-alert-research-v1` HEAD `df474df348f22aa38b1dedaa59fcff66e548b406` (self-compare identical).
- Development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485` (self-compare identical).
- Draft, open, unmerged: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` fetched from PR branch, retains M20 NO-GO, H5 archived NO-GO and KRX storage-vs-tradability distinction.

## Fresh Actions jobs
- #413 Actions 38381997417, 38382214223, 38419111311: each 6/6 jobs SUCCESS. #418 Action 38419649711: 1/1 SUCCESS; later integrated Action 38486028854: 1/1 FAILURE. OpenDART 38419439742: 2/2 SUCCESS.
- Historical archived 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`: reported historical value only; **independent recomputation this run NOT VERIFIED**. Synthetic tests are not PIT/alpha evidence. Earlier 2.9656s serial versus 2.6209s concurrent (1.1315x) is regression-phase only; full CI/real backtest speedup NOT VERIFIED.
- #418 newer integrated CI is FAIL: do not treat earlier SUCCESS as current green gate. Root cause detailed provenance requires immutable manifest bytes and job log cross-check before corrective isolated work; no workflow writes.

## Railway production
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. PIT rebuild 1/1 running, Runtime 1/1 running; KRX historical worker and Kiwoom real-readonly-run 0/1 despite deployment SUCCESS. backend/push offline; db-query-readonly offline with one critical warning.
- Staged environment patch `e113dacb-6705-4416-9997-dc694539d382` since 2026-10-29 06:20:53 UTC; changes [] in environment status, unresolved pending work, no acceptance/deploy.
- Fresh log interval 2026-11-14 21:15–22:25 UTC: PIT rebuild 0 entries, KRX worker 0 entries, Runtime 61 entries (requested limit 60; provider returned 61); 22:20:42 UTC USDKRW Yahoo quote, KOSPI Naver quote, closed-market ECOS previous-close alignment. These are operational quotes, **not** original filing PIT or KRX tradeability validation.

## Gate verdicts (no promotion)
- KRX 2017–2022 private original-pair storage integrity: historical PASS (1565/1565 weekday pairs), independent new rehash NOT VERIFIED. Official sessions, 90 uncertain days, 12003 zero-activity records, corporate actions, listing/suspension, 27 invalid OHLC and executable cost/tax: NOT VERIFIED / fail-closed.
- OpenDART original SGML candidate-row shape: historical 15 rows, Actions SUCCESS. Exact 2021/2022 original first-three-month consolidated operating profit, period/correction lineage, public available-at and historical corp/security mapping: NOT VERIFIED.
- H5 archived robustness and used holdout: NO-GO; no retroactive adjustment or independent reuse.
- M20 source PIT, labels, Purged/CPCV, independent Holdout, annual after-cost-and-tax risk-adjusted NetEV/PF/CAGR/MDD/ES95/99, concentration, date robustness, execution and tiny-capital feasibility: NOT VERIFIED; performance RUN NOT AUTHORIZED.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, Top3/NO_TRADE, all cost/risk/Champion gates unchanged; ORDERING=false. No orders, funding, permissions, deployment, merges, or Champion promotion.

## Next safe actions
1. Source owners independently attest original-filing semantics, exact PIT public available-at and corp/security lineage, and official KRX sessions/tradeability with immutable source hashes.
2. Optimization owner isolate #418 immutable manifest identity failure from job 115599778959 and original archived SHA; synthetic-only parity/fail-closed checks, no workflow bypass.
3. Railway owner independently triage offline/critical status and long-standing staged patch; do not deploy or apply patch here.
4. Only after independent gate PASS, separately seek explicit approval for any new economic run; do not use consumed H5 Holdout.
