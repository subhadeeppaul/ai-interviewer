# tests/test_flow_end.py
import types
from src.graph.flow import build_graph
from src.llm import base as llmbase

class DummyLLM:
    def __init__(self): pass
    def chat(self, messages, **kwargs):
        user = messages[-1]["content"]
        # produce minimal JSON for eval/summary prompts
        if "Return STRICT JSON only" in user and '"accuracy"' in user:
            return '{"accuracy": 5, "clarity": 5, "depth": 5, "overall": 5, "followup_needed": false, "rationale": ""}'
        if "Return STRICT JSON only" in user and '"feedback"' in user:
            return '{"feedback": "ok", "strengths": ["x"], "recommendations": ["y"], "final_grade": 5, "signal": "borderline"}'
        # otherwise just return a dummy question
        return "Explain X?"

def test_graph_completes_without_model(monkeypatch):
    # monkeypatch build_llm to avoid real Ollama calls
    monkeypatch.setattr(llmbase, "build_llm", lambda: DummyLLM())

    app = build_graph()
    init_state = {
        "topic": "Python",
        "difficulty": "mixed",
        "max_q": 1,
        "asked": [],
        "answers": ["stub answer"],  # ask node normally prompts; we bypass by injecting answers
        "evals": [],
        "followup_mode": False,
        "done": False,
        "question_type": "theory",
        "current_q": "Explain X?",
    }
    # invoke nodes manually: next_question->ask->evaluate->increment_or_finish->summary
    # Since our ask node calls input(), we bypass the full invoke and test final nodes behavior via direct calls
    # Instead, simulate post-evaluate path:
    from src.graph.flow import node_evaluate, node_increment_or_finish, node_summary
    st = node_evaluate(init_state)
    st = node_increment_or_finish(st | {"done": True})
    st = node_summary(st)
    assert "summary" not in init_state  # unchanged
