# IndexAlert independent read-only gate — 2026-10-19 09:19 KST

Scope: integration admission and offline-only optimization evidence. No strategy run, official data query, deployment, order, fund, credential, permission, merge, or champion action. No delegated specialist code touched. ORDERING=false.

## Exact checked refs (GitHub connector)
- research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- Draft #414 integration HEAD `4ec707e4cca788c1b139a58debfb28050ee0df0b`, base research `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Draft #413 runtime optimization HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- Draft #418 one-runner HEAD `2f98401cc50a6c6a25808a98516efd5bf0c944ee`, PR base SHA `ca6c5d915d2c0e018f4aa9f82b4488038c16f8d3`; current actual #413 branch HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`. Revalidate merge tree against actual base before accepting any evidence.
- Draft #412 DART HEAD `f1ca535a1a2e8cc8a55d9b28edf5675bce466143`.
- Draft KRX #420 HEAD `d18e373c20a69ff9e94cfef5f5394a84236f2389`; dependent #422 HEAD `c14857620973531013799e44625d43080904fd5f` and recorded base SHA `4472db849dee4266f7ade3345264015f18fc46bb` (stale relative to #420).
All six PRs are open/draft. Do not merge.

## Current Actions
- #412 `39138781560` and `39138781533`: SUCCESS (offline safety; NOT official PIT approval).
- #413 `38508247773`: SUCCESS (offline parity only).
- #418 `39111405562`: SUCCESS (one-runner probe), `39111405494`: SUCCESS (candidate audit, non-admitting), `39111405478`: FAILURE (archived source integrity).
- #420 `39139150924`, `39139150917`, `39139150930`: SUCCESS (offline/no-PIT tests).
- #422 `39001836000`: SUCCESS (synthetic candidate).
- Direct #418 failed job `117628139395` shows `research_v1_runtime_manifest.py` archived blob expected `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Direct #413 file fetch confirms actual Git blob `e0055c66c59398fd4a1158077446d886b54c4e37`. **FAIL**; do not silently repin baseline. Environment gate checked 22 package versions but `exact_wheel_hashes_verified=false` and `os_native_dependency_identity_verified=false`.

## Railway production read-only
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`; no pending work. 3 of 10 services show issues: backend offline 4 warnings; push offline 1 warning; db-query-readonly offline 1 critical. Last listed KRX worker successful deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` from 2026-10-12 13:07 UTC, commit `1e6367d2863a86c3470da13d81a955d277eba485`. Worker log reports 2017–2022 private source 1,565 weekday pairs integrity and 90 unresolved calendar/source gaps; no PIT admission. PIT rebuild last available 2026-10-18 14:46 UTC still `COMMON_OHLC_NONPOSITIVE` and fail-closed. This is not proof of exchange official tradeability.

## Independent offline synthetic (local, no repo change)
Four synthetic byte files: serial SHA-256 equals four-worker read-only SHA-256 (PASS); changing one input detects exactly one changed digest (PASS). Python dict equality considers `False == 0` and `True == 1` (confirmed); strict metadata type identity does not. The #413 `cache_matches` and #418 `handoff_matches` whole-dict equality should not be considered strict typed authority receipt comparison. Neither SHA parity nor synthetic results authorize source/PIT or financial computation.

## Gate decisions
- Source receipt storage SHA: KRX 2017–2022 private pair integrity **PASS limited to stored originals**, official trading calendar/status/CA/fill eligibility **NOT VERIFIED**.
- OpenDART first-original 2022 and comparative 2021 standalone three-month consolidated operating income, exact first-public available-at, correction lineage, historical issuer/security mapping: **NOT VERIFIED**.
- PR #418 merged source identity: **FAIL** in pinned CI; runtime wheel/native full identity **NOT VERIFIED**.
- Costs, taxes, slippage, realistic fills, after-tax NetEV/PF/CAGR/MDD/ES95/ES99, concentration, temporal robustness: **NOT VERIFIED**.
- M20 economic run: **NO-GO** until independent original PIT/tradability evidence is admitted. H5 frozen, M20 horizon20/purge20, WF504/126/126, CPCV, sealed Holdout, Champion, Top3 and NO_TRADE unchanged. ORDERING=false.
- Only independently approved source/code/policy/runtime/evidence SHA256 combinations may permit fail-closed cache reuse. Only read-only postprocessing may parallelize; dependent retraining and capital transition must stay sequential. No PR merges, deployment, real orders or promotion.

Next read-only step: check new original-file first-availability lineage and official KRX session/state evidence from delegated owners, then re-audit actual candidate merge source SHA and runtime closure. Do not repeat other owners' experiments.
