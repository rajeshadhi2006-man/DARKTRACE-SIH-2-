# DARKTRACE-X // REST API Reference

All requests require Bearer token authentication in the `Authorization` header, except `/api/auth/login` and `/api/health`.

---

## 1. Authentication Endpoints

| Endpoint | Method | Role | Description |
| :--- | :---: | :---: | :--- |
| `/api/auth/login` | `POST` | Public | OAuth2 form authentication, returns JWT access token |
| `/api/auth/login/json` | `POST` | Public | JSON body authentication (`username`, `password`) |
| `/api/auth/me` | `GET` | Authenticated | Retrieves active user identity, role, and permissions |

---

## 2. Threat Actor & Persona Endpoints

| Endpoint | Method | Role | Description |
| :--- | :---: | :---: | :--- |
| `/api/actors` | `GET` | Viewer+ | Query threat actors by category, threat level, confidence |
| `/api/actors/{id}` | `GET` | Viewer+ | Full actor dossier (personas, assessments, notes) |
| `/api/personas` | `GET` | Viewer+ | List online personas across platforms |
| `/api/personas/{id}` | `GET` | Viewer+ | Persona profile with stylometric & behavioral metrics |

---

## 3. Graph & Evidence Endpoints

| Endpoint | Method | Role | Description |
| :--- | :---: | :---: | :--- |
| `/api/graph/{actor_id}` | `GET` | Viewer+ | Cytoscape nodes and edges for progressive network rendering |
| `/api/evidence` | `GET` | Viewer+ | Filter evidence records by type and confidence |
| `/api/evidence/{id}` | `GET` | Viewer+ | Evidence detail with SHA-256 integrity check |
| `/api/timeline/{actor_id}` | `GET` | Viewer+ | Chronological timeline of events for an actor |

---

## 4. Attribution & Analytics Endpoints

| Endpoint | Method | Role | Description |
| :--- | :---: | :---: | :--- |
| `/api/attribution/{actor_id}` | `GET` | Viewer+ | Supporting & contradicting evidence for persona relationships |
| `/api/attribution/review` | `POST` | Supervisor+ | Human investigator review sign-off on potential relationships |
| `/api/analytics/run` | `POST` | Analyst+ | Triggers background stylometric or behavior profiling job |
| `/api/analytics/assistant` | `POST` | Analyst+ | Evidence-grounded AI investigator assistant query |

---

## 5. Ingestion, Search & Reporting

| Endpoint | Method | Role | Description |
| :--- | :---: | :---: | :--- |
| `/api/intelligence` | `GET` | Viewer+ | Ingested intelligence records |
| `/api/intelligence/upload` | `POST` | Analyst+ | Multipart upload for CSV/JSON structured datasets |
| `/api/search` | `GET` | Viewer+ | Global cross-entity search across actors, keys, wallets, IPs |
| `/api/reports` | `GET` | Viewer+ | List archived investigation reports |
| `/api/reports/generate` | `POST` | Supervisor+ | Compile official PDF investigation dossier |
| `/api/reports/download/{id}` | `GET` | Viewer+ | Download compiled PDF dossier |
| `/api/audit` | `GET` | Admin | Review immutable investigator audit logs |
