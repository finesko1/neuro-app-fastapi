from typing import List, Optional
from pydantic import BaseModel

from resources.models.llm.chat.message import Message


class ChatRequest(BaseModel):
    messages: List[Message]
    system_prompt: Optional[str] = None
    use_local_collection: Optional[bool] = None
    use_global_collection: Optional[bool] = None
    global_collection: Optional[str] = None
    local_collection: Optional[str] = None

