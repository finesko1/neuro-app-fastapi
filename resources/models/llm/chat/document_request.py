from typing import List
from pydantic import BaseModel

class DocumentChatRequest(BaseModel):
    question: str
    collection_names: List[str]
