# src/services/evaluate.py
from __future__ import annotations
import json
import re
import os
from typing import Dict, Any
from ..llm.base import build_llm
from ..core.prompts import EVAL_PROMPT
from ..core.scoring import normalize_eval


FENCED_JSON_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)


def _extract_json_block(text: str) -> str:
   
    if not text:
        return "{}"
    m = FENCED_JSON_RE.search(text)
    if m:
        return m.group(1)

   
    start = text.find("{")
    while start != -1:
        depth = 0
        in_str = False
        esc = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            else:
                if ch == '"':
                    in_str = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        return text[start : i + 1]
        start = text.find("{", start + 1)
    return "{}"


def evaluate_answer(topic: str, question: str, answer: str) -> Dict[str, Any]:
   
    llm = build_llm()
    prompt = EVAL_PROMPT.format(topic=topic, question=question, answer=answer)

    raw = llm.chat(
        [{"role": "user", "content": prompt}],
        options={"temperature": 0.1, "num_predict": int(os.getenv("EVAL_NUM_PREDICT", 220))},
    ).strip()

    
    try:
        parsed = json.loads(_extract_json_block(raw))
        if not isinstance(parsed, dict):
            parsed = {}
    except Exception:
        parsed = {}

 
    scores_src = parsed.get("scores", parsed)
    accuracy = scores_src.get("accuracy", parsed.get("accuracy", 0.0))
    clarity = scores_src.get("clarity", parsed.get("clarity", 0.0))
    depth = scores_src.get("depth", parsed.get("depth", 0.0))
    overall = scores_src.get("overall", parsed.get("overall", None)) 

    followup_needed = parsed.get("followup_needed", parsed.get("followup", False))
    rationale = parsed.get("rationale", parsed.get("explanation", ""))
    hint = parsed.get("hint", "")
    misconceptions = parsed.get("misconceptions", parsed.get("errors", []))

 
    payload = {
        "accuracy": accuracy,
        "clarity": clarity,
        "depth": depth,
        "overall": overall if overall is not None else 0.0,
        "scores": {
            "accuracy": accuracy,
            "clarity": clarity,
            "depth": depth,
            "overall": overall if overall is not None else 0.0,
        },
        "followup_needed": bool(followup_needed),
        "rationale": str(rationale)[:500],
        "hint": str(hint)[:200],
        "misconceptions": misconceptions if isinstance(misconceptions, list) else [str(misconceptions)],
        "question": question,
        "answer": answer,
        "topic": topic,
    }

   
    try:
        return normalize_eval(payload)
    except Exception:
      
        safe = {
            "accuracy": 0.0,
            "clarity": 0.0,
            "depth": 0.0,
            "overall": 0.0,
            "followup_needed": True,
            "rationale": "Evaluation failed to parse LLM output.",
            "misconceptions": [],
            "hint": "",
            "question": question,
            "answer": answer,
            "topic": topic,
        }
        return normalize_eval(safe)
