import re
import math
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

COMMON_FUNCTION_WORDS = [
    "the", "and", "of", "to", "a", "in", "that", "is", "was", "for", 
    "it", "with", "as", "on", "be", "at", "by", "this", "from", "they",
    "we", "you", "not", "or", "an", "will", "my", "all", "would", "there"
]

DARK_JARGON_MARKERS = [
    "fud", "escrow", "xmr", "monero", "btc", "rat", "stealer", "logs", 
    "fullz", "rdp", "drop", "cashout", "loader", "shell", "priv8", 
    "checker", "combo", "bypass", "zeroday", "botnet", "bulletproof",
    "jabber", "tox", "pgp", "decryptor", "ransom", "leak", "dump"
]

class StylometryEngine:
    """
    AI-based Stylometric Persona Identification and Behavioral Profiler.
    Extracts syntactic writeprints, function word distributions, punctuation entropy,
    lexical diversity, and character n-gram TF-IDF embeddings to link rebranded
    or migrated darkweb personas to known threat actors.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(3, 5),
            min_df=1,
            sublinear_tf=True
        )
        self.actor_corpora: Dict[str, List[str]] = {}
        self.actor_metadata: Dict[str, Dict[str, Any]] = {}
        self._fitted = False

    def train_or_update(self, actors: List[Dict[str, Any]]):
        """Trains the vectorizer on indexed actor sample posts."""
        all_texts = []
        self.actor_corpora.clear()
        self.actor_metadata.clear()

        for actor in actors:
            actor_id = actor["id"]
            posts = actor.get("sample_posts", [])
            if posts:
                self.actor_corpora[actor_id] = posts
                self.actor_metadata[actor_id] = {
                    "primary_handle": actor["primary_handle"],
                    "category": actor["category"],
                    "confidence": actor["attribution_confidence"],
                    "active_hours_utc": actor.get("active_hours_utc", [])
                }
                all_texts.extend(posts)

        if all_texts:
            self.vectorizer.fit(all_texts)
            self._fitted = True

    def extract_writeprint(self, text: str) -> Dict[str, Any]:
        """Extracts granular stylistic markers and quantitative text features."""
        clean_text = text.strip()
        if not clean_text:
            return {
                "avg_sentence_length": 0.0,
                "avg_word_length": 0.0,
                "lexical_richness": 0.0,
                "punctuation_entropy": 0.0,
                "uppercase_ratio": 0.0,
                "function_word_signature": {},
                "detected_slang_jargon": []
            }

        sentences = re.split(r'[.!?]+', clean_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = max(1, len(sentences))

        words = re.findall(r'\b[a-zA-Z0-9_\'-]+\b', clean_text.lower())
        word_count = max(1, len(words))

        # Sentence & Word Length
        avg_sentence_len = round(word_count / sentence_count, 2)
        total_word_chars = sum(len(w) for w in words)
        avg_word_len = round(total_word_chars / word_count, 2)

        # Lexical Richness: Type-Token Ratio (TTR)
        unique_words = set(words)
        lexical_richness = round(len(unique_words) / word_count, 3)

        # Punctuation analysis
        puncts = re.findall(r'[,;:\'\"\-\(\)\[\]!?.]', clean_text)
        punct_count = len(puncts)
        punct_ratio = round(punct_count / max(1, len(clean_text)), 3)

        # Uppercase ratio
        upper_chars = sum(1 for c in clean_text if c.isupper())
        upper_ratio = round(upper_chars / max(1, len(clean_text)), 3)

        # Function word frequency signature
        fw_signature = {}
        for fw in COMMON_FUNCTION_WORDS[:15]:
            count = words.count(fw)
            fw_signature[fw] = round(count / word_count, 4)

        # Cybercrime Jargon Matches
        detected_jargon = [term for term in DARK_JARGON_MARKERS if term in words]

        return {
            "avg_sentence_length": avg_sentence_len,
            "avg_word_length": avg_word_len,
            "lexical_richness": lexical_richness,
            "punctuation_entropy": punct_ratio,
            "uppercase_ratio": upper_ratio,
            "function_word_signature": fw_signature,
            "detected_slang_jargon": detected_jargon
        }

    def estimate_timezone_from_hours(self, active_hours: List[int]) -> Tuple[str, str]:
        """
        Calculates probable timezone from UTC posting distribution.
        Assumes average human activity peaks between 10:00 and 22:00 local time.
        """
        if not active_hours:
            return "UTC+00:00", "Undetermined"

        mean_hour = sum(active_hours) / len(active_hours)
        # If mean peak UTC hour is 16:00 (4 PM UTC), local peak 15:00 corresponds to UTC-1, etc.
        # Reference peak 14:00 local time
        offset = int(round(mean_hour - 14))
        
        # Clamp between -12 and +14
        offset = max(-12, min(14, offset))
        sign = "+" if offset >= 0 else "-"
        tz_str = f"UTC{sign}{abs(offset):02d}:00"

        # Region estimation
        region_map = {
            3: "Eastern Europe / Moscow (MSK) / Middle East",
            2: "Central/Eastern Europe (EET / CEST)",
            1: "Western Europe (CET / BST)",
            0: "UK / Western Africa (GMT/UTC)",
            -4: "North America East Coast (EDT / AST)",
            -5: "North America (EST / CDT)",
            -6: "North America Central (CST)",
            -7: "North America Mountain (MST)",
            -8: "North America Pacific (PST)",
            5: "South Asia / West Central Asia (PKT / UZT)",
            6: "South Asia (IST / BST)",
            8: "East Asia (CST / SGT / HKT)"
        }
        region_desc = region_map.get(offset, f"Probable Longitude Region {tz_str}")
        return tz_str, region_desc

    def match_unknown_post(self, sample_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Compares an unknown forum post, escrow chat, or extortion note against
        known threat actor corpora using character n-gram cosine similarity
        and syntactic feature correspondence.
        """
        if not self._fitted or not self.actor_corpora:
            return []

        sample_features = self.extract_writeprint(sample_text)
        sample_vec = self.vectorizer.transform([sample_text])

        results = []

        for actor_id, posts in self.actor_corpora.items():
            meta = self.actor_metadata[actor_id]
            # Aggregate vector of actor's corpus
            actor_texts_combined = " ".join(posts)
            actor_vec = self.vectorizer.transform([actor_texts_combined])
            
            # Cosine similarity on character n-grams
            cosine_sim = float(cosine_similarity(sample_vec, actor_vec)[0][0])

            # Quantitative feature penalty / bonus
            actor_wp = self.extract_writeprint(actor_texts_combined)
            
            # Sentence length similarity
            s_diff = abs(sample_features["avg_sentence_length"] - actor_wp["avg_sentence_length"])
            s_sim = max(0.0, 1.0 - (s_diff / 30.0))

            # Jargon overlap
            sample_jargon = set(sample_features["detected_slang_jargon"])
            actor_jargon = set(actor_wp["detected_slang_jargon"])
            jargon_overlap = len(sample_jargon.intersection(actor_jargon))
            jargon_bonus = min(0.15, jargon_overlap * 0.05)

            # Combined Stylometric Attribution Score
            raw_score = (0.70 * cosine_sim) + (0.20 * s_sim) + (0.10 * (1.0 - abs(sample_features["lexical_richness"] - actor_wp["lexical_richness"]))) + jargon_bonus
            final_score = min(0.99, max(0.05, raw_score))

            # Attribution Confidence Level
            if final_score >= 0.82:
                level = "CONFIRMED_MATCH"
                pct = int(final_score * 100)
            elif final_score >= 0.65:
                level = "HIGH_PROBABILITY"
                pct = int(final_score * 100)
            elif final_score >= 0.45:
                level = "MODERATE_CORRELATION"
                pct = int(final_score * 100)
            else:
                level = "LOW_SIMILARITY"
                pct = int(final_score * 100)

            # Extract specific stylistic markers for forensic explanation
            markers = []
            if jargon_overlap > 0:
                shared = list(sample_jargon.intersection(actor_jargon))[:4]
                markers.append(f"Shared underground terminology: {', '.join(shared)}")
            if abs(sample_features["uppercase_ratio"] - actor_wp["uppercase_ratio"]) < 0.02:
                markers.append("Identical casing and capitalization frequency pattern")
            if abs(sample_features["avg_word_length"] - actor_wp["avg_word_length"]) < 0.5:
                markers.append("Similar syllable and vocabulary complexity index")
            if cosine_sim > 0.60:
                markers.append("High character 3-5 gram syntactic similarity (>60%)")

            tz_str, tz_desc = self.estimate_timezone_from_hours(meta.get("active_hours_utc", []))

            results.append({
                "actor_id": actor_id,
                "primary_handle": meta["primary_handle"],
                "category": meta["category"],
                "similarity_score": round(final_score, 4),
                "cosine_ngram_similarity": round(cosine_sim, 4),
                "attribution_level": level,
                "confidence_percentage": pct,
                "matching_markers": markers if markers else ["General lexical rhythm correlation"],
                "estimated_timezone": f"{tz_str} ({tz_desc})"
            })

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

stylometry_engine = StylometryEngine()
