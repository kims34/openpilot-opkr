# KRX calendar source row provenance fix — audit-only handoff

**Observed 2026-10-14 KST.** Scope: isolated KRX source-audit branch. **No source PIT promotion, profitability backtest, live order or Railway deployment.**

## Verified read-only status

- The KRX historical worker is live in the existing Railway production environment, with private volume `/data`; latest observed worker deployment remains `16c93d7c-7cd0-4d84-a327-298d2805376c`, SUCCESS, development commit `1e6367d2863a86c3470da13d81a955d277eba485`.
- No runtime KRX worker logs after the last audited execution were returned.
- Existing 3,071 weekday source checkpoints and 184 ambiguous exchange-calendar/source-empty dates remain unchanged; 27 historically problematic securities still quarantined.
- Official [KRX market holiday lookup](https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp) provides a human-operated search/download route, with columns **일자/요일/비고**. [KRX KOSPI market closure rules](https://global.krx.co.kr/contents/GLB/06/0602/0602010201/GLB0602010201T1.jsp) explain Saturday, public holidays, elections, Labor Day, year-end and exceptional closures. Neither page is a verified complete 2015–2026 as-of calendar extraction here.

## Actual safety flaw closed

The older `research_v1_krx_official_calendar_input_preflight.py` checked original file *bytes SHA* versus a separately supplied human-normalized date list. **That did not prove the asserted dates appeared in the original file.** A caller could use a correct checksum for one document but claim different closure dates. The old helper still labels that state `SOURCE_BYTES_HASH_BOUND_CALENDAR_CLAIM_ONLY_NOT_PIT`; it remains a metadata-only preflight, not row attestation.

New [source-row validator](../../research_v1_krx_calendar_csv_source_validator.py) directly parses a locally supplied CSV file, validates its exact three-column layout `일자,요일,비고`, each actual date and Korean weekday, UTF-8 BOM/CP949, duplicates, year, and checks that the **complete weekday-closure date set parsed from bytes equals the sidecar claim**. An unsupported binary XLS/XLSX or HTML response now fails closed instead of trusting the human date claim. The [existing private year runner](../../research_v1_krx_private_calendar_year_runner.py) is updated to require the *actual CSV source-row check* before opening the dedicated KRX private source audit. No network access was added.

**Format limitation:** the KRX download button may deliver a binary Excel file. The validator intentionally cannot parse binary XLS/XLSX, and this work did not confirm a supported direct CSV download format. A genuine original Excel document must be retained, its actual rows independently parsed and cross-checked in a separate authorized and tested route; simply renaming the file to `.csv` or hand-typing dates will not pass. A manually converted CSV is not the original downloaded object and must not be described as such. The source URL and metadata can themselves be forged; a row match does not authenticate KRX origin or original historical publication.

## Test evidence and remaining gates

- [GitHub Actions run 38484453856](https://github.com/kims34/openpilot-opkr/actions/runs/38484453856) succeeded with **85/85 offline tests** at commit `8f8bf4a89c137457005faaff33854cbad437f88f`.
- New test suite: [CSV source-row provenance](../../test_indexalert_krx_calendar_csv_source_validator.py). Regression runner tests reject a manipulated sidecar even with matching source-document SHA, and reject unsupported binary Excel before entering the original source comparison.
- No provider/API call, user credential access, broker action, Railway config/staged deployment, or original private data publication was performed. Frozen/H5, Champion, Holdout unchanged, `ORDERING=false`.

**Actual PIT calendar source still BLOCKED:** an independently authenticated original KRX historical cash-equity calendar, at permitted scope and original date/version provenance, remains absent from the mounted private worker. The date-set comparison against 184 stored empty-day events **has not run**. Even successful calendar comparison would leave the 27-security trading-state lineage and first-available-at PIT separate. **Do not claim actual 184-day resolution or unlock M20 profitability runs.**
