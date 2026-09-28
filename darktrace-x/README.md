# DARKTRACE-X
### AI-Powered Dark Web Threat Intelligence, Entity Resolution & Attribution Platform

DARKTRACE-X is a cyber threat intelligence and attribution system designed for authorized cybersecurity research, law enforcement threat analysis, and digital forensics investigations.

The platform correlates fragmented underground footprints (handles, aliases, PGP fingerprints, cryptocurrency wallet clusters, hosting metadata, and stylometric characteristics) to produce explainable, evidence-backed attribution assessments with mandatory human-in-the-loop validation.

---

## 🏛️ Core Principles

```
COLLECT → NORMALIZE → EXTRACT → RESOLVE → CORRELATE → ANALYZE → FUSE EVIDENCE → CHECK CONTRADICTIONS → GENERATE ASSESSMENT → HUMAN REVIEW
```

- **Explainable & Traceable**: Every analytical conclusion is cited by internal artifact IDs (`[EVID-0001]`, `[SRC-DREAD]`).
- **Active Contradiction Checking**: Actively searches for conflicting indicators (such as temporal divergences or opposing timezones) before outputting an assessment.
- **Strict Compliance**: Operates purely on authorized research datasets, public OSINT, and passive infrastructure correlation. Does NOT engage in unauthorized hacking, network exploitation, or credential theft.

---

## 💻 Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Cytoscape.js, Recharts, Lucide Icons |
| **Backend** | Python 3.12+, FastAPI, SQLAlchemy, Pydantic, Uvicorn, Passlib/Bcrypt |
| **Persistence** | PostgreSQL / SQLite, Neo4j Graph Database, Redis Cache |
| **AI / NLP** | Scikit-learn, TF-IDF Character N-Grams, Stylometric Feature Extractors |
| **Reporting** | ReportLab (PDF), Pandas / CSV, JSON Export |
| **Containerization**| Docker, Docker Compose, Nginx Reverse Proxy |

---

## ⚡ Quickstart Guide

### 1. Requirements
- Python 3.12+
- Node.js v18+ (Node.js v25 verified)

### 2. Launch the Application

From the `darktrace-x/` directory, launch the integrated starter script:

```bash
python start.py
```

*This starts the FastAPI intelligence engine and serves the React + TypeScript command center at `http://127.0.0.1:8000`.*

Alternatively, run with Docker Compose:
```bash
docker compose up -d
```

---

## 🔑 Demo Investigator Accounts

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Lead Analyst** | `investigator` | `Investigator2026!` | Full actor analysis, evidence review, and graph inspection |
| **Admin** | `admin` | `DarktraceAdmin2026!` | User management, audit logs, and system configuration |
| **Supervisor** | `supervisor` | `Supervisor2026!` | Attribution review sign-off and report authorization |
| **Viewer** | `viewer` | `Viewer2026!` | Read-only threat intelligence observation |

---

## 📁 Repository Structure

```
darktrace-x/
├── frontend/                     # React + TypeScript + Vite Client
│   ├── src/
│   │   ├── layouts/AppLayout.tsx # 12-tab sidebar shell and topbar
│   │   ├── pages/                # Dashboard, Actors, Graph, Timeline, Attribution, etc.
│   │   ├── services/api.ts       # Axios API client mapped to FastAPI
│   │   └── types/index.ts        # Pydantic-mirrored TypeScript interfaces
│   └── package.json
│
├── backend/                      # FastAPI Intelligence Engine
│   ├── app/
│   │   ├── api/                  # Modular routers (actors, graph, evidence, attribution, reports)
│   │   ├── database/             # SQLAlchemy connection & synthetic data seeder
│   │   ├── models/entities.py    # Complete database schema
│   │   ├── schemas/entities.py   # Pydantic validation schemas
│   │   ├── security/auth.py      # JWT token management & RBAC guards
│   │   └── main.py               # Application entrypoint & static mount
│   ├── requirements.txt
│   └── Dockerfile
│
├── data/                         # Local database & synthetic intelligence storage
├── reports/                      # Generated forensic PDF dossiers
├── nginx/                        # Nginx reverse proxy configuration
├── docker-compose.yml            # Multi-container orchestration
├── .env.example                  # Environment configuration template
├── ARCHITECTURE.md               # Detailed system design
├── API.md                        # REST API reference documentation
├── DATABASE.md                   # Relational & graph schema reference
├── SECURITY.md                   # Security & compliance standards
└── DEMO.md                       # Step-by-step evaluator walkthrough
```

---

## 🏆 Demonstration Scenario: `ACT-0042`

See **[DEMO.md](file:///d:/ALL%20PROJECT/SIH%202/darktrace-x/DEMO.md)** for a guided 8-step evaluation:
- **Actor ACT-0042** correlates Dread vendor `ShadowX` with BreachForums actor `NightWolf`.
- Cryptographic link via shared PGP Key `KEY-001` `[EVID-0001]`.
- Clearnet origin IP `194.26.29.114` de-cloaked via Apache status leak `[EVID-0002]`.
- 88.4% AI stylometric cosine similarity `[EVID-0003]`.
- Active contradiction detected: 4-hour timezone variance and non-overlapping timeline `[EVID-0004]`.
- Output: `POTENTIAL_PERSONA_RELATIONSHIP` requiring human-in-the-loop review.
