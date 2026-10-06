# Android signing continuity — current decision, 2026-10-07 00:34 KST

This section supersedes the historical 10:55 proposal below. Project INCOMPLETE; no installed-production update or production push continuity is verified.

## Latest owner evidence and scope
The owner ran a recursive USERPROFILE search for *.jks and *.keystore with Get-ChildItem, then Select-Object -ExpandProperty FullName. Three invocations from C:\\Windows\\system32, C:\\Windows and C:\\ returned to the prompt with no displayed path. The command uses the same absolute USERPROFILE scope regardless of working directory; the >> prompt is normal PowerShell continuation. This records no matching file reported within that search scope. ErrorAction SilentlyContinue hides inaccessible-path errors. It does not prove every drive, custom extension, external/cloud backup or original CI signing identity is absent. Do not repeat this completed search or require another handset setup. No key/password was requested, uploaded or read.

Installed com.indexalert.app 4.7/code47 retains verified APK SHA256 9e1b72432b44f41a04c7f502d98502d3c77d69ec451718b8da34a260269eca01 and signer SHA256 ecb7486e3ce65fba42f6bf55ff8359abd0ee7d8268c8305e248340c84443c6fa. Original compatible signing-private-key availability remains unresolved. A public APK/certificate and a new debug key cannot restore that identity. Preserve the installed app and its private preferences/history; no uninstall, clear-data, migration or compatible update was authorized by the search result.

## Completed independent preview
Separate com.indexalert.preview 4.8-preview/code48 was already implemented, CI-built, audited and owner installed/launched; canonical build branch f65f71be88b4675252178a4f2726c13d4a783fed includes the device observation. The title/notices/unavailable display were observed. See INDEXALERT_READONLY_PREVIEW.md and INDEXALERT_PREVIEW_DEVICE_EVIDENCE_2026-10-06.md on index-alert-build for exact dated source/run/artifact evidence.

The isolated module has INTERNET only, allowBackup=false and cleartext=false, no Firebase/WorkManager dependencies, no production registration/receipt/self-test/notification service, and only the existing GET /automation/readiness. That completed isolation path must not be reimplemented. Its UI observation is not a com.indexalert.app 4.8 production upgrade, new-build push evidence, real broker data or order admission. Fresh CI debug APKs do not establish even preview signing continuity.

## Resume and external dependency
Continue independent engineering with GitHub live HEAD/PR/Actions recovery. PR186 feature22d5851bb377cc81532812bb110e36caf4f92604 is now merged as cd9b349ced4958eba478744b680e8074db4c2f28. Both exact feature-head Android Actions jobs passed actual9JUnit cases and APK verification; downloaded verification XML/JSON and preview APK hashes were also checked. See the current INDEXALERT_READONLY_PREVIEW.md on index-alert-build and the latest development Status/Continuity/Handoff. The candidate is not installed; no compatible production signing or new push proof is inferred.

If the owner later volunteers a legitimate original-key backup, verify its public certificate locally before a reviewed compatible update. Never request private-key/password upload. If no original identity is available, replacement/data migration requires a concrete preservation plan and an explicit owner decision; the existing app remains intact. This dependency does not block other development.

Frozen/PIT/holdout burn/promotion criteria remain unchanged; no broker/account request, order, funds movement or production token mutation was performed.

---

# Android signing continuity decision — 2026-10-06 10:55 KST

## Verified inputs
Owner-executed SDK observation: installed com.indexalert.app4.7/code47, APK SHA2569e1b72432b44f41a04c7f502d98502d3c77d69ec451718b8da34a260269eca01, signerSHA256ecb7486e3ce65fba42f6bf55ff8359abd0ee7d8268c8305e248340c84443c6fa. Matches independently audited historical CI artifact. Owner Test-Path of the standard local .android/debug.keystore returned False. This proves absence only at that path, not absence of every possible custom signing identity. No key/password was requested or read.

Build branch actually inspected at aaac565a7dc99f36b369b36cadabaf4e2faf1bf5: index-alert/app/build.gradle.kts uses applicationId com.indexalert.app, version4.8/code48 and Google Services plugin. Manifest allowBackup=true is a configuration flag, NOT tested backup/export/restore evidence. MainActivity stores alert switches, delivered-stage state and history in private state SharedPreferences. Do not claim Android backup or reinstall restores these.

## Reviewable paths
1. Compatible in-place update: requires the original signing private identity, held by its legitimate owner, with public certificate matching the installed fingerprint. Standard local debug file is absent. Known current debug artifacts have different verified fingerprints. No compatible artifact is available from the evidence inspected. A public APK/certificate cannot supply that private key. Do not generate a new random debug key and call it compatible.
2. Separate validation application: proposed independent applicationId, distinct label and separate app data, retaining the installed4.7 unchanged. Not yet implemented/built/install-ready. Must review Firebase/Google Services package registration and notification token/device ownership, prevent duplicate operational alert registrations, and keep existing GET-only unavailable readiness/no orders. Original Firebase application identity must not be silently relabelled as a registered new package. Separate-app UI testing is not a4.8 com.indexalert.app production upgrade or original-device notification continuity.
3. Replacement plus data migration: only after a concrete owner-reviewed export/restore plan and explicit decision accepting installation/data changes. No uninstall/clear-data/backup command is approved or executed. allowBackup=true alone cannot meet migration preservation. Historical preferences/delivery state must not be erased to bypass signing mismatch.

## Exact next development
Inspect initialization/PushBridge and server token ownership contract for feasibility of an isolated, no-production-registration validation flavor. Keep any new preview code off the canonical Android branch until CI and package/config behavior are verified. Do not claim installed4.8, new push receipt or automation readiness. If no evidence-backed isolation path exists, record the actual package/Firebase or data-migration blocker and continue independent research/governance engineering under frozen contracts.

## Safety and continuity
No real orders, funds movement, broker-account permission change, production token mutation, model/threshold/cutoff/promotion changes or private holdout access. All consumed failedv1 hashes and immutable frozen criteria remain unchanged. This is a decision plan, not an accepted research candidate or working release. Owner can disable wireless debugging after inspection; no further handset command is required merely to reconfirm the already matched installed APK.
