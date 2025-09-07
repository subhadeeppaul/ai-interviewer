# src/app.py
from __future__ import annotations
import os
from typing import Optional, List, Dict
import json
from pathlib import Path
from dotenv import load_dotenv
import typer
from rich import print

from .llm.base import build_llm

app = typer.Typer(help="AI Interviewer — CLI", no_args_is_help=True)


# ---------- helper ----------
def join_text(parts: Optional[List[str]], default: str = "") -> str:
    """Join list of words into a single string; fallback to default."""
    return " ".join(parts or []).strip() or default


@app.command()
def ping(text: List[str] = typer.Argument(None, metavar="TEXT...", help="Prompt to send")):
    """
    Example:
      python -m src.app ping Respond with exactly: pong
    """
    load_dotenv()
    llm = build_llm()
    prompt = join_text(text, "Respond with exactly: pong")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]
    reply = llm.chat(messages)
    print(f"[bold cyan]Model ({os.getenv('OLLAMA_MODEL','mistral')}):[/] {reply}")


@app.command("ask-one")
def ask_one(
    topic: str = typer.Option("JavaScript", "--topic", "-t", help="Interview topic"),
    difficulty: str = typer.Option("mixed", "--difficulty", "-d", help="easy|mixed|hard"),
    qtype: str = typer.Option("mixed", "--type", "-y", help="coding|theory|design|debugging|mixed"),
):
    """
    Generate ONE interview question for a topic.
    Example:
      python -m src.app ask-one --topic Python --difficulty mixed --type theory
    """
    from .services.questions import generate_question
    load_dotenv()
    q = generate_question(topic=topic, difficulty=difficulty, question_type=qtype, asked_so_far=[])
    print(f"[bold green]Question:[/] {q}")


@app.command("grade-answer")
def grade_answer(
    topic: str = typer.Option("Python", "--topic", "-t", help="Interview topic"),
    question: str = typer.Option(..., "--question", "-q", help="The interview question"),
    answer: List[str] = typer.Argument(None, metavar="ANSWER...", help="Your answer"),
):
    """
    Score an answer for accuracy, clarity, depth; signal if follow-up is needed.
    """
    load_dotenv()
    from .services.evaluate import evaluate_answer

    ans_text = join_text(answer)
    if not ans_text:
        print("[bold yellow]Provide an answer after the flags — nothing to grade.[/]")
        raise typer.Exit(code=1)

    result = evaluate_answer(topic=topic, question=question, answer=ans_text)
    print(f"Scores → accuracy={result['accuracy']}, clarity={result['clarity']}, depth={result['depth']}, overall={result['overall']}")
    print(f"Follow-up needed → {result['followup_needed']}")
    if result.get("rationale"):
        print(f"Rationale → {result['rationale']}")
    if result.get("misconceptions"):
        print(f"Misconceptions → {', '.join(result['misconceptions'])}")
    if result.get("hint"):
        print(f"Hint → {result['hint']}")


@app.command("next-step")
def next_step(
    topic: str = typer.Option("Python", "--topic", "-t", help="Interview topic"),
    question: str = typer.Option(..., "--question", "-q", help="The original interview question"),
    answer: List[str] = typer.Argument(None, metavar="ANSWER...", help="Candidate answer"),
):
    """
    Evaluate an answer and, if needed, generate a targeted follow-up prompt.
    """
    load_dotenv()
    from .services.evaluate import evaluate_answer
    from .services.followup import generate_followup

    ans_text = join_text(answer)
    if not ans_text:
        print("[bold yellow]Provide an answer after the flags — nothing to evaluate.[/]")
        raise typer.Exit(code=1)

    result = evaluate_answer(topic=topic, question=question, answer=ans_text)
    print(f"Scores → accuracy={result['accuracy']}, clarity={result['clarity']}, depth={result['depth']}, overall={result['overall']}")
    print(f"Follow-up needed → {result['followup_needed']}")
    if result.get("rationale"):
        print(f"Rationale → {result['rationale']}")

    if result["followup_needed"]:
        fup = generate_followup(
            question=question,
            answer=ans_text,
            hint=result.get("hint", ""),
            misconceptions=result.get("misconceptions", []),
        )
        print(f"Next question → {fup}")
    else:
        print("Nice! No follow-up required.")


@app.command("interview")
def interview(
    topics: Optional[str] = typer.Option(None, "--topics", help="Comma-separated list of topics, e.g., Python,JavaScript,ML"),
    topic: str = typer.Option("Python", "--topic", "-t", help="Single topic fallback"),
    difficulty: str = typer.Option("mixed", "--difficulty", "-d", help="easy|mixed|hard"),
    questions: int = typer.Option(4, "--questions", "-q", min=1, max=20, help="Number of main questions"),
    qtype: str = typer.Option("mixed", "--type", "-y", help="coding|theory|design|debugging|mixed"),
    log_json: Optional[str] = typer.Option(None, "--log-json", help="Path to save the full interview session as JSON"),
    stdin_mode: bool = typer.Option(False, "--stdin", help="Type answers in stdin (multi-line; end with blank line)"),
):
    """
    Run a full interactive interview with multi-topic rotation, follow-ups, and summary.
    """
    load_dotenv()
    from .graph.flow import build_graph

    # Parse topics list
    topics_list = [t.strip() for t in topics.split(",") if t.strip()] if topics else [topic]

    # Initialize state
    init_state: Dict = {
    "topics": topics_list,
    "topic_index": 0,
    "difficulty": difficulty,
    "max_q": questions,
    "asked": [],
    "answers": [],
    "evals": [],
    "followup_mode": False,
    "followup_depth": 0,
    "done": False,
    "question_type": qtype,
    "stdin_mode": stdin_mode,
    "difficulty_counts": {"easy": 0, "medium": 0, "hard": 0},
    "steps": 0,   # <-- add this
    "topic_performance": {},
}



    # Build graph and run
    graph = build_graph()
    final_state = graph.invoke(init_state)

    if log_json:
        path = Path(log_json)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(final_state, f, ensure_ascii=False, indent=2)
        print(f"Saved session to {path}")


if __name__ == "__main__":
    app()
