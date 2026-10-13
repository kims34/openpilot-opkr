# M20 2022 Q3 original vs official correction archive source pair (2026-10-13)

**Scope:** one frozen issuer slot 5, official OpenDART source-only provenance. No performance, market-price, broker or holdout requests.

Previous independent official evidence:
- [Initial original ZIP checksum and structure](https://github.com/kims34/openpilot-opkr/actions/runs/38392847048): first-filed 2022 Q3 ZIP SHA256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`.
- [Original official index reported rm=정](https://github.com/kims34/openpilot-opkr/actions/runs/38413190868).
- [Complete bounded follow-up index census](https://github.com/kims34/openpilot-opkr/actions/runs/38415899682): 31 periodic-filing rows, one later 2022-Q3 correction, zero attachment additions through 2026-10-13.

New isolated proof:
- `research_v1_opendart_m20_2022_correction_source_pair.py` and `test_research_v1_opendart_m20_2022_correction_source_pair.py`.
- [Source-pair official CI](https://github.com/kims34/openpilot-opkr/actions/runs/38417433460): offline regression tests **PASS**. The official read-only archive-pair job was **still running at the time of this initial note**; its outcome must be read from Actions before claiming that the corrected document was retrieved.
- Exact original source SHA is pinned. The code derives the single corrected receipt ephemerally from the fixed 2022 Q3 original and complete bounded post-2023 issuer index. It uses at most five read-only official requests and verifies archive ZIP integrity with existing strict bounded helper.
- The results (if the official read succeeds) only record non-reversible ZIP SHA256 values and structural flags. A difference between archived bytes **does not prove a changed financial fact**. Precise edition receipt IDs, dates, issuer IDs and financial amounts are neither printed nor persisted.

Open PIT blockers regardless of success: original standardized 2022 XBRL endpoint status 014, no validated 2022/2021 Q3 standalone CFS operating-profit values, unknown financial-semantic differences between original and amended statements, no original intraday public availability timestamp, no historically PIT-verified issuer/security mapping.

**Safety:** `m20_feature_pit_admitted=false`; `m20_performance_run_authorized=false`; independent Holdout, Champion promotion, real orders, funds and account rights remain unauthorized. `ORDERING=DISABLED`. Draft PR only, no merge.


## 2026-10-13 final verified official pair result

- [Completed real official Actions run #38417433460](https://github.com/kims34/openpilot-opkr/actions/runs/38417433460): **both** offline tests and OpenDART read-only original/correction archive verification **SUCCESS**, not merely queued.
- Original first-filed 2022 Q3 ZIP SHA256: `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`; later amendment ZIP SHA256: `606be9d03928808f0a2a05f052444587bd2457bdef7a47a8f4bff3d2ea098a30`.
- The ZIP **bytes differ**, but each archive contains one legacy SGML/HTML markup entry, zero strict-XML documents and **15** tables with candidate operating-profit row shapes. The previous report's original publication time, 2022/2021 Q3 financial statement cells and corrected financial cell differences **remain unverified**.
- Official safe flags-only artifact `11825490610` (`indexalert-m20-corrected-source-pair-evidence`), digest `sha256:1daf76e9e19f688c10211b2d7607cba5025a0ae1dee357b49e344d3b0cc98d6f`.
- All PIT, M20 performance, Holdout, Champion, real orders and account permissions remain disallowed; `ORDERING=DISABLED`. A difference in archive SHA does **not** mean operating income was changed.
