# 2026-10-07 22:03 KST material source update

Uploaded original KRX reply contradicts the earlier pasted unrestricted web-automation permission text. See INDEXALERT_KRX_ORIGINAL_MESSAGE_CONFLICT_2026-10-07.md. Preserve prior evidence, but do not initiate/resume broader authenticated Data Marketplace collection relying on that text pending a matching original/reconciliation. Exact approved OpenAPI services remain a separate route; no new source/PIT/economics/live admission. Owner matching-message input is now required.

---

# IndexAlert 전달 기준과 작업 우선순위

기준: 2026-10-07 사용자 지시 “효율적이게 일해 중요한것부터”.
확인한 개발 HEAD: 88402bcad220517de2572e1aff50e3ad207375e4. GitHub 최신 상태를 우선한다.
이 문서는 작업 순서를 바꾸며 Frozen·승격·실매매 기준이나 증거의 권위를 바꾸지 않는다.

## 완료 목표를 구분한다
- 읽기 전용 앱/운영 점검: 기존 앱, 서버와 로컬 점검 도구가 구현·배포/패키지 검증돼 있다. 새 APK의 기존 서명과 기기 검증은 별도 미완료이며, 이미 설치된 v4.7을 v4.8 검증으로 취급하지 않는다.
- 실제 계좌 기반 자동매매: 아래 필수 증빙·연동·승인 조건이 충족돼야 한다. 프로그램 작성이나 CI 성공으로 충족됐다고 하지 않는다.

## 중요한 순서
| 순서 | 필수 결과 | 현재 실제 상태 | 다음 실행 조건 |
|---|---|---|---|
| 1 | 믿을 수 있는 데이터와 비용 반영 전략 검증 | 공식 출처/원본 계약 연결, 과거 가용시각/PIT/종목 상태/실현 경제성 미완료. ACCEPTED successor 없음 | 독립적으로 확인할 수 있는 원본 증빙을 찾아 기존 auditor에 연결. 접근·증거가 없으면 정확한 누락 항목을 기록하고 다른 실행 가능한 필수 작업으로 이동 |
| 2 | 새 시장에서 사전 고정 정책 관찰 | 연구의 IA-FRESH-ALPHA-H5-TOP3-20261007 등록 완료, CONTINUE VALIDATION | 동결 이후 실제로 관측·저장된 의사결정/결과만 검토. 126/504 KRX 세션 checkpoint. 과거 재구성·수치 튜닝 금지. formal Shadow S1/S2나 승격 증거로 대체하지 않음 |
| 3 | 키움 실제 인증·체결·계좌 결제 연결 | 전체 계좌 읽기 전용 baseline COMPLETE. type00 LOGIN은 DEVICE_AUTH805004/8050. 결제/체결 출처 및 독립 승인 미완료 | 소유자가 보류를 해제해 현재 IP 등록·현재 계좌 키로 재검사를 완료했으나8050 재현. 공식 설명은 IP 미등록이며, 소유자가 키움 Q&A 제출 완료를 보고함(2026-10-07 21:55KST). 답변/관련 새 사실 전 동일 검사 반복 금지. 이미 끝난 계좌 조회 재요청 금지. 인증 성공 뒤 read-only LOGIN/REG와 실제 자료를 연결하며, 실주문 없이 가능한 범위를 먼저 진행 |
| 4 | 필수 운영 모듈을 한 흐름으로 검증 | 개별 journal/위험·자금/중단·재시작/읽기 전용 점검 구현·검증. early_live_admission_gate는 독립 승인 adapter 미구현을 명시 | 실제 허용된 입력과 계약이 확보되면 기존 모듈을 연결. 입력 플래그를 독립 승인으로 취급하거나 LIVE sender를 조기 활성화하지 않음 |
| 5 | 작은 금액의 명시 승인 직전 전달 | 현재 ready_for_final_user_authorization=false | 기존 frozen Early-Live gates와 적용 단계가 모두 충족되고 실제 통합 검증 완료 후에만 금액·중단 기준과 함께 별도 실매매 승인을 요청 |

우선순위1~3은 연결된 증거 경로다. 한 경로가 외부 자료나 시간 때문에 막히면 대기 루프를 만들지 않고, 다른 실행 가능한 필수 경로를 진행한다. 실제 새 증거가 생기지 않았는데 같은 데이터를 다시 연구하지 않는다.
현재 H5 reference는 최근504 OOS세션에서 admissions가 없고 date-cluster LCB가 음수라는 연구 Ledger 상태를 유지한다. 이 문서는 새로운 성과 평가나 긍정 후보를 만들어내지 않는다.

## 새 수정의 작업 시작 기준
수정은 다음 중 하나를 구체적으로 충족할 때만 시작한다.
1. 필수 사용 흐름을 막는 재현된 오류를 해결한다.
2. 실제 주문 중복·자금 손실·중단 실패로 연결되는 중요한 재현 오류를 해결한다.
3. 누락된 필수 모듈 연결이나 독립 증거 연결을 완료한다.
4. 사용 가능한 결과물 전달을 막는 패키지/서명/배포 문제를 해결한다.

수정 전에 현재 단계, 막힌 필수 조건, 재현 또는 누락 증거, 완료 판정을 짧게 기록한다.
주요 흐름의 영향이 입증되지 않은 저장소 손상 가정 확장, 추가 UI 꾸미기, 반복 정상 테스트와 같은 작업은 후순위다. 이 지시는 이미 입증된 치명적 위험을 무시하라는 의미가 아니다.
PR309~312의 완료된 회귀·CI를 새 변경/실패 없이 반복하지 않는다. PR 수, 테스트 수, 연구 수를 완성률로 사용하지 않는다.

## 보고와 종료 기준
진행 보고는 사용 가능성에 무엇이 달라졌는지, 필수 조건 중 무엇이 완료됐는지, 실제 남은 외부 입력이 무엇인지로 설명한다.
소유자 조치가 실제로 필요할 때만 필요한 행동·이유·영향을 짧게 알린다. 인증/서명 등 이미 완료한 요청을 반복하지 않는다. 최신 소유자 가용성·보류 해제 지시를 우선한다.
실행 가능한 필수 작업이 끝났고 남은 항목이 외부 증거·관찰 시간·소유자 조치뿐이면, 그 사실을 명시하고 “수정할 일을 찾는” 개발을 계속하지 않는다. 백그라운드 무제한 작업을 약속하지 않는다.

MASTER_OFF / real_orders_authorized=false / funds_movement=false / broker_permission_change=false 유지.
Frozen H5/504-126-126/PIT/라벨/WF/Purged-CPCV/비용/체결/NetEV/위험·승격 기준과 소비된 실패-invalid v1 holdout은 변경·재실행하지 않는다.
