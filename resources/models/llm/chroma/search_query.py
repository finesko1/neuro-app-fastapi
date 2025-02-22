from pydantic import BaseModel

class SearchQuery(BaseModel):
    query: str
    n_results: int = 5