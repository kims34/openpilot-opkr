# IndexAlert 1개월 예측 사전기록·사후채점 운영 확인 — 2026-11-16

**목표:** 기존 Android 앱의 SPY/QQQ 향후 21거래일 ±10% 도달확률을 변경하지 않고 실제 발행 시점별로 고정 저장한 뒤, 향후 21거래일의 일중 고가/저가로 자동 채점.

## 현재 상태: 운영 배포 완료

- Railway 기존 `indexalert-backend` 서비스에 **코드 4개 변경** (신규 `monthly_prospective.py`, 기존 `next_day_probability_v33.py` 관찰 호출, `production_v31.py` 집계 조회 API, `Dockerfile` 신규 파일 포함).
- 원래 앱 주소 `https://indexalert-runtime-production.up.railway.app` 유지.
- Railway 배포 고정 커밋: `ce672855390d5f1ff62090e3dbe3837f7c38bbb6` (연구 코드와 독립).
- 배포 `8ecd41af-fe2e-4601-8237-65e2f4277792` `SUCCESS`, 서버 `Online`, 1개 컨테이너 가동, 기존 /data 볼륨 유지.
- 본 기능은 기존 1개월 확률값을 수정하지 않고, SQLite 테이블 `monthly_prospective_v1`에 `INSERT OR IGNORE`로 첫 예측만 고정 저장함.
- 기존 자동 확률 갱신 경로를 통해 새 예측을 저장·만기 결과를 확인하며, 서버가 중단되지 않고 데이터 제공처가 정상 동작해야 함. 외부 데이터 장애나 날짜 누락 시 결과를 추측해 기록하지 않음.
- 최소 21개 **완료된** 미래 거래일 및 엄격한 OHLC 검증을 통과한 경우만 +10%/-10% 장중 터치 이벤트를 별도 채점. 공급업체 사후 수정과 분할·소급조정 시 보류하여 잘못된 실적 산출을 차단함.
- 공개 조회 API: `GET /monthly-prospective-scores` (aggregate only, 원본 계좌나 토큰 노출하지 않음).
- 알림, 자동 주문, 자금이동, FCM 권한, 기존 주가 계산 로직 변경 없음.

## 테스트 근거

- [월간 예측 append-only·시간선/일중 OHLC 11개 테스트 통과](https://github.com/kims34/openpilot-opkr/actions/runs/43824429850)
- [기존 ASGI 서버와 경로 호환성, 1개월 모델 6개 회귀 테스트 통과](https://github.com/kims34/openpilot-opkr/actions/runs/43824621511)
- [Railway 실제 원격 API 확인](https://github.com/kims34/openpilot-opkr/actions/runs/43824995574): `/health` 200/OK, `/status` 200/5개 항목, `/monthly-prospective-scores` 200/JSON 출력 및 주문 기능 False.

## 실제 예측 저장 상태 (2026-11-16 07:36 UTC)

| 지수 | 저장된 발행확률 | 아직 결과 대기 | 채점완료 | 저장된 최초 날짜 |
|---|---:|---:|---:|---|
| SPY | 1 | 1 | 0 | 2026-11-13 |
| QQQ | 1 | 1 | 0 | 2026-11-13 |

21거래일 결과가 아직 완성되지 않았으므로 **prospective Brier 숫자는 아직 없음**. 0건 채점은 오류가 아니다. 차후 새로운 날짜의 실제 발행 예측이 계속 축적되면 Brier와 당시의 장기 기본 도달빈도를 동시 채점할 수 있다. 독립적 검증은 그보다 훨씬 더 많은 기간과 이벤트가 필요하다.

## 연구와 서비스의 분리

- [연도별 기존 앱 코드 직접비교 연구](https://github.com/kims34/openpilot-opkr/blob/indexalert-monthly-expanded-20261116/INDEXALERT_MONTHLY_DIRECT_COMPARISON_20261116.md)
- 과거 가격 재실행은 **retrospective**, 이 기록은 첫 출력 시점부터 고정 저장하는 **prospective** 자료. 둘은 혼동하지 않는다.
- 옵션 IV 기반 새 예측모델을 서비스에 승격하지 않았으며, 기존 1개월 예측은 그대로 사용한다.
