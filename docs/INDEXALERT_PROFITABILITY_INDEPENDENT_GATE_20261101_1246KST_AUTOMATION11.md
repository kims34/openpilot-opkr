# IndexAlert 독립 수익성 입장 감사 — 2026-11-01 12:46 KST

**판정: M20 NO-GO / FAIL-CLOSED.** 이 파일은 격리된 문서 전용 기록이다. 원본 승인 전 M20 실행 금지. Frozen/Holdout/Champion/Top3(4순위 대체 없음)/NO_TRADE 유지, ORDERING=false. 주문·자금·권한·배포·PR 병합·Champion 승격·실제 백테스트 실행 없음.

## 독립 읽기전용 증거 (직전 11:51 KST 감사 대비)

- GitHub branch API 직접 조회: 연구 `3b8b7830612a6284d7c7a60628cb527cb741627a`, 개발 `1e6367d2863a86c3470da13d81a955d277eba485`, KRX 전담 `073d2d49e95f69fb10b943b93e51bb179fb3c698`. 세 브랜치 모두 변경 없음.
- PR #414 HEAD `784c559fd4d6faf0bf600fd931a1060dcdccf869` (본 문서 작성 전), #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`, KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. 모두 Draft/open/unmerged. 다른 전담 트랙에 변경 없음.
- GitHub Actions 최신 25개 조회: 마지막 watchdog #41264126871 (2026-11-01 02:11 UTC), SUCCESS. 실제 job #124723240979의 fail-closed 테스트 4건과 연구 거버넌스 31건 PASS, 그러나 `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. 신규 데이터 승인 아님. Chronology Anchor #41091128151 job #124184971844의 /anchor/latest HTTP 404, 후속 validation SKIPPED 유지.
- OpenDART 공식 read-only #38381866190 job #115244084285: 2022 최초 제출 문서의 **로그 기록 SHA-256** `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, ZIP integrity true, 후보 영업이익 행 형태 15건. 원본 ZIP 바이트 자체의 독립 재해시는 이번 감사에서 불가; 업로드 artifact ZIP SHA와 원본 document SHA를 혼동하지 않는다. 최초 연결 3개월 Q3 영업이익, 2021 비교창, 실제 공개 시각, 전체 정정 계보, 과거 발행사/종목 매핑, universe PIT는 모두 승인 false.
- KRX 과거 원본 daily/master 저장 SHA 1,565쌍 무결성은 과거 저장 무결성에 한정. 공식 휴장·원본 공백 미분류 90 세션 및 별도 prospective 2026-09-28 일반주 803건 중 OHLC 비정상 27건 미해결. 종목별 거래정지·상폐·기업행위·시점별 거래가능성 승인 없음. KRX 전담 private volume 재실행·읽기 없음.
- Railway production PIT service 마지막 **반환된** deploy log 2026-10-31 14:46:01 UTC (23:46:01 KST): `status=FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, source/model/chronology independent approvals false, `session_manifest_sha256=null`, `ordering=DISABLED`, live/real orders false. 반환되지 않은 이후 이벤트가 없었다는 증명은 아님.
- Railway Kiwoom REAL read-only service: 배포 SUCCESS, health `running=0, crashed=1` (표시 `online`과 모순), 신규 인증 성공 증거 없음. Production staged 조회는 `describe-environment`/`get-staged-changes`에서 null이나 `environment-status`에서 빈 patch `e113dacb-6705-4416-9997-dc694539d382`를 보고함. 변경 적용 없음.

## 거래 경제성·안전 게이트

원본 바이트 SHA 독립 재현, 최초 공표시각과 정정본 시점 분리, 거래일/종목별 적격성, 거래정지·상장폐지·기업행위, 당시 호가·체결가능 수량·호가단위·부분체결, 수수료·스프레드·슬리피지·시장충격·회전율·세금/과세시점·세후 장부가 입증되지 않음. 따라서 세후 **NetEV/PF/CAGR/MDD/ES95/ES99는 수치 생성이나 승인 불가**. 504/126/126 train/cal/test, purge20, 20-session horizon, 비용 2배 스트레스 및 사전등록 규칙을 보존하되 M20 실행은 차단한다. H5 및 0-N 기존 아카이브를 신규 독립 Holdout 성과로 재사용하지 않는다.

**변경 판단:** 신규 승인, 필수 사용자 승인 요청, 중대한 신규 차단 없음. 읽기전용 감사 및 이 격리 문서 1건 외 동작 없음.

참조: https://github.com/kims34/openpilot-opkr/pull/414 ; https://github.com/kims34/openpilot-opkr/pull/412 ; https://github.com/kims34/openpilot-opkr/pull/420 ; https://github.com/kims34/openpilot-opkr/pull/422 ; https://github.com/kims34/openpilot-opkr/pull/423 ; https://github.com/kims34/openpilot-opkr/actions/runs/41264126871 ; https://github.com/kims34/openpilot-opkr/actions/runs/41091128151 ; https://github.com/kims34/openpilot-opkr/actions/runs/38381866190
