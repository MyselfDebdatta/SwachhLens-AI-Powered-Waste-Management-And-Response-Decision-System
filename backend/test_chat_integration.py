import os
import sys
import traceback

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

USE_MINIMAL = os.getenv("CHAT_TEST_APP", "main").lower() == "minimal"

try:
    if USE_MINIMAL:
        from backend.chat_app import app
        print("[test] Using minimal chat_app entrypoint")
    else:
        from backend.main import app
        print("[test] Using full backend.main entrypoint")
    from fastapi.testclient import TestClient
except Exception:
    traceback.print_exc()
    raise

client = TestClient(app)

results = []

try:
    resp = client.get("/api/chat/ping")
    results.append(("GET /api/chat/ping", resp.status_code, resp.json()))

    resp = client.post(
        "/api/chat/session",
        json={"user_id": "test_user", "context": {"initial": "true"}},
    )
    results.append(("POST /api/chat/session", resp.status_code, resp.json()))
    session_id = resp.json().get("session_id")
    assert session_id, "session_id missing from session create response"

    resp = client.post(
        "/api/chat/message",
        json={
            "session_id": session_id,
            "role": "user",
            "user_id": "test_user",
            "message": "Hello, this is a test.",
            "context": {"topic": "integration"},
        },
    )
    results.append(("POST /api/chat/message", resp.status_code, resp.json()))

    resp = client.get(f"/api/chat/history/{session_id}")
    results.append((f"GET /api/chat/history/{session_id}", resp.status_code, resp.json()))

except Exception:
    traceback.print_exc()
    raise

for name, status, body in results:
    print("---")
    print(name)
    print("status_code:", status)
    print("body:", body)

print("CHAT_INTEGRATION_OK")
