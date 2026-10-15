# IndexAlert 2026-10-14 isolated candidate-merge offline validation — non-admitting evidence

**Outcome:** Candidate-only offline merge-context proof **PASS**, old original-source replay test **FAIL_CLOSED by design**, independent serial-vs-parallel result **PASS**. This is an engineering/code-lineage result, NOT strategy profitability, KRX/OpenDART PIT admission, merging authority or an H5/M20 market-data backtest.

## Fixed immutable archive (unchanged)

- Original reference Actions #38382214223, reference checkout `05d73661bcc879fe0dd66ffcea5fe1f5ee6fbd56`, fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`.
- Eight original test source Git object blobs, eight unchanged directly imported implementations, `requirements-indexalert-runtime-ci.txt`, Python 3.12 and the 22 version-pinned installed dependency packages remain separately verifiable. These do not pin the entire transitive import graph or wheel/OS bytes.
- The ninth originally imported implementation, `research_v1_runtime_manifest.py`, **intentionally differs** in the new upstream candidate. Hence archived replay verification must **continue failing** in the normal merged-tree pinned-only workflow; do not relax `research_v1_runtime_archived_source_gate.py`.

## Reviewed exact upstream candidate

- Upstream Draft PR #413 HEAD: `396d195d6ad31fcdf8dcab02e87d11eee9db5017`.
- Compared upstream to earlier reviewed `421802db4d8d89a5508f5f158671a6e4b3465568` using GitHub compare: exactly 3 additional commits, changing `research_v1_runtime_manifest.py`, `test_research_v1_runtime_ci_integrity.py` and evidence documentation.
- New upstream cache receipt guard rejects missing/ambiguous/non-boolean `holdout_access_authorized` and `live_orders_authorized`; requires **literal False** for each. Upstream original full six-job parity Actions [#38498767345](https://github.com/kims34/openpilot-opkr/actions/runs/38498767345) **SUCCESS** at this exact SHA.
- Candidate is explicitly bound to exactly 20 checked Git blobs (8 original regression tests + 8 unchanged direct implementation sources + original dependency requirement + 3 reviewed upstream code/control blobs):
  - `research_v1_runtime_manifest.py`: `47a9f6a894dcf402841b282488476da5291f4a24`
  - `research_v1_runtime_one_runner.py`: `0c792b66daa46bdc7725fdcfde17ced975fb2c55`
  - `test_research_v1_runtime_ci_integrity.py`: `b1d17690627bcdb11dff0163d2a161379a6da7a2`
- GitHub pull request event `base.sha` previously reported stale `ca6c5d915d2c0e018f4aa9f82b4488038c16f8d3` even though synthetic-merge checkout first parent was newer. The candidate-only workflow now uses `actions/checkout@v4` with `fetch-depth:2` and reads the actual merged-tree **first parent** `git rev-parse HEAD^1`; mismatches from the reviewed exact upstream SHA stop before reading any candidate test output.

## GitHub proof at exact dependent Draft PR #418 HEAD

Code/test workflow:
- `research_v1_runtime_candidate_merge_gate.py` — strict exact GH synthetic parent, reviewed Git blobs, separate source identity lineage, frozen policy and disabled access flags.
- `test_research_v1_runtime_candidate_merge_gate.py` — 7 adversarial synthetic controls, including actual tested code mutation, upstream SHA drift and wrong PR event/branch.
- `.github/workflows/indexalert-candidate-merge-audit-ci.yml` — standalone read-only, non-admitting candidate merge proof. No flags or actual deployment changed.
- Synthetic fixture was initially incorrect (it compared a synthetic test manifest against the real archived manifest SHA); corrected to use internally consistent synthetic SHA only, without altering production pinned reference.

**Verified run [#38503017187](https://github.com/kims34/openpilot-opkr/actions/runs/38503017187)** at dependent HEAD `1775e268047bbac5c44efcfdd225a6fa17ca1c09`: **SUCCESS**
- Candidate source check exactly **20/20 Git blobs** PASS, upstream parent matches reviewed SHA.
- Synthetic candidate scope tests **7/7** PASS, upstream cache/CI adversity tests **21/21** PASS.
- Python 3.12 and 22 offline dependency package version parity PASS.
- Four separate regression subprocess suites **34/34** match archive SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`.
- Offline regression four-process phase 2.2704 seconds (not real H5/M20 backtest speedup).
- Existing independent serial-vs-parallel candidate workflow [#38503017051](https://github.com/kims34/openpilot-opkr/actions/runs/38503017051) **SUCCESS**.
- Original strict archival replay workflow [#38503017202](https://github.com/kims34/openpilot-opkr/actions/runs/38503017202) **FAIL_CLOSED**, consistent with changed upstream implementation. **This does not constitute permission to merge; the original archive remains unchanged.**

## Decision / next safe execution

- `candidate_source_lineage_consistent=true`; `candidate_approved_for_merge=false`; `official_pit_admitted=false`; `profitability_evaluated=false`; `holdout_accessed=false`; `ordering=false`. No merge, deploy, real orders, funds or Champion changes.
- A later upstream HEAD or additional imported implementation change invalidates this exact candidate until independently reviewed and rerun. The current source audit covers a finite scope; no claim of entire transitive closure / signed dependency artifacts.
- **Primary research blockers remain independent**: authentic KRX historical status/tradability/corporate actions and 2022 first-vintage OpenDART Q3 original 2022/2021 July–September consolidated operating-profit cell/statement/publication-instant/PIT entity binding. M20 cost/tax-adjusted profitability test is not yet authorized. Offline 34-case success must not be reported as an investment strategy success.
