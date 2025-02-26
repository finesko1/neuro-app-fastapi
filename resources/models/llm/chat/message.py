
from typing import Optional
from pydantic import BaseModel, Field

class Message(BaseModel):
    id: Optional[int] = None
    chat_id: Optional[int] = None
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    model: Optional[str] = None
    global_collection: Optional[str] = None
    local_collection: Optional[str] = None
