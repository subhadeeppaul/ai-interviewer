# tests/test_eval_parsing.py
import json
from src.services.evaluate import _extract_json_block
from src.core.scoring import normalize_eval

def test_extract_json_prefers_fenced_block():
    text = """
    blah blah
    ```json
    {"accuracy": 7, "clarity": 8, "depth": 6, "overall": 7, "followup_needed": false}
    ```
    trailing prose
    """
    blob = _extract_json_block(text)
    data = json.loads(blob)
    assert data["accuracy"] == 7
    assert data["followup_needed"] is False

def test_normalize_eval_defaults():
    data = normalize_eval({"accuracy": 11, "clarity": -1, "depth": "5"})
    assert data["accuracy"] == 10.0
    assert data["clarity"] == 0.0
    assert data["depth"] == 5.0
    assert data["overall"] == round((10 + 0 + 5) / 3, 2)
