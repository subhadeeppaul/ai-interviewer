# src/services/summary.py
from __future__ import annotations
import json
import re
from typing import Dict, List
from ..llm.base import build_llm
from ..core.prompts import SUMMARY_PROMPT_TMPL

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

def generate_summary(topic: str, evaluations: List[Dict], max_q: int) -> Dict:
    llm = build_llm()
    payload = json.dumps(evaluations, ensure_ascii=False)
    prompt = SUMMARY_PROMPT_TMPL.substitute(topic=topic, n=max_q)
    messages = [
        {"role": "user", "content": prompt},
        {"role": "user", "content": f"EVALUATIONS_JSON:\n{payload}"},
    ]
    raw = llm.chat(messages).strip()
    try:
        return json.loads(_extract_json_block(raw))
    except Exception:
        return {
            "feedback": raw[:600],
            "strengths": [],
            "recommendations": [],
            "final_grade": 0,
            "signal": "review",
        }
