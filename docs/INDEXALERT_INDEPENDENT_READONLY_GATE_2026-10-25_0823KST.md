# IndexAlert independent delta gate — 2026-10-25 08:23 KST

Read-only GitHub evidence review, one bounded synthetic filesystem demonstration, and a documentation-only record. No official source/PIT admission, economic experiment, model training, Holdout use, order, capital movement, privilege change, Railway change, deployment, merge or Champion promotion.

## Exact checked GitHub references

- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (GitHub branch REST).
- Integration Draft [#414](https://github.com/kims34/openpilot-opkr/pull/414): pre-document HEAD `329362ef591fc8f3ad4e6edfa43e7a5ea3b015c9`; integration-gate Git blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- OpenDART Draft [#412](https://github.com/kims34/openpilot-opkr/pull/412) `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`; runtime Draft [#413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; dependent runner Draft [#418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`, [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`. All Draft/unmerged at check.

## Newer read-only Actions evidence since 07:49 KST ledger

- [Watchdog run 40141599597](https://github.com/kims34/openpilot-opkr/actions/runs/40141599597), 2026-10-24 23:09–23:10 UTC (2026-10-25 08:09–08:10 KST), one job `121014314623` SUCCESS. Decoded job log states **`M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`**. This is a watchdog assessment, **not** independently attested live Railway configuration.
- Uploaded flags-only artifact ID `12578798539` ZIP SHA-256 `eb67b3203689b1dc7cf64246aca8b9d71151d17006f5483f97effe263d482f84` matches decoded Actions upload log and GitHub artifact metadata: **LIMITED PASS for metadata/log consistency**. ZIP bytes were **not** downloaded and independently rehashed; do not call this source-original SHA proof.
- Existing [prospective chronology 39972035700](https://github.com/kims34/openpilot-opkr/actions/runs/39972035700): decoded job `120476944660` ended with `/anchor/latest` HTTP 404, downstream chronology steps SKIPPED: **FAIL/BLOCKED**. No first-public available-at proof.
- [KRX #420 CI 39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) SUCCESS for offline synthetic exception review, not private original-day reconciliation or official tradability. KRX #422/#423 comparator descriptions explicitly state actual private day-set audit was **not run**.
- [Optimization #413 38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) offline jobs SUCCESS; [#418 39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) archived-source gate FAIL before regressions, because expected Git blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b` differs from reviewed #413 candidate `e0055c66c59398fd4a1158077446d886b54c4e37`. Do not repin or reinterpret candidate-only PASS as archived replay.

## Additional independent offline static safety observation (not an exploit claim)

At #418 HEAD, both `research_v1_runtime_archived_source_gate.py` and `research_v1_runtime_candidate_merge_gate.py` use `Path.is_symlink()` / `is_file()` before `path.read_bytes()` for pinned Git-blob comparisons. This is a **check-then-read gap**: Python's `read_bytes()` follows a symlink if the pathname is replaced after the check. A local, synthetic-only temporary-directory demonstration confirmed `precheck_passed=True` and subsequent read of replacement symlink target `True`. No repository files, market data, secrets, CI or Railway were changed. This **does not establish exploitability in isolated GitHub CI** or a current SHA bypass, but means these gates have not demonstrated the same no-follow/TOCTOU protection as #413's cache-manifest file reader. **Review-needed, not a reason to relax the existing FAIL-CLOSED archived gate.** Assigned to #418 runtime owner; integration track must not edit the owner's code or workflow.

## Source/PIT/economic decision

- **LIMITED PASS**: watchdog CI completion, metadata-vs-log ZIP digest consistency, offline synthetic guards. Git blob SHA-1 is code identity, not original DART/KRX SHA-256.
- **FAIL/BLOCKED**: archived #418 identity mismatch; prospective chronology HTTP 404. Railway read-only `list_projects` required interactive user input and did not return projects; actual deployments/logs/`ORDERING` **NOT VERIFIED**.
- **NOT VERIFIED**: 2022/2021 first-original 3-month consolidated operating-profit fact/period/correction lineage and exact first-public available-at; issuer-security historical map; 2017–2022 official KRX session/status/corporate-action/fill, quarantined 27 security rows, fee/slippage/tax economics; after-tax NetEV/PF/CAGR/MDD/ES95/ES99, concentration/date-cluster robustness; complete transitive runtime/wheel/native hashes and full CI/official backtest speedup.
- **NO-GO** for M20 PIT admission and any M20 profitability RUN. Frozen H5; M20 horizon20/purge20; WF504/126/126; PIT/label/Purged/CPCV; consumed independent Holdout; Champion/Top3/NO_TRADE; predeclared costs/tax/risk/promotion unchanged. `ORDERING=false` mandatory; actual live setting not attested.
- Next proofs remain with OpenDART original public-time/quarter semantics owner, KRX official historical day/security/tradability owner, and #418 runtime owner for archived source/TOCTOU/full-runtime closure. No duplicate specialist experiments or source writes. No routine user notification.
