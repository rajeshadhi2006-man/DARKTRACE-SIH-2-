import re
import difflib
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

def compute_handle_similarity(handle_a: str, handle_b: str) -> Tuple[float, List[str]]:
    """
    Analyzes naming pattern reuse, leet-speak variations, and structural tokens.
    """
    obs = []
    ha = handle_a.lower().strip()
    hb = handle_b.lower().strip()

    if ha == hb:
        obs.append(f"Identical handle string reuse across platforms: '{handle_a}'")
        return 100.0, obs

    # Normalize leet speak and separators
    def normalize_handle(h: str) -> str:
        h = h.replace('0', 'o').replace('1', 'i').replace('3', 'e').replace('4', 'a').replace('5', 's').replace('7', 't')
        h = re.sub(r'[\-_\.\s\d]+', '', h)
        return h

    norm_a = normalize_handle(ha)
    norm_b = normalize_handle(hb)

    if norm_a and norm_b and norm_a == norm_b:
        obs.append(f"Leet-speak / number variation of identical root handle ('{ha}' vs '{hb}')")
        return 88.0, obs

    # Substring containment
    if (len(ha) > 4 and ha in hb) or (len(hb) > 4 and hb in ha):
        obs.append(f"Sub-handle stem containment identified ('{ha}' in '{hb}')")
        return 78.0, obs

    # Sequence matcher ratio
    seq_ratio = difflib.SequenceMatcher(None, ha, hb).ratio()
    score = round(seq_ratio * 100.0, 1)

    if score > 70.0:
        obs.append(f"High morphological handle structure similarity ({score}%)")
    elif score > 50.0:
        obs.append(f"Moderate lexical resemblance in handle names ({score}%)")

    return score, obs

def compute_temporal_similarity(
    hours_a: List[str],
    hours_b: List[str],
    timestamps_a: Optional[List[str]] = None,
    timestamps_b: Optional[List[str]] = None
) -> Tuple[float, List[str]]:
    """
    Measures operational diurnal cadence and account migration timing.
    """
    obs = []
    set_a = set(hours_a)
    set_b = set(hours_b)

    if not set_a or not set_b:
        return 50.0, ["Standard default activity window assumed (insufficient timestamps)"]

    intersection = set_a.intersection(set_b)
    union = set_a.union(set_b)
    jaccard = len(intersection) / len(union) if union else 0.0

    score = round(jaccard * 100.0, 1)

    if len(intersection) >= 3:
        obs.append(f"Synchronous operational UTC diurnal windows: {', '.join(sorted(list(intersection)))}")
    elif len(intersection) >= 1:
        obs.append(f"Partial activity window overlap during: {', '.join(sorted(list(intersection)))}")
    else:
        obs.append("Divergent active operational hours observed")

    # Migration timing analysis if timestamps provided
    if timestamps_a and timestamps_b:
        try:
            ts_a_sorted = sorted([datetime.fromisoformat(t.replace('Z', '')) for t in timestamps_a])
            ts_b_sorted = sorted([datetime.fromisoformat(t.replace('Z', '')) for t in timestamps_b])
            last_a = ts_a_sorted[-1]
            first_b = ts_b_sorted[0]
            delta_days = (first_b - last_a).total_seconds() / 86400.0

            if 0 <= delta_days <= 14:
                obs.append(f"Account succession / migration sequence: Persona B emerged {round(delta_days, 1)} days after Persona A cessation")
                score = min(100.0, score + 15.0)
        except Exception:
            pass

    return min(100.0, max(0.0, score)), obs

def compute_infrastructure_similarity(
    infra_list_a: List[Dict[str, Any]],
    infra_list_b: List[Dict[str, Any]]
) -> Tuple[float, List[str]]:
    """
    Analyzes infrastructure indicator overlaps (SSL cert fingerprints, IP/ASN, SSH banners, web headers).
    """
    obs = []
    fps_a = {i.get("fingerprint") or i.get("indicator_value") for i in infra_list_a if i.get("fingerprint") or i.get("indicator_value")}
    fps_b = {i.get("fingerprint") or i.get("indicator_value") for i in infra_list_b if i.get("fingerprint") or i.get("indicator_value")}

    if not fps_a or not fps_b:
        return 35.0, ["No shared infrastructure fingerprints recorded in current observation set"]

    shared_fps = fps_a.intersection(fps_b)
    if shared_fps:
        matched = list(shared_fps)[0]
        obs.append(f"Shared cryptographic SSL/TLS infrastructure certificate fingerprint: {matched[:24]}...")
        return 92.0, obs

    # Check for ASN / Subnet or server software colocation
    types_a = {i.get("type") for i in infra_list_a}
    types_b = {i.get("type") for i in infra_list_b}
    if types_a.intersection(types_b):
        obs.append("Matching hosting configuration architecture identified")
        return 60.0, obs

    return 30.0, ["Independent hosting/infrastructure routing paths observed"]

def compute_identifier_similarity(
    entities_a: List[Dict[str, Any]],
    entities_b: List[Dict[str, Any]]
) -> Tuple[float, List[str]]:
    """
    Cryptographic PGP fingerprints, wallet addresses, and email correlation.
    """
    obs = []
    
    # 1. Check PGP Fingerprint (Hard cryptographic proof of key reuse)
    pgp_a = {e.get("value") for e in entities_a if e.get("type") in ("pgp", "pgp_key", "KEY")}
    pgp_b = {e.get("value") for e in entities_b if e.get("type") in ("pgp", "pgp_key", "KEY")}
    
    if pgp_a and pgp_b and pgp_a.intersection(pgp_b):
        shared_pgp = list(pgp_a.intersection(pgp_b))[0]
        obs.append(f"CRITICAL: Exact PGP public key fingerprint match: {shared_pgp}")
        return 100.0, obs

    # 2. Check Wallet addresses
    wlt_a = {e.get("value") for e in entities_a if e.get("type") in ("wallet", "crypto", "WLT")}
    wlt_b = {e.get("value") for e in entities_b if e.get("type") in ("wallet", "crypto", "WLT")}

    if wlt_a and wlt_b and wlt_a.intersection(wlt_b):
        shared_wlt = list(wlt_a.intersection(wlt_b))[0]
        obs.append(f"Reused cryptocurrency deposit/escrow wallet address: {shared_wlt}")
        return 95.0, obs

    # 3. Check authorized emails
    email_a = {e.get("value") for e in entities_a if e.get("type") == "email"}
    email_b = {e.get("value") for e in entities_b if e.get("type") == "email"}

    if email_a and email_b and email_a.intersection(email_b):
        shared_email = list(email_a.intersection(email_b))[0]
        obs.append(f"Shared contact email address observed: {shared_email}")
        return 90.0, obs

    if pgp_a or wlt_a or pgp_b or wlt_b:
        return 40.0, ["No direct cryptographic identifier crossover (distinct PGP keys / wallets)"]

    return 30.0, ["No cryptographic or wallet identifiers available in observation pool"]
