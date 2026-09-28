# DARKTRACE-X // SIH 3–5 MINUTE LIVE DEMO WALKTHROUGH

## Demonstration Scenario: Unmasking Operator "NightFox" (TA-001)

### Credentials:
- **URL:** `http://127.0.0.1:8000/login`
- **Username:** `investigator`
- **Password:** `Investigator2026!`

---

### Step-by-Step SIH Presentation Script

```text
1. LOGIN & COMMAND CENTER OVERVIEW (0:00 - 0:45)
   • Log in as Lead CTI Analyst.
   • Showcase the live SOC/CTI Dashboard:
     - 21 Tracked Actors, 54 Personas, 30+ Cryptographic PGP Keys, 30+ Wallets, 108 Evidence Items.
     - Diurnal timeline, active threat categories, and real-time intercept feed.

2. INVESTIGATION WORKSPACE & SEED INGESTION (0:45 - 1:45)
   • Navigate to the INVESTIGATIONS tab.
   • Open Case: "CASE-SIH-001" (De-Anonymization of Operator NightFox).
   • Point out the Seed Indicator: Alias "nightfox_404" (from Dread forum).
   • Click "START CORRELATION" to trigger the live 7-stage attribution pipeline:
     - Collection → Entity Extraction → Entity Resolution → Infrastructure Correlation
       → Stylometry → Behavioral Profiling → Composite Attribution Confidence.

3. EXPLAINABLE ATTRIBUTION & CONTRADICTION RADAR (1:45 - 2:45)
   • Show the resulting Attribution Assessment:
     - Target Actor: TA-001 (NightFox)
     - Confidence: 82% (High Confidence)
     - Supporting Evidence: 7 independent artifacts
     - Contradicting Evidence: 1 diurnal operational window disparity
     - Status: "REQUIRES HUMAN VALIDATION"
   • Emphasize the explainability:
     1. PGP Fingerprint Match: 4096-bit RSA key identical between Dread & BreachForums.
     2. Wallet Collateral: 42.50 BTC on-chain escrow cluster overlap.
     3. Infrastructure Leak: TLS SAN on nightfox7x2u...onion exposed clearnet domain
        nightfox-portal.is resolving to 185.220.101.42 (AS200052, Netherlands).
     4. AI Stylometric Congruence: 82% writeprint match across sentence length and slang.
     5. The 1 Conflict: 13-hour diurnal shift gap (warns analyst of multi-operator syndicate).
   • Click "Confirm Attribution" to demonstrate Human-in-the-Loop decision making.

4. RELATIONSHIP GRAPH EXPLORATION (2:45 - 3:30)
   • Navigate to RELATIONSHIP GRAPH for TA-001.
   • Demonstrate interactive Cytoscape canvas:
     - Actor Node (TA-001) connected to Personas (nightfox_404, NightFox, NF_404).
     - Shortest evidentiary path connecting dark web handle to clearnet IP 185.220.101.42.
     - Inspect false-positive decoy node ("nightfox_support") showing disjoint connections.

5. CTI EXPORTS & FORENSIC DOSSIER (3:30 - 4:00)
   • Click "Export STIX 2.1" to show standardized JSON CTI bundle ready for OpenCTI / MISP.
   • Navigate to REPORTS and show generated ReportLab Forensic PDF Dossier.
   • Conclude with compliance statement: 100% legal OSINT & passive correlation.
```
