# DARKTRACE-X // Dark Web Threat Actor Intelligence & Attribution Platform

[![SIH Problem Statement](https://img.shields.io/badge/SIH-Dark%20Web%20Threat%20Actor%20De--Anonymization-00FF88?style=for-the-badge)](https://sih.gov.in)
[![Platform Status](https://img.shields.io/badge/Platform-Production%20Ready-00D9FF?style=for-the-badge)](#)
[![Python 3.12](https://img.shields.io/badge/Python-3.12.10-blue?style=for-the-badge&logo=python)](https://python.org)
[![React 18](https://img.shields.io/badge/React-18%20TypeScript-61DAFB?style=for-the-badge&logo=react)](https://react.dev)
[![STIX 2.1](https://img.shields.io/badge/CTI-OASIS%20STIX%202.1-orange?style=for-the-badge)](#)

An enterprise-grade Cyber Threat Intelligence (CTI) and attribution platform engineered for authorized cybersecurity research, digital forensics, and law enforcement threat analysis.

DARKTRACE-X unmasks dark web operators by correlating fragmented underground footprints across forums, darknet marketplaces, blockchain escrow clusters, passive infrastructure telemetries, AI stylometric writeprints, and multi-relational graph analytics.

---

## 🏛️ End-to-End Investigation Pipeline

```text
AUTHORIZED DATA SOURCES (Forums, Markets, Pastes, CT Logs, Blockchain)
        ↓
COLLECTION ENGINE (Modular Ingestion Adapters)
        ↓
SOURCE VALIDATION (Reliability Grading A–F)
        ↓
DATA NORMALIZATION & SHA-256 HASHING
        ↓
ENTITY EXTRACTION (Regex + NLP, 25+ Entity Types)
        ↓
IDENTITY RESOLUTION (Multi-Signal Equivalence & False Positive Rejection)
        ↓
INFRASTRUCTURE CORRELATION (TLS SANs, Apache Status Leaks, Favicon Hashes)
        ↓
BEHAVIORAL ANALYSIS (24-Hour Diurnal Histogram & Operational Timezone)
        ↓
STYLOMETRIC ANALYSIS (Yule's K, TF-IDF Character 3-5 Grams Cosine Similarity)
        ↓
RELATIONSHIP GRAPH (Cytoscape.js, Shortest Attribution Path, Community Detection)
        ↓
AI CORRELATION COPILOT (RAG-Grounded Assistant with FACT/INFERENCE Guardrails)
        ↓
ATTRIBUTION CONFIDENCE ENGINE (Configurable Multi-Factor Scoring)
        ↓
EVIDENCE & PROVENANCE STORE (Immutable Cryptographic Chain of Custody)
        ↓
INVESTIGATION WORKSPACE (Case Management, Seed Ingestion, Human-in-the-Loop Sign-Off)
        ↓
REPORT GENERATOR (Court-Ready PDF Dossier, CSV, JSON, OASIS STIX 2.1 Bundle)
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+ (Python 3.12 verified)
- Modern Web Browser (Chrome, Edge, Firefox)

### 2. Launch Platform (Single Command)
Run the launcher from the project root:

```bash
python start.py
```

*This starts the FastAPI intelligence engine on port `8000` with clean real-time telemetry streaming and automatically opens the React command center at `http://127.0.0.1:8000/login`.*

---

## 🔑 Demo Investigator Accounts

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Lead Analyst** | `investigator` | `Investigator2026!` | Full actor profiling, correlation pipeline, graph inspection |
| **Administrator**| `admin` | `DarktraceAdmin2026!` | User management, audit logs, system health |
| **Supervisor** | `supervisor` | `Supervisor2026!` | Mandatory attribution review and case sign-off |
| **Viewer** | `viewer` | `Viewer2026!` | Read-only threat intelligence observation |

---

## 🎯 Live Demonstration Flow (Zero Predefined Values)

1. **Zero-State Dashboard & Real-Time Ingestion:**
   - The platform boots in a clean state without predefined mock actors or hardcoded records.
   - **Real-Time Live Countdown:** Watch the telemetry radar tick down from `05s → 0s`. Every time it reaches `0s`, autonomous sensors capture underground intercepts, extract indicators, and stream live packets.
   - **Interactive Zero Controls:** Click **`SET ALL TO 0`** at any point to wipe all values to zero, or click **`ACK ALL → 0`** to clear alert backlogs to zero.
2. **Investigation Workspace:**
   - Create a case with any suspect seed indicator (alias, cryptocurrency wallet, PGP key, or onion service).
3. **Automated Correlation Pipeline:**
   - Execute the correlation pipeline to dynamically resolve identities, cross-reference infrastructure pivots, analyze diurnal histograms, and calculate stylometric similarity.
4. **Explainable Attribution Assessment:**
   - Inspect dynamically computed attribution confidence, weighted across multi-signal evidence, infrastructure overlaps, and contradiction penalties.
5. **Interactive Relationship Graph:**
   - Explore the network topology, trace shortest paths between darknet personas and clearnet origins, and isolate false-positive decoys.
6. **Forensic Intelligence Exports:**
   - Generate court-ready ReportLab PDF dossiers and export OASIS STIX 2.1 JSON bundles dynamically for any case.

---

## 📚 Complete Technical Documentation

- **[System Architecture](file:///d:/ALL%20PROJECT/SIH%202/darktrace-x/ARCHITECTURE.md)**
- **[REST API Reference](file:///d:/ALL%20PROJECT/SIH%202/darktrace-x/API.md)**
- **[Database Schema & Models](file:///d:/ALL%20PROJECT/SIH%202/darktrace-x/DATABASE.md)**
- **[Multi-Relational Graph Model](file:///d:/ALL%20PROJECT/SIH%202/darktrace-x/GRAPH_MODEL.md)**
- **[AI/ML & Stylometric Pipeline](file:///d:/ALL%20PROJECT/SIH%202/darktrace-x/AI_PIPELINE.md)**
- **[Attribution Scoring & Contradiction Model](file:///d:/ALL%20PROJECT/SIH%202/darktrace-x/ATTRIBUTION_MODEL.md)**
- **[Security, Ethics & Compliance](file:///d:/ALL%20PROJECT/SIH%202/darktrace-x/SECURITY.md)**
- **[Production & Docker Deployment](file:///d:/ALL%20PROJECT/SIH%202/darktrace-x/DEPLOYMENT.md)**
- **[SIH Live Demo Guide](file:///d:/ALL%20PROJECT/SIH%202/darktrace-x/DEMO_GUIDE.md)**
- **[SIH 14-Slide Presentation Guide](file:///d:/ALL%20PROJECT/SIH%202/darktrace-x/SIH_PRESENTATION.md)**
- **[Final System Verification Report](file:///d:/ALL%20PROJECT/SIH%202/darktrace-x/FINAL_VERIFICATION_REPORT.md)**

---

## ⚖️ Ethics, Compliance & Safe Operation

1. **Authorized Threat Intelligence Only:** The platform is strictly designed for authorized research, digital forensics, and law enforcement intelligence.
2. **No Exploits / No Offensive Hacking:** The platform does NOT perform attacks against Tor services, does not exploit vulnerabilities, and does not compromise servers.
3. **Passive Correlation:** De-cloaking is achieved purely through passive observations (misconfigured Apache server status, X.509 TLS certificate SANs, and Certificate Transparency logs).
4. **Explainable Attribution with Human-in-the-Loop:** All analytical assessments are presented as confidence ratings with evidence citations; mandatory analyst sign-off is required before any legal referral.
