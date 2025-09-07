# src/core/state.py
from __future__ import annotations
from typing import List, Dict, Optional
from typing_extensions import TypedDict

class InterviewState(TypedDict, total=False):
    # Main topic or multiple topics
    topic: str                    # optional single topic
    topics: List[str]             # list of topics for multi-topic interviews
    topic_index: int              # current topic index (for rotation)

    # Question/difficulty tracking
    difficulty: str               # "easy", "medium", "hard", or "mixed"
    difficulty_counts: Dict[str, int]  # count of questions asked per difficulty
    max_q: int                    # max main questions to ask

    # Asked questions & answers
    asked: List[Dict]             # each item: {"question": str, "topic": str, "difficulty": str}
    answers: List[str]            # user answers
    evals: List[Dict]             # evaluation results for each answer
    topic_performance: Dict[str, Dict[str, float]]  # {"Python": {"questions": 2, "total_score": 15.0}, ...}

    # Current state
    current_q: str
    followup_mode: bool
    done: bool
    question_type: str            # "coding", "theory", "design", "debugging", or "mixed"

    # Optional
    stdin_mode: bool              # True if reading multi-line answers
