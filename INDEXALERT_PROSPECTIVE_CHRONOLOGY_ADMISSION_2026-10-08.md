# Online prospective chronology admission — 2026-10-08

Status: INDEPENDENT CHRONOLOGY VERIFIER IMPLEMENTED — SOURCE/MODEL/ALPHA/LIVE AUTHORITY STILL FALSE.

The hash-only chronology anchor is now bound to the GitHub Actions run that creates it. Future anchor records include GitHub-assigned `workflow_run_id` and `workflow_run_attempt`, and the anchor-branch commit message includes that run ID. This closes an ambiguity in the first anchor design: a later verifier no longer has to guess which workflow execution produced a same-session hash record.

`research_v1_prospective_chronology_admission.py` is the first path permitted to set `independent_chronology_admission_verified=true`. It does not accept a caller-supplied "verified" boolean or pre-fetched commit timestamp. For one private session it reads the immutable local session manifest and decision capture, then independently queries GitHub's public API to:

1. locate the only commit touching `prospective_anchors/YYYY-MM-DD.json` on the dedicated append-only anchor branch;
2. fetch the exact anchor file from that commit and validate its canonical hash-only schema;
3. bind all source/input/producer/model/decision/session hashes back to the private manifest and decision capture;
4. fetch the GitHub Actions run named by the server-assigned run ID and require the exact workflow name/path, `workflow_dispatch`, successful completion, run attempt and `head_sha == workflow_ref_commit`;
5. use GitHub's server-side workflow `created_at` as the chronology trust point, requiring it to be no earlier than the declared decision and no later than the preregistered six-hour anchor window;
6. require the anchor-path commit message to include the same run ID and the commit to be attributed to `github-actions[bot]`.

The git commit timestamp is checked only for consistency; it is not the trust root. The server-side Actions run creation time is the external timestamp used for chronology admission.

Even after chronology admission succeeds, `independent_source_admission_verified`, `independent_model_admission_verified`, `fresh_alpha_observation_admitted`, Shadow S1, Fresh Confirmation S2, promotion and live-order authority remain false. Chronology alone cannot turn a structurally captured session into accepted Alpha evidence.

No market acquisition, historical performance evaluation, consumed holdout access, broker action, funds movement or account-permission change is performed by this verifier.
