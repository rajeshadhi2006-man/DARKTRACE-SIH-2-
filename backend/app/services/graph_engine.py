import networkx as nx
from typing import Dict, Any, List, Optional

class ThreatGraphEngine:
    """
    Cross-Marketplace Entity Resolution Graph Engine.
    Maps handles, PGP keys, crypto wallets, communications, hidden services,
    clearnet IPs, and suspected real-world entities into a multi-relational graph.
    """

    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def build_from_dataset(self, actors: List[Dict[str, Any]], recon_targets: List[Dict[str, Any]]):
        """Builds the in-memory NetworkX relationship graph from actor and recon datasets."""
        self.graph.clear()

        # Ingest Actors
        for actor in actors:
            actor_id = actor["id"]
            self.graph.add_node(
                actor_id,
                label=actor["primary_handle"],
                type="actor",
                category=actor["category"],
                threat_level=actor["threat_level"],
                confidence=actor["attribution_confidence"],
                status=actor["status"]
            )

            # Handles across forums
            for alias in actor.get("aliases", []):
                handle_node = f"handle:{alias}"
                self.graph.add_node(handle_node, label=alias, type="handle")
                self.graph.add_edge(actor_id, handle_node, relation="USES_HANDLE", weight=1.0)

            # Marketplace presence
            for source in actor.get("sources", []):
                market_node = f"market:{source.lower().replace(' ', '_')}"
                self.graph.add_node(market_node, label=source, type="marketplace")
                self.graph.add_edge(actor_id, market_node, relation="OPERATES_ON", weight=0.8)

            # PGP Keys
            for pgp in actor.get("pgp_keys", []):
                pgp_id = f"pgp:{pgp['fingerprint'][-8:]}"
                self.graph.add_node(
                    pgp_id,
                    label=f"PGP: {pgp['fingerprint'][-8:]}",
                    type="pgp_key",
                    fingerprint=pgp["fingerprint"],
                    email=pgp.get("email_identity", "")
                )
                self.graph.add_edge(actor_id, pgp_id, relation="OWNS_PGP_KEY", weight=1.0)

            # Crypto Wallets
            for wallet in actor.get("crypto_wallets", []):
                addr_short = wallet["address"][:8] + "..." + wallet["address"][-6:]
                wallet_id = f"wallet:{wallet['address']}"
                self.graph.add_node(
                    wallet_id,
                    label=f"{wallet['currency']}: {addr_short}",
                    type="wallet",
                    currency=wallet["currency"],
                    full_address=wallet["address"]
                )
                self.graph.add_edge(actor_id, wallet_id, relation="CONTROLS_WALLET", weight=0.95)

            # Communications
            for comm in actor.get("communications", []):
                comm_id = f"comm:{comm['identifier']}"
                self.graph.add_node(
                    comm_id,
                    label=f"{comm['platform']}: {comm['identifier']}",
                    type="comm",
                    platform=comm["platform"]
                )
                self.graph.add_edge(actor_id, comm_id, relation="USES_COMMUNICATION", weight=0.9)

            # Onion services
            for onion in actor.get("associated_onions", []):
                onion_id = f"onion:{onion}"
                self.graph.add_node(
                    onion_id,
                    label=f"Tor: {onion[:10]}...",
                    type="onion",
                    onion_url=onion
                )
                self.graph.add_edge(actor_id, onion_id, relation="DEPLOYS_SERVICE", weight=0.85)

            # Real-world Suspect Link
            suspect = actor.get("real_world_suspect")
            if suspect:
                suspect_id = f"suspect:{actor_id}"
                label_text = suspect.get("probable_legal_name") or "Unmasked Suspect"
                self.graph.add_node(
                    suspect_id,
                    label=label_text,
                    type="real_person",
                    country=suspect.get("suspected_country"),
                    city=suspect.get("suspected_city"),
                    confidence=suspect.get("confidence_level")
                )
                self.graph.add_edge(actor_id, suspect_id, relation="LINKED_TO_REAL_IDENTITY", weight=0.85)

                for clearnet_acc in suspect.get("clearnet_accounts", []):
                    acc_node = f"clearnet_acc:{clearnet_acc}"
                    self.graph.add_node(acc_node, label=clearnet_acc, type="clearnet_account")
                    self.graph.add_edge(suspect_id, acc_node, relation="AUTHENTICATES_AS", weight=0.9)

                for ip in suspect.get("associated_ips", []):
                    ip_node = f"ip:{ip}"
                    self.graph.add_node(ip_node, label=f"Origin IP: {ip}", type="clearnet_ip")
                    self.graph.add_edge(suspect_id, ip_node, relation="LOGGED_FROM_IP", weight=0.9)

        # Cross-link Recon Targets
        for target in recon_targets:
            onion_id = f"onion:{target['onion_address']}"
            if onion_id in self.graph:
                clearnet_ip = target.get("correlated_clearnet_ip")
                if clearnet_ip:
                    ip_node = f"ip:{clearnet_ip}"
                    self.graph.add_node(
                        ip_node,
                        label=f"Origin IP: {clearnet_ip}",
                        type="clearnet_ip",
                        asn=target.get("asn"),
                        country=target.get("country")
                    )
                    self.graph.add_edge(
                        onion_id,
                        ip_node,
                        relation="ORIGIN_SERVER_MISCONFIG",
                        weight=0.95,
                        evidence="Exposed server-status / TLS Cert SAN correlation"
                    )

        # Add trust and escrow relationships between actors/markets
        self._add_inter_actor_trust_links()

    def _add_inter_actor_trust_links(self):
        # Known syndication or money-laundering / escrow links
        trust_links = [
            ("ACTOR-001", "ACTOR-003", "ESCROW_COLLATERAL", "Shared multi-sig escrow wallet on Bohemian market"),
            ("ACTOR-002", "ACTOR-005", "CREDENTIAL_RESALE", "Initial access brokering handoff to ransomware syndicate"),
            ("ACTOR-004", "ACTOR-001", "LAUNDERING_HOP", "Direct Monero-to-Tether mixing service chain"),
            ("ACTOR-005", "ACTOR-003", "EXPLOIT_KIT_LICENSING", "Private Crypter licensing verified via PGP signed message")
        ]
        for src, dst, rel, note in trust_links:
            if src in self.graph and dst in self.graph:
                self.graph.add_edge(src, dst, relation=rel, weight=0.75, note=note)

    def export_graph_for_visualization(self, actor_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Exports nodes and edges formatted for Vis-Network and Cytoscape.js.
        Color-coded and sized according to node types.
        """
        color_map = {
            "actor": {"background": "#ef4444", "border": "#b91c1c", "highlight": "#f87171"},
            "handle": {"background": "#3b82f6", "border": "#1d4ed8", "highlight": "#60a5fa"},
            "marketplace": {"background": "#8b5cf6", "border": "#6d28d9", "highlight": "#a78bfa"},
            "pgp_key": {"background": "#eab308", "border": "#ca8a04", "highlight": "#facc15"},
            "wallet": {"background": "#10b981", "border": "#047857", "highlight": "#34d399"},
            "comm": {"background": "#06b6d4", "border": "#0891b2", "highlight": "#22d3ee"},
            "onion": {"background": "#64748b", "border": "#334155", "highlight": "#94a3b8"},
            "clearnet_ip": {"background": "#f97316", "border": "#c2410c", "highlight": "#fb923c"},
            "real_person": {"background": "#ec4899", "border": "#be185d", "highlight": "#f472b6"},
            "clearnet_account": {"background": "#14b8a6", "border": "#0f766e", "highlight": "#2dd4bf"}
        }

        icon_map = {
            "actor": "user-secret",
            "handle": "at",
            "marketplace": "store",
            "pgp_key": "key",
            "wallet": "wallet",
            "comm": "comment-dots",
            "onion": "shield-halved",
            "clearnet_ip": "server",
            "real_person": "user-check",
            "clearnet_account": "globe"
        }

        nodes = []
        edges = []

        subgraph_nodes = set()
        if actor_filter:
            if actor_filter in self.graph:
                # 2-hop neighborhood
                subgraph_nodes.add(actor_filter)
                for neighbor in self.graph.neighbors(actor_filter):
                    subgraph_nodes.add(neighbor)
                    for n2 in self.graph.neighbors(neighbor):
                        subgraph_nodes.add(n2)
                for predecessor in self.graph.predecessors(actor_filter):
                    subgraph_nodes.add(predecessor)
            else:
                subgraph_nodes = set(self.graph.nodes)
        else:
            subgraph_nodes = set(self.graph.nodes)

        for node_id in subgraph_nodes:
            data = self.graph.nodes[node_id]
            ntype = data.get("type", "unknown")
            color = color_map.get(ntype, {"background": "#94a3b8", "border": "#475569", "highlight": "#cbd5e1"})
            
            # Size
            size = 28 if ntype == "actor" else (32 if ntype == "real_person" else 18)

            nodes.append({
                "id": node_id,
                "label": data.get("label", node_id),
                "title": f"Type: {ntype.upper()}<br>ID: {node_id}<br>" + "<br>".join([f"{k}: {v}" for k, v in data.items() if k not in ["type", "label"]]),
                "type": ntype,
                "color": color,
                "size": size,
                "shape": "dot" if ntype not in ["actor", "real_person"] else "diamond",
                "font": {"color": "#f8fafc", "size": 12, "face": "Inter, sans-serif"},
                "meta": data
            })

        for u, v, key, edge_data in self.graph.edges(keys=True, data=True):
            if u in subgraph_nodes and v in subgraph_nodes:
                relation = edge_data.get("relation", "RELATED_TO")
                edges.append({
                    "id": f"{u}->{v}:{key}",
                    "from": u,
                    "to": v,
                    "label": relation.replace("_", " "),
                    "arrows": "to",
                    "color": {"color": "#475569", "highlight": "#38bdf8", "hover": "#60a5fa"},
                    "font": {"color": "#94a3b8", "size": 9, "align": "middle", "background": "#0f172a"},
                    "relation": relation,
                    "weight": edge_data.get("weight", 0.5),
                    "note": edge_data.get("note", "")
                })

        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }

    def find_shortest_attribution_path(self, source_node: str, target_node: str) -> Optional[List[Dict[str, Any]]]:
        """Finds shortest explanatory attribution chain between darkweb handle and clearnet/suspect node."""
        try:
            path = nx.shortest_path(self.graph.to_undirected(), source=source_node, target=target_node)
            steps = []
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                u_data = self.graph.nodes.get(u, {})
                v_data = self.graph.nodes.get(v, {})
                steps.append({
                    "from_node": u,
                    "from_label": u_data.get("label", u),
                    "from_type": u_data.get("type", "unknown"),
                    "to_node": v,
                    "to_label": v_data.get("label", v),
                    "to_type": v_data.get("type", "unknown")
                })
            return steps
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

graph_engine = ThreatGraphEngine()
