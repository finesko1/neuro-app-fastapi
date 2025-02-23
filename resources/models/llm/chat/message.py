
from typing import Optional
from pydantic import BaseModel, Field

class Message(BaseModel):
    # id: Optional[int] = None
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str
    # model: Optional[str] = None