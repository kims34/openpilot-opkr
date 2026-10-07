# Prospective GitHub chronology anchor — 2026-10-08

Status: HASH-ONLY EXTERNAL TIME-ANCHOR INFRASTRUCTURE — NOT YET INDEPENDENT CHRONOLOGY ADMISSION.

A Railway/local file timestamp is controlled by the same execution environment that creates the decision, so it is not strong independent evidence that a decision existed before its later H5 outcome. The project now has a dedicated GitHub evidence branch, `index-alert-prospective-anchors-v1`, for a second-system time anchor.

The workflow accepts only the session, the private decision timestamp claim, and SHA-256 identities for the source receipt, input snapshot, freeze-anchor producer binding, model bundle, decision capture and final structural session manifest. It writes no symbol, ranking, score, selected candidate, account data, broker data or market outcome.

For each session, `prospective_anchors/YYYY-MM-DD.json` is append-only: an identical retry is a no-op and any differing same-session payload fails. GitHub's eventual commit metadata can therefore be fetched independently and compared with the private decision record. The preregistered operational anchor window is no earlier than the declared decision and no later than six hours afterward; this is a chronology/data-integrity bound, not a performance threshold.

The anchor record itself keeps `independent_chronology_admission_verified=false`. A later trusted adapter must fetch the actual GitHub commit SHA/timestamp, verify the record is present in that commit, bind its hashes back to the private session manifest and decision capture, and only then may the chronology gate be considered for admission. No local boolean or copied commit timestamp may self-promote it.

This workflow is not automatically dispatched by the production runtime yet. No actual future session is anchored by creating this code alone, and no Alpha/Shadow/LIVE evidence count changes.
