# IndexAlert 로컬 운영 점검 도구

Python 3.12로 실행하는 읽기 전용 도구입니다. 주문 전송·권한 활성화 기능은 없습니다.
실제 계좌 출처, 결제 의미, 전체 자료 범위, 전략/Shadow/LIVE 승인 증빙은 별도로 필요합니다.

압축을 푼 폴더에서 필요한 시간대 자료를 설치합니다. Windows에는 IANA 시간대 자료가 기본 포함되지 않는 경우가 있습니다.

```powershell
python -m pip install -r operator-toolkit-requirements.txt
```

기존 저널을 점검합니다. 없는 저널을 새로 만들지 않으며, 조회 시 재접속 복구를 실행하지 않습니다.

```powershell
python shadow_operational_status.py --journal "C:\IndexAlert\journal.sqlite"
```

원본 결제 스냅샷·페이지와 외부 검토 파일을 합친 입력을 점검합니다.

```powershell
python native_settlement_review_cli.py --input "C:\IndexAlert\review-input.json" --journal "C:\IndexAlert\journal.sqlite"
```

로컬 화면은 다음 명령으로 실행한 뒤 `http://127.0.0.1:8765`에서 확인합니다.
결제 파일이 준비되지 않았다면 `--settlement-input`을 생략할 수 있습니다. 종료는 Ctrl+C입니다.

```powershell
python shadow_operational_dashboard.py --journal "C:\IndexAlert\journal.sqlite" --settlement-input "C:\IndexAlert\review-input.json" --port 8765
```

입력 JSON의 최상위 필드는 `account_fingerprint`, `opening`, `closing`, `history`, `review_manifest`입니다.
`opening`/`closing`은 `body`, `captured_at`을, `history`는 `pages`, `request`, `captured_at`을 담습니다.
각 페이지는 `body`, `request_next_key`, `response_cont_yn`, `response_next_key`를 담습니다.
검토 파일 형식은 `native_cashflow_review_manifest.py`에 명시돼 있습니다. 승인 플래그는 입력할 수 없습니다.
빈 자료·누락된 값을 만들어 검증을 통과시키지 마세요. 파일을 요청 URL로 선택하는 기능은 없습니다.

`toolkit-manifest.json`은 해당 CI의 코드 SHA와 파일별 SHA-256을 기록합니다.
해시 일치는 패키지 파일 대조에만 사용되며, 브로커 출처나 거래 성과를 증명하지 않습니다.
저널·원본 계좌 자료·인증정보는 배포 패키지에 포함하지 않습니다.

자료 점검 명령의 종료 코드 0은 입력 경로의 점검 완료를 뜻합니다. 계좌 승인이나 자동매매 허가를 뜻하지 않습니다.
종료 코드 2는 입력·범위·저널 연결 문제로 점검이 막혔음을 뜻합니다.
