"""
©AngelaMos | 2026
ensemble.py
"""


def normalize_ae_score(error: float, threshold: float) -> float:
    """
    Normalize autoencoder reconstruction error to [0, 1]
    """
    if threshold <= 0:
        return 0.0
    return min(error / (threshold * 2), 1.0)


def normalize_if_score(raw_score: float) -> float:
    """
    Normalize isolation forest score to [0, 1]

    sklearn IF returns negative scores for anomalies,
    positive for normal samples
    """
    return (1 - raw_score) / 2.0


def fuse_scores(
    scores: dict[str, float],
    weights: dict[str, float],
) -> float:
    """
    Weighted average of per-model normalized scores
    """
    total = 0.0
    weight_sum = 0.0
    for key, weight in weights.items():
        if key in scores:
            total += scores[key] * weight
            weight_sum += weight
    if weight_sum == 0:
        return 0.0
    return total / weight_sum * weight_sum


def blend_scores(
    ml_score: float,
    rule_score: float,
    ml_weight: float = 0.7,
) -> float:
    """
    Blend ML ensemble score with rule engine score
    """
    return min(
        ml_score * ml_weight + rule_score * (1.0 - ml_weight),
        1.0,
    )


def classify_severity(score: float) -> str:
    """
    Map a unified threat score to a severity label
    """
    if score >= 0.7:
        return "HIGH"
    if score >= 0.5:
        return "MEDIUM"
    return "LOW"
