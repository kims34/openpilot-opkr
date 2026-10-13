# IndexAlert 2026-10-14 archived regression implementation drift — PR merge context NO-GO

**Scope:** exact original offline regression lineage check, not PIT data admission, H5/M20 evaluation, actual backtest acceleration or live trading. **No merge / no workflow bypass.**

## Observed condition

At 2026-10-14 KST, PR #418's isolated head is `aa7b33e297c8d9bcf41f1a03e591daa144cd0de7`. It is based on an older revision of upstream Draft PR #413; upstream #413 independently advanced to `421802db4d8d89a5508f5f158671a6e4b3465568`. The newly hardened archival proof now pins **8 fixed regression test files, 9 directly imported implementation files and 1 pinned package manifest**, all compared against original independent successful archived Actions run #38382214223, commit `05d73661bcc879fe0dd66ffcea5fe1f5ee6fbd56`.

The first CI failure in this implementation-pinning work was caused by an **incorrectly transcribed 39-character** Git blob SHA for `research_v1_ml.py`. Diagnostic CI [#38485750966](https://github.com/kims34/openpilot-opkr/actions/runs/38485750966) exposed the missing final `f`; this was corrected without weakening the gate. All 9 manifest entries were rechecked against actual GitHub file object SHA and are 40 characters.

**Independent head/push is green:** [CI #38485836408](https://github.com/kims34/openpilot-opkr/actions/runs/38485836408) succeeded at `aa7b33e297c8d9bcf41f1a03e591daa144cd0de7`: original 8 test Git blobs + 9 direct implementation Git blobs + dependency requirement blob matched; original Python 3.12 / 22-package version controls passed; 8 existing identity adversarial controls + 8 fixed-parallel controls + 10 source-provenance synthetic tests + 7 runtime-version controls passed; the unchanged archived **34/34** exact case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` passed. Four-suite offline test wall 1.8933 s. This is **not** an H5/M20 investment-performance evaluation.

**PR merge-context CI is appropriately RED:** [CI #38485842001](https://github.com/kims34/openpilot-opkr/actions/runs/38485842001) failed closed before regression execution. Root cause: upstream Draft #413 intentionally modified `research_v1_runtime_manifest.py` for file-level no-follow and post-batch safety. The archived blob is `108f66714602a1bd3ae42c34dcca7c16e38f460b`; its current upstream SHA is `e428789e2e97ca7be3a4482e0df23b483a1ad69d`. GitHub compare from `ca6c5d915d2c0e018f4aa9f82b4488038c16f8d3` to `421802db4d8d89a5508f5f158671a6e4b3465568` shows the security-oriented cache-manifest changes. This is a **genuine, expected source-identity drift** in the synthetic merge checkout, not proof of failed archived fixed test results or an actionable permission to update the baseline.

## Correct handling and decision

- Keep PR #418 **Draft/unmerged**. Keep upstream PR #413 **Draft/unmerged**. Do not re-pin to the newest implementation just to make the PR green, suppress `pull_request` checks, or checkout `head.sha` to bypass review of the target merged tree. Source differences must remain visible.
- If integrating later, review upstream security change, explicitly define a **new candidate/source lineage**, run the whole frozen offline suite and archived controls against that new exact tree, and retain original archived baseline separately. No implicit authority/admission/promotion.
- Direct 9-module source pin does **not** cover every transitive import. Python package versions are not exact signed wheel hashes. Offline SHA test identity is not official PIT data evidence.
- Official KRX historical tradability, original OpenDART 2022 vs 2021 first-vintage standalone CFS quarterly operating-profit semantics/publication PIT, and M20 post-cost strategy profitability still **NOT VERIFIED**. No M20 trial, sealed Holdout, Champion change or broker orders. `ORDERING=false`.
