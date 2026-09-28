from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

TIMEZONE_REGIONS = [
    {"name": "Americas / Eastern (EST/EDT)", "offset_utc": -5, "typical_peak_utc": 19},
    {"name": "Americas / Pacific (PST/PDT)", "offset_utc": -8, "typical_peak_utc": 22},
    {"name": "Western Europe (GMT/BST)", "offset_utc": 0, "typical_peak_utc": 14},
    {"name": "Eastern Europe / CIS (MSK)", "offset_utc": 3, "typical_peak_utc": 11},
    {"name": "South Asia (IST)", "offset_utc": 5.5, "typical_peak_utc": 8},
    {"name": "East Asia (CST/JST)", "offset_utc": 8, "typical_peak_utc": 6},
]

class BehavioralProfilingEngine:
    """
    Behavioral Profiling and Persona Migration Detection Engine.
    Analyzes temporal activity distributions, operational timezone windows,
    and identifies persona migration/rebranding patterns across platforms.
    """

    def compute_behavior_profile(self, timestamps: List[datetime], posts_count: int = 0) -> Dict[str, Any]:
        """
        Builds a 24-hour diurnal activity histogram and estimates operator operational timezone.
        """
        histogram = [0] * 24
        for ts in timestamps:
            histogram[ts.hour] += 1

        total_samples = max(1, sum(histogram))
        normalized_hist = [round(count / total_samples, 4) for count in histogram]

        peak_hour = histogram.index(max(histogram))

        # Best matching timezone region
        best_tz = TIMEZONE_REGIONS[0]["name"]
        min_diff = 999
        for region in TIMEZONE_REGIONS:
            diff = abs(region["typical_peak_utc"] - peak_hour)
            if diff > 12:
                diff = 24 - diff
            if diff < min_diff:
                min_diff = diff
                best_tz = region["name"]

        # Calculate average posting interval (hours)
        mean_interval = 0.0
        if len(timestamps) > 1:
            sorted_ts = sorted(timestamps)
            intervals = [(sorted_ts[i+1] - sorted_ts[i]).total_seconds() / 3600.0 for i in range(len(sorted_ts)-1)]
            mean_interval = round(sum(intervals) / len(intervals), 2)

        return {
            "active_hours_distribution": histogram,
            "normalized_distribution": normalized_hist,
            "peak_active_utc": peak_hour,
            "estimated_timezone": best_tz,
            "posting_interval_mean_hours": mean_interval,
            "sample_count": len(timestamps)
        }

    def detect_persona_migration(
        self,
        retiring_persona: Dict[str, Any],
        emerging_persona: Dict[str, Any],
        stylometric_similarity: float,
        shared_pgp: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Detects potential identity migration (rebranding):
        e.g., Persona A goes dormant/retires on Forum X, and Persona B emerges
        within 30-90 days on Forum Y with matching writing style and/or PGP.
        """
        last_seen_a = retiring_persona.get("last_seen")
        first_seen_b = emerging_persona.get("first_seen")

        if not last_seen_a or not first_seen_b:
            return None

        # Parse datetime if string
        if isinstance(last_seen_a, str):
            last_seen_a = datetime.fromisoformat(last_seen_a.replace("Z", ""))
        if isinstance(first_seen_b, str):
            first_seen_b = datetime.fromisoformat(first_seen_b.replace("Z", ""))

        time_gap_days = (first_seen_b - last_seen_a).days

        # Migration typically happens around the retirement window (-15 to +120 days)
        if -15 <= time_gap_days <= 120:
            evidence_points = []
            confidence = 0.50

            if shared_pgp:
                evidence_points.append("Direct cryptographic PGP signature reuse across platforms.")
                confidence += 0.35

            if stylometric_similarity >= 0.75:
                evidence_points.append(f"High writing style congruence ({int(stylometric_similarity * 100)}%).")
                confidence += 0.20
            elif stylometric_similarity >= 0.60:
                evidence_points.append(f"Moderate writing style congruence ({int(stylometric_similarity * 100)}%).")
                confidence += 0.10

            evidence_points.append(f"Temporal succession: {retiring_persona.get('handle')} inactive, followed by {emerging_persona.get('handle')} appearance {abs(time_gap_days)} days later.")

            confidence = min(0.95, round(confidence, 2))

            return {
                "event_type": "PERSONA_MIGRATION_DETECTED",
                "retiring_persona": retiring_persona.get("handle"),
                "emerging_persona": emerging_persona.get("handle"),
                "retiring_platform": retiring_persona.get("platform"),
                "emerging_platform": emerging_persona.get("platform"),
                "migration_window_days": time_gap_days,
                "confidence_score": confidence,
                "confidence_rating": "HIGH" if confidence >= 0.80 else "MEDIUM",
                "supporting_evidence": evidence_points,
                "detected_at": datetime.utcnow().isoformat() + "Z"
            }

        return None

behavioral_profiler = BehavioralProfilingEngine()
