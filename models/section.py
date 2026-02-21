from pydantic import BaseModel, Field
from typing import Optional

class Section(BaseModel):
    section_id: str = Field(..., description="Unique identifier for the section")
    paper_id: str

    title: Optional[str] = None
    section_type: str = Field(
        ..., description="e.g. abstract, introduction, method, results"
    )

    page_start: Optional[int] = None
    page_end: Optional[int] = None

    text: str