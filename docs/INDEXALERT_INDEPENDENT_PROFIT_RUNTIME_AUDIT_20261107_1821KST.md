# IndexAlert independent profitability/runtime audit — 2026-11-07 18:21 KST

Scope: independent read-only verification, no production or economic experiments. Frozen H5 / M20 horizon20 purge20 / WF504-126-126 / ORDERING=false unchanged.

## GitHub exact evidence
- PR #412 head bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f. All OPEN Draft unmerged.
- PR base snapshots: research 3b8b7830612a6284d7c7a60628cb527cb741627a; development 1e6367d2863a86c3470da13d81a955d277eba485. These are PR base SHAs, NOT independently established current branch HEADs.
- Integration document read from PR #414 branch; first lines explicitly PIT FAIL-CLOSED and M20 no-go. Its current blob SHA was not obtained in this run.
- Action 38419439742 2/2 SUCCESS (candidate rows only), 38419649711 1/1 SUCCESS (synthetic offline runner), 38498552499 6/6 SUCCESS (synthetic parity); chronology 41515392296 auto-anchor FAILURE, validation SKIPPED. No approval of original public-available-at chronology or whole CI acceleration.

## Railway production
- Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- Deployment SUCCESS is not replica health. indexalert-kiwoom-real-readonly a77fb922-b679-4d88-92c4-03054ec579cd: running 0, crashed 1, total 1, despite state online. PIT rebuild and Runtime running 1/1; KRX historical worker running 0, crashed 0, total 1. db-query-readonly criticalCount=1.
- describe_environment staged=null, while get_status/environment_status pendingWork contains empty staged patch e113dacb-6705-4416-9997-dc694539d382; inconsistency unresolved.
- 2026-11-07 06:00Z onward read-only deploy log queries: real-readonly, KRX worker and PIT rebuild yielded zero rows. Runtime logs existed. No new official KRX/PIT proof inferred.

## Gates
- KRX 1565/1565 weekday raw pair storage integrity: PASS on historical evidence only; 90 uncertain days, 27 bad OHLC and 12003 zero-activity records not cleared. Official calendar, halt/delist/corporate actions, historical mapping and execution feasibility: NOT VERIFIED.
- OpenDART SGML 15 candidate row/numeric-adjacency signatures: prior offline PASS only; original filing semantic period, first public available-at, 2021/2022 3-month consolidated operating profit amendment lineage: NOT VERIFIED.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, time stability after costs and taxes: NOT VERIFIED; M20 economic RUN: NOT AUTHORIZED. H5 consumed holdout not reusable.
- Cache only on exact independent source/data/code/Frozen/runtime/evidence SHA-256 match; fail-closed. Only independent read-only postprocessing may parallelize. Dependent retraining and capital transition serial. No official backtest, tuning, merging, deployment, orders or promotion.

## Next read-only work
1. Confirm current research/development branch HEAD directly, separate from PR base snapshots, and fetch integration doc blob SHA.
2. Inspect chronology anchor failed job log and independently validate official filing timestamp semantics, amendment and period lineage.
3. Inspect crashed replica's deployment logs and staged-patch inconsistency without restart/config change.
4. Reconcile KRX official session and execution states against private raw pairs, preserve exclusion.
