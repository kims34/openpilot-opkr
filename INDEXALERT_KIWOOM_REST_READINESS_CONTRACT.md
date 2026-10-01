# IndexAlert Kiwoom REST Readiness Contract — Read-Only / Demo Preparation

Updated: 2026-10-02 KST
Branch: `index-alert-research-v1`
Status: **READ-ONLY / DEMO PREPARATION ONLY — REAL-ACCOUNT ORDERING DISABLED**

This contract freezes the safe preparation boundary for a future Kiwoom Securities REST adapter. It does not authorize real-account ordering, does not close the empirical execution blocker, and does not change any Alpha, statistical, KRX, holdout, promotion, capacity or execution-sufficiency threshold.

## 1. Authority and current disposition

This contract is subordinate to:
1. `INDEXALERT_MASTER_SPEC.md`;
2. `INDEXALERT_RESEARCH_LEDGER.md`;
3. current reproducible GitHub code / Actions;
4. `INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md`;
5. `INDEXALERT_LIVE_EXECUTION_PROVENANCE_CONTRACT.md`;
6. `INDEXALERT_EXECUTION_SUFFICIENCY_PROTOCOL.md` / `.json`;
7. `INDEXALERT_BROKER_EXECUTION_CONTRACT.md`.

Current project state remains fail-closed:
- `genuine_live_provenance_verified=false`;
- `live_empirical_execution_evidence_ready=false`;
- `empirical_execution_sufficiency_assessed=false`;
- `empirical_execution_blocker_closed=false`;
- `promotion_ready=false`;
- `sealed_holdout_authorized=false`;
- `live_trading_authorized=false`.

The only permitted integration work under this contract is official-schema review, secret-safe configuration design, read-only/demo connectivity preparation, broker-native evidence mapping, offline parsers/validators, and tests proving that prohibited order paths remain unavailable.

## 2. Official Kiwoom source snapshot reviewed

The schema review for this contract used the official public repository:
- repository: `Kiwoom-Securities/Kiwoom-REST-API`;
- reviewed branch: `main`;
- reviewed source tree SHA: `953e5dbff123f437ab4d11a78a95191a685eb51f`.

The reviewed official examples include:
- account number query `ka00001`, path `/api/dostk/acnt`;
- account order/fill detail `kt00007`, path `/api/dostk/acnt`;
- filled-order query `ka10076`, path `/api/dostk/acnt`;
- domestic real-time order/fill stream type `00`, path `/api/dostk/websocket`.

This snapshot is documentation provenance only. Before any later Paper, Tiny Live or real-account stage, the then-current official Kiwoom documentation/repository must be re-read and any schema/environment drift reviewed explicitly.

## 3. Credential and account boundary

A Kiwoom login ID is not itself an API credential. Future REST connectivity requires the then-current Kiwoom OpenAPI/REST service enrollment and application credentials issued by Kiwoom.

Secrets and sensitive account material must never be pasted into ChatGPT, committed to Git, stored in GitHub Actions artifacts, printed in logs, or copied into research datasets.

Prohibited material includes at least:
- login ID/password combinations;
- App Key / App Secret;
- access or refresh tokens;
- certificate/private-key material;
- full account numbers in project artifacts.

When credentials are eventually configured, they must be injected by the deployment platform's secret mechanism. Account identity retained for evidence must use a privacy-safe deterministic fingerprint plus separately protected source material where legally/operationally required.

## 4. Environment separation

`DEMO/PAPER` and `REAL` are different evidence classes even when they expose similar API schemas.

Current allowed environment: **DEMO/read-only preparation only**.

Rules:
- demo/paper observations may validate connectivity, parsing, state-machine plumbing and reconciliation mechanics;
- demo/paper observations must never be relabelled `PROSPECTIVE_LIVE_EXECUTION_LOG`;
- demo/paper observations must never set `genuine_live_provenance_verified=true`;
- demo/paper observations cannot satisfy the frozen execution-sufficiency sample or metric gates;
- a successful token, account query, quote query or websocket connection is technical connectivity only;
- possession of REAL credentials alone does not authorize a REAL request or any order submission.

Observed demo plumbing is recorded separately in `INDEXALERT_KIWOOM_DEMO_CONNECTIVITY_EVIDENCE.md`. The observed `TOKEN_OK`, `ACCOUNT_OK`, `BALANCE_OK`, and `FILLS_OK` sequence confirms only demo/read-only connectivity and does not change any project promotion or execution gate.

## 5. Current network permission matrix

Until a later explicit promotion-stage change is committed and independently reviewed:

Allowed after the user configures appropriate demo credentials locally/through a secret manager:
- authentication/token smoke checks against the demo environment;
- read-only demo account-number discovery;
- read-only demo balances/positions/open-order/execution queries;
- read-only market/status queries;
- read-only subscriptions needed to validate event decoding;
- offline transformation into the broker-neutral execution evidence schema.

Forbidden now:
- any request whose purpose is to create, amend or cancel an order in the REAL environment;
- any automatic switch from demo to real because real credentials are present;
- any `TINY_LIVE`, `LIMITED_LIVE` or `LIVE` activation;
- any code path where an unknown/missing mode defaults to real;
- using broker integration to open the sealed holdout;
- using demo/paper results as real fill-quality evidence.

Order-capable Kiwoom endpoints may be documented for future review but must not be invoked by current readiness tooling.

## 6. Broker-native evidence mapping

The reviewed official schema provides fields suitable for later independent provenance/reconciliation.

### Account order/fill detail — `kt00007`
Relevant broker-native fields include:
- `ord_no` — broker order number;
- `ori_ord` — original order number;
- `stk_cd` — symbol/code;
- `ord_qty` / `ord_uv` — submitted quantity/price;
- `cntr_qty` / `cntr_uv` — filled quantity/price;
- `ord_remnq` — remaining quantity;
- `ord_tm` / `cnfm_tm` — lifecycle times;
- `acpt_tp`, `mdfy_cncl`, `dmst_stex_tp` — status/amend-cancel/exchange context.

### Filled-order query — `ka10076`
Relevant broker-native fields include:
- `ord_no`, `orig_ord_no`;
- `stk_cd`, `ord_qty`, `ord_pric`;
- `cntr_qty`, `cntr_pric`, `oso_qty`;
- `tdy_trde_cmsn`, `tdy_trde_tax`;
- `ord_stt`, `ord_tm`, `stex_tp`, `sor_yn`.

### Real-time order/fill stream — type `00`
The reviewed official stream includes broker-native fields for:
- account number (`9201`) — must be privacy-safely transformed before project retention;
- order number (`9203`);
- order status (`913`);
- symbol (`9001`);
- submitted quantity/price (`900`, `901`);
- remaining quantity (`902`);
- original order number (`904`);
- order/fill timestamp (`908`);
- **execution/fill number (`909`)**;
- fill price/quantity (`910`, `911`);
- fee/tax (`938`, `939`);
- rejection reason (`919`);
- exchange/SOR context (`2134`, `2135`, `2136`).

For a future admitted genuine-LIVE evidence bundle, broker order number and execution number must remain broker-native stable identifiers. Project row IDs or CSV row numbers cannot substitute for them.

### Implemented offline normalizers and reconciliation

`research_v1_kiwoom_native_execution.py` implements offline-only normalization for:
- real-time order/fill type `00`;
- REST account order/fill detail `kt00007`;
- REST filled-order query `ka10076`;
- same-order `kt00007` / `ka10076` structural reconciliation.

The implementation contains no network, authentication, account-query, order-create, amend, or cancel code.

A critical source-granularity distinction is frozen:
- real-time type `00` exposes broker-native execution/fill number `909`, so a positive fill quantity requires that execution identifier;
- `kt00007` and `ka10076` expose order-level/aggregate fill snapshots but do **not** expose `909` or an equivalent per-execution identifier in the reviewed schema;
- therefore `kt00007` / `ka10076` normalized rows must retain `record_granularity=order_aggregate_snapshot`, must keep `broker_execution_id` empty, and must set `broker_execution_id_available_in_source=false`;
- the project must never synthesize an execution ID from `ord_no`, a CSV row number, a project row ID, a hash, a timestamp, or any other locally invented value.

The REST reconciliation helper may compare only normalized `kt00007` / `ka10076` rows for the same intended order snapshot. It fail-closes on conflicting account fingerprint, broker order ID, symbol, original-order ID, order/fill quantity, remaining quantity, order price, or fill price when both sources provide the field. A successful structural reconciliation remains plumbing evidence only and always keeps `genuine_live_provenance_verified=false` and `project_live_evidence_admitted=false`.

## 7. Provenance admission remains separate from metric evaluation

No caller-supplied label, filename, CSV hash, source string, self-authored manifest or unit fixture can authenticate a genuine real-account origin.

A later genuine-LIVE bundle must satisfy `INDEXALERT_LIVE_EXECUTION_PROVENANCE_CONTRACT.md`, including at minimum:
- real-account/environment attestation;
- privacy-safe account binding;
- immutable raw/export/query artifact hashes;
- stable broker order IDs and, for fills, stable broker execution IDs where exposed;
- row-level mapping from every admitted evidence row to broker-native source material;
- lifecycle quantity/price/time consistency;
- fees/taxes where used by the frozen assessment;
- explicit retention of no-fill, partial-fill, rejection, expiry and unknown outcomes;
- reconciliation showing no unsupported rows and no double counting.

Only after independent provenance admission may the already-frozen numerical execution-sufficiency evaluator be applied as project evidence. Numerical metric computation alone remains insufficient.

## 8. Historical real-account data boundary

Read-only historical Kiwoom records, if later retrieved from a real account under explicit permission, may be useful for:
- validating broker field mappings;
- reconciliation testing;
- exact status-event economics when the separate status-economics contract accepts the evidence;
- documenting fees/tax and lifecycle semantics.

They do **not** automatically count toward the frozen prospective execution-sufficiency window. Only observations generated under the frozen decision/execution policies and admitted by the provenance contract may enter that window.

## 9. Fail-closed implementation requirements

Any future Kiwoom adapter/readiness module must:
- default to `MASTER_OFF` at the project execution layer;
- require an explicit environment value; unknown values fail closed;
- separate demo and real credentials/configuration;
- keep Alpha/selection code free of Kiwoom-specific logic;
- expose read/query and submit/amend/cancel capabilities separately;
- make order-capable methods unavailable in the current readiness phase;
- redact secrets and full account numbers from logs/errors;
- preserve raw broker-native identifiers needed for later protected reconciliation without exposing them publicly;
- never infer a successful order from a timeout;
- never convert technical connectivity into promotion, holdout or live-trading authority.

## 10. Promotion-stage change control

Moving beyond this readiness boundary requires a separate reviewed change. At minimum it must identify:
- current official Kiwoom documentation/source fingerprint;
- exact demo vs real hosts and authentication behavior;
- rate limits/error semantics;
- account/order/fill reconciliation behavior;
- Kill Switch and risk limits;
- exact order-capable methods to be enabled;
- the project gate that authorizes the next mode.

No such change is authorized by this document.

## 11. Current conclusion

Kiwoom REST is a viable future broker adapter/evidence source based on the reviewed official schema, including broker-native order and execution identifiers plus fill/fee/tax fields. Demo/read-only authentication, account, balance and filled-order connectivity has been observed successfully, and offline normalization/reconciliation plumbing is implemented for the reviewed broker-native schemas.

**Real-account order submission remains disabled. Demo/paper evidence is not genuine LIVE evidence. REST order snapshots without broker execution IDs cannot be promoted into per-execution evidence. The sealed holdout remains untouched.**
