import asyncio
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from backend.services import chat_engine, chat_store


async def run():
    sid = await chat_store.create_session("test_user", {"lang": "en"})
    await chat_store.add_message(
        sid,
        {
            "session_id": sid,
            "role": "user",
            "user_id": "test_user",
            "message": "hi",
            "context": {},
        },
    )
    reply = chat_engine.generate_dummy_reply(
        {
            "session_id": sid,
            "role": "user",
            "user_id": "test_user",
            "message": "hi",
            "context": {},
        }
    )
    await chat_store.add_message(sid, reply)
    msgs = await chat_store.list_messages(sid)
    print("CHAT_TEST_OK", len(msgs))


if __name__ == "__main__":
    asyncio.run(run())
