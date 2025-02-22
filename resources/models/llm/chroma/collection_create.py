from typing import Optional, Dict
from pydantic import BaseModel

class CollectionCreate(BaseModel):
    name: str
    metadata: Optional[Dict] = None
