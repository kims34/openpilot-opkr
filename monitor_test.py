from monitor import app, init_db, init_firebase, send_push

init_db()
init_firebase()
sent = send_push(
    "IndexAlert 연결 테스트",
    "서버 푸시 연결이 정상적으로 완료되었습니다.",
    {"type": "connection_test"},
)
print(f"TEST_PUSH_RESULT sent={sent}", flush=True)
