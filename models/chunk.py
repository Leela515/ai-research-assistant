from pydantic import BaseModel
from typing import Optional

class Chunk(BaseModel):
    chunk_id: str 
    paper_id: str
    title: Optional[str] = None
    section_id: str
    section_title: Optional[str] = None
    chunk_index: int
    text: str
    char_start: int
    char_end: int
    token_count: Optional[int] = None