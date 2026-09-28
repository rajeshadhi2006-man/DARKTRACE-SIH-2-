from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CryptoWallet(BaseModel):
    currency: str  # BTC, XMR, ETH, USDT
    address: str
    first_seen: Optional[str] = None
    total_received: Optional[str] = None
    cluster_tags: List[str] = []

class PGPKey(BaseModel):
    key_id: str
    fingerprint: str
    email_identity: Optional[str] = None
    bits: int = 4096
    created_date: Optional[str] = None

class CommunicationID(BaseModel):
    platform: str  # Jabber/XMPP, Telegram, Tox, Session
    identifier: str

class HiddenServiceIndicator(BaseModel):
    onion_address: str
    misconfiguration_type: str  # 'exposed_server_status', 'ssl_clearnet_san', 'favicon_hash_match', 'banner_leak'
    details: str
    probable_clearnet_ip: Optional[str] = None
    clearnet_domain: Optional[str] = None
    asn_isp: Optional[str] = None
    geo_country: Optional[str] = None
    confidence_score: float = Field(default=0.85, ge=0.0, le=1.0)
    discovered_at: str

class RealWorldSuspect(BaseModel):
    probable_legal_name: Optional[str] = "Under Active Attribution"
    suspected_country: Optional[str] = None
    suspected_city: Optional[str] = None
    probable_timezone: Optional[str] = None
    clearnet_accounts: List[str] = []
    associated_ips: List[str] = []
    confidence_level: str = "High"  # Confirmed, High, Moderate, Low

class ThreatActor(BaseModel):
    id: str
    primary_handle: str
    aliases: List[str] = []
    category: str  # 'Ransomware Cartel', 'Initial Access Broker', 'Carding Syndicate', 'Data Extortionist', 'Darknet Vendor'
    attribution_confidence: int = Field(default=85, ge=0, le=100)
    threat_level: str = "CRITICAL"  # CRITICAL, HIGH, MEDIUM, LOW
    status: str = "ACTIVE"  # ACTIVE, DORMANT, ARRESTED, REBRANDED
    first_seen: str
    last_seen: str
    sources: List[str] = []  # Dread, Exploit.in, BreachForums, AlphaBay, Bohemia, etc.
    pgp_keys: List[PGPKey] = []
    crypto_wallets: List[CryptoWallet] = []
    communications: List[CommunicationID] = []
    associated_onions: List[str] = []
    real_world_suspect: Optional[RealWorldSuspect] = None
    sample_posts: List[str] = []
    active_hours_utc: List[int] = []  # Distribution of posting hours 0-23
    summary: str

class StylometryAnalysisRequest(BaseModel):
    text: str
    candidate_actor_ids: Optional[List[str]] = None

class StylometryFeatureBreakdown(BaseModel):
    avg_sentence_length: float
    avg_word_length: float
    lexical_richness: float
    punctuation_entropy: float
    uppercase_ratio: float
    function_word_signature: Dict[str, float]
    detected_slang_jargon: List[str]

class StylometryComparisonResult(BaseModel):
    actor_id: str
    primary_handle: str
    similarity_score: float
    attribution_level: str
    confidence_percentage: int
    matching_markers: List[str]
    estimated_timezone: str

class OnionScanRequest(BaseModel):
    onion_url: str
    deep_scan: bool = True

class OnionScanResult(BaseModel):
    onion_url: str
    scan_timestamp: str
    status: str
    title: Optional[str] = None
    server_header: Optional[str] = None
    favicon_murmur3: Optional[int] = None
    exposed_misconfigurations: List[Dict[str, Any]] = []
    extracted_indicators: Dict[str, List[str]] = {
        "wallets": [],
        "pgp_fingerprints": [],
        "emails": [],
        "telegrams": []
    }
    correlated_clearnet_ip: Optional[str] = None
    correlated_clearnet_domain: Optional[str] = None
    geo_location: Optional[Dict[str, str]] = None
    de_anonymization_confidence: int = 0
    attribution_trail: List[str] = []
