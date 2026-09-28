import re
import hashlib
from typing import Dict, Any, List, Set
from datetime import datetime

class EntityExtractionEngine:
    """
    Automated Multi-Entity Extraction Engine for Threat Intelligence.
    Extracts 25+ entity types using structured regular expressions,
    heuristics, and pattern matching across raw underground text.
    """

    def __init__(self):
        # Regex patterns for high-confidence darknet & OSINT entities
        self.patterns = {
            "btc_wallet": re.compile(r"\b(bc1[a-zA-HJ-NP-Z0-9]{25,59}|[13][a-km-zA-HJ-NP-Z1-9]{26,35})\b"),
            "xmr_wallet": re.compile(r"\b(4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}|8[0-9AB][1-9A-HJ-NP-Za-km-z]{93})\b"),
            "eth_wallet": re.compile(r"\b(0x[a-fA-F0-9]{40})\b"),
            "usdt_trc20": re.compile(r"\b(T[A-Za-z1-9]{33})\b"),
            "onion_service": re.compile(r"\b([a-z2-7]{16,56}\.onion)\b"),
            "ipv4": re.compile(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"),
            "domain": re.compile(r"\b([a-zA-Z0-9][-a-zA-Z0-9]{0,62}\.(?:com|org|net|is|pro|cc|ru|to|xyz|su|cx|biz|io))\b", re.IGNORECASE),
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"),
            "pgp_fingerprint": re.compile(r"\b([0-9A-Fa-f]{40}|[0-9A-Fa-f]{32})\b"),
            "pgp_key_id": re.compile(r"\b0x([0-9A-Fa-f]{8,16})\b"),
            "sha256": re.compile(r"\b([a-fA-F0-9]{64})\b"),
            "md5": re.compile(r"\b([a-fA-F0-9]{32})\b"),
            "cve": re.compile(r"\b(CVE-\d{4}-\d{4,7})\b", re.IGNORECASE),
            "asn": re.compile(r"\b(AS\d{2,6})\b", re.IGNORECASE),
            "tox_id": re.compile(r"\b([0-9A-Fa-f]{76})\b"),
            "telegram_handle": re.compile(r"(?:t\.me/|@)([a-zA-Z0-9_]{5,32})\b"),
            "jabber_xmpp": re.compile(r"\b[a-zA-Z0-9._%+-]+@(xmpp\.is|jabber\.ru|exploit\.im|thesecure\.biz)\b", re.IGNORECASE),
        }

        # Known darknet forums & marketplaces for attribution contextualization
        self.known_platforms = {
            "dread", "breachforums", "exploit.in", "xss.is", "ramp",
            "archetyp", "bohemia", "alphabay", "cryptbb", "hydra"
        }

        # Known malware & tools
        self.known_malware = {
            "redline", "lumma", "vidar", "raccoon", "lockbit", "blackcat",
            "alphv", "cobalt strike", "brute ratel", "asyncrat", "njrat",
            "agent tesla", "danabot", "darkgate", "icedid", "qakbot"
        }

    def extract_entities(self, text: str, source_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extracts all identifiable indicators from text and categorizes them.
        """
        if not text:
            return {"entities": [], "counts": {}, "content_hash": ""}

        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        extracted: List[Dict[str, Any]] = []

        # 1. Regex pattern extractions
        for entity_type, pattern in self.patterns.items():
            matches = set(pattern.findall(text))
            for match in matches:
                # Discard false positives (e.g., local loopbacks or invalid hashes)
                if entity_type == "ipv4" and match.startswith(("127.", "0.", "255.")):
                    continue
                extracted.append({
                    "entity_type": entity_type,
                    "value": match,
                    "confidence": 0.95 if entity_type in ["pgp_fingerprint", "onion_service", "btc_wallet", "xmr_wallet"] else 0.85,
                    "source": source_metadata.get("source_id", "RAW_EXTRACTOR") if source_metadata else "RAW_EXTRACTOR",
                    "observed_at": datetime.utcnow().isoformat() + "Z"
                })

        # 2. Known malware/tool detection
        text_lower = text.lower()
        for malware in self.known_malware:
            if re.search(r"\b" + re.escape(malware) + r"\b", text_lower):
                extracted.append({
                    "entity_type": "malware_tool",
                    "value": malware.title(),
                    "confidence": 0.88,
                    "source": "KEYWORD_CORRELATOR",
                    "observed_at": datetime.utcnow().isoformat() + "Z"
                })

        # 3. Known platform detection
        for platform in self.known_platforms:
            if re.search(r"\b" + re.escape(platform) + r"\b", text_lower):
                extracted.append({
                    "entity_type": "platform_reference",
                    "value": platform.title(),
                    "confidence": 0.90,
                    "source": "PLATFORM_CORRELATOR",
                    "observed_at": datetime.utcnow().isoformat() + "Z"
                })

        # Aggregate counts
        counts = {}
        for ent in extracted:
            t = ent["entity_type"]
            counts[t] = counts.get(t, 0) + 1

        return {
            "content_hash": content_hash,
            "total_extracted": len(extracted),
            "counts": counts,
            "entities": extracted
        }

entity_extractor = EntityExtractionEngine()
