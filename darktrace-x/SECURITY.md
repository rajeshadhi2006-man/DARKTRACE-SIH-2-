# DARKTRACE-X // Security & Compliance Architecture

## 1. Authentication & Session Management
- **Password Storage**: Passwords hashed using standard `bcrypt` with unique random salt per user.
- **JWT Authorization**: Signed using HMAC-SHA256 with 8-hour expiry.
- **Role-Based Access Control (RBAC)**:
  - `ADMIN`: User management, system configuration, audit review.
  - `SUPERVISOR`: Attribution sign-off, investigation management, report generation.
  - `ANALYST`: Actor investigation, stylometric profiling, entity graph analysis, note creation.
  - `VIEWER`: Read-only intelligence exploration.

---

## 2. Evidence Integrity Assurance
- **SHA-256 Checksums**: Every evidence record calculates a SHA-256 digest of stored text upon creation.
- **Integrity Verification**: Upon viewing, the system recalculates the digest against the stored hash. If a discrepancy is detected, the UI displays `EVIDENCE INTEGRITY WARNING`.

---

## 3. Passive Intelligence & Ethical Guardrails
- **Passive Reconnaissance Only**: The platform exclusively correlates public OSINT, certificate transparency logs, and investigator-provided datasets.
- **No Unauthorized Exploitation**: The system does not attack, exploit, or disrupt Tor hidden services or clearnet hosts.
- **No Automated Identity Claims**: The platform strictly prohibits automated assertions claiming two personas are identical real-world individuals; all candidate links require human investigator corroboration.
