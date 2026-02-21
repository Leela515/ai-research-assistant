from pydantic import BaseModel
from typing import List

class Critique(BaseModel):
    critique_id: str

    target_type: str  # "claim" or "summary"
    target_id: str

    faithfulness: float
    coverage: float
    clarity: float

    issues: List[str]
    recommendation: str # accept, revise, reject