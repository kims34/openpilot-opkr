from monitor import app, send_push

_TEST_SENT = False
_TEST_RESULT = None

@app.get("/internal_fcm_test_once_20260923")
def test_push_once():
    global _TEST_SENT, _TEST_RESULT
    if not _TEST_SENT:
        _TEST_SENT = True
        _TEST_RESULT = send_push(
            "IndexAlert 연결 테스트",
            "서버 푸시 연결이 정상적으로 완료되었습니다.",
            {"type": "connection_test"},
        )
        print(f"TEST_PUSH_RESULT sent={_TEST_RESULT}", flush=True)
    return {"ok": True, "sent": _TEST_RESULT}
