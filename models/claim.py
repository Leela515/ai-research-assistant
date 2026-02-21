from pydantic import BaseModel, Field
from typing import Optional

class Claim(BaseModel):
    claim_id: str
    paper_id: str
    sectiom_id: str

    claim_type: str = Field(
        ..., description="method, result, limitation, assumption, contribution"
    )

    text: str
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Model confidence in this claim"
        )

    supporting_section: Optional[str] = None
