# DARKTRACE-X // Database Architecture & Schemas

DARKTRACE-X employs a hybrid polyglot persistence architecture:
1. **Relational Database (PostgreSQL / SQLite)** for structured intelligence entities, audit logging, and RBAC.
2. **Graph Database (Neo4j / NetworkX)** for multi-relational entity resolution and pathfinding.

---

## 1. Relational Database Tables

| Table | Primary Key | Description |
| :--- | :--- | :--- |
| `users` | `id` (UUID) | System users with role, email, and Argon2/bcrypt hash |
| `roles` | `id` (VARCHAR) | RBAC roles: `ADMIN`, `SUPERVISOR`, `ANALYST`, `VIEWER` |
| `actors` | `id` (`ACT-XXXX`) | High-level threat groups and master syndicates |
| `personas` | `id` (`PER-XXXX`) | Online handles and marketplace accounts |
| `handles` | `id` (`HND-XXXX`) | Normalized alias records mapped to original values |
| `pgp_keys` | `id` (`KEY-XXXX`) | 4096-bit public key fingerprints and identities |
| `wallets` | `id` (`WALLET-XXXX`)| Cryptocurrency addresses (BTC, XMR, ETH, USDT) |
| `domains` | `id` (`DOM-XXXX`) | Tor `.onion` addresses and correlated clearnet domains |
| `infrastructure` | `id` (`INF-XXXX`) | IP addresses, SSL certificate SANs, Murmur3 favicon hashes |
| `sources` | `id` (`SRC-XXXX`) | Monitored forums, markets, and recon sensor nodes |
| `observations` | `id` (`OBS-XXXX`) | Raw ingested intelligence records with SHA-256 integrity hash |
| `evidence` | `id` (`EVID-XXXX`)| Verified evidentiary artifacts with provenance and integrity status |
| `relationships`| `id` (`REL-XXXX`) | Directed graph links between entities with confidence and evidence link |
| `timeline_events`| `id` (`TML-XXXX`)| Chronological observation events |
| `stylometric_profiles`| `id` (`STP-XXXX`)| Linguistic writeprints, function word signatures, and vocabulary richness |
| `behavior_profiles`| `id` (`BEH-XXXX`)| Diurnal UTC posting hour histograms and estimated timezones |
| `attribution_assessments`| `id` (`ATTR-XXXX`)| Evidence fusion evaluations with supporting and contradicting signals |
| `analyst_notes`| `id` (`NOTE-XXXX`)| Case notes annotated by investigators with TLP classification |
| `audit_logs` | `id` (`AUDIT-XXXX`)| Immutable log of logins, searches, dossier views, and report exports |
| `reports` | `id` (`REP-XXXX`) | Compiled investigation dossiers with SHA-256 hash |

---

## 2. Mandatory Intelligence Audit Fields

Every record maintains provenance:
- `id`
- `source_id`
- `timestamp`
- `collection_timestamp`
- `confidence` (0.0 to 1.0)
- `reliability` (`A` to `F`)
- `provenance` (Data origin statement)
- `created_at`
- `updated_at`

---

## 3. Neo4j Graph Model

### Nodes:
- `(:Actor)`
- `(:Persona)`
- `(:Handle)`
- `(:PGPKey)`
- `(:Wallet)`
- `(:Domain)`
- `(:Infrastructure)`
- `(:Evidence)`
- `(:Source)`

### Relationships:
- `[:USES_HANDLE]`
- `[:OPERATES_ON]`
- `[:OWNS_PGP_KEY]`
- `[:CONTROLS_WALLET]`
- `[:CONNECTED_TO]`
- `[:SIMILAR_TO]`
- `[:MIGRATED_TO]`
- `[:SUPPORTED_BY]`
- `[:CONTRADICTED_BY]`
