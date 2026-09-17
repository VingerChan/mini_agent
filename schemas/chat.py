from pydantic import BaseModel
from typing import Any

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    reply: str
    tool_trace: list[dict[str, Any]] = []
