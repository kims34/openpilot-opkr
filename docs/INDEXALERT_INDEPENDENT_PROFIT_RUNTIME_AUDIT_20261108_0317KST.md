# IndexAlert independent profit / isolated runtime audit — 2026-11-08 03:17 KST

## Scope and immutable safety
Read-only GitHub issue/PR metadata, Actions job conclusions, Railway project/services/deployments/logs; no market-source run, broker action, PIT admission, Holdout, merge or deployment. ORDERING=false; M20 NO-GO. Frozen H5, horizon20/purge20, WF504/126/126, costs/taxes and Champion/Top3/NO_TRADE unchanged.

## Fresh GitHub evidence
Repository: kims34/openpilot-opkr. PR #412, #413, #414, #418, KRX #420/#422/#423 all returned state=open via fetch_issue. Note: fetch_issue does not expose reliable PR draft/head_sha, so their *current exact PR HEAD and draft status* are NOT VERIFIED in this pass. The 2026-11-08 02:17 KST prior report listed research HEAD df474df348f22aa38b1dedaa59fcff66e548b406 and development HEAD 1e6367d2863a86c3470da13d81a955d277eba485; these are **prior evidence**, not fresh independently resolved branch HEAD. Railway historical KRX deployment metadata pins dev commit 1e6367d2863a86c3470da13d81a955d277eba485 (deployed 2026-10-12), not proof of current branch HEAD.

GitHub Actions job API checked:
- 38381997417: 6/6 success
- 38382214223: 6/6 success
- 38419111311: 6/6 success
- 38498552499: 6/6 success; PR #413 text reports negative regression-only parallel speed ratio 0.664x (1.7114 s serial vs 2.5776 s parallel)
- 38419649711: 1/1 success
- 38419439742: 2/2 success
- 41515392296: auto-anchor failure, validation skipped

Archived parity fixture SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 remains prior-reported; fresh job conclusions do not independently establish artifact-byte equality. PR #413 source artifact SHA256 7162d9b0b72dcaceb21f925ba02ffa29f064c2e64763d65db7ebaf874c431f64 is PR-text reported, not freshly downloaded. PR #414 integration gate blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be is prior evidence; fetch_file against research branch returned NOT_FOUND, not a new SHA validation.

PR #412 updated 2026-10-26: original 2021 SGML evidence reported 1 SGML, 1,728 tables, 13 profit-label candidates, **zero complete first-filed 2021 Q3 period/CFS profit fact**; reported artifact 12625042488 SHA256 3fe75e2af23f508d3c518a14e98732a399eb0daeca46cccd7b3191b1e2e4777b. This is a material explicit continued source blocker. 2022 first-original and 2021 first-Q3 comparators remain unadmitted.

## Railway evidence
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, production 83d5840b-270e-4d3f-a941-a37fd4a55ff7. describe_service for PIT rebuild, KRX historical worker, Kiwoom REAL read-only and runtime all returned state=live, staged=null, stagedChanges=[] and latest deployment SUCCESS. These fields **do not prove healthy running replicas**.
- PIT rebuild latest deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 (2026-10-10)
- KRX historical latest 16c93d7c-7cd0-4d84-a327-298d2805376c (2026-10-12)
- REAL read-only latest a77fb922-b679-4d88-92c4-03054ec579cd (2026-10-29)
- runtime latest eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 (2026-10-05)
Recent deploy log query starting 2026-11-07T16:00Z returned no PIT, KRX or REAL entries; absence of entries cannot prove repair, outage or good health. Previous PIT FAIL_CLOSED with 27/803 nonpositive OHLC and 27 zero-activity rows (failed session 2026-09-28; manifest SHA null; authority false) remains last substantive observation, **not freshly reproduced in this time window**. Runtime logs at 2026-11-07 18:16–18:17 UTC show Investing USD/KRW HTTP errors and Yahoo fallback; runtime quote telemetry is not an approved PIT or profitability source.

## Decision matrix
- Offline software CI job conclusions: PASS within the job scope only; exact fixture SHA fresh rehash NOT VERIFIED.
- KRX 2017–2022 private 1565/1565 weekday pair storage integrity: prior PASS only; fresh original bytes NOT VERIFIED.
- Official KRX historical calendar, issuer state/actions, exact tradeability/fill: NOT VERIFIED.
- OpenDART original-filing public available-at/PIT and 2021/2022 Q3 period/restatement CFS operating profit: NOT VERIFIED / source completeness blocked.
- Entity/security historical mapping, trading costs/taxes: NOT VERIFIED.
- NetEV, PF, CAGR, MDD, ES95/99, concentration and time robustness: NOT VERIFIED; M20 RUN prohibited.
- End-to-end CI / actual backtest speedup: NOT VERIFIED. Observed isolated parallel regression slowdown is negative evidence, not a production speedup.
- Chronology anchor: FAIL (job), validation SKIPPED.
- PIT source admission: FAIL_CLOSED as last observed, not freshly overturned.
- Holdout reuse, Champion promotion, real orders, capital movements: prohibited.

## Next safe steps
Independently resolve exact branch and PR HEAD, source blob and artifact SHA; obtain original filing available-at and period/restatement lineage from separately authorized source work; audit private exact KRX calendar day sets on approved existing worker without data exfiltration; inspect current PIT bad-row evidence and actual replica health read-only; compare isolated synthetic CI total wall time under fixed immutable evidence SHA. Do not parallelize dependent retraining or capital transitions, bypass security workflow write restrictions, alter shared Work-owned code, or run economic tests before independent source admission.
