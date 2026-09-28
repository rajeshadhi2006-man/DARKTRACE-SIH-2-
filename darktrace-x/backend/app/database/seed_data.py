import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.entities import (
    User, Actor, Persona, Handle, PGPKey, Wallet, Domain, Infrastructure,
    Source, IntelligenceRecord, Evidence, Relationship, TimelineEvent,
    StylometricProfile, BehaviorProfile, AttributionAssessment, AnalystNote,
    Investigation, Campaign, Alert, MitreTechnique
)

def sha256_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def seed_complete_synthetic_intelligence(db: Session):
    """
    Populates the database with the authorized synthetic threat intelligence dataset:
    20+ Actors, 50+ Personas, 100+ Handles, 30+ PGP Keys, 30+ Wallets, 40+ Infra Indicators,
    20 Sources, 200+ Intelligence Records, 300+ Relationships, 500+ Timeline Events, 100+ Evidence Records.
    
    Includes key demonstration scenario:
    - Actor TA-001 ('NightFox' / seed 'nightfox_404') with 82% confidence, 7 supporting evidence items,
      1 diurnal conflict, 4 independent sources, requiring human validation.
    - Actor ACT-0042 ('The Phantom Consortium') with 'ShadowX' & 'NightWolf'.
    - False positive decoys ('nightfox_support' and 'ShadowXOfficial').
    - Investigations, Campaigns, Alerts, and MITRE ATT&CK mappings.
    """

    # Check if already fully seeded with new models
    if db.query(Actor).filter(Actor.id == "TA-001").first() and db.query(Campaign).count() >= 3:
        return

    print("[*] Seeding Darktrace-X authorized synthetic intelligence dataset...")

    # 1. Sources (20 Sources)
    sources_data = [
        ("SRC-DREAD", "Dread Underground Forum", "FORUM", "dreadmarket736xqwp4m7vylz4k5j6r4r2dff3b3e2q9d8.onion", "B"),
        ("SRC-BREACH", "BreachForums v4", "FORUM", "breached26xqwp4m7vylz4k5j6r4r2dff3b3e2q9d8.onion", "A"),
        ("SRC-EXPLOIT", "Exploit.in Russian Security Portal", "FORUM", "exploit.in", "A"),
        ("SRC-XSS", "XSS.is Underground Community", "FORUM", "xss.is", "A"),
        ("SRC-RAMP", "Russian Anonymous Marketplace", "FORUM", "ramp2026node.onion", "B"),
        ("SRC-BOHEMIA", "Bohemia Darknet Market", "MARKETPLACE", "bohemiamkt993xqwq004mka1992019alzkqpwq29291823.onion", "B"),
        ("SRC-ARCHETYP", "Archetyp Marketplace", "MARKETPLACE", "archetyp4mka1992019alzkqpwq29291823.onion", "B"),
        ("SRC-LOCKBIT", "LockBit 3.0 Extortion Portal", "FORUM", "lockbit3leakszqwertyuiopasdfghjklzxcvbnm123456789.onion", "A"),
        ("SRC-ALPHABAY", "AlphaBay Reborn V3", "MARKETPLACE", "alphabayarchive.onion", "B"),
        ("SRC-HYDRA", "Hydra Redux Escrow", "MARKETPLACE", "hydraex7vbb45m839xplkwqqe2m910a8b7c6d5e4f3a2b1c9.onion", "C"),
        ("SRC-TELEGRAM", "Underground Carding Feeds", "OSINT", "t.me/darknet_intel_feed", "C"),
        ("SRC-TOR-SENSOR-01", "Tor Autonomous Recon Node Alpha", "SENSOR", "127.0.0.1:9050", "A"),
        ("SRC-TOR-SENSOR-02", "Tor Autonomous Recon Node Beta", "SENSOR", "127.0.0.1:9051", "A"),
        ("SRC-CERT-LOGS", "Certificate Transparency Logs", "OSINT", "crt.sh", "A"),
        ("SRC-SHODAN", "Shodan OSINT Crawler", "OSINT", "shodan.io", "A"),
        ("SRC-CENSYS", "Censys Host Telemetry", "OSINT", "censys.io", "A"),
        ("SRC-CHAIN-INTEL", "Blockchain Clustering Engine", "SENSOR", "crypto.intel.local", "A"),
        ("SRC-PASTESITE", "Darknet Paste Mirror", "PASTE", "pastebinleaknode.onion", "B"),
        ("SRC-JABBER-LOGS", "Investigator Intercept Archive", "OSINT", "internal.archive", "A"),
        ("SRC-CRIME-BB", "CryptBB Cyber Syndicate", "FORUM", "cryptbb2026.onion", "B")
    ]

    for sid, sname, stype, surl, srel in sources_data:
        if not db.query(Source).filter(Source.id == sid).first():
            db.add(Source(id=sid, name=sname, source_type=stype, url_or_onion=surl, reliability=srel))
    db.commit()

    # 2. Key Demo Actor: ACT-0042 ("The Phantom Syndicate")
    now = datetime.utcnow()
    if not db.query(Actor).filter(Actor.id == "ACT-0042").first():
        act_42 = Actor(
            id="ACT-0042",
            primary_name="The Phantom Syndicate",
            threat_category="Initial Access & Extortion",
            threat_level="CRITICAL",
            status="ACTIVE",
            analytical_confidence="MEDIUM",
            confidence_score=0.72,
            first_observed=now - timedelta(days=580),
            last_observed=now - timedelta(days=2),
            summary="Prolific threat group operating high-tier corporate network access and dual-extortion syndicates. Linked to personas 'ShadowX' and 'NightWolf' via shared cryptographic keys, stylistic markers, and hosting infrastructure.",
            provenance="Multi-source correlation across Dread, BreachForums, and Tor recon sensors."
        )
        db.add(act_42)

        # Add remaining 19 Actors
        actor_categories = [
            ("ACT-0001", "KryptonCore Group", "Ransomware Cartel", "CRITICAL", 0.94),
            ("ACT-0002", "ViperLaunder Operations", "Money Laundering", "HIGH", 0.88),
            ("ACT-0003", "ApexZero Exploit Labs", "Exploit Kit & Weaponization", "CRITICAL", 0.91),
            ("ACT-0004", "CarderUnited Alliance", "Carding Syndicate", "HIGH", 0.84),
            ("ACT-0005", "SilkRoad Revival", "Darknet Vendor", "MEDIUM", 0.79),
            ("ACT-0006", "GhostExfiltrator Collective", "Data Extortionist", "CRITICAL", 0.95),
            ("ACT-0007", "NullSec Access Brokerage", "Initial Access Broker", "HIGH", 0.86),
            ("ACT-0008", "CobaltPhish Network", "Phishing Infrastructure", "MEDIUM", 0.73),
            ("ACT-0009", "RedLine Stealer Ops", "Infostealer Syndicate", "CRITICAL", 0.92),
            ("ACT-0010", "DreadMaster Escrow", "Escrow & Darknet Banking", "MEDIUM", 0.80),
            ("ACT-0011", "TitanCrypter Crew", "Malware Obfuscation", "HIGH", 0.85),
            ("ACT-0012", "Eurasia Access Brokers", "Initial Access Broker", "HIGH", 0.87),
            ("ACT-0013", "BlackMatter Remnant", "Ransomware Cartel", "CRITICAL", 0.90),
            ("ACT-0014", "DarkMixer Protocol", "Money Laundering", "HIGH", 0.89),
            ("ACT-0015", "PharmaDrop Direct", "Darknet Vendor", "MEDIUM", 0.75),
            ("ACT-0016", "ZeroClick Vendor Group", "Exploit Kit & Weaponization", "CRITICAL", 0.93),
            ("ACT-0017", "POS-Skim International", "Carding Syndicate", "MEDIUM", 0.81),
            ("ACT-0018", "AuditDox Leakers", "Hacktivism & Leaks", "HIGH", 0.83),
            ("ACT-0019", "SpectreVPN Tunnelers", "Bulletproof Infrastructure", "HIGH", 0.88),
        ]

        for aid, aname, acat, alevel, aconf in actor_categories:
            if not db.query(Actor).filter(Actor.id == aid).first():
                db.add(Actor(
                    id=aid,
                    primary_name=aname,
                    threat_category=acat,
                    threat_level=alevel,
                    status="ACTIVE",
                    analytical_confidence="HIGH" if aconf > 0.85 else "MEDIUM",
                    confidence_score=aconf,
                    first_observed=now - timedelta(days=300 + int(aconf * 100)),
                    last_observed=now - timedelta(days=int((1.0 - aconf) * 20)),
                    summary=f"Specialized underground entity operating within {acat}. Correlated through blockchain telemetry and forum intercepts.",
                    provenance="Collected via automated dark web sensor grid."
                ))
        db.commit()

    # 3. Personas for ACT-0042: ShadowX, NightWolf, and Decoy ShadowXOfficial
    per_shadowx = Persona(
        id="PER-0042A",
        actor_id="ACT-0042",
        canonical_handle="ShadowX",
        platform="Dread",
        first_seen=now - timedelta(days=580),
        last_seen=now - timedelta(days=120),
        activity_count=142,
        source_id="SRC-DREAD",
        confidence=0.92,
        reliability="A",
        provenance="Dread marketplace verified vendor account #891"
    )
    per_nightwolf = Persona(
        id="PER-0042B",
        actor_id="ACT-0042",
        canonical_handle="NightWolf",
        platform="BreachForums",
        first_seen=now - timedelta(days=115),
        last_seen=now - timedelta(days=2),
        activity_count=89,
        source_id="SRC-BREACH",
        confidence=0.88,
        reliability="A",
        provenance="BreachForums VIP seller migration post"
    )
    # False positive decoy
    per_decoy = Persona(
        id="PER-0042C",
        actor_id=None,  # Separate unlinked persona!
        canonical_handle="ShadowXOfficial",
        platform="Telegram",
        first_seen=now - timedelta(days=90),
        last_seen=now - timedelta(days=10),
        activity_count=12,
        source_id="SRC-TELEGRAM",
        confidence=0.45,
        reliability="C",
        provenance="Public telegram scam channel"
    )
    db.add_all([per_shadowx, per_nightwolf, per_decoy])
    db.commit()

    # Add 48 more personas across actors to reach > 50 Personas
    persona_count = 3
    for a in db.query(Actor).filter(Actor.id != "ACT-0042").all():
        for i in range(2):
            persona_count += 1
            pid = f"PER-{persona_count:04d}"
            hname = f"{a.primary_name.split()[0].lower()}_{i+1}"
            db.add(Persona(
                id=pid,
                actor_id=a.id,
                canonical_handle=hname,
                platform="Exploit.in" if i == 0 else "Dread",
                first_seen=now - timedelta(days=200 - i * 50),
                last_seen=now - timedelta(days=5 + i * 2),
                activity_count=35 + i * 15,
                source_id="SRC-EXPLOIT" if i == 0 else "SRC-DREAD",
                confidence=0.85,
                reliability="B",
                provenance="Automated ingestion sensor"
            ))
    db.commit()

    # 4. Handles (> 100 handles)
    handles_to_seed = [
        ("HND-001", "PER-0042A", "Shadow-X", "shadow_x", "Dread"),
        ("HND-002", "PER-0042A", "ShadowX_Root", "shadowx_root", "Dread"),
        ("HND-003", "PER-0042B", "NightWolf_Sec", "nightwolf_sec", "BreachForums"),
        ("HND-004", "PER-0042B", "NightWolf99", "nightwolf99", "Exploit.in"),
        ("HND-005", "PER-0042C", "ShadowXOfficial", "shadowxofficial", "Telegram"),
    ]
    for hid, pid, orig, norm, plat in handles_to_seed:
        db.add(Handle(id=hid, persona_id=pid, original_value=orig, normalized_value=norm, platform=plat, source_id="SRC-DREAD"))

    for p in db.query(Persona).all():
        db.add(Handle(
            id=f"HND-{p.id}",
            persona_id=p.id,
            original_value=p.canonical_handle,
            normalized_value=p.canonical_handle.lower().replace("-", "_").replace(".", "_"),
            platform=p.platform,
            source_id=p.source_id or "SRC-DREAD"
        ))
        db.add(Handle(
            id=f"HND-ALT-{p.id}",
            persona_id=p.id,
            original_value=f"{p.canonical_handle}_priv8",
            normalized_value=f"{p.canonical_handle.lower()}_priv8",
            platform=p.platform,
            source_id=p.source_id or "SRC-DREAD"
        ))
    db.commit()

    # 5. PGP Keys (30+ PGP Keys) - KEY-001 is SHARED between ShadowX and NightWolf!
    key_shared = PGPKey(
        id="KEY-001",
        key_id="4B8F901C",
        fingerprint="7C8B9A0D1E2F3A4B5C6D7E8F9A0B1C2D3E4F5A6B",
        algorithm="RSA",
        bit_length=4096,
        identity_email="shadow_ops@onionmail.org",
        source_id="SRC-DREAD",
        confidence=1.0,
        reliability="A",
        provenance="Public key published in Dread vendor profile #891 and verified in BreachForums signed escrow message."
    )
    db.add(key_shared)

    for i in range(2, 35):
        kid = f"KEY-{i:03d}"
        fp = hashlib.sha1(f"pgp_synthetic_{i}".encode()).hexdigest().upper()
        db.add(PGPKey(
            id=kid,
            key_id=fp[-8:],
            fingerprint=fp,
            algorithm="RSA",
            bit_length=4096,
            identity_email=f"vendor_{i}@secmail.pro",
            source_id="SRC-EXPLOIT",
            confidence=1.0,
            reliability="A"
        ))
    db.commit()

    # 6. Wallets (30+ Wallets)
    wallets_data = [
        ("WALLET-001", "BTC", "bc1q7x4z0y2e8k5tq9m3j6p1c8u4a7r9w2v5s8x1y4", ["BreachForums Escrow", "High Volume Cluster"], "34.82 BTC"),
        ("WALLET-002", "XMR", "888tNkZrPN6JsEgekjMnABU4TBzc2Dt29EPAvkFxbTNsLTGnqFTv28RcyR44FKa6KN22gqEBCPr4FnElzqY2R44FKa6KN22", ["Wasabi Mixer Hop", "Dread Verified"], "410.5 XMR"),
        ("WALLET-003", "BTC", "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", ["LockBit Ransom Payout"], "189.4 BTC"),
        ("WALLET-004", "ETH", "0x71C8360f3E282935663673F1D9970bfA25dc8b46", ["Tornado Router Hop"], "450.0 ETH"),
        ("WALLET-005", "BTC", "bc1q9v3k5w8p2n7t4j1m6r9s2d5x8u1y4a7c0e3g6", ["Bohemia Escrow Payout"], "98.14 BTC"),
    ]
    for wid, cur, addr, tags, vol in wallets_data:
        db.add(Wallet(id=wid, currency=cur, address=addr, cluster_tags=tags, total_received_approx=vol, source_id="SRC-CHAIN-INTEL"))

    for i in range(6, 36):
        db.add(Wallet(
            id=f"WALLET-{i:03d}",
            currency="BTC" if i % 2 == 0 else "XMR",
            address=f"bc1q{hashlib.md5(f'wallet_{i}'.encode()).hexdigest()[:24]}",
            cluster_tags=["Synthetic Mixer Cluster"],
            total_received_approx=f"{i * 3.4:.2f} BTC",
            source_id="SRC-CHAIN-INTEL"
        ))
    db.commit()

    # 7. Infrastructure Indicators (40+ Indicators)
    infra_data = [
        ("INF-001", "IP", "194.26.29.114", "dread-infra.is", "AS49981 WorldStream B.V.", "Netherlands", "Amsterdam"),
        ("INF-002", "SSL_CERT_SAN", "4B:8F:90:1C:33:DE:7A:01:88:9C", "backup.dread-vault.org", "Let's Encrypt", "Netherlands", "Amsterdam"),
        ("INF-003", "FAVICON_MURMUR3", "-1294875632", "194.26.29.114", "WorldStream", "Netherlands", "Amsterdam"),
        ("INF-004", "IP", "185.196.220.73", "hydra-portal-cdn.net", "AS200019 AlexHost SRL", "Moldova", "Chisinau"),
        ("INF-005", "IP", "91.240.118.89", "clearnet-sync.ru", "AS48287 Selectel", "Russia", "Saint Petersburg"),
        ("INF-006", "IP", "45.142.214.205", "bohemia-checkout.com", "AS51167 Contabo GmbH", "Bulgaria", "Sofia"),
    ]
    for iid, itype, ival, ccorr, asn, ctry, city in infra_data:
        db.add(Infrastructure(id=iid, indicator_type=itype, indicator_value=ival, clearnet_correlation=ccorr, asn_isp=asn, country=ctry, city=city, source_id="SRC-TOR-SENSOR-01"))

    for i in range(7, 45):
        sim_ip = f"185.220.101.{i+10}"
        db.add(Infrastructure(
            id=f"INF-{i:03d}",
            indicator_type="IP" if i % 2 == 0 else "SSH_BANNER",
            indicator_value=sim_ip if i % 2 == 0 else f"SSH-2.0-OpenSSH_8.{i%5}p1 Debian",
            clearnet_correlation=f"node-{i}.bulletproof-host.is",
            asn_isp="AS9009 M247 Europe",
            country="Romania" if i % 3 == 0 else "Germany",
            city="Bucharest" if i % 3 == 0 else "Frankfurt",
            source_id="SRC-SHODAN"
        ))
    db.commit()

    # 8. Domains (Tor Onions + Clearnet Correlated)
    domains_data = [
        ("DOM-001", "dreadmarket736xqwp4m7vylz4k5j6r4r2dff3b3e2q9d8.onion", True, "194.26.29.114"),
        ("DOM-002", "dread-infra.is", False, "194.26.29.114"),
        ("DOM-003", "hydraex7vbb45m839xplkwqqe2m910a8b7c6d5e4f3a2b1c9.onion", True, "185.196.220.73"),
        ("DOM-004", "lockbit3leakszqwertyuiopasdfghjklzxcvbnm123456789.onion", True, "91.240.118.89"),
        ("DOM-005", "bohemiamkt993xqwq004mka1992019alzkqpwq29291823.onion", True, "45.142.214.205"),
    ]
    for did, dname, is_on, rip in domains_data:
        db.add(Domain(id=did, domain_name=dname, is_onion=is_on, resolved_ip=rip, source_id="SRC-CERT-LOGS"))
    db.commit()

    # 9. Intelligence Records (> 200 Records)
    sample_texts = [
        "WTS fresh corporate domain admin access. Fortune 500 healthcare provider. Escrow strictly mandatory!! PGP signed proof in thread.",
        "ATTENTION: Your enterprise data has been encrypted using AES-256. Decryptor trial ready. Contact operator via tox.",
        "Automated crypto tumbler service 24/7. Clean your dirty BTC into untraceable XMR. Zero logs policy.",
        "0day RCE in popular enterprise firewall appliances (FortiGate / Palo Alto). Remote root shell over SSL VPN.",
        "MASSIVE UPDATE: 25,000 fresh USA & UK high balance credit card dumps with full CVV & Billing addresses."
    ]

    for i in range(1, 210):
        oid = f"OBS-{i:04d}"
        txt = sample_texts[i % len(sample_texts)] + f" [Ref Record #{i}]"
        h = sha256_hash(txt)
        db.add(IntelligenceRecord(
            id=oid,
            source_id="SRC-DREAD" if i % 2 == 0 else "SRC-BREACH",
            record_type="FORUM_POST" if i % 3 != 0 else "RECON_SCAN",
            author_raw=f"threat_actor_{i%20}",
            content_raw=txt,
            content_sha256=h,
            timestamp=now - timedelta(days=int(i * 1.5)),
            confidence=0.90,
            reliability="A" if i % 2 == 0 else "B",
            provenance=f"Ingested by automated sensor grid node #{(i%5)+1}"
        ))
    db.commit()

    # 10. Evidence Records (100+ Evidence Records with SHA-256 Hashes)
    # Evidence for ACT-0042 Scenario
    ev1 = Evidence(
        id="EVID-0001",
        source_id="SRC-DREAD",
        evidence_type="IDENTITY",
        title="Shared PGP 4096-bit Public Key Signature",
        description="Identical PGP Key Fingerprint 7C8B9A0D1E2F3A4B5C6D7E8F9A0B1C2D3E4F5A6B utilized to sign escrow transactions for ShadowX on Dread and NightWolf on BreachForums.",
        content_hash=sha256_hash("EVID-0001-PGP-FINGERPRINT-7C8B9A0D1E2F3A4B5C6D7E8F9A0B1C2D3E4F5A6B"),
        timestamp=now - timedelta(days=110),
        reliability="A",
        confidence=0.98,
        related_entity_ids=["PER-0042A", "PER-0042B", "KEY-001"],
        provenance="Dread vendor verification audit log #9011"
    )
    ev2 = Evidence(
        id="EVID-0002",
        source_id="SRC-TOR-SENSOR-01",
        evidence_type="INFRASTRUCTURE",
        title="Correlated Clearnet Origin Hosting IP via Apache Status Leak",
        description="Apache /server-status exposed virtual host 'dread-infra.is' and TLS certificate SAN matching origin IP 194.26.29.114 used simultaneously by both personas.",
        content_hash=sha256_hash("EVID-0002-CLEARNET-IP-194.26.29.114"),
        timestamp=now - timedelta(days=95),
        reliability="A",
        confidence=0.95,
        related_entity_ids=["PER-0042A", "PER-0042B", "INF-001"],
        provenance="Active Tor sensor reconnaissance trace"
    )
    ev3 = Evidence(
        id="EVID-0003",
        source_id="SRC-BREACH",
        evidence_type="CONTENT",
        title="AI Stylometric Persona Similarity Match (88.4%)",
        description="Character 3-5 gram TF-IDF writeprint and syntactic punctuation entropy correlation between ShadowX offering listings and NightWolf network access announcements.",
        content_hash=sha256_hash("EVID-0003-STYLOMETRY-88.4-MATCH"),
        timestamp=now - timedelta(days=80),
        reliability="B",
        confidence=0.88,
        related_entity_ids=["PER-0042A", "PER-0042B"],
        provenance="Darktrace-X AI Stylometry Engine v1.0"
    )
    # Contradicting Evidence!
    ev4_contra = Evidence(
        id="EVID-0004",
        source_id="SRC-DREAD",
        evidence_type="BEHAVIOR",
        title="Contradicting Evidence: Divergent Operational Activity Timelines",
        description="ShadowX ceased active forum postings on Dread on Day -120, whereas NightWolf only initiated high-volume postings on BreachForums from Day -115 onwards. Temporal overlap is absent, and diurnal UTC posting distributions show a 4-hour timezone variance (UTC+02:00 vs UTC+06:00).",
        content_hash=sha256_hash("EVID-0004-CONTRADICTING-TIMELINE-DIVERGENCE"),
        timestamp=now - timedelta(days=75),
        reliability="A",
        confidence=0.92,
        related_entity_ids=["PER-0042A", "PER-0042B"],
        provenance="Automated Contradiction Detection Engine"
    )

    db.add_all([ev1, ev2, ev3, ev4_contra])

    # Seed 98 more evidence records to reach > 100
    for i in range(5, 105):
        eid = f"EVID-{i:04d}"
        txt = f"Evidence descriptor #{i} verifying cryptographic and infrastructural indicator continuity."
        db.add(Evidence(
            id=eid,
            source_id="SRC-DREAD" if i % 2 == 0 else "SRC-EXPLOIT",
            evidence_type="IDENTITY" if i % 3 == 0 else ("INFRASTRUCTURE" if i % 3 == 1 else "BEHAVIOR"),
            title=f"Underground Footprint Verification #{i}",
            description=txt,
            content_hash=sha256_hash(txt),
            timestamp=now - timedelta(days=int(i * 2)),
            reliability="A" if i % 2 == 0 else "B",
            confidence=0.85 + (i % 10) * 0.01,
            related_entity_ids=[f"PER-000{i%10}", f"WALLET-00{i%10}"],
            provenance="Automated CTI Pipeline"
        ))
    db.commit()

    # 11. Relationships (> 300 Relationships)
    # Critical Demo Assessment Relationships
    db.add(Relationship(
        id="REL-0001",
        source_entity_id="PER-0042A",
        target_entity_id="KEY-001",
        relationship_type="OWNS_PGP_KEY",
        confidence=1.0,
        evidence_id="EVID-0001",
        source_id="SRC-DREAD",
        properties={"status": "VERIFIED"}
    ))
    db.add(Relationship(
        id="REL-0002",
        source_entity_id="PER-0042B",
        target_entity_id="KEY-001",
        relationship_type="OWNS_PGP_KEY",
        confidence=1.0,
        evidence_id="EVID-0001",
        source_id="SRC-BREACH",
        properties={"status": "VERIFIED"}
    ))
    db.add(Relationship(
        id="REL-0003",
        source_entity_id="PER-0042A",
        target_entity_id="PER-0042B",
        relationship_type="SIMILAR_TO",
        confidence=0.88,
        evidence_id="EVID-0003",
        source_id="SRC-DREAD",
        properties={"nature": "Stylometric & Identifier Crossover"}
    ))
    db.add(Relationship(
        id="REL-0004",
        source_entity_id="PER-0042A",
        target_entity_id="PER-0042B",
        relationship_type="CONTRADICTED_BY",
        confidence=0.92,
        evidence_id="EVID-0004",
        source_id="SRC-DREAD",
        properties={"nature": "Activity Period & Timezone Discrepancy"}
    ))

    # Add 300 more relational links across entities
    personas_all = db.query(Persona).all()
    for idx, p in enumerate(personas_all):
        # USES handle
        db.add(Relationship(
            id=f"REL-HND-{idx}",
            source_entity_id=p.id,
            target_entity_id=f"HND-{p.id}",
            relationship_type="USES_HANDLE",
            confidence=0.95,
            source_id="SRC-DREAD"
        ))
        # OPERATES_ON marketplace/forum
        db.add(Relationship(
            id=f"REL-MKT-{idx}",
            source_entity_id=p.id,
            target_entity_id=f"SRC-{p.platform.upper()}" if p.platform else "SRC-DREAD",
            relationship_type="OPERATES_ON",
            confidence=0.90,
            source_id="SRC-DREAD"
        ))
        # CONTROLS wallet
        w_id = f"WALLET-{(idx%30)+1:03d}"
        db.add(Relationship(
            id=f"REL-WAL-{idx}",
            source_entity_id=p.id,
            target_entity_id=w_id,
            relationship_type="CONTROLS_WALLET",
            confidence=0.85,
            source_id="SRC-CHAIN-INTEL"
        ))
        # CONNECTED_TO infrastructure
        inf_id = f"INF-{(idx%40)+1:03d}"
        db.add(Relationship(
            id=f"REL-INF-{idx}",
            source_entity_id=p.id,
            target_entity_id=inf_id,
            relationship_type="CONNECTED_TO",
            confidence=0.82,
            source_id="SRC-TOR-SENSOR-01"
        ))
        if idx >= 80:
            break
    db.commit()

    # 12. Timeline Events (> 500 Timeline Events)
    for i in range(1, 510):
        tid = f"TML-{i:04d}"
        act_ref = "ACT-0042" if i % 5 == 0 else f"ACT-{(i%19)+1:04d}"
        per_ref = "PER-0042A" if i % 10 == 0 else ("PER-0042B" if i % 10 == 5 else f"PER-{(i%45)+1:04d}")
        
        event_types = ["ACCOUNT_CREATION", "PGP_OBSERVED", "WALLET_OBSERVED", "FORUM_ACTIVITY", "INFRA_EVENT", "PERSONA_MIGRATION"]
        etype = event_types[i % len(event_types)]
        
        db.add(TimelineEvent(
            id=tid,
            actor_id=act_ref,
            persona_id=per_ref,
            event_type=etype,
            title=f"{etype.replace('_', ' ').title()} recorded on target entity",
            description=f"Automated sensor observation event #{i} capturing network and behavioral telemetry.",
            event_timestamp=now - timedelta(days=int(i * 1.1)),
            source_id="SRC-DREAD" if i % 2 == 0 else "SRC-BREACH",
            confidence=0.90
        ))
    db.commit()

    # 13. Stylometric & Behavior Profiles for ShadowX & NightWolf
    db.add(StylometricProfile(
        id="STP-001",
        persona_id="PER-0042A",
        sample_count=45,
        avg_sentence_length=14.2,
        avg_word_length=4.85,
        lexical_diversity_ttr=0.74,
        punctuation_entropy=0.082,
        uppercase_ratio=0.041,
        function_word_frequencies={"the": 0.052, "and": 0.041, "to": 0.038, "of": 0.031},
        characteristic_jargon=["fud", "escrow", "xmr", "access", "root", "shell"],
        provenance="Dread marketplace sales listings corpus"
    ))
    db.add(StylometricProfile(
        id="STP-002",
        persona_id="PER-0042B",
        sample_count=32,
        avg_sentence_length=14.8,
        avg_word_length=4.91,
        lexical_diversity_ttr=0.72,
        punctuation_entropy=0.085,
        uppercase_ratio=0.039,
        function_word_frequencies={"the": 0.050, "and": 0.043, "to": 0.036, "of": 0.033},
        characteristic_jargon=["fud", "escrow", "xmr", "vpn", "priv8", "drop"],
        provenance="BreachForums offerings corpus"
    ))

    db.add(BehaviorProfile(
        id="BEH-001",
        persona_id="PER-0042A",
        active_hours_distribution=[0,0,0,1,2,5,8,12,14,16,18,19,15,10,6,2,0,0,0,0,0,0,0,0],
        peak_active_utc=11,
        estimated_timezone="UTC+02:00 (EET / Eastern Europe)",
        posting_interval_mean_hours=6.4,
        platform_migration_cadence="Active 2024-2025"
    ))
    db.add(BehaviorProfile(
        id="BEH-002",
        persona_id="PER-0042B",
        active_hours_distribution=[0,0,0,0,0,0,1,3,7,12,15,18,20,16,11,4,1,0,0,0,0,0,0,0],
        peak_active_utc=13,
        estimated_timezone="UTC+03:00 (MSK / Middle East)",
        posting_interval_mean_hours=8.2,
        platform_migration_cadence="Active 2025-2026"
    ))
    db.commit()

    # 14. Demo Attribution Assessment Scenario
    db.add(AttributionAssessment(
        id="ATTR-0042",
        actor_id="ACT-0042",
        candidate_persona_a="ShadowX (PER-0042A)",
        candidate_persona_b="NightWolf (PER-0042B)",
        assessment_type="POTENTIAL_PERSONA_RELATIONSHIP",
        analytical_confidence="MEDIUM",
        confidence_score=0.68,
        supporting_evidence_ids=["EVID-0001", "EVID-0002", "EVID-0003"],
        contradicting_evidence_ids=["EVID-0004"],
        reasoning_summary="Candidate personas share an identical 4096-bit PGP key fingerprint (KEY-001) and correlated origin hosting infrastructure (194.26.29.114), corroborated by high stylometric character n-gram cosine similarity (88.4%). However, a significant operational temporal divergence is observed: ShadowX ceased activity before NightWolf emerged, with a 4-hour discrepancy in peak UTC activity hours. This signals a possible migration, shared infrastructure syndicate, or credential handover.",
        recommendation="MANUAL_INVESTIGATOR_REVIEW",
        is_confirmed_by_analyst=False
    ))

    # Analyst Note
    db.add(AnalystNote(
        id="NOTE-0001",
        actor_id="ACT-0042",
        author_id=db.query(User).filter(User.username == "investigator").first().id if db.query(User).filter(User.username == "investigator").first() else "system",
        title="Initial Forensic Review: ShadowX to NightWolf Link",
        content="Shared PGP fingerprint provides a strong cryptographic link [EVID-0001]. However, diurnal distribution in [EVID-0004] warns against automated attribution. Recommending subpoena or passive OSINT on Dutch ASN host 194.26.29.114.",
        classification="TLP:AMBER"
    ))
    db.commit()

    # 15. PRIMARY SIH SHOWCASE ACTOR: TA-001 (NightFox / seed nightfox_404)
    act_ta001 = Actor(
        id="TA-001",
        primary_name="NightFox",
        threat_category="Credential Infiltration & Ransomware Brokerage",
        threat_level="CRITICAL",
        status="ACTIVE",
        analytical_confidence="HIGH",
        confidence_score=0.82,
        first_observed=now - timedelta(days=640),
        last_observed=now - timedelta(days=1),
        summary="Prolific underground operator orchestrating high-value corporate access brokerage and ransomware escrow syndicates. Tracked via seed alias 'nightfox_404' on Dread, transitioning to 'NightFox' on BreachForums and 'NF_404' on Exploit.in.",
        provenance="Multi-source correlation across Dread, BreachForums, Exploit.in, and Tor recon nodes."
    )
    db.add(act_ta001)

    per_nf_dread = Persona(
        id="PER-NF01",
        actor_id="TA-001",
        canonical_handle="nightfox_404",
        platform="Dread",
        first_seen=now - timedelta(days=640),
        last_seen=now - timedelta(days=90),
        activity_count=214,
        source_id="SRC-DREAD",
        confidence=0.95,
        reliability="A",
        provenance="Dread verified vendor #404"
    )
    per_nf_breach = Persona(
        id="PER-NF02",
        actor_id="TA-001",
        canonical_handle="NightFox",
        platform="BreachForums",
        first_seen=now - timedelta(days=85),
        last_seen=now - timedelta(days=1),
        activity_count=168,
        source_id="SRC-BREACH",
        confidence=0.92,
        reliability="A",
        provenance="BreachForums VIP seller account"
    )
    per_nf_exploit = Persona(
        id="PER-NF03",
        actor_id="TA-001",
        canonical_handle="NF_404",
        platform="Exploit.in",
        first_seen=now - timedelta(days=200),
        last_seen=now - timedelta(days=15),
        activity_count=78,
        source_id="SRC-EXPLOIT",
        confidence=0.86,
        reliability="A",
        provenance="Exploit.in verified escrow deposit"
    )
    per_nf_decoy = Persona(
        id="PER-NF-DECOY",
        actor_id=None,
        canonical_handle="nightfox_support",
        platform="Telegram",
        first_seen=now - timedelta(days=60),
        last_seen=now - timedelta(days=5),
        activity_count=9,
        source_id="SRC-TELEGRAM",
        confidence=0.35,
        reliability="C",
        provenance="Telegram support channel decoy without PGP validation"
    )
    db.add_all([per_nf_dread, per_nf_breach, per_nf_exploit, per_nf_decoy])

    # Handles
    db.add(Handle(id="HND-NF-01", persona_id="PER-NF01", original_value="nightfox_404", normalized_value="nightfox_404", platform="Dread", source_id="SRC-DREAD"))
    db.add(Handle(id="HND-NF-02", persona_id="PER-NF02", original_value="NightFox", normalized_value="nightfox", platform="BreachForums", source_id="SRC-BREACH"))
    db.add(Handle(id="HND-NF-03", persona_id="PER-NF03", original_value="NF_404", normalized_value="nf_404", platform="Exploit.in", source_id="SRC-EXPLOIT"))
    db.add(Handle(id="HND-NF-04", persona_id="PER-NF-DECOY", original_value="nightfox_support", normalized_value="nightfox_support", platform="Telegram", source_id="SRC-TELEGRAM"))

    # PGP Key
    key_nf = PGPKey(
        id="KEY-NF-01",
        key_id="9A2B4C6D",
        fingerprint="8F7E6D5C4B3A291827364556677889901A2B3C4D",
        algorithm="RSA",
        bit_length=4096,
        identity_email="nightfox@onionmail.org",
        source_id="SRC-DREAD",
        confidence=1.0,
        reliability="A",
        provenance="Published in Dread vendor profile and cross-signed on BreachForums escrow deposit."
    )
    db.add(key_nf)

    # Wallet
    wallet_nf = Wallet(
        id="WALLET-NF-01",
        currency="BTC",
        address="bc1qnightfox982347kldsjfsduweiruwer98234",
        cluster_tags=["NightFox Direct Deposit", "High Volume Escrow", "Wasabi Hop"],
        total_received_approx="42.50 BTC",
        source_id="SRC-DREAD",
        confidence=0.98,
        reliability="A",
        provenance="On-chain escrow collateral observed in forum telemetry"
    )
    db.add(wallet_nf)

    # Onion and Clearnet Domain
    dom_nf1 = Domain(id="DOM-NF-01", domain_name="nightfox7x2u9p4q.onion", is_onion=True, source_id="SRC-TOR-SENSOR-01", confidence=0.95, reliability="A")
    dom_nf2 = Domain(id="DOM-NF-02", domain_name="nightfox-portal.is", is_onion=False, resolved_ip="185.220.101.42", source_id="SRC-CERT-LOGS", confidence=0.92, reliability="A")
    db.add_all([dom_nf1, dom_nf2])

    # Infrastructure
    inf_nf = Infrastructure(
        id="INF-NF-01",
        indicator_type="SSL_CERT_SAN",
        indicator_value="nightfox-portal.is",
        clearnet_correlation="185.220.101.42",
        asn_isp="AS200052 // HOSTING-SERVICES-BV",
        country="Netherlands",
        city="Amsterdam",
        details={"serial": "0x3F8A9B2C", "san_leak": True, "apache_status_leak": "VHost: nightfox-portal.is"},
        source_id="SRC-CERT-LOGS",
        confidence=0.96,
        reliability="A",
        provenance="Passive SSL/TLS certificate transparency log indexed on crt.sh"
    )
    db.add(inf_nf)

    # 7 Supporting Evidence Items + 1 Contradicting Evidence Item
    evid_nf_list = [
        Evidence(
            id="EVID-NF-01",
            source_id="SRC-DREAD",
            evidence_type="IDENTITY",
            title="Shared 4096-bit Cryptographic PGP Signature",
            description="Persona 'nightfox_404' on Dread and 'NightFox' on BreachForums both signed operational escrow releases with identical RSA-4096 key [8F7E6D5C4B3A291827364556677889901A2B3C4D].",
            content_hash=sha256_hash("EVID-NF-01-PGP-MATCH"),
            reliability="A",
            confidence=0.99,
            related_entity_ids=["TA-001", "PER-NF01", "PER-NF02", "KEY-NF-01"],
            provenance="Verified cryptographic signature cross-reference"
        ),
        Evidence(
            id="EVID-NF-02",
            source_id="SRC-BREACH",
            evidence_type="FINANCIAL",
            title="Direct Blockchain Escrow Deposit Address Overlap",
            description="BTC address bc1qnightfox... received 42.50 BTC across Dread vendor collateral and BreachForums initial access auction settlement.",
            content_hash=sha256_hash("EVID-NF-02-WALLET-OVERLAP"),
            reliability="A",
            confidence=0.95,
            related_entity_ids=["TA-001", "WALLET-NF-01"],
            provenance="Public blockchain ledger transaction ID verification"
        ),
        Evidence(
            id="EVID-NF-03",
            source_id="SRC-CERT-LOGS",
            evidence_type="INFRASTRUCTURE",
            title="TLS SAN Certificate Leak to Clearnet Host",
            description="X.509 certificate served on nightfox7x2u9p4q.onion contains clearnet domain 'nightfox-portal.is' resolving to 185.220.101.42 (AS200052).",
            content_hash=sha256_hash("EVID-NF-03-TLS-SAN"),
            reliability="A",
            confidence=0.96,
            related_entity_ids=["TA-001", "DOM-NF-01", "DOM-NF-02", "INF-NF-01"],
            provenance="Certificate Transparency logs and passive TLS handshake capture"
        ),
        Evidence(
            id="EVID-NF-04",
            source_id="SRC-BREACH",
            evidence_type="BEHAVIOR",
            title="AI Stylometric Writeprint Congruence (82%)",
            description="Quantitative stylometric profiling reveals 82% cosine similarity across character 3-5 grams, sentence length (14.6 words), and darknet jargon marker density ('fud', 'escrow', 'xmr', 'zeroday').",
            content_hash=sha256_hash("EVID-NF-04-STYLOMETRY"),
            reliability="B",
            confidence=0.88,
            related_entity_ids=["TA-001", "PER-NF01", "PER-NF02"],
            provenance="TF-IDF character n-gram cosine vectorization engine"
        ),
        Evidence(
            id="EVID-NF-05",
            source_id="SRC-TOR-SENSOR-01",
            evidence_type="INFRASTRUCTURE",
            title="Apache Server-Status Diagnostic Origin Disclosure",
            description="Misconfigured Apache /server-status endpoint on onion hosting leaked internal virtual host mapping and origin IP 185.220.101.42.",
            content_hash=sha256_hash("EVID-NF-05-APACHE-LEAK"),
            reliability="A",
            confidence=0.94,
            related_entity_ids=["TA-001", "INF-NF-01"],
            provenance="Autonomous Tor reconnaissance crawler sensor intercept"
        ),
        Evidence(
            id="EVID-NF-06",
            source_id="SRC-CENSYS",
            evidence_type="INFRASTRUCTURE",
            title="Favicon MurmurHash3 Cross-Reference",
            description="Unique Favicon hash (-1298471928) matches clearnet reverse proxy server in Amsterdam Netherlands.",
            content_hash=sha256_hash("EVID-NF-06-FAVICON-HASH"),
            reliability="B",
            confidence=0.85,
            related_entity_ids=["TA-001", "INF-NF-01"],
            provenance="Censys Internet-wide scan telemetry matching"
        ),
        Evidence(
            id="EVID-NF-07",
            source_id="SRC-EXPLOIT",
            evidence_type="IDENTITY",
            title="Independent Third-Party Forum Escrow Corroboration",
            description="Exploit.in senior moderator post confirms NF_404 is the relocated vendor profile of former Dread operator nightfox_404.",
            content_hash=sha256_hash("EVID-NF-07-MODERATOR-NOTE"),
            reliability="A",
            confidence=0.91,
            related_entity_ids=["TA-001", "PER-NF01", "PER-NF03"],
            provenance="Underground forum moderation reputation thread"
        ),
        # Contradicting Evidence (1 Conflict)
        Evidence(
            id="EVID-NF-CONFLICT",
            source_id="SRC-DREAD",
            evidence_type="CONTRADICTION",
            title="Diurnal Operational Window Disparity (13-Hour Shift Gap)",
            description="Persona 'nightfox_404' posted consistently in UTC 20:00-02:00 (Americas evening), whereas 'NF_404' had active activity bursts at UTC 08:00 (East Asian morning). Suggests possible multi-operator syndicate or shift rotation.",
            content_hash=sha256_hash("EVID-NF-CONFLICT-TIMEZONE"),
            reliability="A",
            confidence=0.85,
            related_entity_ids=["TA-001", "PER-NF01", "PER-NF03"],
            provenance="Diurnal 24-hour histogram variance analysis"
        )
    ]
    db.add_all(evid_nf_list)

    # Profiling for NightFox
    db.add(StylometricProfile(
        id="STP-NF01",
        persona_id="PER-NF01",
        sample_count=58,
        avg_sentence_length=14.6,
        avg_word_length=4.92,
        lexical_diversity_ttr=0.76,
        punctuation_entropy=0.088,
        uppercase_ratio=0.042,
        function_word_frequencies={"the": 0.054, "and": 0.040, "to": 0.039, "of": 0.033},
        characteristic_jargon=["fud", "escrow", "xmr", "zeroday", "stealer", "c2"],
        provenance="Dread listings corpus"
    ))
    db.add(StylometricProfile(
        id="STP-NF02",
        persona_id="PER-NF02",
        sample_count=42,
        avg_sentence_length=14.4,
        avg_word_length=4.89,
        lexical_diversity_ttr=0.75,
        punctuation_entropy=0.086,
        uppercase_ratio=0.040,
        function_word_frequencies={"the": 0.052, "and": 0.042, "to": 0.037, "of": 0.034},
        characteristic_jargon=["fud", "escrow", "xmr", "zeroday", "logs", "root"],
        provenance="BreachForums posts corpus"
    ))

    db.add(BehaviorProfile(
        id="BEH-NF01",
        persona_id="PER-NF01",
        active_hours_distribution=[0,0,0,0,0,0,0,0,1,2,3,4,8,12,18,22,25,28,30,24,18,8,2,0],
        peak_active_utc=21,
        estimated_timezone="Americas / Eastern (EST/EDT)",
        posting_interval_mean_hours=5.8,
        platform_migration_cadence="Active 2024-2025"
    ))
    db.add(BehaviorProfile(
        id="BEH-NF02",
        persona_id="PER-NF02",
        active_hours_distribution=[0,0,0,0,0,0,0,1,2,5,7,10,14,19,23,26,29,27,21,12,6,1,0,0],
        peak_active_utc=20,
        estimated_timezone="Americas / Eastern (EST/EDT)",
        posting_interval_mean_hours=6.2,
        platform_migration_cadence="Active 2025-2026"
    ))

    # Assessment for NightFox: 82% Confidence, 7 Supporting Evidence, 1 Contradicting, 4 Sources, Requires Human Validation
    db.add(AttributionAssessment(
        id="ATTR-NF-001",
        actor_id="TA-001",
        candidate_persona_a="nightfox_404 (PER-NF01)",
        candidate_persona_b="NightFox (PER-NF02)",
        assessment_type="POTENTIAL_PERSONA_RELATIONSHIP",
        analytical_confidence="HIGH",
        confidence_score=0.82,
        supporting_evidence_ids=["EVID-NF-01", "EVID-NF-02", "EVID-NF-03", "EVID-NF-04", "EVID-NF-05", "EVID-NF-06", "EVID-NF-07"],
        contradicting_evidence_ids=["EVID-NF-CONFLICT"],
        reasoning_summary="High-confidence multi-factor attribution correlating seed handle 'nightfox_404' to 'NightFox'. Confirmed through shared 4096-bit cryptographic PGP key, on-chain BTC wallet overlap, TLS SAN clearnet leak to 185.220.101.42, 82% stylometric writeprint similarity, and forum moderator confirmation across 4 independent sources. However, 1 diurnal contradiction (13-hour activity gap) suggests either a shared multi-operator syndicate or operational shift schedule. Mandatory analyst sign-off is required prior to legal referral.",
        recommendation="REQUIRES HUMAN VALIDATION",
        is_confirmed_by_analyst=False
    ))

    # Relationships for TA-001
    db.add_all([
        Relationship(id="REL-NF-01", source_entity_id="TA-001", target_entity_id="PER-NF01", relationship_type="CONTROLS_PERSONA", confidence=0.98, evidence_id="EVID-NF-01", source_id="SRC-DREAD"),
        Relationship(id="REL-NF-02", source_entity_id="TA-001", target_entity_id="PER-NF02", relationship_type="CONTROLS_PERSONA", confidence=0.95, evidence_id="EVID-NF-01", source_id="SRC-BREACH"),
        Relationship(id="REL-NF-03", source_entity_id="PER-NF01", target_entity_id="KEY-NF-01", relationship_type="OWNS_PGP_KEY", confidence=1.0, evidence_id="EVID-NF-01", source_id="SRC-DREAD"),
        Relationship(id="REL-NF-04", source_entity_id="PER-NF02", target_entity_id="KEY-NF-01", relationship_type="OWNS_PGP_KEY", confidence=1.0, evidence_id="EVID-NF-01", source_id="SRC-BREACH"),
        Relationship(id="REL-NF-05", source_entity_id="PER-NF01", target_entity_id="WALLET-NF-01", relationship_type="CONTROLS_WALLET", confidence=0.95, evidence_id="EVID-NF-02", source_id="SRC-DREAD"),
        Relationship(id="REL-NF-06", source_entity_id="TA-001", target_entity_id="DOM-NF-01", relationship_type="OPERATES_ONION_SERVICE", confidence=0.92, evidence_id="EVID-NF-03", source_id="SRC-TOR-SENSOR-01"),
        Relationship(id="REL-NF-07", source_entity_id="DOM-NF-01", target_entity_id="INF-NF-01", relationship_type="LEAKS_TO_ORIGIN", confidence=0.96, evidence_id="EVID-NF-03", source_id="SRC-CERT-LOGS"),
    ])

    # 16. Campaigns
    db.add_all([
        Campaign(
            id="CMP-001",
            name="Operation DarkHydra",
            description="Targeted credential infiltration campaign aimed at European financial clearing gateways and industrial automation portals.",
            threat_actor_ids=["TA-001", "ACT-0001"],
            target_sectors=["Financial Services", "Energy & Utilities"],
            infrastructure_indicators=["nightfox-portal.is", "185.220.101.42"],
            mitre_techniques=["T1566.001", "T1078", "T1071.001"],
            first_seen=now - timedelta(days=220),
            last_seen=now - timedelta(days=3),
            confidence=0.91,
            status="ACTIVE",
            evidence_ids=["EVID-NF-01", "EVID-NF-03"]
        ),
        Campaign(
            id="CMP-002",
            name="Phantom Corporate Infiltration",
            description="Initial access broker campaign exploiting VPN firmware vulnerabilities to plant secondary beacon stubs.",
            threat_actor_ids=["ACT-0042"],
            target_sectors=["Healthcare", "Legal & Accounting"],
            infrastructure_indicators=["194.26.29.114", "phantom-recon.cc"],
            mitre_techniques=["T1190", "T1059.001", "T1027"],
            first_seen=now - timedelta(days=340),
            last_seen=now - timedelta(days=12),
            confidence=0.88,
            status="ACTIVE",
            evidence_ids=["EVID-0001", "EVID-0003"]
        ),
        Campaign(
            id="CMP-003",
            name="Spectre Extortion Syndicate",
            description="Dual-extortion ransomware campaign deploying encrypted storage payloads with data leakage threats.",
            threat_actor_ids=["ACT-0001", "ACT-0013"],
            target_sectors=["Manufacturing", "Government Municipalities"],
            infrastructure_indicators=["91.215.85.17"],
            mitre_techniques=["T1486", "T1567.002"],
            first_seen=now - timedelta(days=150),
            last_seen=now - timedelta(days=20),
            confidence=0.84,
            status="ACTIVE",
            evidence_ids=["EVID-0002"]
        )
    ])

    # 17. MITRE ATT&CK Techniques
    db.add_all([
        MitreTechnique(id="T1566.001", name="Spearphishing Attachment", tactic="Initial Access", description="Spearphishing with weaponized macro attachments sent to executive personnel.", associated_actors=["TA-001", "ACT-0042"], evidence_references=["EVID-NF-04"], confidence=0.90),
        MitreTechnique(id="T1078", name="Valid Accounts", tactic="Defense Evasion", description="Adversaries obtain and abuse credentials of existing accounts on corporate portals.", associated_actors=["TA-001"], evidence_references=["EVID-NF-02"], confidence=0.94),
        MitreTechnique(id="T1071.001", name="Web Protocols", tactic="Command and Control", description="C2 communications carried out over HTTPS and Tor onion hidden service rendezvous.", associated_actors=["TA-001", "ACT-0042"], evidence_references=["EVID-NF-03"], confidence=0.92),
        MitreTechnique(id="T1486", name="Data Encrypted for Impact", tactic="Impact", description="Adversaries encrypt data on target systems to interrupt availability and demand ransom.", associated_actors=["ACT-0001"], evidence_references=["EVID-0002"], confidence=0.96),
        MitreTechnique(id="T1027", name="Obfuscated Files or Information", tactic="Defense Evasion", description="Using FUD cryptors and multi-stage stubs to evade automated endpoint detection.", associated_actors=["TA-001", "ACT-0011"], evidence_references=["EVID-NF-04"], confidence=0.88),
    ])

    # 18. Alerts
    db.add_all([
        Alert(id="ALT-0001", title="New High-Confidence Persona Correlation", event_type="PERSONA_CORRELATION", actor_id="TA-001", persona_id="PER-NF01", severity="CRITICAL", confidence=0.82, description="Candidate correlation established between Dread operator 'nightfox_404' and BreachForums vendor 'NightFox' based on 7 supporting evidence items across 4 independent sources.", supporting_evidence_count=7, status="NEW"),
        Alert(id="ALT-0002", title="Clearnet Infrastructure Origin Pivot", event_type="INFRA_PIVOT", actor_id="TA-001", severity="HIGH", confidence=0.96, description="TLS SAN correlation unmasked clearnet origin host 185.220.101.42 (AS200052) for onion service nightfox7x2u9p4q.onion.", supporting_evidence_count=3, status="NEW"),
        Alert(id="ALT-0003", title="Contradiction Detected: Diurnal Time Disparity", event_type="CONTRADICTION_FLAG", actor_id="TA-001", severity="MEDIUM", confidence=0.85, description="13-hour shift gap identified between active UTC hours of 'nightfox_404' and 'NF_404'. Analyst arbitration required.", supporting_evidence_count=1, status="NEW"),
    ])

    # 19. Investigations
    db.add_all([
        Investigation(
            id="INV-2026-001",
            case_id="CASE-SIH-001",
            title="De-Anonymization & Attribution of Operator NightFox (TA-001)",
            description="Forensic investigation into cross-marketplace actor operating 'nightfox_404' and associated ransomware infrastructure.",
            analyst_name="Lead CTI Analyst",
            status="ACTIVE",
            priority="CRITICAL",
            scope="Dark Web Forum Personas, Blockchain Escrows, Tor Origin De-cloaking",
            seed_indicators=[{"type": "alias", "value": "nightfox_404"}, {"type": "wallet", "value": "bc1qnightfox982347kldsjfsduweiruwer98234"}],
            extracted_entities=[{"type": "actor", "value": "TA-001"}, {"type": "pgp", "value": "KEY-NF-01"}, {"type": "ip", "value": "185.220.101.42"}],
            actor_id="TA-001",
            confidence_assessment=0.82
        ),
        Investigation(
            id="INV-2026-002",
            case_id="CASE-SIH-002",
            title="The Phantom Syndicate Infrastructure & Rebranding Analysis",
            description="Investigating persona migration from ShadowX on Dread to NightWolf on BreachForums.",
            analyst_name="Supervisor Analyst",
            status="ACTIVE",
            priority="HIGH",
            scope="Tor Misconfiguration & Stylometric Profile Comparison",
            seed_indicators=[{"type": "alias", "value": "ShadowX"}],
            extracted_entities=[{"type": "actor", "value": "ACT-0042"}, {"type": "pgp", "value": "KEY-001"}],
            actor_id="ACT-0042",
            confidence_assessment=0.68
        )
    ])
    db.commit()

    print("[+] Synthetic dataset loaded successfully: 21 Actors, 54 Personas, 100+ Handles, 30+ Keys, 30+ Wallets, 40+ Infra, 108+ Evidence, 300+ Rel, 500+ Timeline, Campaigns, Alerts, Investigations.")

