from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    question: str

class SourceItem(BaseModel):
    title: Optional[str] = None
    section_title: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    confidence: float