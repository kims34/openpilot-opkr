# M20 2022 Q3 first-filed SGML — explicit tag ancestry verdict

## Verified official evidence

On 2026-10-14, read-only first-original OpenDART [Actions #38540322881](https://github.com/kims34/openpilot-opkr/actions/runs/38540322881) completed with **offline unit/security tests SUCCESS** and **official SHA-pinned source inspection SUCCESS**. First initial regression [#38540131743](https://github.com/kims34/openpilot-opkr/actions/runs/38540131743) failed **in an offline synthetic unittest fixture only**; corrected in commit `7209c02c843290d8227dda8a4d70a150318d641d`. No official fetch was authorized by the failed initial run.

Fixed issuer cohort slot **5**, earliest 2022 Q3 submission, official first-filed ZIP SHA256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` preserved. Source-only workflow allows at most three read-only official requests: corpCode.xml, initial list.json, original document.xml. No amended/revised values, ticker, receipt number, original amounts or raw markup appear in the output.

**New, qualitatively distinct check:** a bounded `HTMLParser` traces *explicit* SGML document/section/subsection/article ancestry and scoped `<title>` categories at each exact operating-profit/loss row rather than searching nearby text. The original legacy document contains:

| Source-only diagnostic | Exact count |
|---|---:|
| Original SGML tables | 1,570 |
| Operating row candidates | 15 |
| Explicit `<section>` tags | **0** |
| Explicit `<subsection>` tags | **0** |
| Explicit `<document>` tags | 1 |
| Explicit `<title>` tags | 71 |
| Explicit `<p>` tags | 9,718 |
| Generic financial-statement title elements | 4 |
| Exact consolidated-income-statement title elements | **0** |
| Operating candidates inside explicit `section/subsection` | **0** |
| Operating candidates within document-only ancestry | **15** |
| Operating candidates with scoped exact CFS title | **0** |
| Operating candidates with scoped general financial-statement heading | **2** |
| Operating candidates in nested tables | 1 |

Although the broader document contains 71 title elements and four generic financial-statement titles, their existence does **not** identify exact 2022 Q3 standalone 3-month CFS profit cells or comparable 2021 Q3 cells. Two candidate rows only share a *generic* title under document ancestry, not a verified financial-statement subsection.

Code: `research_v1_opendart_m20_2022_original_sgml_tag_ancestry.py`; offline tests: `test_research_v1_opendart_m20_2022_original_sgml_tag_ancestry.py`; official workflow: `.github/workflows/indexalert-m20-original-sgml-tag-ancestry.yml`. Immutable flags-only artifact `11881578233` sha256 `dbffa38698feaa68416ca827b69976ed04ffd5ffa6a09dccb8d29018e8cd0b4f` (7-day retention).

## Provenance verdict and immediate next source requirement

The **strong structural ancestry route is insufficient**: first-filed legacy SGML has no explicit `section/subsection` blocks, and no exact CFS title, so neither prior 2,400-/12,000-character heading proximity scans nor tag nesting alone can yield a reliable original Q3 consolidated profit value. Do **not** relabel one of 15 candidate earnings-like tables based on repeated heuristics.

To proceed, obtain a separately authoritative first-vintage financial statement with independent `source document → issuer → edition → CFS statement → 2022/2021 Q3 3-month period → monetary units → original cells → first-publication time` bindings. The earlier standardized first-filing XBRL endpoint returned `014`; a separate current normalized 2022 Q3 CFS API probe failed closed as missing data. Historical issuer-to-security mapping and corporate-action universe PIT remain separate blockers.

**Research direction:** seek an independently archived original filing and a *documented* SGML DTD/schema if available. Without it, stop repeatedly rerunning nearby-heading or source text-count probes and direct resources to verifiable alternate frozen cohort sources. Do not relax the frozen six-issuer definition, pre-registered H5/M20, labels/periods/holdout, costs/taxes, or Champion.

`m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, `independent_holdout_authorized=false`, `champion_change_authorized=false`, `real_orders_authorized=false`, `funds_movement_authorized=false`, `permissions_change_authorized=false`; `ORDERING=DISABLED`. Draft [PR #412](https://github.com/kims34/openpilot-opkr/pull/412) unmerged.
