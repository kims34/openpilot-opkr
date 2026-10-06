# Latest readiness transport verification — 2026-10-07 00:42 KST

PR186 feature22d5851bb377cc81532812bb110e36caf4f92604 merged as cd9b349ced4958eba478744b680e8074db4c2f28 on index-alert-build. The original readiness GET inherited automatic redirects. The connection now disables them, retaining only configured GET /automation/readiness, UNKNOWN for non200, existing8192-character cap and5000ms connect/read timeouts. It exposes no new endpoint, controls, account access or orders. Production and preview copies are byte-identical.

Exact feature-head preview CI37488276397/job112353949952 SUCCESS: actual4authority-contract+5transport JUnit cases, no failures/errors/skips; actual isolated APK, metadata/merged manifest/permissions/noFirebase/noWorkManager/signature verified. Production-module CI37488276454/job112353942785 SUCCESS: same9JUnit cases; actual debug and unsigned release APK/package/signing verified. Both workflows now require the five named transport cases, not merely a total count. Local workflow YAML/embedded Python syntax and byte equality checks passed; no local Android compilation was claimed.

Downloaded preview-verification artifact11424935000 ZIPsha256f373f1bf186881fbc8c76be0a98098b377bb4f788229f1abade28a313a9d0d03 and production-module verification11424467394 ZIPsha2565c1e165a01f371627ad3e944641c461600749db844b71fd52293d3a19579b1d4 were independently checked against actual XML test cases and exact feature head. Downloaded preview APK artifact11424715831 ZIPsha256e0168b20335627d88dc691305ebbe9d066b4183d1d34be45a8286c69cbdb607a contains actual APKsha256b5df1da0b221b5785d401178af03e4b77af126c335ec9312e1f144f73a93bd81,820653bytes, matching verification JSON. CI apksigner verified preview certificate43d3af27b7b002d498ad5f61cd985532fb440e12be2d0ff7430082a5c179f9d3. The production debug CI signer5c46f2f6f0022efd02c9b33f4cbcf2cee49e370976557d565de6f74c100b6552 differs from installed4.7.

These are fresh CI candidates; they have not been owner installed and do not establish signing continuity, new production push/device E2E or empirical KRX/LIVE/Alpha evidence. The owner observation below remains tied to its older dated APK, not this new one. Do not reinstall merely to repeat that already completed UI observation. Preserve installed com.indexalert.app4.7 and data. No real order, broker request, funds movement, production token or Frozen/PIT/holdout gate change.

Merge-push exact code HEADcd9b349ced4958eba478744b680e8074db4c2f28 Actions37489030714/job112356536839(preview) and37489030742/job112356536289(app) both SUCCESS. Their actual verification JSON confirms9JUnit cases at that merge head. This is a second checkout/build of the same implementation, not independent empirical evidence. Development Status/Continuity/Handoff on index-alert-position-regen-fix-v1 hold the authoritative cross-branch resume checkpoint.

---

# Isolated Android readiness preview

This separate application uses com.indexalert.preview4.8-preview/code48 and the label IndexAlert 검증. It does not update com.indexalert.app or migrate its data. Its only network operation is the existing4.8 GET /automation/readiness contract. It contains no Firebase, registration/receipt/self-test sender, notifications, workers, broker requests, trading controls or data-sharing permissions. It cannot validate production notification E2E or original-package4.8 signing continuity.

The readiness implementation and four contract tests are exact copies of the canonical app files. CI checks byte equality before compilation, runs actual preview JUnit tests, builds a real debug APK and verifies package/version/signature, merged manifest permissions/components and absence of Firebase/WorkManager dependencies. Any source drift fails CI. Canonical app build stays explicitly scoped to :app tasks.

Debug signing is for isolated verification only. No stable release signing identity or future preview update continuity is claimed. Owner installed4.7 APK/hash/signer evidence and standard local debug-key absence are recorded in the development branch. Keep the existing app and private data. No APK installation, uninstall or data migration is performed by CI.

## Actual isolated preview build proof — 2026-10-06

PR53 merged to index-alert-build as 52377357c0c5260673fc823be3e8a0451abbea72. Workflow run 37402266619 completed successfully for source head 06e23a33def235fa7505d30fe1443267e13eb847.

Verified artifact:
- applicationId: com.indexalert.preview
- versionName/versionCode: 4.8-preview / 48
- APK SHA-256: c46bf10dc036bfaff5ab0b7d00938a66081cedac4ef2c20ce72d7bfa5e38564f
- size: 820613 bytes
- signer certificate SHA-256: 52083f68874f93989f232571fd811bb5b2e45f685a3980c33dcca02b89605bf4
- signature_verified: true
- unit tests: 4 passed, 0 failures/errors/skips
- readiness source byte-identical to canonical app: true
- permissions: android.permission.INTERNET only
- Firebase dependency: absent
- WorkManager dependency: absent
- production app updated: false
- broker request/order/live authority: false

The downloaded workflow artifact was independently hashed after extraction and matched the recorded APK SHA-256 exactly.

## Owner device observation — 2026-10-06

The owner reported ADB installation of the isolated package succeeded after removing only a pre-existing signer-incompatible com.indexalert.preview package. The production com.indexalert.app v4.7 package was not removed or updated. The owner then supplied a handset screenshot showing the isolated UI title "IndexAlert 4.8 검증", the explicit separate-app/no-notification/no-auto-trading notice, and the GET-derived unavailable state "현재 자동매매를 사용할 수 없습니다."

This establishes only that the isolated preview launched on the owner's handset and rendered the fail-closed unavailable readiness state. It is not production com.indexalert.app v4.8 installation proof, signing continuity, notification E2E, broker/account provenance, Shadow completion, Alpha admission, execution sufficiency, or real-order authority.

Original frozen gates and consumed failed holdout remain unchanged.
