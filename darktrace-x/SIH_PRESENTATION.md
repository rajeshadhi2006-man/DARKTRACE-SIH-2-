# DARKTRACE-X // SMART INDIA HACKATHON (SIH) PRESENTATION

## Slide Deck Architecture (14 Slides)

---

### Slide 1: Problem Definition
- **Challenge:** Dark web threat actors operate with apparent impunity behind Tor hidden service encryption and onion routing.
- **Pain Point:** Fragmented underground identities across decentralized forums, pseudonymity, and high risk of false attributions in manual digital forensic investigations.

---

### Slide 2: Existing Challenges & Limitations
- Current law enforcement and threat intelligence tools rely on brittle single-point indicators (e.g. searching a single handle).
- High false-positive rates when actors reuse common nicknames or spoof handles.
- Lack of explainability: Black-box AI models that cannot stand up to evidentiary scrutiny in court.

---

### Slide 3: Proposed Solution — DARKTRACE-X
- An AI-Powered Threat Actor Intelligence & Attribution Analysis Platform.
- Multi-dimensional correlation fusing:
  - Cryptographic PGP keys & on-chain blockchain escrows.
  - Passive infrastructure decloaking (TLS SANs, Apache leaks, Favicon hashes).
  - AI Stylometric Writeprints (Yule's K, character n-gram cosine similarity).
  - Diurnal behavioral profiling & persona migration detection.
  - Multi-relational graph analytics with shortest attribution paths.

---

### Slide 4: System Architecture
- End-to-end 14-stage analytical pipeline:
  `Collect → Normalize → Extract → Resolve → Correlate → Profile → Graph → AI RAG → Attribution Score → Human Review → Dossier Export`.
- Resilient Dual-Engine Design: PostgreSQL/SQLite dual storage, Neo4j/NetworkX graph analysis, and in-memory cache fallbacks.

---

### Slide 5: Data Collection & Source Reliability
- Modular ingestion adapters for Darknet Forums, Marketplaces, Paste Sites, and OSINT Feeds.
- Transparent Source Reliability Grading (A Confirmed, B Reliable, C Fairly Reliable).
- Immutable cryptographic SHA-256 evidence hashing for every ingested artifact.

---

### Slide 6: Entity Resolution & Contradiction Detection
- Resolves identities using multi-signal weighted fusion: handle Jaro-Winkler similarity, PGP key matching, and crypto wallet clusters.
- **Active Contradiction Checking:** Detects diurnal timezone conflicts and disjoint cryptographic keys to automatically reject false-positive decoys.

---

### Slide 7: AI/ML Analysis & Stylometric Writeprinting
- Evaluates subconscious author writing style: Yule's Characteristic K, Type-Token Ratio (TTR), and punctuation entropy.
- Sub-word character 3–5 gram TF-IDF cosine similarity to overcome intentional misspellings and slang obfuscation.
- 24-Hour Diurnal Histogram predicting operator operational timezone windows.

---

### Slide 8: Multi-Relational Graph Intelligence
- Interactive Cytoscape.js canvas mapping Actors, Personas, Handles, PGP Keys, Wallets, Domains, and Infrastructure.
- Shortest Evidentiary Path: Uncovers the multi-hop attribution chain from an anonymous dark web persona to clearnet origin hosting.
- Syndicate Community Detection identifying high-centrality brokers and shared infrastructure cartels.

---

### Slide 9: Transparent Attribution Confidence Engine
- Explainable composite confidence scoring with configurable weights (Identifier 20%, Infra 20%, PGP 15%, Behavior 15%, Stylometry 15%, Temporal 10%, Corroboration 5%).
- Explicitly presents Supporting Evidence, Contradicting Evidence, and Missing Evidence.
- Mandatory Human-in-the-Loop Analyst Review guards (`Confirm`, `Reject`, `Needs More Evidence`).

---

### Slide 10: Investigation Command Center Dashboard
- Sleek cyber-intelligence SOC interface (#05070A dark mode, #00FF88 / #00D9FF accents).
- Real-time telemetry feed, interactive timeline of persona migrations, and live anomaly alerts.

---

### Slide 11: Core Differentiating Innovations
1. **Explainable Attribution:** Every finding links directly to immutable evidence artifact IDs.
2. **False Positive Prevention:** Automatically flags impersonation decoys.
3. **Persona Migration Tracker:** Identifies when an actor closes one account and rebrands on another platform.
4. **Standardized CTI:** Instant export to OASIS STIX 2.1 bundles and MITRE ATT&CK technique mapping.

---

### Slide 12: Real-World Impact
- Accelerates digital forensics and cyber threat intelligence workflows from weeks to minutes.
- Provides law enforcement and security operations teams with court-admissible forensic dossiers (TLP:AMBER classification).

---

### Slide 13: Security, Ethics & Compliance
- **100% Authorized & Passive:** Does NOT perform network attacks, exploit vulnerabilities, or breach Tor hidden service security.
- Comprehensive Role-Based Access Control (RBAC) and immutable user audit trail.
- Strict AI safety guardrails preventing evidence hallucination.

---

### Slide 14: Future Scope & Roadmap
- Integration with decentralized blockchain tracing node clusters.
- Federated multi-agency collaborative case spaces.
- Real-time zero-day exploit forum watcher feeds.
