import networkx as nx
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ...models.entities import (
    Actor, Persona, Handle, PGPKey, Wallet, Domain, Infrastructure, Relationship
)

class GraphIntelligenceEngine:
    """
    Forensic Multi-Relational Graph Analysis Engine.
    Executes shortest attribution path discovery, community syndicate clustering,
    and centrality metrics across underground entities.
    """

    def build_networkx_graph(self, db: Session, actor_filter: Optional[str] = None) -> nx.MultiDiGraph:
        """Constructs an in-memory NetworkX directed multi-graph from the relational intelligence database."""
        G = nx.MultiDiGraph()

        # 1. Actors
        actor_query = db.query(Actor)
        if actor_filter:
            actor_query = actor_query.filter(Actor.id == actor_filter)
        actors = actor_query.all()
        for a in actors:
            G.add_node(
                a.id,
                label=a.primary_name,
                type="Actor",
                threat_level=a.threat_level,
                category=a.threat_category,
                confidence=a.confidence_score
            )

        # 2. Personas
        personas = db.query(Persona).all()
        for p in personas:
            G.add_node(
                p.id,
                label=f"{p.canonical_handle} ({p.platform})",
                type="Persona",
                platform=p.platform,
                handle=p.canonical_handle
            )
            if p.actor_id and (not actor_filter or p.actor_id == actor_filter):
                G.add_edge(
                    p.actor_id,
                    p.id,
                    relation="CONTROLS_PERSONA",
                    weight=0.1,
                    confidence=0.95
                )

        # 3. Handles
        handles = db.query(Handle).all()
        for h in handles:
            G.add_node(h.id, label=h.original_value, type="Handle", platform=h.platform)
            if h.persona_id:
                G.add_edge(h.persona_id, h.id, relation="USES_HANDLE", weight=0.1, confidence=0.95)

        # 4. PGP Keys
        pgp_keys = db.query(PGPKey).all()
        for k in pgp_keys:
            G.add_node(
                k.id,
                label=f"PGP: {k.key_id or k.fingerprint[-8:]}",
                type="PGPKey",
                fingerprint=k.fingerprint,
                bits=k.bit_length
            )

        # 5. Wallets
        wallets = db.query(Wallet).all()
        for w in wallets:
            w_short = w.address[:6] + "..." + w.address[-4:]
            G.add_node(
                w.id,
                label=f"{w.currency}: {w_short}",
                type="Wallet",
                currency=w.currency,
                address=w.address
            )

        # 6. Domains & Infrastructure
        domains = db.query(Domain).all()
        for d in domains:
            G.add_node(d.id, label=d.domain_name, type="Domain", is_onion=d.is_onion)

        infras = db.query(Infrastructure).all()
        for inf in infras:
            G.add_node(
                inf.id,
                label=f"{inf.indicator_type}: {inf.indicator_value[:18]}",
                type="Infrastructure",
                indicator_type=inf.indicator_type,
                clearnet=inf.clearnet_correlation,
                asn=inf.asn_isp
            )

        # 7. Relationships
        rels = db.query(Relationship).all()
        for r in rels:
            cost = max(0.01, round(1.0 - (r.confidence or 0.7), 3))
            G.add_edge(
                r.source_entity_id,
                r.target_entity_id,
                relation=r.relationship_type,
                confidence=r.confidence,
                evidence_id=r.evidence_id,
                weight=cost
            )

        return G

    def find_shortest_attribution_path(
        self,
        db: Session,
        source_id: str,
        target_id: str
    ) -> Dict[str, Any]:
        """
        Calculates the evidentiary bridge linking an anonymous darknet handle
        to an unmasked clearnet origin or real-world entity.
        """
        G = self.build_networkx_graph(db)

        if source_id not in G:
            return {"found": False, "error": f"Source entity '{source_id}' not found in intelligence graph"}
        if target_id not in G:
            return {"found": False, "error": f"Target entity '{target_id}' not found in intelligence graph"}

        U = G.to_undirected()
        try:
            path_nodes = nx.shortest_path(U, source=source_id, target=target_id, weight="weight")
            path_length = nx.shortest_path_length(U, source=source_id, target=target_id, weight="weight")
        except nx.NetworkXNoPath:
            return {
                "found": False,
                "error": f"No attribution path exists between '{source_id}' and '{target_id}'"
            }

        steps = []
        for i in range(len(path_nodes) - 1):
            u = path_nodes[i]
            v = path_nodes[i + 1]
            u_data = G.nodes.get(u, {})
            v_data = G.nodes.get(v, {})

            edge_data = {}
            if G.has_edge(u, v):
                edge_data = G.get_edge_data(u, v).get(0, {})
            elif G.has_edge(v, u):
                edge_data = G.get_edge_data(v, u).get(0, {})

            steps.append({
                "step": i + 1,
                "source": {"id": u, "label": u_data.get("label", u), "type": u_data.get("type", "Unknown")},
                "target": {"id": v, "label": v_data.get("label", v), "type": v_data.get("type", "Unknown")},
                "relation": edge_data.get("relation", "CONNECTED_TO"),
                "confidence": edge_data.get("confidence", 0.8),
                "evidence_id": edge_data.get("evidence_id")
            })

        return {
            "found": True,
            "source_id": source_id,
            "target_id": target_id,
            "path_hop_count": len(path_nodes) - 1,
            "composite_distance_cost": round(path_length, 4),
            "evidentiary_steps": steps
        }

    def detect_syndicate_clusters(self, db: Session) -> Dict[str, Any]:
        """
        Uses greedy modularity community detection to discover
        interconnected dark web threat clusters and shared infrastructure syndicates.
        """
        G = self.build_networkx_graph(db)
        U = G.to_undirected()

        isolates = list(nx.isolates(U))
        U.remove_nodes_from(isolates)

        communities = list(nx.algorithms.community.greedy_modularity_communities(U))
        clusters = []
        centrality = nx.degree_centrality(U)

        for idx, comm in enumerate(communities):
            members = []
            for node_id in comm:
                ndata = G.nodes.get(node_id, {})
                members.append({
                    "id": node_id,
                    "label": ndata.get("label", node_id),
                    "type": ndata.get("type", "Unknown"),
                    "centrality_score": round(centrality.get(node_id, 0.0), 4)
                })

            members.sort(key=lambda m: m["centrality_score"], reverse=True)
            clusters.append({
                "cluster_id": f"CLUSTER-{idx + 1:02d}",
                "total_entities": len(members),
                "key_pivot_node": members[0] if members else None,
                "members": members[:15]  # Top 15 prominent members
            })

        clusters.sort(key=lambda c: c["total_entities"], reverse=True)

        return {
            "total_clusters_detected": len(clusters),
            "isolated_entities_excluded": len(isolates),
            "clusters": clusters[:10]  # Top 10 primary clusters
        }

graph_engine = GraphIntelligenceEngine()
