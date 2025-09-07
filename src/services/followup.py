# src/services/followup.py
from __future__ import annotations
from typing import List
from ..llm.base import build_llm
from ..core.prompts import FOLLOWUP_PROMPT

def generate_followup(question: str, answer: str, hint: str = "", misconceptions: List[str] | None = None) -> str:
    llm = build_llm()
    msg = FOLLOWUP_PROMPT.format(
        question=question,
        answer=answer,
        hint=hint or "",
        misconceptions=", ".join(misconceptions or []),
    )
    out = llm.chat([{"role": "user", "content": msg}]).strip()
    # Normalize to end with '?'
    if not out.endswith("?"):
        out = out.rstrip(".") + "?"
    # Tagging follow-ups is useful later for counting main vs follow-up Qs
    return f"(Follow-up) {out}"
