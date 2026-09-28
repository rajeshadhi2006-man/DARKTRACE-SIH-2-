import re
import hashlib
import random
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ...models.entities import IntelligenceRecord, Source, Evidence, AuditLog

import uuid

DARKNET_SIMULATED_INTERCEPTS = [
    {
        "source_id": "SRC-BREACH",
        "source_name": "BreachForums v4",
        "author": "ViperZero",
        "raw_text": (
            "Exclusive database leak: Financial services portal in Southeast Asia breached. "
            "1.8M KYC records, salted hashes, national IDs. Bids start at 15 XMR. "
            "PGP Key ID: 0x9B2C4E1A (Fingerprint: 8A7B6C5D4E3F2A1B0C9D8E7F6A5B4C3D2E1F0A9B). "
            "Deposit collateral to XMR wallet: 888tNkZrPN6JsEgekjMnABU4TBzc2Dt29EPAvkFxbTNsLTGnqFTv28RcyR44FKa6KN22gqEBCPr4FnElzqY2R44FKa6KN22. "
            "Escrow available via Jabber: viperzero@xmpp.is"
        ),
        "category": "Data Breach & Access Broker"
    },
    {
        "source_id": "SRC-DREAD",
        "source_name": "Dread Underground Forum",
        "author": "Cipher_Ghost",
        "raw_text": (
            "FUD Crypter service updated for Windows 11 24H2 Defender bypass. "
            "0/72 Runtime detections verified on DynCheck. "
            "Host hidden service online at: http://cipherghost7x2u9p4q.onion. "
            "Clearnet staging mirror detected at IP 185.220.101.42 (AS200052). "
            "Payment BTC only: bc1q8w7x6y5z4a3b2c1d0e9f8g7h6i5j4k3l2m1n0. "
            "Contact Tox: 76A28E3490BCDF21984712093847120938471209384712093847120938471209"
        ),
        "category": "Malware & Cryptor Infrastructure"
    },
    {
        "source_id": "SRC-DREAD",
        "source_name": "Archetyp Market",
        "author": "NordicChemicals",
        "raw_text": (
            "Direct bulk supplies: Research chemicals and reagent precursors. "
            "Vacuum-sealed stealth dispatch across EU/Schengen. "
            "Escrow collateral: 3.5 BTC locked in 3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy. "
            "Official PGP: 4096R/B3D4F5A6 (Fingerprint: 1F2E3D4C5B6A7F8E9D0C1B2A3F4E5D6C7B8A9F0E)."
        ),
        "category": "Contraband Marketplace"
    },
    {
        "source_id": "SRC-BREACH",
        "source_name": "Exploit.in Mirror",
        "author": "KernelPanik_0day",
        "raw_text": (
            "Priv8 RCE weaponized exploit targeting enterprise VPN gateway appliances (CVE-2026-9812). "
            "Complete unauthenticated root access with reverse interactive shell. "
            "Price: $80,000 USDT (TRC-20: TXx98K1mPqL7nR3sT5vW8yZ2bN4cE6gH0j). "
            "Staging server active at 91.215.85.17 (AS51852 AS-GLOBAL-LTD)."
        ),
        "category": "Weaponized Exploit Broker"
    },
    {
        "source_id": "SRC-DREAD",
        "source_name": "XSS Underground Portal",
        "author": "VoidReaper",
        "raw_text": (
            "Ransomware-as-a-Service (RaaS) partner recruitment: 80/20 profit split. "
            "Full automated extortion blog hosted at: http://voidreap5xkz3m4a.onion. "
            "Collateral BTC escrow: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa. "
            "Decentralized Tox contact: 89B37E4190BCDF21984712093847120938471209384712093847120938471211"
        ),
        "category": "Ransomware Operations"
    },
    {
        "source_id": "SRC-BREACH",
        "source_name": "RAMP Russian Market",
        "author": "SpecterNet",
        "raw_text": (
            "Bulletproof reverse proxy and fast-flux CDN cluster for botnet C2 resilience. "
            "Egress traffic forwarded through IP 194.26.29.112 (AS44050 BGP-ANON). "
            "PGP Key Fingerprint: 4E5F6A7B8C9D0E1F2A3B4C5D6E7F8A9B0C1D2E3F. "
            "Monero address: 44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otRfh3XUQCNPr2emGJAZ6UPZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ"
        ),
        "category": "Bulletproof Hosting Infrastructure"
    },
    {
        "source_id": "SRC-DREAD",
        "source_name": "Darknet Escrow Alpha",
        "author": "ViperZero",
        "raw_text": (
            "Updated telemetry mirror for banking logs. Synchronizing Tor hidden service at http://vipernet4499xxza.onion. "
            "Clearnet fallback endpoint: 195.123.246.77. "
            "Signed with master PGP key: 8A7B6C5D4E3F2A1B0C9D8E7F6A5B4C3D2E1F0A9B."
        ),
        "category": "Identity Drift & Infrastructure Shift"
    }
]

class AutonomousIntelligenceCollector:
    """
    Simulated continuous darknet crawler & interceptor.
    Harvests darknet forum posts, extracts cryptographic & network indicators,
    and indexes them with cryptographic hashes.
    """

    def __init__(self):
        # Regex indicator extractors
        self.re_btc = re.compile(r"\b(bc1[a-zA-HJ-NP-Z0-9]{25,45}|[13][a-km-zA-HJ-NP-Z1-9]{26,35})\b")
        self.re_xmr = re.compile(r"\b(8[0-9a-zA-Z]{94}|4[0-9a-zA-Z]{94})\b")
        self.re_onion = re.compile(r"\b([a-z2-7]{16,56}\.onion)\b")
        self.re_ip = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")
        self.re_fingerprint = re.compile(r"\b([0-9A-Fa-f]{32,40})\b")

    def extract_indicators(self, text: str) -> Dict[str, List[str]]:
        return {
            "btc_wallets": list(set(self.re_btc.findall(text))),
            "xmr_wallets": list(set(self.re_xmr.findall(text))),
            "onion_services": list(set(self.re_onion.findall(text))),
            "clearnet_ips": list(set(self.re_ip.findall(text))),
            "pgp_fingerprints": list(set(self.re_fingerprint.findall(text)))
        }

    def trigger_crawler_cycle(self, db: Session, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Executes a single crawl & ingestion sweep across monitored feeds."""
        feed = random.choice(DARKNET_SIMULATED_INTERCEPTS)
        raw_text = feed["raw_text"]
        content_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
        now = datetime.utcnow()

        uid = uuid.uuid4().hex[:6].upper()
        rec_id = f"OBS-AUTO-{now.strftime('%H%M%S')}-{uid}"
        record = IntelligenceRecord(
            id=rec_id,
            source_id=feed["source_id"],
            record_type="AUTONOMOUS_INTERCEPT",
            author_raw=feed["author"],
            content_raw=raw_text,
            content_sha256=content_hash,
            timestamp=now,
            confidence=0.92,
            reliability="A",
            provenance=f"Autonomous Ingestion Daemon -> {feed['source_name']}"
        )
        db.add(record)

        # Extract indicators
        extracted = self.extract_indicators(raw_text)

        # Create Evidence record matching SQLAlchemy schema
        evid_id = f"EVID-AUTO-{now.strftime('%H%M%S')}-{uid}"
        evid = Evidence(
            id=evid_id,
            source_id=feed["source_id"],
            observation_id=rec_id,
            evidence_type="IDENTITY",
            title=f"Autonomous Intercept: {feed['author']} on {feed['source_name']}",
            description=raw_text,
            content_hash=content_hash,
            confidence=0.90,
            reliability="A",
            related_entity_ids=[rec_id],
            provenance=f"Autonomous Ingestion Daemon -> {feed['source_name']} (Operator: {user_id or 'DAEMON'})"
        )
        db.add(evid)

        # Audit
        if user_id:
            audit = AuditLog(
                user_id=user_id,
                action="AUTONOMOUS_CRAWL_CYCLE",
                object_type="IntelligenceRecord",
                object_id=rec_id,
                details={"source": feed["source_name"], "extracted_indicators": extracted}
            )
            db.add(audit)

        db.commit()

        res = {
            "status": "CRAWL_CYCLE_COMPLETED",
            "record_id": rec_id,
            "evidence_id": evid_id,
            "source": feed["source_name"],
            "author": feed["author"],
            "content_hash": content_hash,
            "extracted_indicators": extracted,
            "timestamp": now.isoformat() + "Z"
        }

        # Real-time WebSocket broadcast to all connected investigator dashboards
        try:
            from ..realtime.manager import ws_manager
            ws_manager.broadcast_sync({
                "type": "NEW_DARKNET_INTERCEPT",
                "event_title": f"Live Dark Web Intercept: {feed['author']} on {feed['source_name']}",
                "source": feed["source_name"],
                "author": feed["author"],
                "data": res,
                "timestamp": now.isoformat() + "Z"
            })
        except Exception:
            pass

        return res

autonomous_collector = AutonomousIntelligenceCollector()
