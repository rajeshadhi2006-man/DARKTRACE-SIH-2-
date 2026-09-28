# DARKTRACE-X // MULTI-RELATIONAL GRAPH DATA MODEL

## 1. Graph Architecture Overview

DARKTRACE-X utilizes a dual-engine graph architecture:
- **Primary Engine:** Neo4j Property Graph Database (Bolt protocol on `bolt://localhost:7687`).
- **Resilient Fallback Engine:** In-memory NetworkX MultiDiGraph directed multi-relational graph engine.

The graph captures cross-marketplace identities, shared cryptocurrency deposit clusters, infrastructure misconfigurations, cryptographic keys, and communication channels.

---

## 2. Node Schema

| Node Label | Core Properties | Example Identifier |
| :--- | :--- | :--- |
| **`Actor`** | `id`, `name`, `threat_category`, `threat_level`, `confidence_score` | `TA-001`, `ACT-0042` |
| **`Persona`** | `id`, `canonical_handle`, `platform`, `activity_count`, `confidence` | `PER-NF01` (`nightfox_404`) |
| **`Handle`** | `id`, `original_value`, `normalized_value`, `platform` | `HND-NF-01` (`nightfox_404`) |
| **`PGPKey`** | `id`, `key_id`, `fingerprint`, `bit_length`, `algorithm` | `KEY-NF-01` (`8F7E6D5C...`) |
| **`Wallet`** | `id`, `currency`, `address`, `cluster_tags`, `total_received` | `WALLET-NF-01` (`bc1qnightfox...`) |
| **`Domain`** | `id`, `domain_name`, `is_onion`, `resolved_ip` | `DOM-NF-01` (`nightfox7x...onion`) |
| **`Infrastructure`**| `id`, `indicator_type`, `indicator_value`, `clearnet_correlation`, `asn_isp` | `INF-NF-01` (`185.220.101.42`) |
| **`Campaign`** | `id`, `name`, `target_sectors`, `mitre_techniques`, `confidence` | `CMP-001` (`Operation DarkHydra`) |
| **`Forum`** | `id`, `name`, `onion_url`, `reliability` | `SRC-DREAD`, `SRC-BREACH` |

---

## 3. Edge Schema (Relationships)

Every edge contains cryptographic provenance metadata:
```json
{
  "relation": "LEAKS_TO_ORIGIN",
  "confidence": 0.96,
  "evidence_id": "EVID-NF-03",
  "source": "SRC-CERT-LOGS",
  "timestamp": "2026-09-27T12:00:00Z"
}
```

| Edge Type | Source Node | Target Node | Evidentiary Meaning |
| :--- | :--- | :--- | :--- |
| **`CONTROLS_PERSONA`** | `Actor` | `Persona` | Threat group operates designated underground persona. |
| **`USES_HANDLE`** | `Persona` | `Handle` | Specific handle string variant utilized across forums. |
| **`OWNS_PGP_KEY`** | `Persona` | `PGPKey` | Persona signed or published the 4096-bit RSA public key. |
| **`CONTROLS_WALLET`** | `Persona` | `Wallet` | Blockchain address used for escrow or ransom collateral. |
| **`OPERATES_ONION_SERVICE`** | `Actor` | `Domain` | Threat actor hosts hidden service portal on Tor network. |
| **`LEAKS_TO_ORIGIN`** | `Domain` | `Infrastructure` | TLS SAN or Apache server-status leaks origin clearnet IP. |
| **`ATTRIBUTED_TO`** | `Campaign` | `Actor` | Campaign activity linked to threat actor. |
| **`MIGRATED_TO`** | `Persona` | `Persona` | Rebranding succession detected across platforms. |

---

## 4. Graph Algorithms & Analytics

1. **Shortest Attribution Path (Dijkstra / BFS):**
   Discovers the exact evidentiary bridge from an anonymous forum handle (e.g. `nightfox_404`) to an unmasked real-world IP (e.g. `185.220.101.42`).
2. **Community Detection (Greedy Modularity / Louvain):**
   Partitions the entity graph into tightly-knit cybercrime syndicates and infrastructure-sharing cartels.
3. **Degree & Betweenness Centrality:**
   Identifies critical key brokers, shared escrow wallets, and bulletproof hosting providers connecting disparate threat personas.
