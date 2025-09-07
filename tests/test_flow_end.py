# tests/test_flow_end.py
import types
from src.graph.flow import build_graph
from src.llm import base as llmbase

class DummyLLM:
    def __init__(self): pass
    def chat(self, messages, **kwargs):
        user = messages[-1]["content"]
        if "Return STRICT JSON only" in user and '"accuracy"' in user:
            return '{"accuracy": 5, "clarity": 5, "depth": 5, "overall": 5, "followup_needed": false, "rationale": ""}'
        if "Return STRICT JSON only" in user and '"feedback"' in user:
            return '{"feedback": "ok", "strengths": ["x"], "recommendations": ["y"], "final_grade": 5, "signal": "borderline"}'
        return "Explain X?"

def test_graph_completes_without_model(monkeypatch):
    monkeypatch.setattr(llmbase, "build_llm", lambda: DummyLLM())

    app = build_graph()
    init_state = {
        "topic": "Python",
        "difficulty": "mixed",
        "max_q": 1,
        "asked": [],
        "answers": ["stub answer"], 
        "evals": [],
        "followup_mode": False,
        "done": False,
        "question_type": "theory",
        "current_q": "Explain X?",
    }

    from src.graph.flow import node_evaluate, node_increment_or_finish, node_summary
    st = node_evaluate(init_state)
    st = node_increment_or_finish(st | {"done": True})
    st = node_summary(st)
    assert "summary" not in init_state  
