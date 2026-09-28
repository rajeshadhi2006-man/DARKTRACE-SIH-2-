from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.connection import get_db, get_neo4j_session
from ..models.entities import Actor, Persona, Handle, PGPKey, Wallet, Infrastructure, Relationship, Evidence
from ..security.auth import get_current_user
from ..services.graph_analysis.engine import graph_engine

router = APIRouter(prefix="/graph", tags=["Intelligence Graph"])

@router.get("/attribution-path")
def get_attribution_path(
    source_id: str,
    target_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Finds the shortest weighted evidentiary attribution path connecting
    an anonymous handle to an unmasked infrastructure or real-world entity.
    """
    result = graph_engine.find_shortest_attribution_path(db, source_id, target_id)
    if not result.get("found"):
        raise HTTPException(status_code=404, detail=result.get("error", "No attribution path found"))
    return result

@router.get("/clusters")
def get_syndicate_clusters(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Performs community detection (greedy modularity) across the entity network
    to identify tightly-knit darknet threat syndicates and high-centrality brokers.
    """
    return graph_engine.detect_syndicate_clusters(db)

@router.get("/{actor_id}")
def get_actor_subgraph(
    actor_id: str,
    depth: int = 2,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Returns Cytoscape-compatible nodes and edges for an actor's entity network.
    Queries Neo4j if available, or synthesizes progressive graph from relational data.
    """
    actor = db.query(Actor).filter(Actor.id == actor_id).first()
    if not actor:
        raise HTTPException(status_code=404, detail="Actor not found")

    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    seen_nodes = set()

    def add_node(nid: str, label: str, ntype: str, props: Dict[str, Any]):
        if nid not in seen_nodes:
            seen_nodes.add(nid)
            nodes.append({
                "data": {
                    "id": nid,
                    "label": label,
                    "type": ntype,
                    **props
                }
            })

    def add_edge(eid: str, src: str, dst: str, rel_type: str, conf: float, evid: Optional[str] = None):
        edges.append({
            "data": {
                "id": eid,
                "source": src,
                "target": dst,
                "label": rel_type.replace("_", " "),
                "confidence": conf,
                "evidence_id": evid
            }
        })

    # Root Actor Node
    add_node(actor.id, actor.primary_name, "Actor", {
        "category": actor.threat_category,
        "threat_level": actor.threat_level,
        "confidence": actor.confidence_score
    })

    # Connected Personas
    for p in actor.personas:
        add_node(p.id, p.canonical_handle, "Persona", {
            "platform": p.platform,
            "activity_count": p.activity_count,
            "confidence": p.confidence
        })
        add_edge(f"edge_{actor.id}_{p.id}", actor.id, p.id, "OPERATES_PERSONA", 0.95)

        # Handles
        for h in p.handles:
            hid = f"hnd_{h.id}"
            add_node(hid, h.original_value, "Handle", {"platform": h.platform})
            add_edge(f"edge_{p.id}_{hid}", p.id, hid, "USES_HANDLE", 0.95)

        # PGP Keys, Wallets, and Infra linked via Relationships
        rel_links = db.query(Relationship).filter(
            (Relationship.source_entity_id == p.id) | (Relationship.target_entity_id == p.id)
        ).all()

        for r in rel_links:
            other_id = r.target_entity_id if r.source_entity_id == p.id else r.source_entity_id
            
            # Identify node type
            if other_id.startswith("KEY-"):
                k = db.query(PGPKey).filter(PGPKey.id == other_id).first()
                if k:
                    add_node(k.id, f"PGP: {k.key_id}", "PGPKey", {"fingerprint": k.fingerprint, "bits": k.bit_length})
                    add_edge(r.id, p.id, k.id, r.relationship_type, r.confidence, r.evidence_id)
            elif other_id.startswith("WALLET-"):
                w = db.query(Wallet).filter(Wallet.id == other_id).first()
                if w:
                    add_node(w.id, f"{w.currency}: {w.address[:8]}...", "Wallet", {"currency": w.currency, "address": w.address})
                    add_edge(r.id, p.id, w.id, r.relationship_type, r.confidence, r.evidence_id)
            elif other_id.startswith("INF-"):
                inf = db.query(Infrastructure).filter(Infrastructure.id == other_id).first()
                if inf:
                    add_node(inf.id, f"{inf.indicator_type}: {inf.indicator_value[:14]}", "Infrastructure", {"type": inf.indicator_type, "asn": inf.asn_isp})
                    add_edge(r.id, p.id, inf.id, r.relationship_type, r.confidence, r.evidence_id)
            elif other_id.startswith("PER-"):
                other_p = db.query(Persona).filter(Persona.id == other_id).first()
                if other_p:
                    add_node(other_p.id, other_p.canonical_handle, "Persona", {"platform": other_p.platform})
                    add_edge(r.id, r.source_entity_id, r.target_entity_id, r.relationship_type, r.confidence, r.evidence_id)

    return {
        "actor_id": actor_id,
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges)
    }
