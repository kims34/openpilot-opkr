# IndexAlert installed APK update verification

## Actual build evidence, 2026-10-06 KST

Android v4.8/code48 adds a GET-only unavailable automation readiness display. It does not implement or enable orders, account access or persisted automation controls. PR46 and PR47 compiled/built successfully. Canonical build Actions37376946309 on f772ce57d8ef9fd313797559b9d0a37aa417f7c0 independently verified four actual JUnit cases with zero failures/errors/skips, APK package/version/digests and SDK signatures.

Its unsigned release APK SHA256 is f8e3c9e32355355ea412a0a4a55ddd8db9afff41ea9f6399ed617ceec6370e4b. Source artifact11372392458 is IndexAlert-v4.8-unsigned-release from that exact run. Unsigned means it is not install-ready; do not invent a signature or label it signed.

PR48 Actions37377380596/job111989964638 downloaded the exact immutable historical and candidate debug artifacts, verified their source metadata and actual SDK APK signatures. Both packages are com.indexalert.app, but certificates differ:

- Audited v4.7 artifact11158994269/run36856589300/head5154ef7943353791f615622394523ecd52ef8b0f: actual APK SHA2569e1b72432b44f41a04c7f502d98502d3c77d69ec451718b8da34a260269eca01; signerSHA256ecb7486e3ce65fba42f6bf55ff8359abd0ee7d8268c8305e248340c84443c6fa.
- v4.8 PR47 artifact11371148102/run37376198533/head9b39efcb7977dfa77c54f3274d17a90469cdd194: actual APK SHA2566ae4cc5f6ca503461396c9ca69dd19866d5f3077375b923a41162b9a543e7855; signerSHA25624d1f8adf0b2ed7ad2d47c2f7d957105ce8297fa76b6620d908549c22286ad23.
- Canonical v4.8 run37376946309 debug signerSHA25696c9cfd617adeca8003ba60db7d5dcbe0e5792add2a3cb7112e5d22ed6cb09a7 is also different. Per-run debug keys are not a stable release signing identity.

The old audit's Debug SHA2560aec298a0d0276f8a5e40dc22429b595e8bb11636f22ceeea75cb018a4a7e411 matches the GitHub artifact ZIP archive digest, not the contained APK digest. Preserve the original record and use the explicit archive/APK distinction above.

This establishes artifact-level mismatch only. It does not prove which signer is installed on the user's handset. Existing v4.7 physical E2E evidence remains historical; it does not establish v4.8 device notification/readiness E2E. No installation, uninstall, app-data migration, signing-key access or broker request occurred.

## Prepared read-only handset inspection

Use Python3 and Android SDK platform/build tools on a computer already authorized by its owner to read one USB-connected physical handset. This development environment has no attached handset and cannot perform that step. Do not change device/account permissions silently or ask for signing-key/password uploads.

First inspect the installed public APK without downloading or signing any candidate. This requires no private signing key and does not change the app:

```sh
python verify_indexalert_installed_apk.py --adb /path/to/adb --aapt2 /path/to/aapt2 --apksigner /path/to/apksigner
```

This emits installed public version/hash/certificate metadata only. candidate=null, candidate_signer_comparison_performed=false and installed_signing_continuity_verified=false remain explicit; exit0 means inspection succeeded, not that an update is compatible. Keep the current app/data. After a candidate has been signed locally with an existing independently verified signing identity, the owner can separately compare:

```sh
python verify_indexalert_installed_apk.py candidate-signed.apk --adb /path/to/adb --aapt2 /path/to/aapt2 --apksigner /path/to/apksigner
```

The tool performs only adb -d get-state, pm path com.indexalert.app and pull of that app's public base APK into a temporary directory. It verifies both actual APK identities/signatures with SDK tools, emits only public version/hash/certificate metadata, and deletes the temporary public APK copy. It never reads app data, device IDs, credentials, account/broker state or private signing keys, and never installs or uninstalls anything. Multiple/unauthorized devices, ambiguous base paths, wrong package, unsigned APK or tool errors fail closed. With a candidate, exit0 means the two inspected APKs have matching signers; exit1 is a signer mismatch; exit2 is unverified. Without a candidate, exit0 means installed-only inspection succeeded and provides no update/signing-continuity authority. Matching signers alone is not general install permission or physical E2E proof; version/update compatibility remains separately reviewable.

If the installed signer differs, retain the current app/data. A compatible signed release requires the corresponding existing signing identity; a new random debug key cannot supply it. If that key is unavailable, app/data migration needs the user's concrete decision and a separate reviewable plan. No uninstall workaround is authorized by this guide.

## Evidence boundary and continuation

Tests use synthetic public-APK bytes and mocked tool responses only. They establish inspection/no-mutation behavior, not a handset observation. Record any future actual inspection with exact signed APK hash/source and public certificate fingerprints, without serials, credentials or key material. After a legitimately compatible installation, re-run the existing exact-device/exact-build real receipt verifier for4.8-48 and separately observe the unavailable readiness UI. Do not manufacture a push ACK, reuse4.7 evidence as4.8, or change statistical/source/PIT/holdout/trading gates. Real stock orders, funds movement and broker-account permission changes require separate explicit authority and remain disabled.
