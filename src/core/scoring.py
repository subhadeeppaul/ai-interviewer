# src/core/scoring.py
from __future__ import annotations
from typing import Dict

def clamp_score(x) -> float:
    try:
        return max(0.0, min(10.0, float(x)))
    except Exception:
        return 0.0

def recompute_overall(acc: float, cla: float, dep: float) -> float:
    return round((clamp_score(acc) + clamp_score(cla) + clamp_score(dep)) / 3.0, 2)

def normalize_eval(payload: Dict) -> Dict:
    """Normalize/validate the eval JSON returned by the model."""
    defaults = {
        "accuracy": 0.0,
        "clarity": 0.0,
        "depth": 0.0,
        "overall": 0.0,
        "followup_needed": False,
        "rationale": "",
        "misconceptions": [],
        "hint": "",
    }
    if not isinstance(payload, dict):
        payload = {}
    out = {**defaults, **payload}
    # coerce types
    out["accuracy"] = clamp_score(out.get("accuracy"))
    out["clarity"] = clamp_score(out.get("clarity"))
    out["depth"] = clamp_score(out.get("depth"))
    if not out.get("overall"):
        out["overall"] = recompute_overall(out["accuracy"], out["clarity"], out["depth"])
    out["followup_needed"] = bool(out.get("followup_needed"))
    if not isinstance(out.get("misconceptions"), list):
        out["misconceptions"] = [str(out["misconceptions"])] if out.get("misconceptions") else []
    out["rationale"] = str(out.get("rationale", ""))[:500]
    out["hint"] = str(out.get("hint", ""))[:200]
    return out
