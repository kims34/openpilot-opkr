# IndexAlert 수익성 검증 총괄 — 증거 통합 게이트 (2026-10-13 KST)

> **성격:** 기존 증거를 재사용하기 위한 총괄 판정·작업 경계 문서. 신규 전략, 매매 신호, M20 수익률 또는 데이터 승인서가 아니다. 공개 저장소에는 원본 공시·종목별 값·계좌·인증정보를 남기지 않는다.
>
> **핵심 판정:** KRX 원본 저장 무결성 PASS; 과거 시장 거래가능성·공시 시각·M20 전체 PIT 미검증/차단; H5 및 0-N의 아카이브 개발 경제성은 NO-GO; M20 실제 세후 수익성 미실행/미검증. Tiny Live 및 주문 불승인.

## 출처별 최신 검증 증거 (2026-10-13 확인)

| 트랙 | 판정 | 원본 증거 | 남은 차단 요인 |
|---|---|---|---|
| KRX 2017–2022 원본 취득 | **저장 무결성 PASS, 투자 PIT FAIL-CLOSED** | Railway dedicated worker 배포 `16c93d7c-7cd0-4d84-a327-298d2805376c`; 커밋 [1e6367d](https://github.com/kims34/openpilot-opkr/commit/1e6367d2863a86c3470da13d81a955d277eba485), [PR #404](https://github.com/kims34/openpilot-opkr/pull/404). 총 1,565/1,565 평일 일별/마스터 원본 쌍 저장 SHA 확인, 저장 쌍 누락 0. | 휴장/원본공백 90일 분류 미검증; zero-activity OHLC 표본 12,003건 및 기타 invalid 표본 1건은 거래가능 상태로 인정하지 않음. 과거 공식 거래상태, 거래정지·상장폐지, 기업행위, 시점별 시총 및 실체결 불충족. 2026-09-28 27개 의심 종목 진입 금지 유지. |
| OpenDART 2022–2023 최초 Q3 | **PIT/분기 수익 특성 FAIL-CLOSED** | 공인 read-only [Action 38259347729](https://github.com/kims34/openpilot-opkr/actions/runs/38259347729) 및 6개 flags-only artifacts, [PR #409](https://github.com/kims34/openpilot-opkr/pull/409). 원본 XBRL 쌍 5/6, 고정 슬롯5 2022 최초 XBRL 공식 014 FILE_NOT_FOUND, 두 해 원본·현행 비교 모두 일치 3/6, 2022 원본 대 현행 비교 불일치 2건, 관측된 다섯 쌍 모두 2022/23 QName 차이. | 최초 제출 `document.xml` 기반 별도 구조 진단 [PR #411](https://github.com/kims34/openpilot-opkr/pull/411)은 공식 XBRL 사실값 대용 아님. [PR #412](https://github.com/kims34/openpilot-opkr/pull/412), [원본 SGML 실실행 38380988990](https://github.com/kims34/openpilot-opkr/actions/runs/38380988990): 최초 ZIP/1개 SGML 원본, 1,570개 표, 영업이익 후보 행 형태 15개, **정확한 Q3 기간 창 일치 0개, 연결 분기 영업이익 증명 0개**. 후속 read-only [38381866190](https://github.com/kims34/openpilot-opkr/actions/runs/38381866190) 공식 검증은 조회 시 진행 중이라 결과를 통과로 가정하지 않음. 최초공시 재무제표/기간/연결/정정 lineage, 발행시각 available-at, 과거 corp/security mapping, 전체 universe 정식 검증 필요. 원본 부족분을 정정본으로 역채우기 금지. |
| H5/0–N 연구 아카이브 | **현 증거로 승격 NO-GO** | 2026-10-06 고정 연구 [Action 37471348547](https://github.com/kims34/openpilot-opkr/actions/runs/37471348547), [Action 37473983749](https://github.com/kims34/openpilot-opkr/actions/runs/37473983749). [PR #384](https://github.com/kims34/openpilot-opkr/pull/384) H5 278-trade date-LCB/상위 5일 제거 취약성 판정. [PR #410](https://github.com/kims34/openpilot-opkr/pull/410) 5개 개발 대안 재평가 코드(새 백테스트 없음); 0–N 두 아카이브 8,734 / 5,806 trades, 양의 평균 거래수익은 robust Alpha 승인 증거가 아님. | 개별 최대 수익 일자 의존, date cluster bootstrap LCB95 음수, best-five-day 제거 민감성, 극소 자금/호가단위 수용능력, 독립 Holdout은 재사용 불가. 원본 artifact 검증을 유지하되 동일 과거 대안 재실행 금지. |
| M20 원본 사전등록 실험 | **수익성 미검증/실행 금지** | 위 PIT source gates `m20_performance_run_authorized=false`. | DART PIT source/분기연결 수치/중립적인 universe, KRX 역사적 거래·시총·기업행위·체결/비용/세금, 라벨 PIT를 모두 검증하기 전에는 실수익률 생성 금지. |
| 백테스트 최적화 전담 | **오프라인 회귀 동등성 PASS, 실 백테스트 성능 미검증** | [PR #413](https://github.com/kims34/openpilot-opkr/pull/413), [Actions 38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417): 6/6 CI jobs 성공, 34/34 시험 결과 일치, test-phase 실행시간 2.8951초 → 2.7165초 (약 1.066배). | 실제 PIT 통과 수익성 평가에서 wall-clock 이득 아직 미검증. 캐시는 source SHA / observed-at / commit SHA / Frozen protocol 결합, 독립 비용·위험·게이트만 병렬화; 공식 M20 성과 실행/검증과 혼동 금지. |

## 단일 중요 경로

1. **공시 Work**가 원본 Q3 영업이익의 정확한 연결 3개월 시점 수치와 최초 제출 문서/정정/공표시간 관계를 증명한다. 불가능한 슬롯은 자료 부족으로 고정한 뒤 원본 결손이 M20 사전등록 universe 판정을 어떻게 가로막는지 공식적으로 판단한다. 근거 없는 대체 데이터 금지.
2. **KRX Work**가 원본 수집/저장 통과와 거래 가능 상태를 구별하여 공식 시장 달력, 장기 상장상태, 기업행위 및 27건 veto를 해결한다. 단순히 27종목을 제외해 백테스트를 통과시키지 않는다.
3. **최적화 Work**는 동일 입력·동일 결과 수치/지문을 유지하면서 wall-clock 감소를 측정한다. 소스/PIT 게이트 통과 전 수익률 생성 작업을 열지 않는다.
4. **총괄 Work**는 위 결과가 GitHub SHA + 실제 Action/Railway 로그에서 PASS인 경우에만 **사전등록 M20을 단 한 번 본 평가**한다: 20-session horizon, 504/126/126 train/cal/test, purge20, Top3/no rank-4 backfill, NO_TRADE, 사전 고정 비용 및 2x-cost stress. 세금·수수료·슬리피지·체결제약 반영 후 Net EV, Profit Factor, CAGR, MDD, ES95/99, 손실지속기간, 수익 집중도, date-cluster LCB, best-five-day ablation, 종목/연도별 민감도 및 tiny-capital lot feasibility를 함께 판단한다.
5. **불합격 시** 이미 실패한 Holdout을 독립 새 검증으로 재활용하지 않고 비용/체결/데이터/집중도 원인을 판정한다. 사전등록된 *독립적인* Challenger 연구가 필요한지 별도 판단하되 Champion/H5/M20 실험 고정값을 수정하지 않는다.

## 변경 불가 원칙

- 기존 Frozen H5·Champion·M20 사전등록·독립 Holdout 유지. H5와 M20 purge 차이를 혼동하지 않는다(H5=5, M20=20).
- 해당 판단 문서는 권한 부여 아님. `ORDERING=DISABLED` / `KIWOOM_ORDERING_ENABLED=false` 유지; 실주문·자금이동·계좌권한 변경·Champion 승격 불승인.
- 성공한 CI, 파일 다운로드, XBRL ZIP 존재, KRX 1,565쌍 저장 성공은 각각 다른 의미이며 모두 Alpha PASS로 승격할 수 없다.
- 사용자 작업이 꼭 필요한 허가/외부 장애인 경우에만 보고. 루틴 현황 알림 및 중복 과거 수익성 분석 금지.

**총괄 다음 게이트:** 각 Work의 실제 커밋/증거 수집 → PIT/market/source PASS 다중 검증 → 단일 M20 비용차감 WF 판정 → 분리된 독립 승격·실거래 승인.
