SCORE = {"correct": 1.0, "partial": 0.5, "incorrect": 0.0}

def sum_score(verdicts: list[str]) -> float:
    return float(sum(SCORE.get(v, 0.0) for v in verdicts))
