import difflib
from typing import Dict, Any, List, Optional
from datetime import datetime

class EntityResolutionEngine:
    """
    Multi-Signal Entity Resolution Engine.
    Correlates fragmented underground personas and indicators across
    multiple signal dimensions to determine entity equivalence.
    """

    def calculate_handle_similarity(self, handle_a: str, handle_b: str) -> float:
        """Computes normalized string similarity (0.0 to 1.0) between handles."""
        ha = handle_a.lower().replace("-", "_").replace(".", "")
        hb = handle_b.lower().replace("-", "_").replace(".", "")
        if ha == hb:
            return 1.0
        matcher = difflib.SequenceMatcher(None, ha, hb)
        return round(matcher.ratio(), 3)

    def resolve_identities(
        self,
        persona_a: Dict[str, Any],
        persona_b: Dict[str, Any],
        shared_pgp: bool = False,
        shared_wallets: List[str] = None,
        shared_infrastructure: List[str] = None,
        stylometry_similarity: float = 0.0,
        behavior_similarity: float = 0.0,
        temporal_overlap: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluates multi-signal correlation between two candidate personas.
        Returns evidence classification, confidence score, and explainability breakdown.
        """
        supporting_evidence: List[Dict[str, Any]] = []
        contradicting_evidence: List[Dict[str, Any]] = []
        scores: Dict[str, float] = {}

        # 1. Handle similarity signal
        h_sim = self.calculate_handle_similarity(
            persona_a.get("handle", ""),
            persona_b.get("handle", "")
        )
        scores["handle_similarity"] = h_sim
        if h_sim >= 0.85:
            supporting_evidence.append({
                "factor": "HANDLE_SIMILARITY",
                "weight": "MODERATE",
                "detail": f"High lexical handle similarity ({int(h_sim * 100)}%) between '{persona_a.get('handle')}' and '{persona_b.get('handle')}'."
            })
        elif h_sim < 0.30 and not shared_pgp and not shared_wallets:
            contradicting_evidence.append({
                "factor": "HANDLE_DISPARITY",
                "weight": "WEAK",
                "detail": f"Substantially different handle naming conventions ({int(h_sim * 100)}%)."
            })

        # 2. Cryptographic PGP correlation (Strongest Signal)
        if shared_pgp:
            scores["pgp_correlation"] = 1.0
            supporting_evidence.append({
                "factor": "SHARED_PGP_KEY",
                "weight": "STRONG",
                "detail": "Both personas reference or publish identical 4096-bit cryptographic PGP fingerprint."
            })
        else:
            scores["pgp_correlation"] = 0.0

        # 3. Cryptocurrency wallet overlap
        if shared_wallets and len(shared_wallets) > 0:
            scores["wallet_overlap"] = 1.0
            supporting_evidence.append({
                "factor": "SHARED_CRYPTO_WALLET",
                "weight": "STRONG",
                "detail": f"Direct blockchain overlap: {len(shared_wallets)} shared wallet addresses ({', '.join(shared_wallets[:2])})."
            })
        else:
            scores["wallet_overlap"] = 0.0

        # 4. Infrastructure correlation
        if shared_infrastructure and len(shared_infrastructure) > 0:
            scores["infrastructure_correlation"] = 0.90
            supporting_evidence.append({
                "factor": "INFRASTRUCTURE_OVERLAP",
                "weight": "MODERATE",
                "detail": f"Shared staging server, SSL/TLS certificate serial, or Favicon hash: {', '.join(shared_infrastructure[:2])}."
            })
        else:
            scores["infrastructure_correlation"] = 0.0

        # 5. Stylometric writing style similarity
        scores["stylometry_similarity"] = stylometry_similarity
        if stylometry_similarity >= 0.75:
            supporting_evidence.append({
                "factor": "STYLOMETRIC_CONGRUENCE",
                "weight": "MODERATE",
                "detail": f"AI Stylometric profiling reveals {int(stylometry_similarity * 100)}% writeprint congruence across vocabulary and punctuation entropy."
            })
        elif stylometry_similarity < 0.35 and stylometry_similarity > 0.0:
            contradicting_evidence.append({
                "factor": "STYLOMETRIC_DIVERGENCE",
                "weight": "MODERATE",
                "detail": f"Substantial divergence in grammatical complexity and function word frequencies ({int(stylometry_similarity * 100)}%)."
            })

        # 6. Behavioral & Diurnal Activity
        scores["behavior_similarity"] = behavior_similarity
        if behavior_similarity >= 0.70:
            supporting_evidence.append({
                "factor": "BEHAVIORAL_ALIGNMENT",
                "weight": "MODERATE",
                "detail": f"Matching diurnal posting schedule and platform activity cadence ({int(behavior_similarity * 100)}% match)."
            })
        elif behavior_similarity < 0.30 and behavior_similarity > 0.0:
            contradicting_evidence.append({
                "factor": "TIMEZONE_DISPARITY",
                "weight": "STRONG",
                "detail": "Opposing peak operational UTC hours (suggesting different geographical timezones)."
            })

        # 7. Weighted Composite Score Calculation
        # Weights: PGP (25%), Wallet (20%), Infra (15%), Stylometry (15%), Behavior (15%), Handle (10%)
        composite_score = (
            scores["pgp_correlation"] * 0.25 +
            scores["wallet_overlap"] * 0.20 +
            scores["infrastructure_correlation"] * 0.15 +
            scores["stylometry_similarity"] * 0.15 +
            scores["behavior_similarity"] * 0.15 +
            scores["handle_similarity"] * 0.10
        )

        # Contradiction penalty
        penalty = len(contradicting_evidence) * 0.12
        adjusted_score = max(0.05, min(0.98, composite_score - penalty))

        # Qualitative classification
        if adjusted_score >= 0.80 and len(contradicting_evidence) == 0:
            rating = "VERY HIGH"
            evidence_tier = "STRONG_EVIDENCE"
            recommendation = "HIGH_CONFIDENCE_ATTRIBUTION"
        elif adjusted_score >= 0.60:
            rating = "HIGH" if len(contradicting_evidence) == 0 else "MEDIUM"
            evidence_tier = "MODERATE_EVIDENCE"
            recommendation = "REQUIRES_HUMAN_VALIDATION"
        elif adjusted_score >= 0.35:
            rating = "MODERATE"
            evidence_tier = "WEAK_EVIDENCE"
            recommendation = "INSUFFICIENT_EVIDENCE_FOR_MERGE"
        else:
            rating = "LOW"
            evidence_tier = "CONTRADICTORY_OR_UNKNOWN"
            recommendation = "DO_NOT_MERGE_SEPARATE_ENTITIES"

        return {
            "candidate_persona_a": persona_a.get("handle"),
            "candidate_persona_b": persona_b.get("handle"),
            "confidence_score": round(adjusted_score, 3),
            "confidence_rating": rating,
            "evidence_tier": evidence_tier,
            "recommendation": recommendation,
            "supporting_evidence_count": len(supporting_evidence),
            "contradicting_evidence_count": len(contradicting_evidence),
            "supporting_evidence": supporting_evidence,
            "contradicting_evidence": contradicting_evidence,
            "signal_scores": scores,
            "evaluated_at": datetime.utcnow().isoformat() + "Z"
        }

entity_resolver = EntityResolutionEngine()
