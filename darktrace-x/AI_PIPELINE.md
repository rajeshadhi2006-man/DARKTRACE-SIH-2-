# DARKTRACE-X // AI & NATURAL LANGUAGE INTELLIGENCE PIPELINE

## 1. Pipeline Architecture

```text
RAW UNDERGROUND TEXT
        ↓
ENTITY EXTRACTION (Regex + NLP, 25+ Entities)
        ↓
STYLOMETRIC PROFILING (Yule's K, TF-IDF Character 3-5 Grams)
        ↓
BEHAVIORAL PROFILING (24-Hour Diurnal Histogram, Operational UTC Timezone)
        ↓
CONTRADICTION ENGINE (Active Checks: Disjoint PGP, Timezone Conflicts, Decoys)
        ↓
AI CORRELATION & COPILOT (RAG Entity Grounding, FACT/INFERENCE/HYPOTHESIS Guardrails)
```

---

## 2. Stylometric Writeprint Analysis

### Mathematical Formulations

1. **Yule's Characteristic K Metric:**
   Measures vocabulary richness independent of text sample length:
   $$K = 10^4 \cdot \frac{\sum_{i=1}^{\infty} i^2 V(i, N) - N}{N^2}$$
   where $N$ is total word tokens, and $V(i, N)$ is the count of words appearing exactly $i$ times.

2. **Lexical Diversity (Type-Token Ratio / TTR):**
   $$TTR = \frac{|V|}{N}$$
   where $|V|$ is unique vocabulary count.

3. **Character 3–5 Gram TF-IDF Cosine Similarity:**
   Transforms extortion notes, forum posts, and listings into character sub-word vectors to resist intentional obfuscation or misspelling:
   $$\text{Similarity}(u, v) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$

4. **Invariant Function Word Frequencies:**
   Analyzes usage ratios of 30 invariant grammatical stop words (`the`, `and`, `to`, `of`, `that`, `with`, `for`, `which`, `from`, `not`) that reflect subconscious author writing habits.

---

## 3. Behavioral Timezone & Migration Profiling

- **Diurnal Histogram:** Evaluates 24-hour UTC posting timestamps to determine peak operational windows.
- **Timezone Classification:** Maps peak activity to geographical regions:
  - Eastern Europe / CIS (MSK): Typical peak UTC 11:00–13:00.
  - Western Europe (GMT/BST): Typical peak UTC 14:00–16:00.
  - Americas / Eastern (EST/EDT): Typical peak UTC 19:00–22:00.
  - East Asia (CST/JST): Typical peak UTC 06:00–08:00.
- **Migration Detection:** Automatically flags when an established persona ceases activity on one forum and a new persona emerges within a 15–120 day window possessing matching PGP keys or congruent stylometrics.

---

## 4. AI Security Guardrails & Labeling

The RAG-grounded AI Investigator Copilot enforces strict evidentiary guardrails:
- **`FACT`**: Direct database observation verified by an immutable SHA-256 evidence record.
- **`INFERENCE`**: High-confidence correlation supported by multiple intersecting signals (e.g. shared PGP + matching TLS SAN).
- **`HYPOTHESIS`**: Analytical possibility requiring corroborative evidence.
- **`UNCERTAINTY`**: Explicit gaps or missing pieces of evidence that prevent full attribution.
- **Zero Hallucination:** The model only cites indexed entities (`[EVID-NF-01]`, `[SRC-DREAD]`).
