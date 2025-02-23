from pydantic import BaseModel

class DocumentChatRequest(BaseModel):
    question: str
    collection_name: str
