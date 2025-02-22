from typing import Optional,List
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    """Модель ответа для операций с документами."""
    status: str
    message: str
    document_id: Optional[str] = None
    chunks: Optional[List[str]] = None