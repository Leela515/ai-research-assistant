from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class Paper(BaseModel):
    paper_id: str = Field(..., description="Stable internal ID for the paper")
    title: str
    authors: List[str]
    year: int

    abstract: Optional[str] = None
    arxiv_id: Optional[str] = None
    pdf_url: Optional[str] = None
    pdf_path: Optional[str] = None
    ingestion_date: datetime
    source: str = Field(..., description="Source of the paper, e.g. arxiv")