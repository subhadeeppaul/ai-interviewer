from typing import List, Literal, Dict
from pydantic import BaseModel, Field

Verdict = Literal["correct", "partial", "incorrect"]

class InterviewState(BaseModel):
    """
    Session state carried throughout the interview.
    Kept intentionally small and explicit so it's easy to reason about in the flow.
    """
    topic: str
    q_index: int = 0
    max_q: int = 3
    messages: List[Dict] = Field(default_factory=list)     # [{"role":"assistant","content":"..."}]
    verdicts: List[Verdict] = Field(default_factory=list)
    followup_used: List[bool] = Field(default_factory=list)
    score: float = 0.0
