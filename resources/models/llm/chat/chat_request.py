from typing import List, Optional
from pydantic import BaseModel

from resources.models.llm.chat.message import Message


class ChatRequest(BaseModel):
    messages: List[Message]
    system_prompt: Optional[str] = None
