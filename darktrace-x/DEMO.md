# DARKTRACE-X // Demonstration Scenario & Evaluation Guide

This guide walks an investigator or evaluator through the complete demonstration scenario designed to test entity resolution, stylometry, infrastructure correlation, contradiction detection, and report generation.

---

## 🎭 The Demonstration Scenario

### Threat Actor: `ACT-0042` ("The Phantom Syndicate")
- **Persona A**: `ShadowX` (Active on Dread, verified seller)
- **Persona B**: `NightWolf` (Active on BreachForums, network access broker)
- **Decoy Persona**: `ShadowXOfficial` (Public Telegram channel - false positive decoy)

### Discovered Corroborating Signals:
1. **Shared Cryptographic PGP Key `[EVID-0001]`**:
   Both personas signed escrow messages with identical 4096-bit RSA PGP key `KEY-001` (Fingerprint: `7C8B9A0D1E2F3A4B5C6D7E8F9A0B1C2D3E4F5A6B`).
2. **Hosting Infrastructure Correlation `[EVID-0002]`**:
   Origin server de-cloaked to IP `194.26.29.114` (AS49981 WorldStream B.V., Amsterdam) via Apache status leak and TLS SAN certificate match.
3. **AI Stylometric Consistency `[EVID-0003]`**:
   TF-IDF character 3–5 gram cosine similarity of 88.4%, with matching punctuation entropy and invariant function word ratios.

### Active Contradicting Evidence `[EVID-0004]`:
- **Temporal Divergence**: ShadowX ceased activity on Dread 120 days ago, while NightWolf emerged 115 days ago on BreachForums.
- **Diurnal Variance**: UTC posting distributions show a 4-hour variance in peak operating hours (UTC+02:00 vs UTC+06:00).

### Resulting Assessment:
- **Type**: `POTENTIAL_PERSONA_RELATIONSHIP`
- **Analytical Confidence**: `MEDIUM` (68%)
- **Supporting Evidence**: 3
- **Contradicting Evidence**: 1
- **Recommendation**: `MANUAL_INVESTIGATOR_REVIEW`

---

## 🚀 8-Step Walkthrough

1. **Step 1 - Access Platform & Authenticate**:
   Navigate to `http://127.0.0.1:8000/login`. Click **"Lead Analyst"** to prefill demo credentials (`investigator` / `Investigator2026!`). Click **Access Intelligence Platform**.

2. **Step 2 - Open Intelligence Dashboard**:
   View real-time database KPIs (Total Actors: 20, Personas: 41, Evidence Items: 104, Relationships: 168). Examine **"High-Priority Attribution Findings"** and click on `Potential Persona Link: ShadowX ↔ NightWolf`.

3. **Step 3 - Inspect Actor Dossier**:
   Review the dossier for `ACT-0042`. Explore the **Personas** tab to see normalized handles and platforms.

4. **Step 4 - Explore Relationship Graph**:
   Click **"Explore Graph"** (or open the **Relationship Graph** tab). Cytoscape.js visualizes the multi-relational network. Click on `ShadowX`, `NightWolf`, and the connected diamond node `KEY-001`. Notice the inspector sidebar shows relationship confidence and evidence references.

5. **Step 5 - Inspect Evidence Integrity**:
   Open the **Evidence** tab. Select `[EVID-0001]`. Notice the glowing `VERIFIED_INTEGRITY` status badge and SHA-256 cryptographic digest ensuring tamper-proof provenance.

6. **Step 6 - Review Attribution & Contradictions**:
   Open the **Attribution** tab. Observe the side-by-side presentation of **SUPPORTING EVIDENCE (3)** alongside **CONTRADICTING EVIDENCE (1)** highlighting the diurnal timezone shift.

7. **Step 7 - Conduct Human Review**:
   Click **"Conduct Investigator Review"**. Input rationale (e.g., *"Confirmed probable migration based on PGP continuity and infrastructure alignment"*), and click **Confirm Link**. Notice the status updates to `CONFIRMED BY ANALYST`.

8. **Step 8 - Generate Forensic Dossier PDF**:
   Navigate to the **Reports** tab (or click **"Export Dossier PDF"** on the actor dossier). Click **Generate New Investigation Dossier**. A court-admissible PDF document is compiled via ReportLab with executive summary, identifiers, contradiction breakdown, and audit markings.
