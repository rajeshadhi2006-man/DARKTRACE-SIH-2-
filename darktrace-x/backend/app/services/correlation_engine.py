from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .pattern_engine import (
    compute_handle_similarity,
    compute_temporal_similarity,
    compute_infrastructure_similarity,
    compute_identifier_similarity
)
from .stylometry_engine import (
    extract_stylometric_features,
    compare_stylometric_profiles
)
from .gemini_service import analyze_with_gemini

# In-memory store for generated analysis results for instant fast lookup by analysis_id
_analysis_cache: Dict[str, Any] = {}

def correlate_personas(
    persona_a_data: Dict[str, Any],
    persona_b_data: Dict[str, Any],
    investigation_id: str = "INV-001"
) -> Dict[str, Any]:
    """
    Full pipeline execution:
      Raw Observations -> Feature Extraction -> Deterministic Scoring -> Gemini AI Reasoning -> Confidence Calculation -> Graph Provenance
    """
    handle_a = persona_a_data.get("handle") or persona_a_data.get("name", "entity_a")
    handle_b = persona_b_data.get("handle") or persona_b_data.get("name", "entity_b")

    # 1. Deterministic Handle Similarity
    handle_score, handle_obs = compute_handle_similarity(handle_a, handle_b)

    # 2. Deterministic Temporal Similarity
    hours_a = persona_a_data.get("active_hours", ["18:00", "19:00", "21:00", "22:00"])
    hours_b = persona_b_data.get("active_hours", ["19:00", "20:00", "21:00", "23:00"])
    timestamps_a = persona_a_data.get("timestamps", ["2026-08-10T19:30:00Z", "2026-08-14T21:00:00Z"])
    timestamps_b = persona_b_data.get("timestamps", ["2026-08-18T20:15:00Z", "2026-08-22T23:45:00Z"])
    temporal_score, temporal_obs = compute_temporal_similarity(hours_a, hours_b, timestamps_a, timestamps_b)

    # 3. Deterministic Infrastructure Similarity
    infra_a = persona_a_data.get("infrastructure", [])
    infra_b = persona_b_data.get("infrastructure", [])
    infra_score, infra_obs = compute_infrastructure_similarity(infra_a, infra_b)

    # 4. Deterministic Identifier Similarity (PGP, Wallets)
    entities_a = persona_a_data.get("entities", [])
    entities_b = persona_b_data.get("entities", [])
    id_score, id_obs = compute_identifier_similarity(entities_a, entities_b)

    # 5. Deterministic Stylometry & Linguistic Similarity
    sample_text_a = persona_a_data.get("sample_text", "Selling valid credentials, high quality leaks, escrow only, contact via pgp.")
    sample_text_b = persona_b_data.get("sample_text", "Offering fresh enterprise credentials and initial access listings, escrow accepted, pgp signed.")
    profile_a = extract_stylometric_features(sample_text_a)
    profile_b = extract_stylometric_features(sample_text_b)
    ling_score, ling_obs = compare_stylometric_profiles(profile_a, profile_b)

    # Behavior score synthesis
    behavior_score = round((temporal_score * 0.6) + (ling_score * 0.4), 1)

    combined_observations = handle_obs + temporal_obs + infra_obs + id_obs + ling_obs

    deterministic_scores = {
        "identifier_score": id_score,
        "behavior_score": behavior_score,
        "linguistic_score": ling_score,
        "infrastructure_score": infra_score,
        "temporal_score": temporal_score,
        "observations": combined_observations
    }

    # Construct Structured Investigation Object
    structured_investigation = {
        "investigation_id": investigation_id,
        "persona_a": handle_a,
        "persona_b": handle_b,
        "entities": entities_a + entities_b,
        "behavior": {
            "active_hours": list(set(hours_a + hours_b)),
            "posting_frequency": persona_a_data.get("posting_frequency", 3.8),
            "topics": list(set(persona_a_data.get("topics", []) + persona_b_data.get("topics", [])))
        },
        "language_features": {
            "average_sentence_length": profile_a.get("average_sentence_length", 12.0),
            "punctuation_pattern": profile_a.get("punctuation_pattern", "standard"),
            "common_terms": list(set(profile_a.get("common_terms", []) + profile_b.get("common_terms", []))),
            "writing_embedding_reference": "vector-mini-lm-v2"
        },
        "infrastructure": infra_a + infra_b,
        "evidence_pool": persona_a_data.get("evidence_pool", []) + persona_b_data.get("evidence_pool", [])
    }

    # Execute Gemini AI reasoning (with automatic fallback to deterministic reasoning if key/model issue)
    analysis_result = analyze_with_gemini(structured_investigation, deterministic_scores)

    # Cache result
    analysis_id = analysis_result.get("analysis_id", f"ANL-{investigation_id}")
    _analysis_cache[analysis_id] = analysis_result

    # Sync to Supabase Cloud database
    try:
        from .supabase_service import save_ai_analysis_to_supabase
        save_ai_analysis_to_supabase(analysis_result)
    except Exception:
        pass

    return analysis_result

def get_cached_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    return _analysis_cache.get(analysis_id)

def get_demo_scenario_data() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Returns synthetic SIH demo scenario:
      Persona A: shadow_vendor_01 (Dread forum, active until 2026-08-15)
      Persona B: night_market_7 (BreachForums mirror, active from 2026-08-17)
    """
    persona_a = {
        "handle": "shadow_vendor_01",
        "platform": "Dread Onion Forum",
        "active_hours": ["18:00", "19:00", "20:00", "22:00"],
        "timestamps": ["2026-08-10T18:15:00Z", "2026-08-12T19:40:00Z", "2026-08-15T22:10:00Z"],
        "topics": ["initial-access", "corporate-credentials", "database-dump"],
        "sample_text": "High reliability corporate access for sale... Escrow via trusted admin only. PGP signature available upon request. Serious buyers only...",
        "entities": [
            {"type": "handle", "value": "shadow_vendor_01", "source": "SRC-DREAD", "evidence_id": "EV-000101"},
            {"type": "pgp", "value": "F82B 9912 C104 AA29 443B", "source": "SRC-DREAD", "evidence_id": "EV-000102"},
            {"type": "wallet", "value": "bc1q9v8u47s9a473957m2g3q7f7", "source": "SRC-DREAD", "evidence_id": "EV-000103"}
        ],
        "infrastructure": [
            {"type": "certificate", "fingerprint": "SHA256:7B8A91C042E3FA71", "details": {"issuer": "Let's Encrypt / Tor Proxy"}, "evidence_id": "EV-000104"},
            {"type": "ip", "fingerprint": "185.220.101.45", "details": {"asn": "AS44552", "country": "NL"}, "evidence_id": "EV-000105"}
        ],
        "evidence_pool": [
            {"id": "EV-000101", "source": "SRC-DREAD", "title": "Handle Registration", "timestamp": "2026-08-10T18:15:00Z"},
            {"id": "EV-000102", "source": "SRC-DREAD", "title": "PGP Public Key Post", "timestamp": "2026-08-11T12:00:00Z"},
            {"id": "EV-000103", "source": "SRC-DREAD", "title": "Escrow Deposit Address", "timestamp": "2026-08-12T19:40:00Z"},
            {"id": "EV-000104", "source": "SRC-SENSOR", "title": "TLS Cert Fingerprint 7B8A", "timestamp": "2026-08-14T03:00:00Z"}
        ]
    }

    persona_b = {
        "handle": "night_market_7",
        "platform": "BreachForums Mirror",
        "active_hours": ["19:00", "20:00", "22:00", "23:00"],
        "timestamps": ["2026-08-17T19:00:00Z", "2026-08-20T20:30:00Z", "2026-08-25T22:45:00Z"],
        "topics": ["corporate-credentials", "initial-access", "vpn-logins"],
        "sample_text": "Fresh corporate credential packages and VPN access... Escrow via trusted moderator only. Serious buyers only...",
        "entities": [
            {"type": "handle", "value": "night_market_7", "source": "SRC-BREACH", "evidence_id": "EV-000201"},
            {"type": "pgp", "value": "A109 443B C104 7729 9912", "source": "SRC-BREACH", "evidence_id": "EV-000202"},
            {"type": "wallet", "value": "bc1q9v8u47s9a473957m2g3q7f7", "source": "SRC-BREACH", "evidence_id": "EV-000203"}
        ],
        "infrastructure": [
            {"type": "certificate", "fingerprint": "SHA256:7B8A91C042E3FA71", "details": {"issuer": "Let's Encrypt / Tor Proxy"}, "evidence_id": "EV-000204"},
            {"type": "ip", "fingerprint": "185.220.101.99", "details": {"asn": "AS44552", "country": "NL"}, "evidence_id": "EV-000205"}
        ],
        "evidence_pool": [
            {"id": "EV-000201", "source": "SRC-BREACH", "title": "Handle Registration", "timestamp": "2026-08-17T19:00:00Z"},
            {"id": "EV-000202", "source": "SRC-BREACH", "title": "PGP Key Rotation", "timestamp": "2026-08-18T10:00:00Z"},
            {"id": "EV-000203", "source": "SRC-BREACH", "title": "Deposit Address Match", "timestamp": "2026-08-20T20:30:00Z"},
            {"id": "EV-000204", "source": "SRC-SENSOR", "title": "TLS Cert Fingerprint 7B8A Reuse", "timestamp": "2026-08-22T04:15:00Z"}
        ]
    }

    return persona_a, persona_b
