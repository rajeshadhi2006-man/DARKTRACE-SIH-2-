# DARKTRACE-X // System Architecture Specification

## 1. Architectural Philosophy

DARKTRACE-X is designed as an evidence-grounded, human-in-the-loop cyber threat intelligence and attribution system. It follows the core investigative sequence:

```
COLLECT
   ↓
NORMALIZE
   ↓
EXTRACT
   ↓
RESOLVE
   ↓
CORRELATE
   ↓
ANALYZE
   ↓
FUSE EVIDENCE
   ↓
CHECK CONTRADICTIONS
   ↓
GENERATE ASSESSMENT
   ↓
HUMAN REVIEW
```

---

## 2. Component Diagram

```mermaid
flowchart TB
    subgraph Client ["Frontend Client (React + TypeScript + Vite)"]
        UI["Cyber Command Center (#05070A)"]
        CytoGraph["Cytoscape.js Entity Graph"]
        RechartsVis["Recharts Telemetry Analytics"]
        AuthLayer["RBAC & JWT Client Guard"]
    end

    subgraph API ["Application Layer (FastAPI)"]
        Gateway["Nginx / FastAPI Router (/api)"]
        AuthService["Argon2 & JWT Authentication"]
        IngestionSvc["Normalization & Ingestion Pipeline"]
        GraphSvc["Graph Analysis & Neo4j/NetworkX Service"]
        StylometrySvc["AI Stylometric Profiler (TF-IDF & N-Grams)"]
        FusionSvc["Evidence Fusion & Contradiction Detection"]
        ReportSvc["ReportLab Forensic PDF Engine"]
    end

    subgraph DataTier ["Data & Persistence Tier"]
        Postgres[("PostgreSQL / SQLite Storage")]
        Neo4j[("Neo4j Graph Database")]
        RedisQueue[("Redis Cache & Celery Queue")]
    end

    UI --> Gateway
    Gateway --> AuthService
    Gateway --> IngestionSvc
    Gateway --> GraphSvc
    Gateway --> StylometrySvc
    Gateway --> FusionSvc
    Gateway --> ReportSvc

    AuthService --> Postgres
    IngestionSvc --> Postgres
    GraphSvc --> Neo4j
    GraphSvc --> Postgres
    StylometrySvc --> Postgres
    FusionSvc --> Postgres
    ReportSvc --> Postgres
    Gateway --> RedisQueue
```

---

## 3. Core Engine Mechanics

### 3.1 Entity Resolution & Normalization
Identifiers are normalized (lowercasing, symbol replacement, hash indexing) while preserving raw source values. Potential links are generated as candidate relationships rather than automatic merges.

### 3.2 Evidence Fusion & Contradiction Detection
Multi-factor signals (Cryptographic PGP keys, origin hosting IP correlations, stylometric cosine similarity) are weighted. Crucially, the system actively checks for contradictory evidence (divergent operational timelines, opposing timezones) before outputting an analytical assessment.

### 3.3 Evidence Integrity
Every evidence record computes and validates a SHA-256 hash across stored content. If a record has been tampered with or modified outside authorized channels, the system immediately flags `EVIDENCE INTEGRITY WARNING`.
