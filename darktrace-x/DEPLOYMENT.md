# DARKTRACE-X // PRODUCTION DEPLOYMENT & CONTAINERIZATION

## 1. Local Quickstart (Single Command)

From the project root directory or `darktrace-x/`, execute:

```bash
python start.py
```

- Boots FastAPI Intelligence Gateway on `http://127.0.0.1:8000`.
- Automatically initializes SQLite database and seeds 21 threat actors, campaigns, and alerts.
- Launches default browser to `http://127.0.0.1:8000/login`.

---

## 2. Docker Compose Multi-Container Architecture

```bash
docker compose up -d
```

### Services Orchestrated:

| Container Service | Image / Base | Internal Port | Description |
| :--- | :--- | :--- | :--- |
| **`backend`** | Python 3.12-slim | `8000` | FastAPI REST API Gateway & CTI Engine |
| **`frontend`** | Nginx Alpine | `80` | Pre-built React 18 + Vite static command center |
| **`postgres`** | `postgres:16-alpine` | `5432` | Relational intelligence and audit repository |
| **`neo4j`** | `neo4j:5.18-community` | `7474`, `7687` | Property graph database for network analytics |
| **`redis`** | `redis:8.0-alpine` | `6379` | Cache broker and background worker queue |
| **`worker`** | Python 3.12-slim | N/A | Celery background pipeline processor |

---

## 3. Environment Variables Configuration (`.env`)

```ini
APP_ENV=production
DATABASE_URL=postgresql://darktrace_user:darktrace_password@postgres:5432/darktrace_db
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=darktrace_neo4j_password
REDIS_URL=redis://redis:6379/0
JWT_SECRET=DARKTRACE_PRODUCTION_JWT_SECRET_2026_KEY
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```
