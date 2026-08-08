from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class SessionCreatePayload(BaseModel):
    user_id: str = Field(..., example="user_123")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SessionCreateResponse(BaseModel):
    session_id: str
    user_id: str


class ChatMessage(BaseModel):
    session_id: str
    role: str = Field(..., example="user")
    user_id: str = Field(..., example="user_123")
    message: str = Field(..., example="Hello, how are you?")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ChatReply(BaseModel):
    session_id: str
    role: str = Field(..., example="assistant")
    user_id: str = Field(..., example="system")
    message: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
