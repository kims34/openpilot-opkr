# IndexAlert 독립 신규정보 연구 — Work 2026-10-05~06

이 문서는 공개 근거·source feasibility 연구다. 아래 11개 항목은 모두 IDEA 단계이며 실제 PREREGISTERED/RUNNING/EVALUATED trial이나 ACCEPTED_CHALLENGER가 아니다. “조건부 사전등록 후보”는 다음 자료 gate를 통과했을 때 사전등록을 고려한다는 정성적 판정이다. 성과 수치·부호·순위를 확인한 것이 아니다.

## 실제 GitHub 복구 기준

- Repository: kims34/openpilot-opkr; branch: index-alert-research-v1.
- 최신 확인 기준 HEAD: `1edb94a5af5192556d4ae1a137e20565168b6ece`, 2026-10-06T00:42:16Z, “Retain actual final checkpoint Actions counts and exact verified document heads”.
- 최초 2026-10-05 조회 HEAD c490974ff6619bb978dc6f83f9c24f2c46622f85에서 변경된 내용을 실제 재조회했다. 이전 인계·과거 문서의 미사용 holdout 표기는 아래 최신 상태를 덮어쓸 수 없다.
- 아래 11개 문서 전체를 실제 조회하고 main Ledger 전체 및 economics branch Ledger를 중복검사했다. 경제연구 전용 branch index-alert-research-v1-krx-economics-audit는 5aefb98988f7b4ccf7c95e7cdf2a671a7bdfee7e에서 조회했다. 그 branch의 오래된 holdout 문구보다 main의 최신 authoritative continuation을 우선한다.

| Canonical document | 실제 blob SHA |
|---|---|
| [INDEXALERT_MASTER_SPEC.md](https://github.com/kims34/openpilot-opkr/blob/1edb94a5af5192556d4ae1a137e20565168b6ece/INDEXALERT_MASTER_SPEC.md) | `798e658d2b3414f95ce648c58945425d9a579182` |
| [INDEXALERT_RESEARCH_LEDGER.md](https://github.com/kims34/openpilot-opkr/blob/1edb94a5af5192556d4ae1a137e20565168b6ece/INDEXALERT_RESEARCH_LEDGER.md) | `20733a0769ab4aba91ad12546b141658ba2f4c94` |
| [INDEXALERT_RESEARCH_STATUS.md](https://github.com/kims34/openpilot-opkr/blob/1edb94a5af5192556d4ae1a137e20565168b6ece/INDEXALERT_RESEARCH_STATUS.md) | `aed323c62ca57daa7b63d17ad722a4bdcd798ac4` |
| [INDEXALERT_CONTINUITY_SNAPSHOT.md](https://github.com/kims34/openpilot-opkr/blob/1edb94a5af5192556d4ae1a137e20565168b6ece/INDEXALERT_CONTINUITY_SNAPSHOT.md) | `07e0e5ccf5a5e92880bc5f5dc1b87b5b62d9cf28` |
| [INDEXALERT_CONTINUOUS_RESEARCH_CONTRACT.md](https://github.com/kims34/openpilot-opkr/blob/1edb94a5af5192556d4ae1a137e20565168b6ece/INDEXALERT_CONTINUOUS_RESEARCH_CONTRACT.md) | `d50f6726f198a12d29c68b327d0d8afd7583614e` |
| [INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md](https://github.com/kims34/openpilot-opkr/blob/1edb94a5af5192556d4ae1a137e20565168b6ece/INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md) | `32bca0d6a7c4170eb51f853113e702e2f4c3df73` |
| [INDEXALERT_KRX_SOURCE_ACCESS_CONTRACT.md](https://github.com/kims34/openpilot-opkr/blob/1edb94a5af5192556d4ae1a137e20565168b6ece/INDEXALERT_KRX_SOURCE_ACCESS_CONTRACT.md) | `40d8f48ec51d35baf79eb79bb688297e0d0f2f15` |
| [INDEXALERT_KRX_SOURCE_GATE_AUDIT.md](https://github.com/kims34/openpilot-opkr/blob/1edb94a5af5192556d4ae1a137e20565168b6ece/INDEXALERT_KRX_SOURCE_GATE_AUDIT.md) | `67c6951aad6e8e60c011f25f8ac825d3ba71eb54` |
| [INDEXALERT_KRX_STATUS_ECONOMICS_CONTRACT.md](https://github.com/kims34/openpilot-opkr/blob/1edb94a5af5192556d4ae1a137e20565168b6ece/INDEXALERT_KRX_STATUS_ECONOMICS_CONTRACT.md) | `b313fa6ec3cce8c5ed2732df2b19f07e52f705c5` |
| [INDEXALERT_LIVE_EXECUTION_PROVENANCE_CONTRACT.md](https://github.com/kims34/openpilot-opkr/blob/1edb94a5af5192556d4ae1a137e20565168b6ece/INDEXALERT_LIVE_EXECUTION_PROVENANCE_CONTRACT.md) | `6363c289bfe14073db7d761c8c7018ae50882bb3` |
| [INDEXALERT_BROKER_EXECUTION_CONTRACT.md](https://github.com/kims34/openpilot-opkr/blob/1edb94a5af5192556d4ae1a137e20565168b6ece/INDEXALERT_BROKER_EXECUTION_CONTRACT.md) | `9be4dfee0bacc63c2d5b7fde2738607ea2b98caa` |

## 복구된 상태와 안전선

**H5 DEVELOPMENTAL / NOT CURRENTLY PROMOTABLE.** Canonical Ledger의 역사적 개발 결과: 278 entries, 137 trade days, mean NetReturn 약 +1.150%, PF 약 1.546, MDD 약 -24.39%, date-cluster LCB<0, 최근 504 OOS admissions=0, remove-best-5 mean -0.362%/PF0.836. 이 실행에서 재시험한 결과가 아니다. 수정된 60-case CPCV도 robust edge를 확립하지 못했다.

Frozen: H5 Core; anchored 504/126/126; horizon-matched purge/embargo; original Top3 fixed/no-backfill; frozen costs; CPCV60; one-shot 원칙과 결과 후 cutoff/model/threshold/subtype 변경 금지. H10 rejected/do-not-retune 및 H20 archive를 부활시키지 않는다.

**Holdout: CONSUMED_FAILED_INVALID_V1_HOLDOUT.** 최신 canonical 메타데이터에는 cutoff 2026-09-25, consumed window 2026-09-28..10-01, passed=false가 기록돼 있다. ResultSHA 30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82; manifestSHA ff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907; receiptSHA 3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63. Manifest/result discrepancy와 immutable lineage 585d763542b2fbbdc3f928621f679fb14c8c3bbf 보존. reset/reseal/delete/relabel/re-evaluate/retune/private-outcome rescue 금지. 이 실행은 공개 canonical 상태 메타데이터만 읽었고 private holdout outcome bundle은 접근/파싱하지 않았다. 새로운 holdout을 자동으로 승인하지 않는다.

**KRX/source:** acquisition completion은 source admission 또는 realized economics가 아니다. Seed27/27, identity binding145/145, per-security14296/14296, cleanup context27/27 완료 이력이 있어도 full scope/PIT/integrity admission 및 exact affected-position fill/recovery cashflows는 미확립. 공개 source-gate audit의 status A/B/E PARTIAL, C/D BLOCKED, F PASS는 개인/내부 연구 범위만; investor D PARTIAL. F PASS를 외부 재배포권으로 해석하지 않는다. Source gate6 PASS도 별도 performance testing/promotion 권한이 아니다. feature_performance_testing_authorized=false 유지.

**Execution:** Execution Evidence Contract는 SHADOW/PAPER/genuine LIVE를 분리한다. LIVE 문자열·CSV hash·caller boolean·synthetic rows로 native provenance를 증명할 수 없다. 독립 broker-native row traceability와 frozen metric gates 모두 필요하다. 600 genuine observations/200 decision dates/400 fills, 고정 participation0.0005와 near-capacity120 등 기준을 변경하지 않는다. Native account/day/whole-account/ownership, 실제 fees/settlement evidence와 immutable registration/admission chronology는 OPEN. Genuine LIVE 검증 없음, empirical execution blocker OPEN, real-account ordering MASTER_OFF/disabled.

Continuous Research Contract의 prereg timestamp syntax/JSON type hardening 및 CI 성공은 independent prereg-before-outcomes receipt나 empirical acceptance가 아니다. IDEA 연구를 계속할 수 있지만 Core/holdout/orders authority는 없다.

## 공통 연구·평가 경계

아래 expected effect는 mechanism 가설이며 한국 H5 NetEV/PF/MDD/ES95/99 개선의 측정치가 아니다. 공식 schema/원문 페이지 확인과 데이터 전체 확보·PIT admission을 구분한다. 원자료 bulk network acquisition·증권별 수익률 결합·가상 fill 생성은 하지 않았다.

Veto 연구는 원래 Top3를 줄이는 방식이므로 최근 Core admissions=0인 상태의 신규 수익기회를 만들 수 없다. NO_TRADE를 숨기거나 rank4+로 채우지 않는다. 향후 허가된 시험에서 surviving trades의 PF만 보고 채택하지 않고 동일 결정날짜 전체 정책의 비용차감 portfolio 차이, abstention/coverage, date-cluster uncertainty, MDD/ES95/99, recent stability, capacity 및 선행 episode 정보 조건부 effect를 함께 평가해야 한다. 현재 승인되지 않은 추가 평가 기준·수치 threshold를 임의로 발명하지 않는다.

시험이 별도로 허가되면 immutable 독립 사전등록 → PIT/leakage validation → frozen costs → anchored Walk-Forward → Purged validation → CPCV60 순서. 필요조건이 없는 후보는 시험하지 않는다. 본 문서를 immutable trial receipt로 내세우지 않는다.

## 이번 실행의 11개 평가

### REGISTERED-LOCKUP-EXPIRY-H5-01 — 의무보유등록 해제

1. **아이디어/가설:** 공개된 의무보유등록 해제 일정이 H5 보유기간에 걸릴 때 잠재적 유통물량 증가를 반영한다. 실제 매도를 가정하지 않는다.

2. **기존 연구와 독립성·중복성:** 실제 담보 반대매매·내부자 매도와 다른, 사전 예정된 매도 가능 상태 전환. 신규상장/증자에서 파생하면 해당 financing episode와 연결한다.

3. **공식·학술·시장 근거:** KSD 작성 월별 해제 예정 보도자료에는 날짜·종목·수량 및 제외범위가 있다. Field & Hanka(2001)는 미국 IPO lockup 관련 가격·거래량 반응을 보고한다. 한국 H5의 비용차감 효과를 입증하지 않는다. [S1,S2]

4. **PIT availability:** 월별 최초 공개자료의 available_at 이후 결정에서만 예정일 사용. 공시 전 계산된 예상일은 공식 공개와 동일시하지 않는다.

5. **Look-ahead/leakage:** 실제 해제 결과·실제 매도량·최종 보유량을 사전 신호에 넣지 않는다. 자료 기준일과 배포일, 정정본을 구분한다.

6. **Historical data 현실성:** 공개 보도자료와 증권별 보유등록 원문 수집 경로 후보가 있다. 전체 2015년 이후 자료·시각·상장폐지 포함 coverage는 검증되지 않았다.

7. **H5 연결:** 공개 시점에 이미 알려진 해제일이 고정 H5에 겹치는지 확인하는 후보다. 신규상장 H5 적격성부터 확인한다.

8. **NetEV/PF 개선 mechanism:** 공급압력 구간의 불리한 진입 회피 가설. 매도 가능성과 실제 매도는 다르며 이미 가격반영됐을 수 있다. 개선량은 미측정.

9. **MDD·ES95/99:** 급락 회피 가능성만 가설. 갭 발생 후 veto면 보호하지 못하며 정상 수익거래 제외로 MDD가 악화될 수도 있다. ES95/99 미측정.

10. **Date-cluster uncertainty:** 같은 월별 발표와 해제일에 여러 종목이 묶인다. 종목 수를 독립 표본 수로 세지 않는다.

11. **Recent-period stability:** IPO/보호예수 구조·시장흡수능력의 변화 때문에 미국 과거 효과를 현재 한국으로 옮길 수 없다.

12. **Coverage/capacity:** 전체 시장 해제 수량은 Core overlap이 아니다. 적격 보통주, 원래 Top3, 실제 유동성·고정 capacity를 별도 확인해야 한다.

13. **Core 대비 incremental effect:** 원래 정책 대비 동일 날짜의 정책 차이를 평가할 미래 후보. veto만으로 최근 0 admissions를 늘릴 수 없고 backfill은 금지.

14. **Event family/episode:** 등록→공개된 해제 예정→실제 해제→실제 매도를 한 episode로 연결. 후속 매도는 이전 해제 정보 조건부 marginal transition.

15. **최종 판정·다음 gate:** 조건부 사전등록 후보. 다음 gate: 최초 발표 vintage·security lineage·정정 이력·Core 적격 coverage의 수익률 없는 source audit.

### OFFICIAL-INDEX-DELETION-H5-01 — 공식 지수 편출

1. **아이디어/가설:** 공식 발표된 지수 편출의 시행일까지 고정 H5가 걸칠 때 패시브 재조정 매도 위험을 검토한다. 예상 편출은 제외.

2. **기존 연구와 독립성·중복성:** ESG/DJSI 평가나 실현 투자자 flow와 구별되는 기계적 수요 변경. 부실·상장폐지 때문에 편출되면 기존 부실 family 조건부다.

3. **공식·학술·시장 근거:** MSCI 공식 리뷰 안내는 발표·시행시점이 다름을 확인한다. Greenwood & Sammon(2025)의 Disappearing Index Effect는 과거 효과가 약화됐다는 반증도 제공한다. [S3,S4]

4. **PIT availability:** 정확한 삭제 종목 목록이 실제 공개된 시점 이후에만 사용. 일정 공개만으로 구성종목 정보가 공개됐다고 간주하지 않는다.

5. **Look-ahead/leakage:** 유료 고객 사전 접근, 비공개 목록, 사후 구성종목 DB를 공공 최초 발표시각으로 소급하지 않는다. 최초 파일 hash와 정정 이력 필요.

6. **Historical data 현실성:** 공식 발표 archive 후보는 있지만 public list 전기간 completeness와 이용권리는 미검증. MSCI와 KRX 지수 source 계약은 별개다.

7. **H5 연결:** 정기 리뷰의 발표→시행 동안 H5와 겹치는 노출만 후보. 반등 BUY나 기간 최적화는 이번 연구 범위에 넣지 않는다.

8. **NetEV/PF 개선 mechanism:** 강제 패시브 수요 감소에 따른 불리한 진입 회피. 차익거래 선반영·시행 후 반등으로 순효과가 반대일 수 있다. 미측정.

9. **MDD·ES95/99:** 시행일 거래집중과 갭 tail을 피할 가능성. 여러 종목 동시 제외·기회손실 때문에 MDD/ES 개선을 보장하지 않는다.

10. **Date-cluster uncertainty:** 리뷰 발표와 시행 날짜가 공통 cluster. 한 리뷰의 다수 편출을 독립 사건으로 세지 않는다.

11. **Recent-period stability:** 최근 index effect 약화 문헌 때문에 고우선으로 올리지 않는다. 현대 한국 표본의 독립 recent evidence가 필요하다.

12. **Coverage/capacity:** 편출 종목과 original Top3 overlap은 미확인. 시행일 종가 auction 체결을 보장하지 않으며 frozen execution/capacity 유지.

13. **Core 대비 incremental effect:** Core 모델 정보와 비교하는 별도 후보. 추가 veto는 최근 거래 부재를 해결하지 못한다. surviving trades PF만으로 채택하지 않는다.

14. **Event family/episode:** 정기 mechanical deletion은 구별하되 listing/규제/부실 원인 편출은 그 episode에 연결; 편출 단계의 신규정보만 조건부 평가.

15. **최종 판정·다음 gate:** 조건부 사전등록 후보. 다음 gate: 공개 constituent archive·실제 available_at·이용권리·원인 분류 audit. 문헌 반증을 사전등록에 포함.

### TREASURY-ONMARKET-DISPOSAL-H5-01 — 장내 자기주식 처분

1. **아이디어/가설:** 발행사가 새로 공개한 보통주 자기주식 장내 매도 계획의 기간이 H5와 겹치는 공급위험 가설.

2. **기존 연구와 독립성·중복성:** 자사주 매입·소각, 대주주 매도, 신주 SEO와 구별된다. 기업 보유 기존 주식의 시장 재유입이다. 기존 자사주 family의 방향 반전만으로 성과를 추론하지 않는다.

3. **공식·학술·시장 근거:** OpenDART 자기주식 처분 결정 API는 2015년 이후 정보, 접수번호, 처분기간·목적, 장내/시간외/장외/기타 방법을 구분한다. FSC 공시 개선 자료는 regime 변화의 근거다. [S5,S6]

4. **PIT availability:** dp_dd는 의사결정일이지 시장 이용가능 시각이 아니다. 최초 공시 실제 공개시각 이후에만 사용하고 정확한 rcept_no version을 보존.

5. **Look-ahead/leakage:** 정정공시가 원공시를 덮어쓰지 않도록 한다. 사후 처분결과·최종 수량으로 최초 결정을 바꾸지 않는다.

6. **Historical data 현실성:** 11개 후보 중 공식 구조화 schema 확보 현실성이 비교적 높다. API 실제 전체 자료·최초 timestamp·rights·보통주 연결 admission은 수행하지 않았다.

7. **H5 연결:** dp_m_mkt의 양수 여부는 거래방식 분류이며 성과 최적화 threshold가 아니다. 임직원 지급·장외 전략투자·시간외 block은 다른 구조로 사전 제외.

8. **NetEV/PF 개선 mechanism:** 추가 장내 공급과 issuer 정보신호로 불리한 진입을 회피할 수 있다는 가설. 유동성 확보 목적이 긍정적이거나 매도가 실행되지 않을 수도 있다.

9. **MDD·ES95/99:** 공급압력 tail 회피 가능성은 있으나 대규모 distress와 중복되기 쉽다. 고정 비용 적용 후 MDD/ES95/99 미측정.

10. **Date-cluster uncertainty:** 동일 issuer의 반복·정정·결과공시는 같은 처분 episode. 자사주 제도변경 시 공통 날짜 shock도 고려.

11. **Recent-period stability:** 2025/26 공시제도 변화 때문에 과거와 현재의 발견확률·설명내용이 다를 수 있다. 유리한 regime subset만 고를 수 없다.

12. **Coverage/capacity:** 공시가 많아도 순수 보통주 장내매도·Core original Top3 overlap은 미확인. 실제 매도물량이나 체결 capacity를 계획수량으로 대체하지 않는다.

13. **Core 대비 incremental effect:** 기존 financing/유동성 위험정보를 조건으로 추가 의사결정 가치만 평가할 미래 후보. size/purpose subset의 결과 후 탐색 금지.

14. **Event family/episode:** 발행사 자사주 처분 episode를 연결하고 financing distress 중복은 별도로 표시. 결정→정정→실행→종료를 여러 Alpha로 계산하지 않는다.

15. **최종 판정·다음 gate:** 조건부 사전등록 후보. 다음 gate: 원문·정정 version/PIT/처분방법 분류 audit와 source admission. 아직 실제 PREREGISTERED trial이 아니다.

### EXPORT-RELEASE-PIT-EXPOSURE-H5-01 — 수출 잠정발표 × 사전 사업노출

1. **아이디어/가설:** 공식 1~20일 잠정 수출 발표를 이미 공개된 사업별 수출노출과 연결해 별도의 fundamental context 가능성을 검토.

2. **기존 연구와 독립성·중복성:** FOMC/TOM·미국 지수/환율 price context와 다른 실물수요 정보. peer/sector 공통변수와 겹치는 marginal 정보가 실제 존재해야 한다.

3. **공식·학술·시장 근거:** 관세청의 공식 잠정 수출입 발표는 대상기간과 발표일을 구분한다. 이것은 issuer 실현 매출이나 H5 return 근거가 아니다. [S7]

4. **PIT availability:** 측정기간 마지막 날이 아니라 최초 공개 available_at 이후 사용. 회사 노출은 그 시점 이전의 공시만 허용.

5. **Look-ahead/leakage:** 최종 수정 통계·사후 업종재분류·미래 사업보고서로 노출을 덮어쓰지 않는다. 컨센서스 surprise가 없으면 임의 기대값을 만들지 않는다.

6. **Historical data 현실성:** 공식 보도자료 archive 후보는 현실적이나 전기간 초기 vintage와 정확한 시각 및 HS→issuer mapping은 미검증.

7. **H5 연결:** H5 mean/context challenger 가능성은 veto보다 넓지만, 실제 단기 수요정보와 독립성을 입증하지 못해 보류.

8. **NetEV/PF 개선 mechanism:** 기존 price context에 없는 수요 방향 정보로 rank/NetEV 예측을 개선할 가설. 환율·상품가격·수출금액의 혼합으로 부호도 불명.

9. **MDD·ES95/99:** 분산시장 shock를 포착할 가능성과 수출 호조에 고점 진입하는 위험이 공존. MDD/ES 개선 미측정.

10. **Date-cluster uncertainty:** 발표일 cluster가 유효표본 단위. 노출 issuer 수를 독립 관측치로 부풀리지 않는다.

11. **Recent-period stability:** 수출구성·결제통화·공장 해외이전으로 노출이 변한다. recent mapping 및 발표 빈도 안정성 미확인.

12. **Coverage/capacity:** 기업별 물량·수익성을 국가 총계로 대체할 수 없다. issuer mapping 미확인인 종목은 미지원으로 처리.

13. **Core 대비 incremental effect:** sector/FX/기존 peer 정보를 조건으로 더해지는 부분만 후보. 기존 Core를 바꾸거나 q25를 완화하지 않는다.

14. **Event family/episode:** 한 관세청 발표를 공통 macro episode로 묶는다. 뒤의 earnings 공시는 발표 때 알려진 정보를 조건으로 새 정보만 평가.

15. **최종 판정·다음 gate:** HOLD. 다음 gate: 초도 vintage·사전 issuer exposure의 검증 가능한 공개 mapping. 수익률 계산 없이 먼저 feasibility 확인.

### NXT-VENUE-FRAGMENTATION-H5-01 — NXT 거래시장 분산

1. **아이디어/가설:** 거래시장·세션별 유동성 분산이 동일 KRX 결정·실행 정책에 주는 execution risk를 검토.

2. **기존 연구와 독립성·중복성:** 새 시장구조지만 단순 spread/유동성 feature면 기존 execution family에 속한다. 자동으로 독립 Alpha로 인정하지 않는다.

3. **공식·학술·시장 근거:** FSC 공식 자료는 NXT와 KRX의 시간·주문·최선집행 구조 차이를 설명하고 2025년 출범을 확인한다. 이는 체결 개선 성과가 아니다. [S8]

4. **PIT availability:** 양 venue quote·session·broker route의 실제 동시 available_at 필요. 종가나 통합 사후 feed로 decision-time 체결가능성을 역산하지 않는다.

5. **Look-ahead/leakage:** NXT 개장 전 거래를 frozen KRX regular-open 대신 쓰거나 사후 최적 venue를 고르는 것은 금지.

6. **Historical data 현실성:** 2025년 이전 NXT history는 존재할 수 없다. 전기간 2015년 학습 feature로 부적절하며 현재 route/quote history admission도 없다.

7. **H5 연결:** H5 수익정보보다는 실행비용·불충분 quote fail-closed 문제. frozen market/session·fill rule 변경 authority 없음.

8. **NetEV/PF 개선 mechanism:** 실제로 불리한 route/체결을 피하면 비용차감 economics에 영향 가능. 최적 체결이 보장되거나 개선됐다고 가정하지 않는다.

9. **MDD·ES95/99:** thin session slippage tail 축소 가설은 broker-native route 증거 필요. MDD/ES 개선 수치 없음.

10. **Date-cluster uncertainty:** 출범·대상종목 확대일의 공통 cluster와 제도 transition 때문에 독립 날짜 수가 짧다.

11. **Recent-period stability:** 출범 이후 짧고 구조가 계속 변해 recent 안정성을 입증하지 못했다.

12. **Coverage/capacity:** 보통주 대상범위·양시장 depth·route별 수수료·actual fills 필요. 미상은 zero spread 또는 fill로 대체하지 않는다.

13. **Core 대비 incremental effect:** 현재 비용 모델 대비 실제 추가 비용정보의 marginal 가치부터 확인. Core 변경을 승인하지 않고 execution evidence backlog에 둔다.

14. **Event family/episode:** 시장구조/실행 family로 관리. 같은 broker routing의 후속 장애를 별도 Alpha로 세지 않는다.

15. **최종 판정·다음 gate:** HOLD. 다음 gate: 공식 route contract·동시 quote archive·genuine broker-native provenance. 이번 실행에서는 broker API 접근 없음.

### VOLUNTARY-ERROR-RESTATEMENT-H5-01 — 발행사 자발적 오류 정정

1. **아이디어/가설:** 감독기관 확정 전 발행사가 처음 공개한 중요한 전기 오류 정정이 정보신뢰도를 바꾸는지 검토.

2. **기존 연구와 독립성·중복성:** regulator-confirmed fraud와 공개상태는 다르지만 accounting-information episode의 선행 transition이다. 독립 Alpha 추가는 부적절.

3. **공식·학술·시장 근거:** IAS 8은 중요한 전기 오류와 회계추정/정책 변경을 구분한다. 회계처리 원칙은 주가나 fraud 확정 증거가 아니다. [S9]

4. **PIT availability:** 최초 issuer 공시 공개시각만 사용. 오류 해당 회계연도로 공개일을 소급하지 않는다.

5. **Look-ahead/leakage:** restated 비교숫자가 과거 feature/label history를 덮어쓰면 leakage. 최초/정정 vintage를 유지해야 한다.

6. **Historical data 현실성:** 원공시·정정공시 archive 후보는 있으나 오류/추정/정책 판별과 완전한 timestamp history를 미확인.

7. **H5 연결:** H5에서 신뢰도 shock가 가능하나 이미 알려진 감사·ICFR·going-concern 정보 조건부가 필요.

8. **NetEV/PF 개선 mechanism:** 불리한 회계정보 회피 또는 불확실성 해소라는 반대 mechanism 모두 가능. 긍정/부정 부호를 가정하지 않는다.

9. **MDD·ES95/99:** 부정적 tail은 기존 accounting family가 포착할 수 있으며 중복 제거 뒤 추가 tail 효과는 불명.

10. **Date-cluster uncertainty:** 동일 issuer 정정 series는 한 episode. regulator 후속 확정·제재를 독립 표본으로 세지 않는다.

11. **Recent-period stability:** 공시 taxonomy·XBRL version 변화 및 발견확률 때문에 recent 비교가 어렵다.

12. **Coverage/capacity:** 중요한 오류의 판별과 original Top3 overlap을 확인하지 않았다. generic correction은 범위가 너무 넓다.

13. **Core 대비 incremental effect:** 동일 episode 선행 정보가 무엇이었는지를 조건으로 전환의 incremental 정보를 평가하는 state 기록만 적절.

14. **Event family/episode:** issuer 최초 정정→감사/조사→공식 fraud 확정→강제조치로 연결. 단순 오류를 fraud veto로 재분류하지 않는다.

15. **최종 판정·다음 gate:** 기존 family 흡수. 다음 gate: accounting episode taxonomy에 원문/vintage 상태전환을 연결; 별도 Alpha 시험 없음.

### INDUSTRIAL-POWER-TARIFF-H5-01 — 산업용 전기요금 × 사전 노출

1. **아이디어/가설:** 공식 산업용 전기요금 변경이 사전 공개된 실제 전력사용·요금종별 issuer 비용에 주는 정보 가설.

2. **기존 연구와 독립성·중복성:** 화재·정전 생산능력 상실이나 규제 영업정지와 다른 marginal input cost. generic sector return 패턴 반복은 제외.

3. **공식·학술·시장 근거:** 2024-10-23 정부/KEPCO 공식 자료는 다음날 적용되는 산업용 요금 조정을 설명한다. 한국 H5 성과는 입증하지 않는다. [S10]

4. **PIT availability:** 실제 발표시각 이후와 발표 이전 issuer 노출 자료만 사용. 적용일을 최초 정보시각으로 대체하지 않는다.

5. **Look-ahead/leakage:** 사후 전력비·실제 제조원가, 미래 공장사용량, 미검증 surprise 추정은 금지.

6. **Historical data 현실성:** 정책 발표는 공개돼 있지만 issuer kWh·실제 계약 종별·헤지/전가능력의 전기간 PIT mapping은 현실성이 낮다.

7. **H5 연결:** 비용충격은 존재 가능하나 현금흐름 반영기간이 H5보다 길 수 있다. 공기업/공급자와 사용기업의 방향이 다르다.

8. **NetEV/PF 개선 mechanism:** 가격 전가가 어려운 노출기업 진입 회피 가설. 발표 선반영·계약 차이로 부호 미확정.

9. **MDD·ES95/99:** 공통 비용shock tail 완화 가능성만 가설. 희소 사건으로 ES95/99 독립 추정이 어렵다.

10. **Date-cluster uncertainty:** 전국 단위 몇 개 요금 발표일 cluster. 수백 기업 노출이 표본 수를 늘리지 않는다.

11. **Recent-period stability:** 정책/에너지 위기 regime와 전가능력 변화로 recent 안정성 미확인.

12. **Coverage/capacity:** 업종명을 실제 요금계약이나 전력비 비중으로 대체할 수 없다. 미상 노출을 zero로 넣지 않는다.

13. **Core 대비 incremental effect:** 기존 원자재/환율/sector 정보를 조건으로 실제 추가 surprise가 있어야 한다. Core fixed 유지.

14. **Event family/episode:** 한 요금발표가 macro cost episode. 이후 수익성 공시는 선행 요금정보를 조건으로 새 정보만 평가.

15. **최종 판정·다음 gate:** HOLD. 다음 gate: 사전 공개된 계약종별·사용량 exposure와 초도 발표 archive. 전기업종 universal SELL 금지.

### TYPHOON-FORECAST-FACILITY-EXPOSURE-H5-01 — 태풍 예보 × 공개 생산시설

1. **아이디어/가설:** 실제 피해 전의 공식 태풍 예보 vintage와 사전에 공개된 생산시설 위치를 결합한 위험정보 가설.

2. **기존 연구와 독립성·중복성:** exogenous physical production shock는 피해가 발생한 상태, 이 후보는 피해 전 예측이다. transition은 구별되나 같은 태풍 episode에 조건부.

3. **공식·학술·시장 근거:** 기상청 archive는 발표/예측시각을 구분한다. SF Fed Pricing Poseidon은 시설노출·극단기상 불확실성의 금융반응을 연구하며 한국 H5 BUY/veto를 입증하지 않는다. [S11,S12]

4. **PIT availability:** 공식 forecast가 공개된 시각 이후만 사용하고 당시 알 수 있던 시설 주소·가동상태를 결합.

5. **Look-ahead/leakage:** 사후 best-track·실제 침수경로·미래 공장목록은 금지. 본사를 공장으로, 예보 반경을 피해확률로 대체하지 않는다.

6. **Historical data 현실성:** 공식 과거 forecast 조회 가능성은 확인했으나 전체 vintage를 다운받거나 admission하지 않았다. 시설 capacity/geocode history가 특히 어렵다.

7. **H5 연결:** H5에 겹치는 예정 경로 exposure를 조건부 위험으로 보는 후보이며 damage event 이후 정보를 앞당기지 않는다.

8. **NetEV/PF 개선 mechanism:** 시설위험 불확실성으로 불리한 진입을 회피할 가설. 미발생 피해와 공급가격 상승 수혜기업 때문에 부호를 일괄 지정할 수 없다.

9. **MDD·ES95/99:** 큰 물리피해 tail 보호 가설은 있으나 예보 오경보의 기회손실·coverage 감소도 크다. ES95/99 미측정.

10. **Date-cluster uncertainty:** 태풍 ID와 예보/결정 날짜 모두 연결. 예보 수정마다 독립 Alpha나 태풍별 기업 수만큼 독립표본을 만들지 않는다.

11. **Recent-period stability:** 기상모델·기후·시설방재와 유동성 구조 변화, 연간 희소성으로 recent 안정성 부족.

12. **Coverage/capacity:** 공개 공장 geocode와 중요 생산능력 mapping이 미검증. 정상 quote가 있어도 actual production exposure는 미상.

13. **Core 대비 incremental effect:** 기존 physical-shock family를 조건으로 피해 전 정보의 marginal 가치를 별도 확인할 후보. H5 Core 수정 없음.

14. **Event family/episode:** 태풍 예보→경로수정→실제 물리피해→생산중단→복구를 같은 episode로 연결. 각 transition 신규정보만 허용.

15. **최종 판정·다음 gate:** HOLD. 다음 gate: forecast original vintage·사전 facility geocode/capacity의 실제 검증. best-track 기반 가상 backtest 금지.

### PUBLIC-ANALYST-DOWNGRADE-H5-01 — 공개 애널리스트 투자의견 하향

1. **아이디어/가설:** 발행 증권사 원문에서 처음 공개된 equity recommendation 하향의 새로운 정보 가능성을 검토.

2. **기존 연구와 독립성·중복성:** credit rating/watch와 다른 equity analyst 정보지만 earnings/guidance/공시 echo면 독립성이 없다.

3. **공식·학술·시장 근거:** Womack(1996)는 미국 추천변경 반응을 연구한다. 국내 증권사 공개 research 목록은 제공 경로 후보이나 원문 작성일이 최초 dissemination 시각은 아니다. [S13,S14]

4. **PIT availability:** 일반 공개/기관 선배포를 구분하고 실제 first_public_available_at을 확인해야 한다.

5. **Look-ahead/leakage:** PDF 작성일·현재 링크·사후 재발행 시각을 최초 공개로 소급하지 않는다. 종료 분석가·폐업기관 누락도 위험.

6. **Historical data 현실성:** 현재 공개 보고서는 있지만 전기간 recommendation change·원문 version·정확한 시각·이용권리 확보는 미검증.

7. **H5 연결:** 오래된 미국 수개월 drift는 한국 현대 H5와 다르다. 즉시반응 후 next eligible open에서는 정보가 소진될 수 있다.

8. **NetEV/PF 개선 mechanism:** 새로운 독립 분석정보로 불리한 진입 회피 가설. 공시 echo이면 marginal value가 없고 reverse causality도 가능.

9. **MDD·ES95/99:** negative recommendation tail 회피는 가능 가설이지만 이미 하락 후 등급변경과 긍정적 반등을 제외할 위험.

10. **Date-cluster uncertainty:** 동일 실적발표에 대한 여러 분석가 변경은 한 underlying episode. 동일일 종목·보고서를 독립 표본으로 세지 않는다.

11. **Recent-period stability:** 공개배포 방식·coverage selection·등급 inflation·기관 선배포 변화로 recent stability 미확인.

12. **Coverage/capacity:** 대형주 coverage 편중과 recommendation taxonomy 차이. analyst 없어도 zero downgrade로 간주하지 않는다.

13. **Core 대비 incremental effect:** 기존 earnings/guidance/price 정보를 조건으로 original research만 추가 가치 후보. target-price/분석가 subgroup 최적화 금지.

14. **Event family/episode:** 공식 사건→분석가 해석은 동일 episode일 수 있다. 공통정보 echo를 새 Alpha로 추가하지 않는다.

15. **최종 판정·다음 gate:** HOLD. 다음 gate: 발행사 original-public timestamp·version·coverage·rights와 독립정보 분류 audit.

### DECLARED-CASH-DIVIDEND-WITHDRAWAL-H5-01 — 이미 발표한 현금배당 철회

1. **아이디어/가설:** 명시적으로 발표된 현금배당을 공식 철회/지급누락하는 최초 공시만 검토한다. 배당기대 미충족·ex-date 가격조정은 제외.

2. **기존 연구와 독립성·중복성:** generic guidance·자사주·TOM과 구별되지만 liquidity distress에 연결된다. 법적 지급의무 실제 불이행이면 FIRST-CASH-DEFAULT family에 흡수.

3. **공식·학술·시장 근거:** Michaely/Thaler/Womack(1995)는 미국 배당 개시/생략 반응을 연구하지만 이미 발표된 한국 배당 철회의 증거가 아니다. KIND 공시는 결의와 주총 승인 상태 구분 필요를 보여준다. [S15,S16]

4. **PIT availability:** 원래 배당발표와 실제 철회 공시의 두 공개 vintage를 연결. 지급일 침묵만으로 공개 이벤트를 만들지 않는다.

5. **Look-ahead/leakage:** 연말 dividend history의 zero를 과거 철회 공시로 소급하지 않는다. 주총 승인 전 조건부 계획과 확정채무를 구분.

6. **Historical data 현실성:** 검색에서 무관한 주총안건 철회도 나왔으며 실제 한국 배당철회 사례 census를 검증하지 못했다. 빈도·full history를 추정하지 않는다.

7. **H5 연결:** 단기 신뢰도/현금상황 정보 가능성은 있으나 타당한 actual-event sample 자체가 미확인.

8. **NetEV/PF 개선 mechanism:** 배당신뢰도 상실은 부정적, 현금보존·부채감소는 긍정적일 수 있다. 비용차감 부호와 크기 모두 미확정.

9. **MDD·ES95/99:** distress tail 회피 가능성은 기존 cash-default 정보 조건부. 희소표본으로 MDD/ES 독립 효과 불명.

10. **Date-cluster uncertainty:** issuer 배당 episode 단위 및 공시일 cluster. 계획·철회·지급불이행을 독립 사건으로 세지 않는다.

11. **Recent-period stability:** 배당 기준일·공시 관행 변화로 taxonomy stability 불명. 역사적 omission 문헌은 최근 한국 근거가 아니다.

12. **Coverage/capacity:** 보통주 original Top3 overlap과 실제 사건 빈도 미확인. 배당 omitted 회사 수로 fabricated sample을 만들지 않는다.

13. **Core 대비 incremental effect:** 배당발표/유동성/going-concern 정보 대비 철회 transition의 추가정보만 평가할 후보.

14. **Event family/episode:** 선언→주총조건/승인→철회→실제 지급불이행을 같은 episode로 연결. 실제 지급의무 불이행은 상위 cash-default family.

15. **최종 판정·다음 gate:** HOLD. 다음 gate: 실제 원공시-철회공시 쌍과 법적 상태를 확인하는 수익률 없는 event census. 사례가 없으면 시험하지 않는다.

### FIRST-PUBLIC-COVENANT-BREACH-NO-CASH-DEFAULT-H5-01 — 현금 default 전 최초 공개 재무약정 위반

1. **아이디어/가설:** 실제 이자/원금 지급불이행이 없는 상태에서 issuer가 처음 공개한 실제 financial covenant 위반과 채권자 권리변화를 조사했다. 위반 가능성·순수 유동부채 재분류는 이벤트가 아니다.

2. **기존 연구와 독립성·중복성:** cash default/회생/워크아웃과 법적·정보 상태는 다르다. 그러나 같은 financing distress episode의 선행 transition이며 going-concern/credit watch보다 추가정보가 있어야 한다. 전체 두 Ledger에서 covenant/재무약정 연구항목은 찾지 못했다.

3. **공식·학술·시장 근거:** IFRS 공식 IAS1 covenant 개정 설명은 조기상환 위험에 관한 공시정보를 구분한다. Nini/Smith/Sufi(2012)의 논문 공개초록은 payment default 밖의 creditor control뿐 아니라 위반 이후 기업성과·주가 개선도 보고한다. 단순 negative veto의 반증이며 한국 H5 효과가 아니다. [S17,S18]

4. **PIT availability:** 실제 최초 공시 available_at에 이미 알려진 위반·면제·재협상 상태를 함께 기록. 회계기간 말의 위반일은 시장 공개시각이 아니다.

5. **Look-ahead/leakage:** 사후 waiver·기한이익상실·추후 현금 default를 최초 위반 신호에 소급하지 않는다. 수정된 재무비율로 예전 covenant breach를 역산하지 않는다.

6. **Historical data 현실성:** 공시 footnote 경로는 있지만 전기간 한국 상장 보통주 실제 위반 원문 census/PIT pair는 검증하지 못했다. 검색의 비상장기업 보도·가정사례·generic 약정은 실제 적격 event로 세지 않았다.

7. **H5 연결:** H5 내 financing constraint 신호 가능성이 있지만 연차보고서 공개 때에는 위반과 면제가 이미 오래됐을 수 있다.

8. **NetEV/PF 개선 mechanism:** 조기상환 권리·추가 제약은 부정적, creditor discipline/면제·재협상은 긍정적일 수 있다. signed NetEV/PF 개선을 선언하지 않는다.

9. **MDD·ES95/99:** 급격한 refinancing tail 위험 가능성은 기존 부실 정보 조건부. 포괄 veto는 개선기업까지 제외할 수 있어 MDD/ES95/99 순효과 미상.

10. **Date-cluster uncertainty:** 동일 issuer/loan의 반복 covenant test와 정정공시는 같은 episode. 분기보고서 공시일 및 lender 공통 shock cluster도 연결한다.

11. **Recent-period stability:** IFRS covenant 공시 개정이 2024년 이후 적용돼 과거와 최근 발견가능성 비교가 어렵다. 한국 적용범위·원문 completeness는 별도 확인.

12. **Coverage/capacity:** 원문 중 loan 주체가 issuer·연결자회사·최대주주 SPC인지 식별 필요. 비상장 borrower 보도를 상장 issuer exposure로 자동 이전하지 않는다. Core overlap 미측정.

13. **Core 대비 incremental effect:** 기존 going-concern/financing/credit state 대비 최초 공개 약정위반의 추가정보만 미래 평가 대상. 수익률 확인 후 ratio/waiver subtype 최적화 금지.

14. **Event family/episode:** 약정 준수→위반→waiver/재협상 또는 실제 acceleration→cash default→workout/회생. 알려진 상태를 조건으로 marginal transition만 관리; default 이후 위반 재서술은 상위 family 흡수.

15. **최종 판정·다음 gate:** HOLD. 다음 gate: 실제 상장 issuer 원문·최초 공개시각·waiver 현재상태와 loan identity를 수익률 없이 검증. generic covenant-risk disclosure를 성능시험하지 않는다.

## 전체 판정표

| 아이디어 | 독립성 | PIT 가능성 | 데이터 현실성 | H5 적합성 | 예상효과 | 주요위험 | 판정 | 다음 gate |
|---|---|---|---|---|---|---|---|---|
| 의무보유등록 해제 | 별도 supply transition | 공개 일정 이후 | archive 미검증 | 조건부 | 공급압력 회피 가설 | 실제 매도 아님 | 조건부 사전등록 후보 | 초도자료·identity audit |
| 공식 지수 편출 | 기계적 수요; 부실원인 중복 | 공식 목록 공개 이후 | public history/rights 미검증 | 조건부 | passive 매도 회피 가설 | 효과 약화·동시 cluster | 조건부 사전등록 후보 | 목록·공개시각 audit |
| 장내 자기주식 처분 | issuer supply; 자사주와 연결 | 원공시 공개 이후 | 공식 API schema 확인 | 조건부 | 장내 공급 위험 회피 | 계획≠실행·정정 leakage | 조건부 사전등록 후보 | 처분방법·version audit |
| 수출발표×사업노출 | 실물수요; sector 중복 | 초도발표+기존 exposure | 기업 mapping 어려움 | 미확인 | 새 수요정보 예측 가설 | 개정치·공통일·부호 | HOLD | vintage·노출 mapping |
| NXT 시장 분산 | execution family 연계 | 동시 quote/route 필요 | 2025 이전 없음 | 실행문제 | 불리한 체결비용 회피 | genuine route 증거 부재 | HOLD | venue archive·native 증거 |
| 자발적 오류 정정 | 회계 episode 선행단계 | 최초 정정 공시 | 원문·version 필요 | 별도Alpha 부적절 | 신뢰도 변화; 부호 미정 | fraud와 중복·과거 덮어쓰기 | 기존 family 흡수 | 회계 state taxonomy |
| 전기요금×노출 | 별도 input cost | 발표+사전 계약노출 | issuer 계약/사용량 어려움 | 약함 | 추가 비용정보 가설 | 희소공통일·전가·선반영 | HOLD | 실제 사전 exposure |
| 태풍예보×시설 | 피해전 transition | 초도예보+기존 시설 | forecast/시설 이력 필요 | 조건부 | 피해전 위험정보 가설 | best-track leakage·오경보 | HOLD | forecast·facility audit |
| 공개 투자의견 하향 | equity 정보; 공시 echo 위험 | 최초 public 배포시각 | 전기간/rights 어려움 | 미확인 | 새 분석정보 가설 | 선배포·동일정보 중복 | HOLD | 시각·권리·독립정보 |
| 발표된 배당 철회 | default 이전 transition | 원발표/철회 pair | 실제 사례 census 미확인 | 약함 | 신뢰도/현금정보 가설 | 현금보존 반대효과·희소 | HOLD | 원공시 pair·상태 audit |
| 최초 재무약정 위반 | default 전 financing transition | 최초공시+waiver 상태 | 적격 원문 census 미확인 | 조건부 | 새 채권자 권리정보 가설 | 공시지연·면제·반대효과 | HOLD | 원문·waiver·loan identity |

조건부 사전등록 후보3, HOLD7, 기존 family 흡수1. 고우선 사전등록 후보·검증된 유망 Alpha·accepted challenger는 없음. 장내 자기주식 처분은 공식 구조화 schema가 있어 source audit 착수 현실성이 상대적으로 높다는 뜻이지 투자효과가 우월하다는 뜻이 아니다.

## 기존 인계 연구의 보존과 반복 방지

사용자가 이번 Work 진입 시 전달한 기존 연구결과는 GitHub empirical trial admission으로 간주하지 않는다. 현재 확인한 두 Ledger에서 아래 최근 인계 ID들은 찾지 못했으므로, **사용자 인계에 의한 기존 조사 이력 / 신규조사 금지**로 보존한다. 효과를 재확인하거나 후보를 승격한 것이 아니다.

인계상 조건부/고우선 후보군: `CLINICAL-FUTILITY-SAFETY-STOP-VETO-H5-01`, `EXOGENOUS-PRODUCTION-SHOCK-VETO-H5-01`, `ISSUER-SELF-REHABILITATION-FILING-VETO-H5-01`, `FIRST-CASH-DEFAULT-VETO-H5-01`, `COURT-ORDERED-ASSET-FREEZE-VETO-H5-01`, `REGULATOR-CONFIRMED-ACCOUNTING-FRAUD-VETO-H5-01`, `CREDITOR-BANKRUPTCY-PETITION-VETO-H5-01`, `REGULATORY-CORE-BUSINESS-LOSS-VETO-H5-01`, `PUBLIC-PROCUREMENT-DEBARMENT-VETO-H5-01`, `ACTUAL-CONTROLLING-SHAREHOLDER-FORCED-LIQUIDATION-H5-01`, `AUDIT-REPORT-DELAY-VETO-H5-01`.

인계상 HOLD/조건부 및 상위 family 흡수 가능군: `LICENSE-OUT-TERMINATION-VETO-H5-01`, `REGULATORY-PRODUCT-APPROVAL-REVOCATION-VETO-H5-01`, `ENFORCEMENT-RAID-VETO-H5-01`, `CONTROL-TRANSFER-FAILURE-H5-01`, `PATENT-SALES-INJUNCTION-VETO-H5-01`, `CREDITOR-WORKOUT-ENTRY-H5-01`, `COUNTERPARTY/MAJOR-CUSTOMER-INSOLVENCY-CONTAGION`, `CB-EARLY-REPAYMENT-DEFAULT`, `FORMAL-DISHONOUR`. CB early repayment default와 formal dishonour는 FIRST-CASH-DEFAULT 상위 family 연결.

사용자가 제시한 기존 대표 후보(reversal, peer, TOM/FOMC, 52W-high, earnings-attention, buyback, CB/refixing, SEO/rights, supply contract, audit/going-concern, credit watch/rating, short selling, activism, KRX alerts, production suspension, patent/M&A/split, cyber/strike/recall/sanctions/ESG/guidance/ICFR/CEO/NPS/divestiture/shareholder change/insider sale/option/pledge 등)와 전체 Ledger의 완료·기각 연구를 기존 이력으로 취급했다. 신규 ID 문자열 부재만으로 경제적 독립성을 인정하지 않았으며 각각 위 항목2/14에서 중복을 판정했다.

인계상 기각/별도 Alpha 금지: generic voluntary clinical stop; large supply-contract BUY; generic production suspension/patent invalidation/labor-dispute stop; treasury-share cancellation BUY; sudden CEO departure; default amount threshold optimization/repeated default; accounting-fraud follow-up penalty; serious industrial accident independent family; founder arrest warrant; bankruptcy petition dismissal BUY; listing eligibility independent veto; regulatory stay BUY; generic business suspension; regulatory-loss×listing-review; forced liquidation size optimization; extreme rating downgrade independent feature; workout termination BUY; generic recall; clean audit after delay BUY; generic audit delay/duration optimization. 이 실행에서 반복 성능연구하지 않았다.

## 확인한 공개 근거

학술 자료는 확인 가능한 초록/공개 본문 범위만 사용했다. 다른 나라·장기 horizon 논문을 한국 H5 성과로 번역하지 않았다. S1은 KSD 원저자 자료의 미러본이며 정식 archive/권리/PIT admission을 대체하지 않는다. S14는 publisher 공개목록 존재만 확인하며 최초 배포시각과 이용권리는 OPEN. S16은 배당 철회 사례가 아니다.

- [S1] [KSD 작성 의무보유등록 해제 예정 자료(미러 PDF)](https://files-scs.pstatic.net/2026/05/03/tMgU3stgzf/20260430_%EB%B3%B4%EB%8F%84%EC%9E%90%EB%A3%8C_2026%EB%85%84%2B5%EC%9B%94%2B%EC%A4%91%2B56%EA%B0%9C%EC%82%AC%2B2%EC%96%B5%2B242%EB%A7%8C%EC%A3%BC%2B%EC%9D%98%EB%AC%B4%EB%B3%B4%EC%9C%A0%EB%93%B1%EB%A1%9D%2B%ED%95%B4%EC%A0%9C%2B%EC%98%88%EC%A0%95.pdf)
- [S2] [Field & Hanka(2001), Expiration of IPO Share Lockups](https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00334)
- [S3] [MSCI May2025 official review announcement](https://app2.msci.com/webapp/index_ann/DocGet?format=html&lang=en&pub_key=dPl%2BamlyUQA%3D)
- [S4] [Greenwood & Sammon(2025), Disappearing Index Effect](https://onlinelibrary.wiley.com/doi/10.1111/jofi.13410)
- [S5] [OpenDART 자기주식 처분 결정 API 공식 schema](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS005&apiId=2020039)
- [S6] [FSC 자기주식 공시 관련 자료(2025-12-23)](https://www.fsc.go.kr/no010101/85932)
- [S7] [관세청 공식 1~20일 잠정 수출입 발표](https://www.customs.go.kr/kcs/na/ntt/selectNttInfo.do?bbsId=1362&mi=2891&nttSn=10177443&nttSnUrl=b76927b3d643e2a959deed83783dc1b8)
- [S8] [FSC 대체거래소·최선집행 공식 자료](https://www.fsc.go.kr/po010106/83953)
- [S9] [IFRS IAS8 공식 기준 설명](https://www.ifrs.org/issued-standards/list-of-standards/ias-8-basis-of-preparation-of-financial-statements/)
- [S10] [정부/KEPCO 산업용 전기요금 발표](https://www.korea.kr/news/policyNewsView.do?newsId=148935391)
- [S11] [기상청 태풍 예보 archive](https://data.kma.go.kr/data/typhoonData/typInfoTYList.do?pgmNo=689)
- [S12] [SF Fed, Pricing Poseidon](https://www.frbsf.org/research-and-insights/publications/working-papers/2023/09/pricing-poseidon-extreme-weather-uncertainty-and-firm-return-dynamics/)
- [S13] [Womack(1996), Investment Recommendations](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1996.tb05205.x)
- [S14] [미래에셋증권 발행 research 공개 목록](https://securities.miraeasset.com/bbs/board/message/list.do?categoryId=1521&curPage=4&direction=1&listType=1&searchEndDay=01&searchEndMonth=01&searchEndYear=2026&searchStartDay=01&searchStartMonth=01&searchStartYear=2025&searchType=2&startId=zzzzz~&startPage=1)
- [S15] [Michaely/Thaler/Womack(1995), Dividend Initiations and Omissions](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1995.tb04796.x)
- [S16] [KIND 실제 보고서: 배당 결의/승인 상태 구분용, 철회 확정사례 아님](https://kind.krx.co.kr/external/2026/06/01/001444/20260601002355/11011.htm)

- [S17] [IFRS 공식 non-current liabilities with covenants 개정 설명](https://www.ifrs.org/news-and-events/news/2022/10/iasb-amends-accounting-standard-to-improve-information-about-long-term-debt-with-covenants/)
- [S18] [Nini/Smith/Sufi(2012), 저자 소속 대학의 논문 기록·초록](https://researchdiscovery.drexel.edu/esploro/outputs/journalArticle/Creditor-Control-Rights-Corporate-Governance-and/991021873115004721)

## 이번 Work 실행 여부

| 항목 | 실제 실행 |
|---|---|
| Core 변경 | 하지 않음 |
| 코드 변경 | 하지 않음 |
| Frozen 기준 변경 | 하지 않음 |
| Feature 성능시험/백테스트 | 하지 않음 |
| Sealed holdout private outcomes 접근 | 하지 않음; canonical 공개 상태 메타데이터만 확인 |
| Genuine LIVE 수집/검증 | 하지 않음 |
| Real-account ordering 활성화/주문 | 하지 않음 |
| KRX bulk collection/worker 재실행 | 하지 않음 |
| 새 성과·fill/recovery economics 생성 | 하지 않음 |
| 연구 문서 | 이 IDEA 연구기록 작성; source recovery와 근거·판정만 기록 |

이 기록은 완료된 프로젝트나 거래승인을 선언하지 않는다. 다음 연구의 첫 gate는 성능시험이 아니라 각 후보의 실제 원자료/vintage/독립성/권리 검증이다. 이미 기각된 cutoff/threshold/model/subtype을 결과를 보고 구제하지 않는다.
