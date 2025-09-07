from src.services.questions import _tag, _pick_type

def test_tagging_and_question_mark():
    q = _tag("Explain decorators", "theory")
    assert q.lower().startswith("[theory]")
    assert q.endswith("?")

def test_mixed_balancing_prefers_least_used():
    asked = ["[coding] q1?", "[theory] q2?"]
    t = _pick_type("mixed", asked)
   
    assert t in {"design", "debugging"}
