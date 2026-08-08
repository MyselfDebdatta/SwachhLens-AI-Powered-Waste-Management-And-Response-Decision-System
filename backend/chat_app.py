"""
Minimal FastAPI app for Phase 1 chat API validation.

Use when full backend.main import is too heavy for local testing:
  uvicorn backend.chat_app:app --reload
  CHAT_TEST_APP=minimal python backend/test_chat_integration.py
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.chat import router as chat_router
from backend.services import chat_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    chat_cleanup_task = asyncio.create_task(chat_store.cleanup_loop())
    print("[ChatApp] Chat session cleanup task started.")
    yield
    chat_cleanup_task.cancel()
    try:
        await chat_cleanup_task
    except asyncio.CancelledError:
        pass
    print("[ChatApp] Chat session cleanup task stopped.")


app = FastAPI(
    title="SwachhLens Chat API (Minimal)",
    description="Phase 1 chat-only entrypoint for integration testing.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/chat")
