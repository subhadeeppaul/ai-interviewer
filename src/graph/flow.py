# src/graph/flow.py
from __future__ import annotations
from typing import Dict, List, Any
import os
import sys
import re

# safety: allow deeper recursion in the graph runner if needed
sys.setrecursionlimit(300)

# langgraph StateGraph import (works with installed langgraph)
from langgraph.graph.state import StateGraph

# define simple START/END markers used by the StateGraph edges
START = "__start__"
END = "__end__"

from ..core.state import InterviewState
from ..services.questions import generate_question
from ..services.evaluate import evaluate_answer
from ..services.followup import generate_followup
from ..services.summary import generate_summary

# ---------- configuration ----------
MAX_FOLLOWUPS_PER_Q = int(os.getenv("MAX_FOLLOWUPS_PER_Q", "1"))  # set to 0 to disable follow-ups
MAX_TOTAL_STEPS = int(os.getenv("MAX_TOTAL_STEPS", "500"))        # hard safety limit

# ---------- helpers ----------
TYPE_TAG_RE = re.compile(r"^\s*\[(coding|theory|design|debugging)\]\s*", flags=re.IGNORECASE)


def _strip_type_tag(q: str) -> str:
    return TYPE_TAG_RE.sub("", q).strip()


def _read_multiline_answer(prompt: str = "Your answer (blank line to finish): ") -> str:
    """Read a multiline answer from stdin. (user ends with a blank line)."""
    print(prompt, end="", flush=True)
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line.strip():
            break
        lines.append(line.rstrip())
    return "\n".join(lines).strip()


# ---------- nodes ----------
def node_next_question(state: InterviewState) -> InterviewState:
    """Pick next main question, avoid duplicates, track difficulty, show progress."""
    if state.get("done"):
        return state

    topics = state.get("topics", [state.get("topic", "Python")])
    topic_index = int(state.get("topic_index", 0))
    current_topic = topics[topic_index % len(topics)]

    difficulty_counts = state.get("difficulty_counts", {"easy": 0, "medium": 0, "hard": 0})
    chosen_diff = state.get("difficulty", "mixed")
    if chosen_diff == "mixed":
        chosen_diff = min(difficulty_counts, key=difficulty_counts.get)

    # build list of previously asked main questions for this topic (strings)
    asked_strings = [
        q["question"] for q in state.get("asked", [])
        if isinstance(q, dict) and q.get("topic") == current_topic and q.get("difficulty") != "follow-up"
    ]

    try:
        q_tagged = generate_question(
            topic=current_topic,
            difficulty=chosen_diff,
            question_type=state.get("question_type", "mixed"),
            asked_so_far=asked_strings,
        )
    except Exception as e:
        print(f"Error generating question: {e}")
        return {**state, "done": True}

    shown = _strip_type_tag(q_tagged)

    asked = [*state.get("asked", []), {"question": q_tagged, "topic": current_topic, "difficulty": chosen_diff}]
    difficulty_counts[chosen_diff] = difficulty_counts.get(chosen_diff, 0) + 1

    main_qs = [q for q in asked if isinstance(q, dict) and q.get("difficulty") != "follow-up"]
    max_q = int(state.get("max_q", 4))
    print(f"Question {len(main_qs)} of {max_q} (Topic: {current_topic}, Difficulty: {chosen_diff})")

    # reset follow-up depth for new main question
    return {
        **state,
        "current_q": shown,
        "asked": asked,
        "followup_mode": False,
        "followup_depth": 0,
        "topic_index": topic_index + 1,
        "difficulty_counts": difficulty_counts,
    }


def node_ask(state: InterviewState) -> InterviewState:
    """Display current question and capture answer (single line or multiline)."""
    if not state.get("current_q"):
        print("No question available.")
        return state

    print(f"\n[Q] {state['current_q']}")
    if state.get("stdin_mode"):
        ans = _read_multiline_answer()
        if not ans:
            ans = "(no answer)"
    else:
        ans = input("Your answer: ").strip() or "(no answer)"

    answers = [*state.get("answers", []), ans]
    # safe step counter to prevent runaway
    steps = int(state.get("steps", 0)) + 1
    return {**state, "answers": answers, "steps": steps}


def node_evaluate(state: InterviewState) -> InterviewState:
    """Evaluate last answer and handle short/off-topic answers with simple heuristics."""
    question = state.get("current_q", "")
    answers = state.get("answers", [])
    answer = answers[-1] if answers else ""
    topic_index = int(state.get("topic_index", 0))
    topics = state.get("topics", [state.get("topic", "Python")])
    current_topic = topics[(topic_index - 1) % len(topics)] if topic_index > 0 else topics[0]

    try:
        # quick "I don't know" handling
        if not answer.strip() or answer.strip().lower() in {
            "i dont know", "sorry, i dont know", "idk", "don't know", "do not know",
        }:
            eval_data = {
                "accuracy": 0.0,
                "clarity": 0.0,
                "depth": 0.0,
                "overall": 0.0,
                "scores": {"accuracy": 0.0, "clarity": 0.0, "depth": 0.0, "overall": 0.0},
                "rationale": "Candidate explicitly said they do not know.",
                "followup_needed": True,
                "hint": "",
                "misconceptions": [],
                "question": question,
                "answer": answer,
                "topic": current_topic,
            }
        else:
            raw = evaluate_answer(question=question, answer=answer, topic=current_topic)
            if not isinstance(raw, dict):
                raw = {}
            # ensure we have a scores dict
            if "scores" not in raw:
                raw_scores = {
                    "accuracy": raw.get("accuracy", 0.0),
                    "clarity": raw.get("clarity", 0.0),
                    "depth": raw.get("depth", 0.0),
                    "overall": raw.get("overall", 0.0),
                }
            else:
                raw_scores = raw.get("scores", {"accuracy": 0.0, "clarity": 0.0, "depth": 0.0, "overall": 0.0})

            eval_data = {
                "accuracy": raw.get("accuracy", raw_scores.get("accuracy", 0.0)),
                "clarity": raw.get("clarity", raw_scores.get("clarity", 0.0)),
                "depth": raw.get("depth", raw_scores.get("depth", 0.0)),
                "overall": raw.get("overall", raw_scores.get("overall", 0.0)),
                "scores": raw_scores,
                "rationale": raw.get("rationale", ""),
                "followup_needed": bool(raw.get("followup_needed", False)),
                "hint": raw.get("hint", ""),
                "misconceptions": raw.get("misconceptions", []),
                "question": question,
                "answer": answer,
                "topic": current_topic,
            }

            # Simple heuristics to catch junk answers that just repeat keywords:
            words = [w for w in re.findall(r"\w+", answer) if w]
            if len(words) < 3:
                # too short -> penalize heavily
                eval_data["scores"] = {"accuracy": 0.0, "clarity": max(eval_data["scores"].get("clarity", 0.0), 1.0), "depth": 0.0, "overall": 0.0}
                eval_data["rationale"] = (eval_data.get("rationale", "") + " | Overridden: Answer too short or uninformative.").strip(" |")
                eval_data["followup_needed"] = True
            else:
                # check at least some token overlap with question tokens
                q_tokens = set(re.findall(r"\w+", question.lower()))
                overlap = sum(1 for w in words if w.lower() in q_tokens)
                if overlap == 0:
                    # no overlap -> penalize accuracy
                    eval_data["scores"]["accuracy"] = min(eval_data["scores"].get("accuracy", 0.0), 2.0)
                    eval_data["rationale"] = (eval_data.get("rationale", "") + " | Penalized: Answer may not address the question.").strip(" |")
                    eval_data["followup_needed"] = True

    except Exception as e:
        print(f"Error evaluating answer: {e}")
        eval_data = {
            "accuracy": 0.0,
            "clarity": 0.0,
            "depth": 0.0,
            "overall": 0.0,
            "scores": {"accuracy": 0.0, "clarity": 0.0, "depth": 0.0, "overall": 0.0},
            "rationale": f"Evaluation failed: {e}",
            "followup_needed": True,
            "hint": "",
            "misconceptions": [],
            "question": question,
            "answer": answer,
            "topic": current_topic,
        }

    # Update topic performance
    topic_perf = state.get("topic_performance", {}) or {}
    tp = topic_perf.get(current_topic, {"questions": 0, "total_score": 0.0})
    tp["questions"] = tp.get("questions", 0) + 1
    tp["total_score"] = tp.get("total_score", 0.0) + float(eval_data["scores"].get("overall", 0.0))
    topic_perf[current_topic] = tp

    # print evaluation info
    scores = eval_data["scores"]
    print(f"→ Scores: accuracy={scores['accuracy']}, clarity={scores['clarity']}, depth={scores['depth']}, overall={scores['overall']}")
    print(f"→ Rationale: {eval_data.get('rationale','')}")
    if eval_data.get("followup_needed"):
        print("→ Follow-up flagged.")

    evals = [*state.get("evals", []), eval_data]
    return {**state, "evals": evals, "last_eval": eval_data, "topic_performance": topic_perf}


def node_followup(state: InterviewState) -> InterviewState:
    """Generate follow-up question as dict, but limit how many follow-ups we allow per main question."""
    last = state.get("evals", [])[-1] if state.get("evals") else {}
    followup_depth = int(state.get("followup_depth", 0))

    # If follow-ups disabled
    if MAX_FOLLOWUPS_PER_Q <= 0:
        # explicitly clear followup mode and continue to next main question
        return {**state, "followup_mode": False, "followup_depth": 0}

    # If we've already exhausted follow-ups for this main question, stop follow-ups
    if followup_depth >= MAX_FOLLOWUPS_PER_Q:
        return {**state, "followup_mode": False, "followup_depth": 0}

    # Otherwise generate a focused follow-up
    fq = generate_followup(
        question=last.get("question", ""),
        answer=last.get("answer", ""),
        hint=last.get("hint", ""),
        misconceptions=last.get("misconceptions", []),
    )

    asked = [*state.get("asked", []), {"question": fq, "topic": last.get("topic"), "difficulty": "follow-up"}]

    return {
        **state,
        "current_q": fq,
        "asked": asked,
        "followup_mode": True,
        "followup_depth": followup_depth + 1,
    }


def node_increment_or_finish(state: InterviewState) -> InterviewState:
    """Decide whether to finish interview or continue with another main question."""
    main_qs = [q for q in state.get("asked", []) if isinstance(q, dict) and q.get("difficulty") != "follow-up"]
    max_q = int(state.get("max_q", 4))
    done = len(main_qs) >= max_q

    # also stop if we exceeded a total steps safety limit
    steps = int(state.get("steps", 0))
    if steps >= MAX_TOTAL_STEPS:
        print("Reached total step limit; finishing interview to avoid infinite loop.")
        done = True

    return {**state, "done": done}


def node_summary(state: InterviewState) -> InterviewState:
    """Create and print final summary using the summary service."""
    summary = generate_summary(
        topic="Multi-topic",
        evaluations=state.get("evals", []),
        max_q=int(state.get("max_q", 4)),
    )

    print("\n===== Interview Summary =====")
    print(f"Topics Covered: {state.get('topics', [state.get('topic', 'Python')])}")
    print(f"Asked: {len([q for q in state.get('asked', []) if isinstance(q, dict) and q.get('difficulty') != 'follow-up'])} main question(s)")
    print(f"Final grade: {summary.get('final_grade')}, signal: {summary.get('signal')}")
    if summary.get("feedback"):
        print(f"\nFeedback: {summary['feedback']}")

    if state.get("topic_performance"):
        print("\nPer-topic Performance:")
        for topic, perf in state["topic_performance"].items():
            avg = perf["total_score"] / perf["questions"] if perf["questions"] else 0.0
            print(f"  • {topic}: {perf['questions']} questions, Avg Score: {avg:.2f}")

    if summary.get("strengths"):
        print("\nStrengths:")
        for s in summary["strengths"]:
            print(f"  • {s}")
    if summary.get("recommendations"):
        print("\nRecommendations:")
        for r in summary["recommendations"]:
            print(f"  • {r}")
    print("=============================\n")

    return {**state, "summary": summary}


# ---------- conditions ----------
def cond_need_followup(state: InterviewState) -> str:
    evals = state.get("evals", [])
    if not evals:
        return "continue"
    last = evals[-1]
    # Only ask follow-up if model flagged one, we are not already in followup_mode,
    # and followup_depth < MAX_FOLLOWUPS_PER_Q and follow-ups are enabled.
    if last.get("followup_needed") and not state.get("followup_mode") and MAX_FOLLOWUPS_PER_Q > 0 and int(state.get("followup_depth", 0)) < MAX_FOLLOWUPS_PER_Q:
        return "followup"
    return "continue"


def cond_continue_or_finish(state: InterviewState) -> str:
    return "finish" if state.get("done") else "continue"


# ---------- build graph ----------
def build_graph():
    g = StateGraph(InterviewState)

    g.add_node("next_question", node_next_question)
    g.add_node("ask", node_ask)
    g.add_node("evaluate", node_evaluate)
    g.add_node("followup", node_followup)
    g.add_node("increment_or_finish", node_increment_or_finish)
    g.add_node("summary", node_summary)

    g.add_edge(START, "next_question")
    g.add_edge("next_question", "ask")
    g.add_edge("ask", "evaluate")

    g.add_conditional_edges("evaluate", cond_need_followup, {
        "followup": "followup",
        "continue": "increment_or_finish",
    })

    g.add_edge("followup", "ask")

    g.add_conditional_edges("increment_or_finish", cond_continue_or_finish, {
        "finish": "summary",
        "continue": "next_question",
    })

    g.add_edge("summary", END)

    return g.compile()
