# src/web_app.py
import streamlit as st
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.nodes import (
    node_next_question,
    node_evaluate,
    node_followup,
    node_increment_or_finish,
    node_summary,
    MAX_FOLLOWUPS_PER_Q,
)
from app.nodes import MAX_FOLLOWUPS_PER_Q
from graph.flow import build_graph
from core.state import InterviewState
from llm.base import build_llm

from src.app.nodes import MAX_FOLLOWUPS_PER_Q


if "state" not in st.session_state:
    st.session_state.state = InterviewState(
        topics=["Machine Learning"],
        topic_index=0,
        difficulty="easy",
        max_q=4,
        asked=[],
        answers=[],
        evals=[],
        followup_mode=False,
        followup_depth=0,
        done=False,
        question_type="mixed",
        stdin_mode=True,
        difficulty_counts={"easy": 0, "medium": 0, "hard": 0},
        steps=0,
        topic_performance={},
        current_q=None,
        last_eval={},
        summary={},
    )

state = st.session_state.state
st.title("🧠 AI Interviewer")


st.sidebar.header("Interview Settings")
topics_input = st.sidebar.text_input("Topics (comma-separated)", value="Machine Learning")
difficulty_input = st.sidebar.selectbox("Difficulty", ["easy", "mixed", "hard"], index=0)
num_questions = st.sidebar.slider("Number of Questions", 1, 20, 4)
question_type_input = st.sidebar.selectbox(
    "Question Type", ["coding", "theory", "design", "debugging", "mixed"], index=4
)

state.topics = [t.strip() for t in topics_input.split(",") if t.strip()]
state.difficulty = difficulty_input
state.max_q = num_questions
state.question_type = question_type_input


if not state.current_q and not state.followup_mode:
    state = node_next_question(state)

st.write(f"**Question:** {state.current_q}")


user_answer = st.text_area("Your Answer:")

if st.button("Submit Answer"):
   
    state.answers.append(user_answer.strip() or "(no answer)")

  
    state = node_evaluate(state)

  
    if state.last_eval.get("followup_needed") and state.followup_depth < MAX_FOLLOWUPS_PER_Q:
        state = node_followup(state)
        st.success("Follow-up question triggered!")
    else:
        state = node_increment_or_finish(state)

    
    st.session_state.state = state
    st.experimental_rerun() 


if state.evals:
    st.subheader("Last Answer Evaluation")
    last_eval = state.evals[-1]
    st.write("Scores:", last_eval.get("scores", {}))
    st.write("Rationale:", last_eval.get("rationale", ""))
    if last_eval.get("hint"):
        st.write("Hint:", last_eval.get("hint"))
    if last_eval.get("misconceptions"):
        st.write("Misconceptions:", ", ".join(last_eval.get("misconceptions")))


if state.done:
    state = node_summary(state)
    st.subheader("Interview Summary")
    summary = state.summary
    st.write(f"Final Grade: {summary.get('final_grade')}")
    st.write(f"Feedback: {summary.get('feedback')}")
    st.write("Per-topic Performance:")
    for topic, perf in state.topic_performance.items():
        avg = perf["total_score"] / perf["questions"] if perf["questions"] else 0.0
        st.write(f"- {topic}: {perf['questions']} questions, Avg Score: {avg:.2f}")
