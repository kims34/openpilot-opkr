# IndexAlert independent evidence audit — 2026-11-10 10:19 KST

Read-only snapshot. No approval to run M20, trade, merge, deploy, or modify Frozen policy.

## GitHub
- Research HEAD df474df348f22aa38b1dedaa59fcff66e548b406; development HEAD 1e6367d2863a86c3470da13d81a955d277eba485. Compare development relative to research: diverged, ahead 1148, behind 281.
- PRs 412/413/414/418/420/422/423: all open draft at read. Their head SHAs were not captured in this audit; do not treat as verified.
- PR #414 gate document on branch indexalert-profitability-integration-evidence-20261013: blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be. File absent at research branch path (404), not proof of deletion on PR branch.
- Actions 38381997417, 38382214223, 38419111311: each 6/6 jobs success. 38419649711: 1/1 success. 38419439742: 2/2 success. Historical test SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and synthetic 28 cases remain historical reported evidence, not newly rehashed today. Serial 2.9656 s versus concurrent 2.6209 s is regression-phase 1.1315x only, not full-backtest acceleration.

## Railway production
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, replica running 1/1; Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, replica running 1/1.
- KRX worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, 0 running / 0 crashed / total 1 (idle or status ambiguity; not proof of historical market-state coverage).
- Kiwoom real readonly deployment a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS but running 0, crashed 1, total 1: runtime health FAIL despite UI online.
- Backend, Push, db-query-readonly offline. Empty staged environment patch e113dacb-6705-4416-9997-dc694539d382 present; do not apply.
- PIT, KRX, Kiwoom readonly log queries 2026-11-10 00:00–01:20 UTC each returned 0 entries. Therefore earlier 27/803 OHLC anomalies are NOT VERIFIED resolved; log absence is not health PASS.

## Gate decisions
- KRX 2017–2022 weekday private pair storage 1565/1565: historical storage integrity PASS only; official trading calendar, status, corporate actions, execution feasibility NOT VERIFIED.
- OpenDART original and amended SGML 15 candidate row adjacency: historical software evidence PASS, precise first-public available-at, consolidated three-month 2021/2022 operating-profit period and correction lineage NOT VERIFIED.
- Historical issuer/security mapping, transaction costs and taxes, PIT labels, independent holdout, NetEV/PF/CAGR/MDD/ES95/99, concentration and time robustness: NOT VERIFIED.
- M20 PIT/performance execution: NOT AUTHORIZED (NO-GO). H5 consumed/failed holdout cannot be reused. Frozen H5/M20 horizon20 purge20 WF504/126/126, NO_TRADE and ORDERING=false unchanged.
- Offline optimization CI PASS for recorded jobs; independent end-to-end speed and official-market economic performance NOT VERIFIED.

## Next permitted steps
Obtain official original-filing timestamps, consolidated three-month periods and correction chain from source owners; official KRX trade-state/corporate-action/market calendar mapping and execution cost provenance; independently bind immutable source/code/policy/runtime SHA-256 before considering PIT gate. Continue only synthetic offline safety tests and read-only evidence review. No workflow edits, no merge, no deployment, no real orders.
