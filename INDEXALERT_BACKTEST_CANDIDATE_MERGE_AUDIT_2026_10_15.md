# IndexAlert: October 15, 2026 KST — Candidate Offline Parity / Source Audit

**Verdict:** **CODE-LINEAGE & OFFLINE REGRESSION PASS** for *exactly* reviewed upstream Draft PR #413 revision `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`, dependent Draft PR #418 code `f50b6750192da675820483cf3ebad9beb11afd61`. **NO** official historical-source admission, return evidence, real trading, Holdout authorization, automatic merger, or actual H5/M20 speedup.

## Why this review was necessary
Previous independently green candidate proof [#38503017187](https://github.com/kims34/openpilot-opkr/actions/runs/38503017187) belonged only to upstream `396d195d6ad31fcdf8dcab02e87d11eee9db5017`. Upstream #413 subsequently added five commits through `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`. GitHub `compare` independently showed the only changed code/test files across these five commits to be `research_v1_runtime_manifest.py` and `test_research_v1_runtime_ci_integrity.py`, plus documentation; no Frozen H5 strategy, data, model, broker or capital modifications.

The reviewed cache receipt guard now requires local order/Holdout permissions **literal false**, and rejects active, ambiguous or non-boolean input values for six optional cross-service authority aliases (independent Holdout, real orders, funds movement, permission changes, Champion changes, M20 performance run). These are **synthetic/cache metadata protection**, not proofs of source issuer, PIT, fill economics or live system safety.

## Separate immutable original versus new candidate
The original archived offline 34-case parity SHA256 remains exactly `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, from original successful archived [GitHub CI #38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), checkout `05d73661bcc879fe0dd66ffcea5fe1f5ee6fbd56`.

The **distinct candidate-only** source audit checks **exactly 21 Git blobs**: eight fixed historical test source files, eight original unchanged directly tested implementation blobs, original pinned requirements text, and four separately reviewed updated candidate code/control files:

| Candidate file | Reviewed exact Git object SHA1 |
|---|---|
| `research_v1_runtime_manifest.py` | `e0055c66c59398fd4a1158077446d886b54c4e37` |
| `research_v1_runtime_one_runner.py` | `0c792b66daa46bdc7725fdcfde17ced975fb2c55` |
| `test_research_v1_runtime_ci_integrity.py` | `bb2e5d8f81d9052a16005d1b5642598268dd17d8` |
| `research_v1_runtime_ci.py` | `7306e4f57e0056960452f1991b5c95ba7413f11e` |

The fourth blob `research_v1_runtime_ci.py` is important: that code evaluates case identities, failures and fixed 34-case digests. A new synthetic control rejects modification to that evaluator while keeping testcase names intact. The candidate-only audit checks the **actual first parent** of the GitHub synthetic PR merge, not stale GitHub event `base.sha` or an unchecked PR head. This exact scope is **not** equivalent to replaying the original byte-for-byte implementation.

## Verified live GitHub Actions proof (same exact dependent code HEAD)
- **[Candidate merge audit #38597706612](https://github.com/kims34/openpilot-opkr/actions/runs/38597706612)**: SUCCESS. `CANDIDATE_MERGED_SOURCE_PROOF`: 21/21 Git source identities, pinned source-lineage upstream SHA, `candidate_source_lineage_consistent=true`, `candidate_approved_for_merge=false`, `original_archived_manifest_replayed_without_change=false`.
- Source / merge attack scenarios: **8/8 synthetic tests PASS**. Upstream cache authorization/TOCTOU hardening: **23/23 synthetic tests PASS**. Existing 4-suite parallel offline regressions **34/34**, exact unchanged original SHA256 verified. Python 3.12 and original 22 installed package-version checks PASS. Parallel-only 34-case phase `3.1443` seconds on that run; **not** the market backtest runtime.
- **[Original independent one-runner parity #38597706496](https://github.com/kims34/openpilot-opkr/actions/runs/38597706496)**: SUCCESS.
- Upstream standalone six-job CI **[#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773)** at exact reviewed upstream `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`: **all six jobs SUCCESS**.
- **Original immutable archive-only PR merge-context replay remains intentionally FAIL_CLOSED** on its revised `research_v1_runtime_manifest.py` (because original archive and candidate legitimately differ). Do **not** silently update its original Git blob, skip workflow or report a 100%-green/merge-ready PR.

## Remaining NO-GO gates
This source audit is not signed wheel/OS image, entire transitive import closure or historical publisher authentication. There is still no first-vintage official OpenDART 2022/2021 Jul–Sep 3-month consolidated operating profit/CFS PIT binding, no fully admitted historic KRX tradability/issuer mapped panel, no official eligible frozen M20 post-cost performance run or safe Tiny Live enablement. The four-suite speed numbers vary by runner: no reliable entire CI or actual historical backtest acceleration claim.

**Frozen H5/M20/purged WF/labels/holdout/Champion preserved**, both PRs Draft/unmerged, `ORDERING=false`, no assets, secrets, keys, Railway config, broker orders, money movement or permission changes.
