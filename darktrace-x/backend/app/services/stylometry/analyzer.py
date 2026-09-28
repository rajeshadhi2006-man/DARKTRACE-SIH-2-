import re
import math
from typing import Dict, Any, List, Optional
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

COMMON_FUNCTION_WORDS = [
    "the", "and", "to", "of", "a", "in", "that", "is", "for", "it", 
    "with", "as", "on", "was", "at", "by", "an", "be", "this", "which",
    "or", "from", "but", "not", "they", "we", "he", "she", "you", "if"
]

DARK_JARGON = [
    "fud", "escrow", "xmr", "monero", "btc", "rat", "stealer", "logs",
    "fullz", "rdp", "drop", "cashout", "loader", "shell", "priv8",
    "checker", "combo", "bypass", "zeroday", "botnet", "bulletproof",
    "exploit", "stealth", "ransom", "cryptor", "stub", "inject", "c2"
]

TIMEZONE_REGIONS = [
    {"name": "Americas / Eastern (EST/EDT)", "offset": -5, "typical_peak_utc": 19},
    {"name": "Americas / Pacific (PST/PDT)", "offset": -8, "typical_peak_utc": 22},
    {"name": "Western Europe (GMT/BST)", "offset": 0, "typical_peak_utc": 14},
    {"name": "Eastern Europe / CIS (MSK)", "offset": 3, "typical_peak_utc": 11},
    {"name": "South Asia (IST)", "offset": 5.5, "typical_peak_utc": 8},
    {"name": "East Asia (CST/JST)", "offset": 8, "typical_peak_utc": 6},
]

class StylometryAnalyzer:
    """
    Forensic-grade Stylometric & Behavioral Profiler.
    Extracts lexical richness, Yule's K metric, character 3-5 gram TF-IDF cosine similarity,
    invariant function word distributions, and diurnal timezone offsets.
    """

    def _tokenize_words(self, text: str) -> List[str]:
        return re.findall(r"\b[a-zA-Z0-9_\'-]+\b", text.lower())

    def _compute_yules_k(self, words: List[str]) -> float:
        """
        Calculates Yule's Characteristic K measure of vocabulary richness.
        K is statistically independent of text sample length.
        """
        if not words:
            return 0.0
        n = len(words)
        freqs = Counter(words)
        m2 = sum(count * count for count in freqs.values())
        if n == 0 or (m2 - n) <= 0:
            return 0.0
        k = 10000.0 * (m2 - n) / (n * n)
        return round(float(k), 2)

    def analyze_text(self, text: str) -> Dict[str, Any]:
        clean_text = text.strip()
        if not clean_text:
            return {"error": "Empty text sample"}

        sentences = [s.strip() for s in re.split(r'[.!?]+', clean_text) if s.strip()]
        sentence_count = max(1, len(sentences))

        words = self._tokenize_words(clean_text)
        word_count = max(1, len(words))

        avg_sentence_len = round(word_count / sentence_count, 2)
        total_word_chars = sum(len(w) for w in words)
        avg_word_len = round(total_word_chars / word_count, 2)

        unique_words = set(words)
        lexical_richness_ttr = round(len(unique_words) / word_count, 3)
        yules_k = self._compute_yules_k(words)

        puncts = re.findall(r'[,;:\'\"\-\(\)\[\]!?.]', clean_text)
        punct_entropy = round(len(puncts) / max(1, len(clean_text)), 3)

        upper_chars = sum(1 for c in clean_text if c.isupper())
        uppercase_ratio = round(upper_chars / max(1, len(clean_text)), 3)

        fw_freqs = {}
        for fw in COMMON_FUNCTION_WORDS:
            fw_freqs[fw] = round(words.count(fw) / word_count, 4)

        detected_jargon = [term for term in DARK_JARGON if term in words]

        return {
            "metrics": {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_sentence_length": avg_sentence_len,
                "avg_word_length": avg_word_len,
                "lexical_diversity_ttr": lexical_richness_ttr,
                "yules_characteristic_k": yules_k,
                "punctuation_entropy": punct_entropy,
                "uppercase_ratio": uppercase_ratio,
                "function_word_frequencies": fw_freqs,
                "characteristic_jargon": detected_jargon
            },
            "disclaimer": "Potential stylistic similarity requiring independent corroboration. Stylometry alone cannot confirm real-world identity."
        }

    def compare_texts(self, text_a: str, text_b: str) -> Dict[str, Any]:
        """
        Calculates character 3-5 gram TF-IDF cosine similarity,
        function word cosine alignment, and composite stylometric match score.
        """
        sample_a = text_a.strip()
        sample_b = text_b.strip()
        if not sample_a or not sample_b:
            return {"error": "Both text samples must be non-empty"}

        # 1. Character 3-5 gram TF-IDF Cosine Similarity
        vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=1,
            sublinear_tf=True
        )
        try:
            tfidf_matrix = vectorizer.fit_transform([sample_a, sample_b])
            char_ngram_sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
        except Exception:
            char_ngram_sim = 0.0

        # 2. Function Word Vector Similarity
        prof_a = self.analyze_text(sample_a)
        prof_b = self.analyze_text(sample_b)

        fw_a = [prof_a["metrics"]["function_word_frequencies"].get(w, 0.0) for w in COMMON_FUNCTION_WORDS]
        fw_b = [prof_b["metrics"]["function_word_frequencies"].get(w, 0.0) for w in COMMON_FUNCTION_WORDS]
        vec_a = np.array(fw_a).reshape(1, -1)
        vec_b = np.array(fw_b).reshape(1, -1)
        
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a > 0 and norm_b > 0:
            fw_sim = float(np.dot(vec_a, vec_b.T)[0][0] / (norm_a * norm_b))
        else:
            fw_sim = 0.5

        # 3. Punctuation & Structural Delta
        punct_delta = abs(prof_a["metrics"]["punctuation_entropy"] - prof_b["metrics"]["punctuation_entropy"])
        punct_sim = max(0.0, 1.0 - (punct_delta * 4.0))

        # 4. Composite Match Score
        composite_score = round(
            (0.50 * char_ngram_sim) + (0.30 * fw_sim) + (0.20 * punct_sim),
            4
        )

        match_confidence = "HIGH" if composite_score >= 0.78 else ("MEDIUM" if composite_score >= 0.55 else "LOW")

        return {
            "composite_similarity": composite_score,
            "match_confidence": match_confidence,
            "components": {
                "character_ngram_cosine_similarity": round(char_ngram_sim, 4),
                "function_word_vector_similarity": round(fw_sim, 4),
                "punctuation_structural_similarity": round(punct_sim, 4)
            },
            "profile_a": prof_a["metrics"],
            "profile_b": prof_b["metrics"],
            "evidentiary_assessment": (
                f"Stylometric match is {match_confidence} ({int(composite_score*100)}%). "
                "Corroborating cryptographic or network indicators required for positive attribution."
            )
        }

    def estimate_diurnal_timezone(self, utc_hours: List[int]) -> Dict[str, Any]:
        """
        Estimates the probable physical operational timezone of a threat actor
        based on their historical UTC posting hour distribution.
        """
        if not utc_hours:
            return {"error": "No UTC hours provided"}

        hour_counts = [0] * 24
        for h in utc_hours:
            if 0 <= h < 24:
                hour_counts[h] += 1

        total = len(utc_hours)
        peak_hour = int(np.argmax(hour_counts))

        # Find 6-hour consecutive window with minimum activity (dormant/sleep window)
        min_activity_sum = float("inf")
        dormant_start = 0
        for i in range(24):
            window_sum = sum(hour_counts[(i + j) % 24] for j in range(6))
            if window_sum < min_activity_sum:
                min_activity_sum = window_sum
                dormant_start = i

        dormant_window = f"{dormant_start:02d}:00 - {(dormant_start + 6) % 24:02d}:00 UTC"

        # Match against candidate timezone regions
        candidates = []
        for reg in TIMEZONE_REGIONS:
            diff = abs(peak_hour - reg["typical_peak_utc"])
            diff = min(diff, 24 - diff)
            fit_score = max(0.0, round(1.0 - (diff / 12.0), 2))
            candidates.append({
                "region": reg["name"],
                "utc_offset": reg["offset"],
                "fit_probability": fit_score
            })

        candidates.sort(key=lambda x: x["fit_probability"], reverse=True)
        primary = candidates[0]

        return {
            "total_observed_events": total,
            "peak_operational_hour_utc": peak_hour,
            "estimated_dormant_window_utc": dormant_window,
            "most_probable_timezone": primary["region"],
            "estimated_utc_offset": primary["utc_offset"],
            "regional_candidates": candidates[:3],
            "confidence": "HIGH" if total >= 25 else "PRELIMINARY"
        }

stylometry_analyzer = StylometryAnalyzer()
