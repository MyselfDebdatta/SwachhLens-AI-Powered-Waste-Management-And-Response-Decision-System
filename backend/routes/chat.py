from fastapi import APIRouter, HTTPException
from typing import List
from backend.schemas.chat import SessionCreatePayload, SessionCreateResponse, ChatMessage, ChatReply
from backend.services import chat_store, chat_engine
import asyncio

router = APIRouter()


@router.post("/session", response_model=SessionCreateResponse, tags=["Chat"])
async def create_session(payload: SessionCreatePayload):
    """Explicitly create a chat session for a user. Must be called before /message."""
    session_id = await chat_store.create_session(payload.user_id, payload.context)
    return {"session_id": session_id, "user_id": payload.user_id}


@router.post("/message", response_model=ChatReply, tags=["Chat"])
async def post_message(msg: ChatMessage):
    """Post a message to an existing session. Does NOT auto-create sessions."""
    # Verify session exists
    sess = await chat_store.get_session(msg.session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found. Create via /session first.")

    incoming = {
        "session_id": msg.session_id,
        "role": msg.role,
        "user_id": msg.user_id,
        "message": msg.message,
        "context": msg.context or {}
    }

    # store user message
    await chat_store.add_message(msg.session_id, incoming)

    # generate dummy assistant reply
    reply = chat_engine.generate_dummy_reply(incoming)

    # store reply
    await chat_store.add_message(msg.session_id, reply)

    return reply


@router.get("/history/{session_id}", response_model=List[dict], tags=["Chat"])
async def get_history(session_id: str):
    """Return the message history for a session."""
    try:
        msgs = await chat_store.list_messages(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    return msgs


@router.get("/ping", tags=["Chat"])
def ping():
    return {"status": "ok"}
