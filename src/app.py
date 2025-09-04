"""
CLI entry. For Level 2, I'm only verifying the state model and prompt plumbing.
Real LLM calls arrive in Level 3.
"""

from src.core.state import InterviewState
from src.core.prompts import INTERVIEWER_SYSTEM, EVAL_PROMPT, FOLLOWUP_PROMPT, SUMMARY_PROMPT
from src.core.scoring import sum_score

def main():
    topic = input("Choose a topic (e.g., JavaScript, Machine Learning): ").strip() or "JavaScript"
    state = InterviewState(topic=topic, max_q=3)

    # Show that prompts render cleanly
    print("\n[system prompt]")
    print(INTERVIEWER_SYSTEM.format(topic=state.topic))

    # Fake a round just to show formatting (no LLM yet)
    fake_q = "What is a closure in JavaScript?"
    fake_a = "It lets a function remember variables from the outer scope."
    print("\n[eval prompt]")
    print(EVAL_PROMPT.format(question=fake_q, answer=fake_a))

    print("\n[follow-up prompt]")
    print(FOLLOWUP_PROMPT.format(question=fake_q, answer="Not sure"))

    # Pretend we did three questions with verdicts:
    state.verdicts = ["correct", "partial", "incorrect"]
    state.score = sum_score(state.verdicts)
    print("\n[summary prompt]")
    print(SUMMARY_PROMPT.format(score=state.score, max_q=state.max_q))

    print("\n(Level 2 smoke test done — prompts/state look good.)")

if __name__ == "__main__":
    main()
