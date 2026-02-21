from pydantic import BaseModel, Field
from typing import Optional

class Chunk(BaseModel):
    chunk_id: str 
    paper_id: str
    section_id: str
    chunk_index: int
    text: str
    char_start: int
    char_end: int
    token_count: Optional[int] = None