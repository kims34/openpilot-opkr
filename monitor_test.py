import os
from fastapi import HTTPException
from monitor import app, send_push

_TEST_SENT = False
_TEST_RESULT = None

@app.get("/test_push/{key}")
def test_push(key: str):
    global _TEST_SENT, _TEST_RESULT
    expected = os.getenv("TEST_PUSH_KEY", "")
    if not expected or key != expected:
        raise HTTPException(status_code=404, detail="not found")
    if not _TEST_SENT:
        _TEST_SENT = True
        _TEST_RESULT = send_push(
            "IndexAlert 연결 테스트",
            "서버 푸시 연결이 정상적으로 완료되었습니다.",
            {"type": "connection_test"},
        )
        print(f"TEST_PUSH_RESULT sent={_TEST_RESULT}", flush=True)
    return {"ok": True, "sent": _TEST_RESULT}
