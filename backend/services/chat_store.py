import asyncio
import uuid
import time
from typing import Dict, List, Any, Optional

# In-memory store for chat sessions and messages
_SESSIONS: Dict[str, Dict[str, Any]] = {}
_LOCK = asyncio.Lock()

# Configuration
SESSION_TTL_SECONDS = 60 * 60  # 1 hour
CLEANUP_INTERVAL_SECONDS = 60  # run cleanup every 60s


async def create_session(user_id: str, context: Optional[Dict[str, Any]] = None) -> str:
    async with _LOCK:
        session_id = str(uuid.uuid4())
        _SESSIONS[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "context": context or {},
            "created_at": time.time(),
            "last_activity": time.time(),
            "messages": []  # list of message dicts
        }
        return session_id


async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    async with _LOCK:
        return _SESSIONS.get(session_id)


async def add_message(session_id: str, message: Dict[str, Any]) -> None:
    async with _LOCK:
        sess = _SESSIONS.get(session_id)
        if not sess:
            raise KeyError("session not found")
        sess["messages"].append(message)
        sess["last_activity"] = time.time()


async def list_messages(session_id: str) -> List[Dict[str, Any]]:
    async with _LOCK:
        sess = _SESSIONS.get(session_id)
        if not sess:
            raise KeyError("session not found")
        return list(sess["messages"])


async def delete_session(session_id: str) -> None:
    async with _LOCK:
        if session_id in _SESSIONS:
            del _SESSIONS[session_id]


async def cleanup_once() -> int:
    """Remove sessions inactive beyond TTL. Returns number removed."""
    now = time.time()
    to_remove = []
    async with _LOCK:
        for sid, sess in list(_SESSIONS.items()):
            if (now - sess.get("last_activity", sess.get("created_at", now))) > SESSION_TTL_SECONDS:
                to_remove.append(sid)
        for sid in to_remove:
            del _SESSIONS[sid]
    return len(to_remove)


async def cleanup_loop() -> None:
    """Long-running cleanup loop intended to be started by FastAPI lifespan."""
    try:
        while True:
            removed = await cleanup_once()
            if removed:
                print(f"[ChatStore] Cleaned up {removed} expired sessions")
            await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
    except asyncio.CancelledError:
        # Graceful exit on cancel
        return
