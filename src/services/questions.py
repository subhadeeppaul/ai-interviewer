from __future__ import annotations
from typing import List, Dict, Literal, Optional
import random, json, os
from ..llm.base import build_llm
from ..core.prompts import SYSTEM_INTERVIEWER, QUESTION_GEN_PROMPT

QuestionType = Literal["coding", "theory", "design", "debugging", "mixed"]

SEED_PATH = os.getenv("QUESTION_SEED_PATH", os.path.join("data", "questions.json"))

def _load_seeds() -> Dict[str, Dict[str, List[str]]]:
    try:
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _pick_type(requested: QuestionType, asked: List[str] | None) -> str:
    """Pick a question type, balancing least-used if 'mixed'."""
    if requested != "mixed":
        return requested
    types = ["coding", "theory", "design", "debugging"]
    asked = asked or []

    # ensure all asked items are strings
    asked_strs = []
    for q in asked:
        if isinstance(q, dict):
            asked_strs.append(q.get("question", ""))
        elif isinstance(q, str):
            asked_strs.append(q)
    counts = {t: sum(1 for q in asked_strs if f"[{t}]" in q.lower()) for t in types}
    least = min(counts.values()) if counts else 0
    candidates = [t for t, c in counts.items() if c == least] or types
    return random.choice(candidates)

def _tag(q: str, t: str) -> str:
    ttag = t.lower()
    if not q.endswith("?"):
        q = q.rstrip(".") + "?"
    return f"[{ttag}] {q}"

def _strip_tag(q: str) -> str:
    """Remove type tag from a question string."""
    if q.startswith("["):
        close = q.find("]")
        if close != -1:
            return q[close+1:].strip()
    return q

def _pick_seed_question(topic: str, qtype: str, asked: List[str]) -> Optional[str]:
    """Return a tagged seed question not yet used, otherwise None."""
    seeds = _load_seeds()
    topic_bucket = seeds.get(topic) or {}
    type_bucket = topic_bucket.get(qtype) or []
    if not type_bucket:
        return None

    # normalize asked set: dicts -> question strings
    asked_strs = []
    for q in asked:
        if isinstance(q, dict):
            asked_strs.append(q.get("question", ""))
        elif isinstance(q, str):
            asked_strs.append(q)
    asked_norm = {_strip_tag(q).lower() for q in asked_strs}

    remaining = [q for q in type_bucket if q.lower().strip().rstrip("?") not in asked_norm]
    if not remaining:
        return None
    return _tag(random.choice(remaining), qtype)

def generate_question(
    topic: str,
    difficulty: str = "mixed",
    question_type: QuestionType = "mixed",
    asked_so_far: List[str] | None = None,
) -> str:
    """Generate a single interview question (seed first, else LLM)."""
    asked = asked_so_far or []
    qtype = _pick_type(question_type, asked)

    # 1) try seed first
    seed_q = _pick_seed_question(topic, qtype, asked)
    if seed_q:
        return seed_q

    # 2) fall back to LLM
    llm = build_llm()
    user_prompt = QUESTION_GEN_PROMPT.format(
        topic=topic, difficulty=difficulty, question_type=qtype
    )
    messages: List[Dict] = [
        {"role": "system", "content": SYSTEM_INTERVIEWER},
        {"role": "user", "content": user_prompt},
    ]
    q = llm.chat(messages).strip()
    return _tag(q, qtype)
