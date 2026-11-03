# IndexAlert independent profitability gate evidence — 2026-10-20 16:51 KST

Scope: read-only independent review. This document grants no PIT, performance, merge, deployment, ordering, or trading authority. It does not modify any dedicated team's code or the integration gate.

## Exact refs (read-only GitHub connector)
- Research branch index-alert-research-v1 at PR #414 base: 3b8b7830612a6284d7c7a60628cb527cb741627a.
- Development branch index-alert-position-regen-fix-v1 at KRX PR #420 base: 1e6367d2863a86c3470da13d81a955d277eba485.
- Integration Draft PR #414 HEAD: 10c9cd2643e61654fa0365dd4f7e348e7af0bdd2; gate document Git blob: 984c933651f39f1ee9e26a1d7ac3893aaa5335be.
- OpenDART Draft PR #412 HEAD: 215cefe4e595084323f52cc152f16d343c705b53.
- KRX Draft PR #420 HEAD: 4de15557224aaa2a8feec17d0b94fd649967401d.
- All three PRs remain draft and unmerged in this inspection. Mergeability is not PIT or financial approval.

## GitHub Actions latest on exact PR HEADs
- DART 39347989440: success, one job toc-js-identity-no-network; offline TOC synthetic only.
- DART 39347989451: success, one job original-receipt-synthetic-no-network; log explicitly reports 12/12 synthetic tests PASS, flags m20_feature_pit_admitted=False, m20_performance_run_authorized=False, ordering=DISABLED.
- KRX 39347477816: success, one job synthetic-no-provider-no-order; log includes 2021 private calendar 22/22 and parity 8/8 synthetic tests, no private source PIT admission.
- KRX 39347477798: success, one job no-source-no-orders; log 8/8 synthetic tests, exact calendar synthetic and strict private source no-PIT flag.
- KRX 39347477885: success, account settlement binding job; this is not evidence of PIT market tradability or model performance.
- Integration #414 exact HEAD: no PR-triggered Actions returned by connector; no independent PASS inference.

## Railway IndexAlert production read-only
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7, 10 services checked, 3 with issues, pendingWork empty.
- db-query-readonly offline / critical 1, no active deployment; service deploy log query returned empty; diagnosis NOT VERIFIED.
- indexalert-push offline / warning 1; indexalert-backend offline / warnings 4.
- indexalert-krx-historical-worker online, settled deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS created 2026-10-12T13:07:31Z, deployed commit 1e6367d2863a86c3470da13d81a955d277eba485; current read-only deploy log query returned empty, so private source raw SHA recheck NOT VERIFIED in this run.
- indexalert-kiwoom-real-readonly state online but replicaStatus running=0 crashed=1 total=1; no operational intervention performed. This discrepancy requires separate operational diagnosis before claiming runtime health.
- No staged/applying deployment changes.

## Evidence verdicts
- Historical KRX 2017-2022 private raw storage 1565/1565 pairs: PASS only as archived prior deployment evidence, NOT independently reverified from current raw logs.
- Official historical exchange session date/vintage, security status, corporate actions, tradability and fill: NOT VERIFIED; zero-activity, 27 questionable symbols and 90 session classifications remain fail-closed.
- 2022/2021 original first-filed 3-month consolidated operating profit, exact public available-at, amendment lineage, historical issuer-security mapping: NOT VERIFIED.
- PIT-compliant source admission: NOT VERIFIED / fail-closed.
- Real after-tax costs, NetEV, PF, CAGR, MDD, ES95/ES99, return concentration and time robustness: NOT VERIFIED; no performance calculation executed.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, holdout, champion, Top3/NO_TRADE unchanged.
- ORDERING=false; M20 performance run NO-GO; no trading, money movement, credentials, deployment, merge, or champion promotion.

Next permitted step: independent read-only provenance/available-at and official exchange state verification from real receipts with exact SHA and contemporaneous timestamps. Do not run M20 economics until official PIT and tradability gates independently PASS.
