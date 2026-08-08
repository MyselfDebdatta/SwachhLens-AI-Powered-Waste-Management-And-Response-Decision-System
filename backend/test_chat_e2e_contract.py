import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from backend.main import app

def test_full_chat_e2e_contract():
    client = TestClient(app)

    # 1. Health Probe Check
    ping_res = client.get("/api/chat/ping")
    assert ping_res.status_code == 200, f"Ping failed: {ping_res.text}"
    assert ping_res.json() == {"status": "ok"}
    print("[PASS] Test 1: Ping endpoint returned 200 OK")

    # 2. Session Initialization
    session_res = client.post("/api/chat/session", json={"user_id": "operator_e2e", "context": {"source": "e2e_test"}})
    assert session_res.status_code == 200, f"Session creation failed: {session_res.text}"
    session_data = session_res.json()
    assert "session_id" in session_data
    assert session_data["user_id"] == "operator_e2e"
    session_id = session_data["session_id"]
    print(f"[PASS] Test 2: Created session {session_id}")

    # 3. First User Message
    msg1_res = client.post("/api/chat/message", json={
        "session_id": session_id,
        "role": "user",
        "user_id": "operator_e2e",
        "message": "Show bins above 80%",
        "context": {"screen": "overview"}
    })
    assert msg1_res.status_code == 200, f"Message 1 failed: {msg1_res.text}"
    msg1_data = msg1_res.json()
    assert msg1_data["session_id"] == session_id
    assert msg1_data["role"] == "assistant"
    assert "placeholder" in msg1_data["message"]
    print("[PASS] Test 3: First user message sent & assistant response received")

    # 4. Second User Message (Session Continuity)
    msg2_res = client.post("/api/chat/message", json={
        "session_id": session_id,
        "role": "user",
        "user_id": "operator_e2e",
        "message": "What is today route summary?",
        "context": {"screen": "routes"}
    })
    assert msg2_res.status_code == 200, f"Message 2 failed: {msg2_res.text}"
    print("[PASS] Test 4: Second user message sent & assistant response received")

    # 5. History Verification
    history_res = client.get(f"/api/chat/history/{session_id}")
    assert history_res.status_code == 200, f"History fetch failed: {history_res.text}"
    history_items = history_res.json()
    assert len(history_items) == 4, f"Expected 4 messages (2 pairs), got {len(history_items)}"
    assert history_items[0]["message"] == "Show bins above 80%"
    assert history_items[2]["message"] == "What is today route summary?"
    print("[PASS] Test 5: History retrieval verified (4 messages in sequence)")

    # 6. Invalid Session Error Handling (404)
    invalid_res = client.post("/api/chat/message", json={
        "session_id": "non_existent_session_999",
        "role": "user",
        "user_id": "operator_e2e",
        "message": "Test invalid session",
        "context": {}
    })
    assert invalid_res.status_code == 404, f"Expected 404 for invalid session, got {invalid_res.status_code}"
    print("[PASS] Test 6: Invalid session handling returned 404 Not Found")

    print("\nALL E2E CHAT CONTRACT TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_full_chat_e2e_contract()
