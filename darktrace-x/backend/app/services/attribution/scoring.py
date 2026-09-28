from typing import Dict, Any, List, Optional
from datetime import datetime

DEFAULT_ATTRIBUTION_WEIGHTS = {
    "identifier_match": 0.20,
    "infrastructure_correlation": 0.20,
    "pgp_correlation": 0.15,
    "behavior_similarity": 0.15,
    "stylometric_similarity": 0.15,
    "temporal_correlation": 0.10,
    "independent_corroboration": 0.05
}

class AttributionConfidenceEngine:
    """
    Transparent Multi-Factor Attribution Scoring Engine.
    Computes explainable confidence ratings using configurable evidentiary weights,
    quantifies supporting vs contradicting vs missing evidence,
    and enforces strict human-in-the-loop review guards.
    """

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or DEFAULT_ATTRIBUTION_WEIGHTS

    def evaluate_attribution(
        self,
        signals: Dict[str, float],
        evidence_chain: List[Dict[str, Any]],
        contradictions: List[Dict[str, Any]],
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculates attribution assessment confidence score and factor breakdown.
        """
        active_weights = custom_weights or self.weights
        factor_breakdown: List[Dict[str, Any]] = []

        total_score = 0.0
        for factor_name, weight in active_weights.items():
            factor_score = signals.get(factor_name, 0.0)
            weighted_contrib = factor_score * weight
            total_score += weighted_contrib

            factor_breakdown.append({
                "factor": factor_name,
                "factor_label": factor_name.replace("_", " ").title(),
                "weight_percentage": int(weight * 100),
                "raw_score": round(factor_score, 3),
                "weighted_contribution": round(weighted_contrib, 3),
                "status": "STRONG" if factor_score >= 0.8 else ("MODERATE" if factor_score >= 0.5 else "WEAK_OR_MISSING")
            })

        # Apply contradiction penalty
        contradiction_penalty = len(contradictions) * 0.10
        final_score = max(0.0, min(1.0, total_score - contradiction_penalty))
        percentage = int(round(final_score * 100))

        # Qualitative Confidence Tier
        if percentage >= 80:
            rating = "VERY HIGH"
        elif percentage >= 60:
            rating = "HIGH"
        elif percentage >= 30:
            rating = "MODERATE"
        else:
            rating = "LOW"

        # Missing evidence identification
        missing_evidence = []
        for factor in factor_breakdown:
            if factor["raw_score"] < 0.3:
                missing_evidence.append(f"Independent corroboration needed for: {factor['factor_label']}")

        # Recommendation
        if len(contradictions) > 0:
            recommendation = "REQUIRES HUMAN VALIDATION // CONTRADICTION DETECTED"
        elif rating in ["VERY HIGH", "HIGH"]:
            recommendation = "HIGH CONFIDENCE ATTRIBUTION // HUMAN SIGN-OFF REQUIRED"
        else:
            recommendation = "INSUFFICIENT EVIDENCE FOR DEFINITIVE ATTRIBUTION"

        return {
            "confidence_percentage": percentage,
            "confidence_score": round(final_score, 3),
            "confidence_rating": rating,
            "recommendation": recommendation,
            "factor_breakdown": factor_breakdown,
            "supporting_evidence_count": len(evidence_chain),
            "contradicting_evidence_count": len(contradictions),
            "missing_evidence_count": len(missing_evidence),
            "supporting_evidence": evidence_chain,
            "contradicting_evidence": contradictions,
            "missing_evidence": missing_evidence,
            "contradiction_penalty_applied": round(contradiction_penalty, 2),
            "computed_at": datetime.utcnow().isoformat() + "Z"
        }

attribution_engine = AttributionConfidenceEngine()
