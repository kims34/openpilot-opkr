# IndexAlert independent profit/runtime audit — 2026-11-07 08:20 KST

Scope: read-only GitHub and Railway evidence, no economic backtest or deployment. Historical evidence is not treated as current PASS.

## Source identity
- research branch index-alert-research-v1: compare(ref,ref) base SHA `df474df348f22aa38b1dedaa59fcff66e548b406`, identical.
- development branch index-alert-position-regen-fix-v1: compare(ref,ref) base SHA `1e6367d2863a86c3470da13d81a955d277eba485`, identical.
- PR #414 HEAD `18c5418d9684d1717df58261ea27f28e514385b2`; gate document blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be` read directly.
- PR #412/#413/#414/#418/#420/#422/#423: OPEN, Draft, unmerged as read from PR endpoints.
- GitHub Actions 38498552499: 6/6 jobs success; 38419649711: 1/1 success; 38419439742: 2/2 success. These are offline software evidence, NOT economic approval.
- Chronology Anchor 41515392296: auto-anchor FAILURE; validation SKIPPED. Prior HTTP 404 at /anchor/latest remains an unverified root-cause blocker.

## Railway production (read-only)
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; environment staged=null.
- KRX historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, created 2026-10-12; PIT rebuild `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, created 2026-10-10; runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, created 2026-10-05.
- KRX and PIT service log queries from 2026-11-06 22:00Z yielded zero entries: **no evidence of correction**. Historical 27 invalid OHLC and 90 uncertain sessions remain unresolved, not claimed freshly reproduced.
- Runtime deploy logs through 2026-11-06 23:19Z show Investing.com USD/KRW HTTP failure with Yahoo fallback; this is NOT PIT evidence.

## Independent admission decisions
- Original filing semantics, exact public available-at/PIT, 2021/2022 first-three-month consolidated operating-profit correction lineage: NOT VERIFIED.
- Historical issuer/security mapping, official KRX session/trading states, corporate actions, execution feasibility and tax/cost assumptions: NOT VERIFIED.
- Historical private raw pair storage 1565/1565: previously PASS for storage integrity ONLY; official market truth NOT VERIFIED.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness, annual risk-adjusted after-tax returns: NOT VERIFIED; M20 NO-GO.
- Offline synthetic parity/CI: PASS for listed job conclusions only. Existing 2.9656s serial vs 2.6209s concurrent phase (1.1315x) is prior evidence; whole-CI and real backtest acceleration NOT VERIFIED.
- H5 consumed holdout and dynamic findings cannot be reused as independent evidence. Frozen H5, M20 horizon20/purge20, WF504/126/126 and all gate/risk/cost criteria unchanged.
- ORDERING=false; no order, money movement, champion promotion, CI workflow change, deployment, merge, official return replay or model search.

## Next independent checks
1. Read-only match Anchor Action URL/404 response to deployed route and commit contract; do not change workflow.
2. Compare 27 bad OHLC and 90 uncertain sessions against independently timestamped official originals and their SHA before changing admission.
3. Verify first-filing SGML/XBRL period and correction lineage, public timestamp, historical issuer mapping, then review PIT admission independently.
4. For isolated runtime work, restrict to synthetic offline parity, cache provenance SHA-256 equality, fail-closed invalidation and read-only post-processing parallelism. Do not parallelize dependent refits/capital transitions.

No operational or source code changes made.
