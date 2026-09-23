from monitor import app, send_push

@app.on_event("startup")
def send_one_connection_test_push():
    sent = send_push(
        "IndexAlert 연결 테스트",
        "서버 푸시 연결이 정상적으로 완료되었습니다.",
        {"type": "connection_test"},
    )
    print(f"TEST_PUSH_RESULT sent={sent}", flush=True)
