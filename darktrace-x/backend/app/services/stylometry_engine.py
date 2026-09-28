import re
import math
from collections import Counter
from typing import Dict, Any, List, Tuple

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with",
    "by", "about", "as", "into", "like", "through", "after", "over", "between",
    "out", "against", "during", "without", "before", "under", "around", "among"
}

def extract_stylometric_features(text: str) -> Dict[str, Any]:
    """
    Extracts deterministic stylometric metrics from forensic darknet text samples.
    NOTE: Strict safety adherence - never infers nationality, ethnicity, or gender.
    """
    if not text or not text.strip():
        return {
            "sentence_count": 0,
            "word_count": 0,
            "average_sentence_length": 0.0,
            "average_word_length": 0.0,
            "lexical_diversity_ttr": 0.0,
            "punctuation_density": 0.0,
            "punctuation_pattern": "standard",
            "common_terms": [],
            "top_trigrams": []
        }

    # Sentences split
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    sentence_count = max(1, len(sentences))

    # Words split
    words = re.findall(r'\b[a-zA-Z0-9_\-]+\b', text.lower())
    word_count = len(words)
    if word_count == 0:
        return {
            "sentence_count": sentence_count,
            "word_count": 0,
            "average_sentence_length": 0.0,
            "average_word_length": 0.0,
            "lexical_diversity_ttr": 0.0,
            "punctuation_density": 0.0,
            "punctuation_pattern": "standard",
            "common_terms": [],
            "top_trigrams": []
        }

    avg_sentence_len = round(word_count / sentence_count, 1)
    avg_word_len = round(sum(len(w) for w in words) / word_count, 2)
    lexical_diversity = round(len(set(words)) / word_count, 3)

    # Punctuation counts
    punct_count = len(re.findall(r'[,;:!?"\'.\(\)\-\[\]]', text))
    punct_density = round(punct_count / word_count, 3)

    punct_pattern = "standard"
    if "..." in text or ".." in text:
        punct_pattern = "frequent_ellipses"
    elif "!?" in text or "?!" in text or "!!" in text:
        punct_pattern = "multiple_exclamations"
    elif ";" in text or "--" in text:
        punct_pattern = "clause_heavy"

    # Common informative terms (excluding common stopwords)
    informative_words = [w for w in words if w not in STOPWORDS and len(w) > 3]
    word_freq = Counter(informative_words)
    common_terms = [word for word, _ in word_freq.most_common(8)]

    # Character trigrams
    cleaned_compact = re.sub(r'\s+', ' ', text.lower())
    trigrams = [cleaned_compact[i:i+3] for i in range(len(cleaned_compact)-2)]
    trigram_freq = Counter(trigrams)
    top_trigrams = [t for t, _ in trigram_freq.most_common(10)]

    return {
        "sentence_count": sentence_count,
        "word_count": word_count,
        "average_sentence_length": avg_sentence_len,
        "average_word_length": avg_word_len,
        "lexical_diversity_ttr": lexical_diversity,
        "punctuation_density": punct_density,
        "punctuation_pattern": punct_pattern,
        "common_terms": common_terms,
        "top_trigrams": top_trigrams
    }

def compare_stylometric_profiles(profile_a: Dict[str, Any], profile_b: Dict[str, Any]) -> Tuple[float, List[str]]:
    """
    Computes linguistic similarity score (0-100) between two profiles.
    Returns (score, observations_list).
    """
    observations = []

    # 1. Sentence length similarity (20 pts)
    sl_a = profile_a.get("average_sentence_length", 0.0)
    sl_b = profile_b.get("average_sentence_length", 0.0)
    diff_sl = abs(sl_a - sl_b)
    sl_score = max(0.0, 20.0 - (diff_sl * 1.5))
    if diff_sl < 3.0:
        observations.append(f"Near-identical sentence syntax cadence (A: {sl_a} vs B: {sl_b} words/sentence)")

    # 2. Vocabulary overlap (Jaccard similarity on common terms) (35 pts)
    terms_a = set(profile_a.get("common_terms", []))
    terms_b = set(profile_b.get("common_terms", []))
    if terms_a and terms_b:
        shared = terms_a.intersection(terms_b)
        union = terms_a.union(terms_b)
        jaccard = len(shared) / len(union) if union else 0.0
        vocab_score = jaccard * 35.0
        if len(shared) >= 2:
            observations.append(f"Shared technical lexicon: {', '.join(list(shared)[:4])}")
    else:
        vocab_score = 10.0

    # 3. Trigram overlap (25 pts)
    tri_a = set(profile_a.get("top_trigrams", []))
    tri_b = set(profile_b.get("top_trigrams", []))
    if tri_a and tri_b:
        shared_tri = tri_a.intersection(tri_b)
        tri_score = (len(shared_tri) / max(len(tri_a), len(tri_b))) * 25.0
        if len(shared_tri) >= 4:
            observations.append(f"High sub-word n-gram concurrence ({len(shared_tri)} common trigrams)")
    else:
        tri_score = 8.0

    # 4. Punctuation profile similarity (20 pts)
    pat_a = profile_a.get("punctuation_pattern", "")
    pat_b = profile_b.get("punctuation_pattern", "")
    punct_score = 20.0 if (pat_a == pat_b and pat_a != "standard") else (14.0 if pat_a == pat_b else 6.0)
    if pat_a == pat_b and pat_a != "standard":
        observations.append(f"Distinctive punctuation habit matched: '{pat_a}'")

    total_score = round(min(100.0, max(0.0, sl_score + vocab_score + tri_score + punct_score)), 1)
    return total_score, observations
