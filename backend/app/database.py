import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from .services.graph_engine import graph_engine
from .services.stylometry_engine import stylometry_engine
from .services.tor_recon import tor_recon_engine

DATA_DIR = os.path.dirname(__file__)
INTEL_FILE_PATH = os.path.join(DATA_DIR, "data", "initial_intel.json")

class ThreatIntelDatabase:
    """
    Central Threat Intelligence & Forensic Store.
    Provides indexing, search, timeline filtering, and connects
    the graph and AI stylometry modules.
    """

    def __init__(self):
        self.actors: Dict[str, Dict[str, Any]] = {}
        self.live_telemetry_feed: List[Dict[str, Any]] = []
        self._load_initial_data()

    def _load_initial_data(self):
        if os.path.exists(INTEL_FILE_PATH):
            with open(INTEL_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                for actor in data:
                    self.actors[actor["id"]] = actor

        # Train engines
        self.refresh_engines()

        # Seed initial telemetry feed
        self._seed_telemetry()

    def refresh_engines(self):
        actor_list = list(self.actors.values())
        recon_list = tor_recon_engine.list_all_recon_targets()
        
        # Build graph
        graph_engine.build_from_dataset(actor_list, recon_list)
        
        # Train AI stylometry vectorizer
        stylometry_engine.train_or_update(actor_list)

    def _seed_telemetry(self):
        self.live_telemetry_feed = [
            {
                "id": "FEED-091",
                "timestamp": "2026-09-25T14:22:10Z",
                "source": "BreachForums v4",
                "event_type": "FORUM_POST",
                "author": "KryptonGhost",
                "summary": "New thread: 'WTS Domain Admin Fortune 500 Healthcare - 5 BTC'",
                "correlated_actor_id": "ACTOR-001",
                "confidence": 94
            },
            {
                "id": "FEED-090",
                "timestamp": "2026-09-25T12:05:44Z",
                "source": "Tor Recon Sensor #4",
                "event_type": "INFRA_MISCONFIG_DETECTED",
                "author": "System Sensor",
                "summary": "Apache /server-status leak detected on dreadmarket736...onion exposing internal host api.dread-infra.is",
                "correlated_actor_id": "ACTOR-001",
                "confidence": 96
            },
            {
                "id": "FEED-089",
                "timestamp": "2026-09-24T21:18:00Z",
                "source": "LockBit Extortion Mirror",
                "event_type": "EXTORTION_DEADLINE",
                "author": "LockBit_Syndicate_Op",
                "summary": "Countdown expired for target victim. 140GB unencrypted CAD diagrams leaked.",
                "correlated_actor_id": "ACTOR-002",
                "confidence": 98
            },
            {
                "id": "FEED-088",
                "timestamp": "2026-09-24T18:40:12Z",
                "source": "Bohemia Marketplace",
                "event_type": "ESCROW_TRANSACTION",
                "author": "ViperVendor",
                "summary": "12.4 XMR escrow payout released to wallet 48edfHu7V9Z84Yzz...",
                "correlated_actor_id": "ACTOR-003",
                "confidence": 92
            },
            {
                "id": "FEED-087",
                "timestamp": "2026-09-24T11:02:50Z",
                "source": "Exploit.in",
                "event_type": "ZERO_DAY_LISTING",
                "author": "ZeroDay_Broker",
                "summary": "Listing posted: 'FortiGate SSL-VPN Unauthenticated RCE PoC' - $80k escrow",
                "correlated_actor_id": "ACTOR-005",
                "confidence": 91
            }
        ]

    def get_all_actors(
        self,
        category: Optional[str] = None,
        source: Optional[str] = None,
        min_confidence: Optional[int] = None,
        query: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        results = []
        for actor in self.actors.values():
            # Category filter
            if category and category.lower() not in actor.get("category", "").lower():
                continue
            # Source filter
            if source and not any(source.lower() in s.lower() for s in actor.get("sources", [])):
                continue
            # Confidence filter
            if min_confidence is not None and actor.get("attribution_confidence", 0) < min_confidence:
                continue
            # Date filter (using last_seen or first_seen)
            if start_date and actor.get("last_seen", "") < start_date:
                continue
            if end_date and actor.get("first_seen", "") > end_date:
                continue
            # Text query
            if query:
                q = query.lower()
                blob = json.dumps(actor).lower()
                if q not in blob:
                    continue

            results.append(actor)
        return results

    def get_actor_by_id(self, actor_id: str) -> Optional[Dict[str, Any]]:
        return self.actors.get(actor_id)

    def add_or_update_actor(self, actor_data: Dict[str, Any]) -> Dict[str, Any]:
        actor_id = actor_data.get("id")
        if not actor_id:
            actor_id = f"ACTOR-{len(self.actors) + 1:03d}"
            actor_data["id"] = actor_id
        
        self.actors[actor_id] = actor_data
        self.refresh_engines()
        return actor_data

    def get_summary_stats(self) -> Dict[str, Any]:
        total_actors = len(self.actors)
        total_wallets = sum(len(a.get("crypto_wallets", [])) for a in self.actors.values())
        total_pgp_keys = sum(len(a.get("pgp_keys", [])) for a in self.actors.values())
        total_onions = sum(len(a.get("associated_onions", [])) for a in self.actors.values())
        unmasked_suspects = sum(1 for a in self.actors.values() if a.get("real_world_suspect"))
        avg_confidence = round(sum(a.get("attribution_confidence", 0) for a in self.actors.values()) / max(1, total_actors), 1)

        category_distribution = {}
        for a in self.actors.values():
            cat = a.get("category", "Other")
            category_distribution[cat] = category_distribution.get(cat, 0) + 1

        return {
            "total_actors": total_actors,
            "total_crypto_wallets": total_wallets,
            "total_pgp_keys": total_pgp_keys,
            "monitored_onion_services": total_onions,
            "unmasked_real_world_suspects": unmasked_suspects,
            "avg_attribution_confidence": avg_confidence,
            "category_distribution": category_distribution,
            "telemetry_event_count": len(self.live_telemetry_feed)
        }

db = ThreatIntelDatabase()
