# KRX market calendar — historical public notice evidence recovered, 2026-10-14

**Purpose:** prioritize actual historical KOSPI stock-market closure evidence, rather than adding another synthetic calendar proxy. **Only one historic KRX-hosted public market announcement was identified in this batch; other notices are secondary corroboration.**

## New actual historical lead

**KRX KIND-hosted 2024 market notice, KOSPI stock market:** [2024-12-17 archived exchange notice](https://kind.krx.co.kr/external/2024/12/17/000106/20241217000237/99303.htm). Direct public text says the final 2024 stock session was **2024-12-30**, the year-end market closure was **2024-12-31**, and the 2025-01-02 stock-market reopening was delayed until **10:00 KST**. The original public URL is housed on the exchange's disclosure host and its path contains date `2024/12/17`; **the precise first-available-at time and original archival file bytes or revision history are not independently proven**. This link establishes a useful concrete exchange-hosted announcement for that *one date*, not an annual market session calendar.

**Other public source leads** (see [manifest](./2026-10-14-krx-year-end-exchange-notice-candidates.json)):

| Closure candidate | Source type | Public evidence | Publication time status |
|---|---|---|---|
| 2019-12-31 | Financial Investment Association written reply | [KOFIA reply 2020-01-14](https://www.kofia.or.kr/voc/m_113/view.do?answer_seq=737&page=9&srchTp=&srchWord=&voc_id=1645) citing a KRX-transmitted 2019 year-end notice | **RETROSPECTIVE**, too late as direct 2019 historical PIT |
| 2021-12-31 | Broker notice | [Hanyang Securities notice](https://m.hygood.co.kr/board/customerNotice/detail/1360), shown date 2021-12-30 | Date-level publication only, original KRX timestamp unknown |
| 2022-12-30 | Broker notice | [Eugene Investment 2022-12-22 notice](https://m.eugenefn.com/no20r.do?msgId=426947&pageNo=1&topFlag=0) | Date-level publication only, original KRX timestamp unknown |
| 2023-12-29 | Broker notice | [Samsung Securities 2023 year-end market schedule](https://www.samsungpop.com/ux/kor/customer/notice/notice/noticeViewContent.do?MenuSeqNo=20474) | First-publication time unverified |
| **2024-12-31** | **KRX KIND-hosted** | [KIND 2024/12/17 public market notice](https://kind.krx.co.kr/external/2024/12/17/000106/20241217000237/99303.htm) | Date in archive path; precise notice-first-seen time unverified |
| 2025-12-31 | Exchange-style notice republished | [Maeil Business stock disclosure notice](https://stock.mk.co.kr/news/disclosure/template/840009) | First publication and original exchange document unverified |

These six public date candidates are **NOT** six verified private provider-empty KRX receipts; source/data set equality has not occurred. The separate 2026-06-03 and 2026-07-17 secondary KRX-attributed notices are documented in [earlier evidence](./2026-10-14-krx-2026-contemporaneous-closures-pit-boundary.md).

## Implementation and verification

- Created [machine-readable official-host vs broker source-tier manifest](./2026-10-14-krx-year-end-exchange-notice-candidates.json), with years, exact closure days, last cash-equity market sessions, URLs and date-only vs retrospective/unknown publication flags.
- Created [offline evidence reviewer](../../research_v1_krx_public_notice_leads.py) and [unittest regression](../../test_indexalert_krx_public_notice_leads.py). It keeps KRX KIND hosted evidence separate from broker/republication/retrospective sources, and refuses impossible dates, duplicated years, mismatched domain source tiers, forged first-published claims and all unexpected data-admission flags.
- [GitHub Actions run 38503190289](https://github.com/kims34/openpilot-opkr/actions/runs/38503190289) COMPLETED SUCCESS: **111/111 offline tests passed**, code commit `97c7319b3b3e52343a7fc8393aa4b6222d0bf06c`.
- No user authentication, private KRX source/API reads, unapproved six-provider-GET repeats, Railway restart/deploy/config change, source data export, sealed holdout or live orders.

## Actual uncompleted PIT work — non-negotiable distinction

The existing original KRX private worker has **3,071 SHA-backed weekday source-pair checkpoints; 184 provider-empty ambiguous market dates remain unresolved; 27 securities still quarantined**. The KRX historical worker still runs original development commit `1e6367d2863a86c3470da13d81a955d277eba485`, with mounted restricted volume `/data` and no new relevant deployment. This tool connection can see worker metadata/logs but cannot read or operate on raw files inside the private volume. We therefore did **not** compare any of these six public closure notices to the corresponding private checkpoint record.

To advance beyond candidate leads, obtain a permitted, date-complete historical KOSPI market-session source with provenance/version/publication as-of metadata, then run existing read-only per-day SHA private comparator. This year's **one KIND-hosted notice** can be used to test 2024-12-31 privately *only when the original 2024-12-31 KRX checkpoint actually is read and verified*. Until then, do not subtract even one from 184.

**Final guard state:** source gates C/D blocked; official historical full date set unverified; H5/Frozen, Champion and sealed Holdout unchanged; M20 NetEV/profitability run not authorized; `ORDERING=false`, no trade or money movement.
