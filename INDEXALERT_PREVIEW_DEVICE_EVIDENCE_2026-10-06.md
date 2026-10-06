# IndexAlert isolated preview device observation — 2026-10-06

Evidence source: owner-provided handset screenshot after successful ADB installation of the separately packaged `com.indexalert.preview` APK.

Observed UI:
- title: `IndexAlert 4.8 검증`
- separate-app notice displayed
- readiness result displayed: `현재 자동매매를 사용할 수 없습니다.`
- refresh control displayed

Interpretation:
- the isolated preview launched on the handset and rendered the fail-closed unavailable readiness state.
- this is device UI evidence for the isolated GET-only preview only.
- it is NOT production `com.indexalert.app` v4.8 installation/signing continuity evidence.
- it is NOT notification E2E, broker/account provenance, Shadow completion, Early-Live admission, real-order authority, or production promotion evidence.
- existing v4.7 must remain preserved; no conclusion about its private data is drawn from this screenshot.

Authority remains:
- live_ordering_authorized=false
- real_orders_authorized=false
- funds_movement_authorized=false
- broker_permission_change_authorized=false

Frozen research, holdout, execution-sufficiency, source/PIT and promotion criteria are unchanged.
