# IndexAlert isolated read-only safety audit — 2026-10-18 17:23 KST

**Scope:** Offline-only cache/runner safety; independent cross-track gate review. This document is NOT PIT admission, an economic evaluation, merge approval, or trading authority. No delegated code, Frozen/H5/M20/Holdout/Champion/Top3 policy, or Railway deployment modified. ORDERING=false.

## Pinned GitHub refs (read-only checked this run)
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Draft #414 integration HEAD `4ec707e4cca788c1b139a58debfb28050ee0df0b`, document blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- Draft #413 optimization HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`, manifest blob `e0055c66c59398fd4a1158077446d886b54c4e37`.
- Draft #418 independent one-runner HEAD `c9b125ff5d3d080848dd9ab1f23a8755af4faaa9`, candidate gate blob `9bfc94edb43c10c7c06bb37b2bbafe6a05a0865c`.
- Draft #412 OpenDART HEAD `dcb4a6d30c47fd84a4e7667453af5bd5a6bcf1d0`.
- KRX delegated Draft #420 HEAD `588bc296eafa58525954f691a763ff6eb413f053`, dependent #422 HEAD `c14857620973531013799e44625d43080904fd5f`.

## Actual CI and source gates
- #413 offline Actions 38508247773: 6/6 jobs SUCCESS; earlier immutable 34-case outcome SHA256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`. This is offline parity only.
- #418 original merged-context Actions 38822156136: 1/1 job FAILURE; candidate-only 38822156164: 1/1 SUCCESS, **explicit candidate_approved_for_merge=false**. Source archive parity and reviewed changed-candidate parity are separate claims; never substitute one for the other. Candidate code explicitly returns `all_transitive_imports_pinned=false`.
- OpenDART 39001867286: two jobs SUCCESS; official artifact hashes only, not original 2022/2021 standalone 3-month CFS operating-income semantics or earliest public PIT.
- KRX 39001950024: one offline synthetic job SUCCESS; does not establish official historical exchange calendar or tradability.
- #418 one-runner historical Actions 38419649711: 1/1 SUCCESS, 34-case immutable digest preserved; subprocess serial 2.9656s versus parallel 2.6209s (1.1315x test-phase only). Full CI and genuine market-backtest speedup NOT VERIFIED.

## Railway read-only snapshot
Project IndexAlert, production, no staged/pending changes. Dedicated KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, commit `1e6367d2863a86c3470da13d81a955d277eba485`, verified 1,565/1,565 stored weekday raw daily/master pairs, 0 invalid stored pairs; 90 unresolved calendar/source-gap sessions, 12,003 sampled zero-activity OHLC rows and 1 other invalid OHLC row. Explicit `historical_publication_pit_verified=false`, `official_trading_status_verified=false`, `corporate_action_paths_verified=false`, `m20_performance_testing_authorized=false`, `ordering=DISABLED`. Other operational caveats: `db-query-readonly` OFFLINE with 1 critical notification; `indexalert-kiwoom-real-readonly` state ONLINE but replica summary 0 running/1 crashed. No claim that these conditions are new or that they prove any data loss; no operational action taken.

## Independent local synthetic-only controls (NOT repo CI)
- Strict cache design test: 1 positive receipt accepted; byte mutation of each of source, code, policy, runtime, approval evidence rejected (5/5); literal type mismatch `False` vs `0` rejected by strict comparator (3/3), although Python ordinary dict equality accepts those aliases (3/3). Unknown elevated metadata keys rejected by strict comparator (3/3). This is a proposed safety acceptance pattern, not evidence that current repository comparators enforce it.
- Four deterministic read-only hash tasks: serial and concurrent outputs exactly equal (4/4); no dependent training, capital transition, real data, profitability or orders.
- Real `cache_matches()` and `handoff_matches()` in pinned sources still use `stored == expected`; exact-type comparison and explicit metadata allowlisting require separate source-owner review. The #413 cache only hashes explicitly supplied source/code paths and independently authenticated receipts remain caller responsibility.

## Independent gate verdict
- Raw storage SHA integrity: PASS only for stated six-year scope.
- OpenDART first-original standalone Q3 CFS operating-income 2022/2021, earliest available-at/PIT, correction lineage and issuer/security mapping: NOT VERIFIED.
- KRX official historical sessions, trading state, corporate actions, fills and tradability: NOT VERIFIED.
- Realistic commissions, tax, spread/slippage, NetEV, PF, CAGR, MDD, ES95/99, concentration and time robustness: NOT VERIFIED (no M20 run).
- PR #413/#418 merge: BLOCKED; original merge-context CI failure and transitive source/runtime reproducibility proof incomplete.
- Next source-owner-only actions: resolve original merge-context SHA discrepancy without re-pinning frozen archive; explicitly pin transitive imports and dependency versions; add strict typed/allowlisted cache metadata tests; independently obtain authoritative DART/KRX PIT/tradability proofs before any financial evaluation. No automatic merge, deploy, Champion promotion, live orders, funding or permission changes.
