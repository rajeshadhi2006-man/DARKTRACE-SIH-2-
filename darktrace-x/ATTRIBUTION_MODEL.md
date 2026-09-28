# DARKTRACE-X // ATTRIBUTION CONFIDENCE & CONTRADICTION MODEL

## 1. Multi-Factor Attribution Scoring Model

DARKTRACE-X uses an explainable, multi-factor attribution model with configurable evidentiary weights:

$$\text{Composite Score} = \sum_{i=1}^{n} (w_i \cdot s_i) - \text{Contradiction Penalty}$$

### Configurable Factor Weights:

| Evidentiary Dimension | Default Weight ($w_i$) | Signal Description ($s_i$) |
| :--- | :---: | :--- |
| **Identifier Match** | **20%** | String similarity, handle permutations, and alias re-use across forums. |
| **Infrastructure Correlation** | **20%** | TLS SAN cert leaks, Apache `/server-status` leaks, Favicon Murmur3 hashes. |
| **PGP Key Correlation** | **15%** | Direct 4096-bit RSA cryptographic public key and fingerprint matches. |
| **Behavioral Similarity** | **15%** | Diurnal active hours distribution, peak UTC alignment, interval pacing. |
| **Stylometric Similarity** | **15%** | TF-IDF character n-gram cosine similarity, Yule's K vocabulary richness. |
| **Temporal Correlation** | **10%** | Persona migration window succession and timeline non-collision. |
| **Independent Corroboration** | **5%** | Cross-source confirmation from 3rd party research or forum escrow moderators. |

---

## 2. Confidence Tiers & Verdicts

| Score Range | Analytical Rating | Recommended Action |
| :---: | :---: | :--- |
| **80% – 100%** | **VERY HIGH** | Potential attribution; mandatory human analyst sign-off before legal referral. |
| **60% – 79%** | **HIGH** | High-probability correlation; requires human investigator validation. |
| **30% – 59%** | **MODERATE** | Inconclusive; requires independent corroboration. |
| **0% – 29%** | **LOW** | Disjoint personas; do not merge. |

---

## 3. False Positive Prevention & Contradiction Penalty

To prevent erroneous attributions:
1. **Diurnal Timezone Disparity:** A difference of $\ge 7$ hours in peak UTC active hours applies a **-0.20** penalty and triggers a `CONTRADICTION DETECTED` flag.
2. **Disjoint Cryptographic Keys:** Active usage of non-cross-signed PGP keys across concurrent active threads applies a **-0.25** penalty.
3. **Decoy Patterns:** Handles using impersonation keywords (`official`, `support`, `admin`) without cryptographic key ownership trigger a `PHISHING DECOY` warning.
4. **Concurrent Collisions:** Simultaneous actions logged in mutually exclusive auctions flag a multi-operator syndicate warning.
