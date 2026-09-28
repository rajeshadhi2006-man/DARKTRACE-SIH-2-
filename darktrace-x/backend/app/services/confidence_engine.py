from typing import Dict, Any, Tuple

def calculate_overall_correlation(
    identifier_score: float,
    behavior_score: float,
    linguistic_score: float,
    infrastructure_score: float,
    temporal_score: float,
    evidence_count: int = 5
) -> Tuple[float, str, str]:
    """
    Transparent, deterministic confidence calculation formula:
      30% Identifier correlation
      20% Behavioral similarity
      20% Linguistic similarity
      15% Infrastructure correlation
      15% Temporal correlation

    Returns:
      (overall_score, confidence_level_key, confidence_level_display)
    """
    if evidence_count < 2:
        return 0.0, "insufficient_evidence", "Insufficient Evidence"

    # Clamp scores to 0-100
    id_s = max(0.0, min(100.0, float(identifier_score)))
    bh_s = max(0.0, min(100.0, float(behavior_score)))
    lg_s = max(0.0, min(100.0, float(linguistic_score)))
    inf_s = max(0.0, min(100.0, float(infrastructure_score)))
    tmp_s = max(0.0, min(100.0, float(temporal_score)))

    overall = (
        (id_s * 0.30) +
        (bh_s * 0.20) +
        (lg_s * 0.20) +
        (inf_s * 0.15) +
        (tmp_s * 0.15)
    )
    overall = round(overall, 1)

    if overall >= 80.0:
        level_key = "very_strong_correlation"
        display = "Very Strong Correlation"
    elif overall >= 60.0:
        level_key = "strong_correlation"
        display = "Strong Correlation"
    elif overall >= 30.0:
        level_key = "possible_correlation"
        display = "Possible Correlation"
    else:
        level_key = "weak_correlation"
        display = "Weak Correlation"

    return overall, level_key, display

def format_provenance_step(step_name: str, observation: str, evidence_ids: list, weight_pct: int, feature_score: float):
    return {
        "step": step_name,
        "observation": observation,
        "evidence_ids": evidence_ids,
        "weight_contribution": f"{weight_pct}%",
        "feature_score": feature_score
    }
