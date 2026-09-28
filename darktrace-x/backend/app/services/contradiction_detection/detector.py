from typing import Dict, Any, List, Optional
from datetime import datetime

class ContradictionDetectionEngine:
    """
    Contradiction Detection & False Positive Prevention Engine.
    Identifies conflicting signals (temporal divergences, opposing timezones,
    disjoint cryptographic keys) to prevent false attributions and mistaken merges.
    """

    def analyze_contradictions(
        self,
        actor_id: str,
        persona_a: Dict[str, Any],
        persona_b: Dict[str, Any],
        observed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes active contradiction checks between two suspected identities.
        """
        contradictions: List[Dict[str, Any]] = []
        is_false_positive_risk = False

        # 1. Check Diurnal Timezone Conflict
        tz_a = persona_a.get("estimated_timezone")
        tz_b = persona_b.get("estimated_timezone")
        peak_utc_a = persona_a.get("peak_active_utc")
        peak_utc_b = persona_b.get("peak_active_utc")

        if peak_utc_a is not None and peak_utc_b is not None:
            time_diff = abs(peak_utc_a - peak_utc_b)
            if time_diff > 12:
                time_diff = 24 - time_diff
            if time_diff >= 7:  # E.g. UTC+8 (East Asia) vs UTC-5 (Americas)
                contradictions.append({
                    "type": "TEMPORAL_TIMEZONE_CONFLICT",
                    "severity": "HIGH",
                    "title": "Severe Diurnal Timezone Disparity",
                    "description": f"Persona A operates primarily at {peak_utc_a}:00 UTC ({tz_a or 'Unknown'}), whereas Persona B operates at {peak_utc_b}:00 UTC ({tz_b or 'Unknown'}). A time difference of {time_diff} hours strongly contradicts persona equivalence without operational shift handoff."
                })
                is_false_positive_risk = True

        # 2. Check Conflicting Cryptographic Identifiers
        pgp_a = persona_a.get("pgp_fingerprint")
        pgp_b = persona_b.get("pgp_fingerprint")
        if pgp_a and pgp_b and pgp_a.upper() != pgp_b.upper():
            contradictions.append({
                "type": "DISJOINT_PGP_KEYS",
                "severity": "HIGH",
                "title": "Active Disjoint PGP Key Ownership",
                "description": f"Persona A signs communications with Key [{pgp_a[-8:]}], whereas Persona B actively uses a distinct key [{pgp_b[-8:]}]. No cryptographic cross-signing or key transition proof exists."
            })
            is_false_positive_risk = True

        # 3. Check Known Impersonator / Decoy Indicators
        handle_a = persona_a.get("handle", "").lower()
        handle_b = persona_b.get("handle", "").lower()
        decoy_keywords = ["official", "support", "admin", "real", "escrow_bot", "team"]
        has_decoy_keyword = any(kw in handle_b and kw not in handle_a for kw in decoy_keywords)

        if has_decoy_keyword and observed_data.get("shared_pgp") is False:
            contradictions.append({
                "type": "IMPERSONATION_DECOY_PATTERN",
                "severity": "CRITICAL",
                "title": "Suspected Handle Impersonation / Phishing Decoy",
                "description": f"Persona '{persona_b.get('handle')}' utilizes high-risk administrative suffix without corresponding cryptographic credentials. High probability of an opportunistic scam decoy."
            })
            is_false_positive_risk = True

        # 4. Check Activity Timeline Collision
        # Two accounts posting simultaneously in mutually exclusive live auction threads
        simultaneous_actions = observed_data.get("simultaneous_actions_detected", False)
        if simultaneous_actions:
            contradictions.append({
                "type": "CONCURRENT_ACTIVITY_COLLISION",
                "severity": "HIGH",
                "title": "Concurrent Live Activity Across Disparate Networks",
                "description": "Simultaneous live escrow interactions were timestamped within seconds across two disjoint forums from different geographical subnets."
            })
            is_false_positive_risk = True

        # Decision
        if is_false_positive_risk and len(contradictions) >= 2:
            status = "CONTRADICTION_FLAGGED"
            verdict = "INSUFFICIENT_EVIDENCE_SEPARATE_ENTITIES"
            confidence_penalty = 0.40
        elif len(contradictions) == 1:
            status = "POTENTIAL_CONFLICT"
            verdict = "REQUIRES_HUMAN_INVESTIGATOR_ARBITRATION"
            confidence_penalty = 0.15
        else:
            status = "NO_CONTRADICTIONS"
            verdict = "UNCONTRADICTED_CORRELATION"
            confidence_penalty = 0.0

        return {
            "actor_id": actor_id,
            "status": status,
            "verdict": verdict,
            "contradiction_count": len(contradictions),
            "is_false_positive_risk": is_false_positive_risk,
            "confidence_penalty": confidence_penalty,
            "contradictions": contradictions,
            "checked_at": datetime.utcnow().isoformat() + "Z"
        }

contradiction_engine = ContradictionDetectionEngine()
