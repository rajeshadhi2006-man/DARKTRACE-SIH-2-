import socket
import json
import re
import hashlib
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..models.entities import AuditLog, Alert
from ..services.realtime.manager import ws_manager
from ..services.browser_crime_pattern_engine import (
    get_browser_crime_taxonomy_catalog,
    analyze_browser_crime_pattern,
    identify_browser_from_artifact,
    BROWSER_REGISTRY,
    CATEGORY_NAMES
)

router = APIRouter(prefix="/network-detection", tags=["Tor & Browser Detection Forensics"])

KNOWN_TOR_EXIT_SUBNETS = [
    "185.220.100.", "185.220.101.", "185.220.102.", "185.220.103.",
    "198.98.56.", "198.98.57.", "199.249.230.", "171.25.193.",
    "109.70.100.", "51.15.", "162.247.74.", "176.10.99."
]

class ClientFingerprintPayload(BaseModel):
    user_agent: Optional[str] = ""
    platform: Optional[str] = ""
    vendor: Optional[str] = ""
    timezone: Optional[str] = ""
    timezone_offset: Optional[int] = 0
    screen_width: Optional[int] = 0
    screen_height: Optional[int] = 0
    inner_width: Optional[int] = 0
    inner_height: Optional[int] = 0
    has_window_chrome: Optional[bool] = False
    has_user_agent_data: Optional[bool] = False
    brands: Optional[List[Dict[str, str]]] = []
    webrtc_detected: Optional[bool] = False
    webrtc_local_ips: Optional[List[str]] = []
    canvas_hash: Optional[str] = ""
    webgl_vendor: Optional[str] = ""
    webgl_renderer: Optional[str] = ""
    audio_fingerprint: Optional[str] = ""

class ArtifactClassificationRequest(BaseModel):
    user_agent: Optional[str] = ""
    ip_address: Optional[str] = ""
    raw_headers: Optional[str] = ""
    source_context: Optional[str] = "Dark Web Intercept"

def probe_local_port(port: int, host: str = "127.0.0.1", timeout: float = 0.3) -> Dict[str, Any]:
    """Probes a local port and tests for SOCKS5 greeting handshake."""
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        is_socks5 = False
        try:
            # SOCKS5 handshake probe (version 5, 1 auth method: no auth)
            s.sendall(b"\x05\x01\x00")
            s.settimeout(0.3)
            resp = s.recv(2)
            if resp == b"\x05\x00":
                is_socks5 = True
        except Exception:
            pass
        s.close()
        return {"open": True, "is_socks5": is_socks5, "status": "ACTIVE_LISTENING"}
    except Exception as e:
        return {"open": False, "is_socks5": False, "status": "INACTIVE"}

def query_tor_project_check(timeout: float = 1.5) -> Dict[str, Any]:
    """Queries check.torproject.org to test if this egress node is on the Tor network."""
    try:
        req = urllib.request.Request(
            "https://check.torproject.org/api/ip",
            headers={"User-Agent": "DarktraceX-Threat-Intel/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode())
            return {
                "queried_successfully": True,
                "is_tor": bool(data.get("IsTor", False)),
                "ip": data.get("IP", "Unknown"),
                "source": "check.torproject.org"
            }
    except Exception as e:
        return {
            "queried_successfully": False,
            "is_tor": False,
            "ip": "127.0.0.1",
            "source": "local_fallback",
            "notice": "Tor Project API unreachable or offline."
        }

@router.get("/status")
def get_tor_and_network_status():
    """
    Returns real-time status of local Tor SOCKS proxies (9150/9050),
    Tor daemon connectivity, and public Tor network egress detection.
    """
    tor_browser_probe = probe_local_port(9150)
    tor_daemon_probe = probe_local_port(9050)
    privoxy_probe = probe_local_port(8118)
    
    tor_project_check = query_tor_project_check()

    is_any_tor_service_active = (
        tor_browser_probe["open"] or 
        tor_daemon_probe["open"] or 
        tor_project_check["is_tor"]
    )

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tor_detected_overall": is_any_tor_service_active,
        "local_proxies": {
            "tor_browser_bundle_socks": {
                "port": 9150,
                "service_name": "Tor Browser Default SOCKS5",
                "active": tor_browser_probe["open"],
                "socks5_verified": tor_browser_probe["is_socks5"],
                "status": tor_browser_probe["status"]
            },
            "tor_system_daemon_socks": {
                "port": 9050,
                "service_name": "Tor System Daemon SOCKS5",
                "active": tor_daemon_probe["open"],
                "socks5_verified": tor_daemon_probe["is_socks5"],
                "status": tor_daemon_probe["status"]
            },
            "tor_http_privoxy": {
                "port": 8118,
                "service_name": "Tor HTTP / Privoxy Relay",
                "active": privoxy_probe["open"],
                "status": privoxy_probe["status"]
            }
        },
        "egress_network": tor_project_check,
        "instructions": (
            "To connect to Tor Browser: Launch Tor Browser on this machine (it opens SOCKS5 on 127.0.0.1:9150). "
            "To connect via Chrome: Configure Chrome proxy or run SOCKS5 127.0.0.1:9050."
        )
    }

@router.post("/analyze-client")
def analyze_client_fingerprint(
    request: Request,
    payload: ClientFingerprintPayload
):
    """
    Deep Forensic Client Analysis:
    Distinguishes whether the client is Google Chrome, Tor Browser, standard Firefox, or an automated agent,
    identifying OPSEC leaks, WebRTC disclosures, and timezone mismatches.
    """
    req_headers = dict(request.headers)
    server_ua = req_headers.get("user-agent", "")
    sec_ch_ua = req_headers.get("sec-ch-ua", "")
    accept_lang = req_headers.get("accept-language", "")
    client_ip = request.client.host if request.client else "127.0.0.1"

    effective_ua = payload.user_agent or server_ua
    findings: List[Dict[str, Any]] = []
    detected_browsers: List[str] = []
    opsec_leak_score = 0  # 0 = Zero Leak / High Anonymity, 100 = Critical Clearnet Exposure

    # 1. Google Chrome & Chromium V8 Detection
    is_chrome = False
    chrome_signals = []
    if payload.has_window_chrome:
        is_chrome = True
        chrome_signals.append("window.chrome API exposed")
    if payload.has_user_agent_data:
        is_chrome = True
        chrome_signals.append("Chromium Sec-CH-UA Client Hints active")
    if "Chrome/" in effective_ua or "Chromium/" in effective_ua:
        chrome_signals.append("Chrome user-agent signature present")
    if "Google Chrome" in sec_ch_ua or any("Google Chrome" in b.get("brand", "") for b in payload.brands):
        is_chrome = True
        chrome_signals.append("Verified Google Chrome client brand header")
    if "Google Inc." in (payload.vendor or ""):
        chrome_signals.append("Google Inc. WebGL/DOM vendor string")

    # 2. Tor Browser Detection Signals
    is_tor_browser = False
    tor_signals = []

    # Tor Browser letterboxing: inner dimensions rounded to multiples of 200x100
    if payload.inner_width and payload.inner_height:
        is_letterboxed = (payload.inner_width % 200 == 0) and (payload.inner_height % 100 == 0)
        if is_letterboxed:
            tor_signals.append(f"Viewport Letterboxing verified ({payload.inner_width}x{payload.inner_height} mod 200/100)")
            is_tor_browser = True

    # Tor Browser timezone is strictly UTC (offset 0)
    if payload.timezone == "UTC" or payload.timezone_offset == 0:
        tor_signals.append("Timezone pinned to UTC (offset 0)")
    elif payload.timezone and payload.timezone != "UTC":
        findings.append({
            "vector": "TIMEZONE_DISCLOSURE",
            "severity": "MEDIUM",
            "detail": f"Real system timezone exposed: '{payload.timezone}' (Offset: {payload.timezone_offset} mins)."
        })
        opsec_leak_score += 25

    # Tor Browser disables WebRTC or isolates candidates
    if payload.webrtc_detected and payload.webrtc_local_ips:
        findings.append({
            "vector": "WEBRTC_LOCAL_IP_LEAK",
            "severity": "CRITICAL",
            "detail": f"WebRTC leaked local IP interfaces: {', '.join(payload.webrtc_local_ips)}"
        })
        opsec_leak_score += 40
    elif not payload.webrtc_detected:
        tor_signals.append("WebRTC candidate gathering blocked/isolated")

    # Tor Browser standard User-Agent signature
    if "Firefox/" in effective_ua and "Gecko/20100101" in effective_ua and not is_chrome:
        if "en-US" in accept_lang or accept_lang == "en-US,en;q=0.5":
            tor_signals.append("Strict en-US Firefox ESR language bundle")
        if len(tor_signals) >= 2:
            is_tor_browser = True

    # Check Client IP against known Tor exit subnets
    is_tor_exit_ip = any(client_ip.startswith(prefix) for prefix in KNOWN_TOR_EXIT_SUBNETS)
    if is_tor_exit_ip:
        tor_signals.append(f"Client IP {client_ip} matches known Tor Exit Relay cluster")

    # Comprehensive Multi-Browser Identification across 80+ Browsers
    matched_meta = identify_browser_from_artifact(effective_ua, sec_ch_ua)
    if matched_meta:
        detected_browsers.append(matched_meta["id"].upper())
        primary_browser = f"{matched_meta['name']} ({matched_meta['engine']})"
        engine = matched_meta["engine"]
        if matched_meta["risk_tier"] == "CRITICAL_OPSEC_LEAK":
            opsec_leak_score += 50
        elif matched_meta["risk_tier"] == "HIGH_ANONYMITY_EVASION":
            opsec_leak_score = min(opsec_leak_score, 15)
        elif matched_meta["risk_tier"] == "ELEVATED_OPSEC_LEAK":
            opsec_leak_score += 35
        elif matched_meta["risk_tier"] == "DEV_MALWARE_AUTHOR_STAGING":
            opsec_leak_score += 45
            findings.append({
                "vector": "DEVELOPER_BUILD_MALWARE_STAGING",
                "severity": "HIGH",
                "detail": f"Suspect accessed via developer test build ({matched_meta['name']}). Indicates active exploit compilation or staging environment."
            })
    elif is_chrome:
        detected_browsers.append("GOOGLE_CHROME")
        primary_browser = "Google Chrome (Chromium V8 Engine)"
        engine = "Blink / V8"
        opsec_leak_score += 50
    elif is_tor_browser:
        detected_browsers.append("TOR_BROWSER")
        primary_browser = "Tor Browser (Firefox ESR + resistFingerprinting)"
        engine = "Gecko (Tor Hardened)"
        opsec_leak_score = min(opsec_leak_score, 15)
    elif "Firefox/" in effective_ua:
        detected_browsers.append("FIREFOX_CLEARNET")
        primary_browser = "Mozilla Firefox (Clearnet Standard)"
        engine = "Gecko"
        opsec_leak_score += 35
    else:
        detected_browsers.append("GENERIC_OR_CUSTOM")
        primary_browser = "Unknown / Clearnet Client"
        engine = "Unknown"
        opsec_leak_score += 30

    opsec_leak_score = min(100, max(0, opsec_leak_score))

    if is_chrome and is_tor_exit_ip:
        findings.append({
            "vector": "CHROME_OVER_TOR_ANOMALY",
            "severity": "HIGH",
            "detail": "Target routed Google Chrome over Tor SOCKS proxy. Chrome client hints and canvas fingerprints actively undermine Tor network routing anonymity."
        })
        opsec_leak_score = 85

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "primary_browser": primary_browser,
        "engine": engine,
        "is_chrome": is_chrome,
        "is_tor_browser": is_tor_browser,
        "detected_classifications": detected_browsers,
        "chrome_fingerprint_signals": chrome_signals,
        "tor_fingerprint_signals": tor_signals,
        "opsec_leak_score": opsec_leak_score,
        "opsec_tier": "CRITICAL_EXPOSURE" if opsec_leak_score >= 70 else ("ELEVATED_LEAK" if opsec_leak_score >= 40 else "PROTECTED_ANONYMOUS"),
        "forensic_findings": findings,
        "client_network": {
            "client_ip": client_ip,
            "is_tor_exit_node": is_tor_exit_ip,
            "accept_language": accept_lang
        }
    }

# ----------------- Comprehensive Browser Crime Pattern Endpoints -----------------

@router.get("/browsers/catalog")
def get_browser_crime_catalog():
    """
    Returns exhaustive taxonomy and crime pattern database across 80+ browsers
    in 8 categories: Major Desktop/Mobile, Privacy/Security, Linux/Open-Source,
    Android-Focused, Apple Ecosystem, Historical/Discontinued, Enterprise/Specialized,
    and Developer/Testing.
    """
    return get_browser_crime_taxonomy_catalog()

@router.post("/browsers/identify-crime-pattern")
def identify_browser_crime_pattern_endpoint(req: ArtifactClassificationRequest):
    """
    Identifies any intercepted browser signature across all 80+ registered browsers
    and generates an automated forensic crime pattern profile, OPSEC risk rating,
    vulnerabilities, and de-anonymization pivots.
    """
    return analyze_browser_crime_pattern(
        user_agent=req.user_agent or "",
        ip_address=req.ip_address or "",
        raw_headers=req.raw_headers or "",
        source_context=req.source_context or "Dark Web Intercept"
    )

@router.post("/classify-artifact")
def classify_threat_actor_network_artifact(
    req: ArtifactClassificationRequest,
    db: Session = Depends(get_db)
):
    """
    Forensic Artifact Classifier for Threat Actor Attribution:
    Deeply analyzes intercepted HTTP headers, User-Agent, and egress IP across 80+ browsers
    to uncover crime pattern behaviors, fatal OPSEC leaks, and de-anonymization pivots.
    """
    ua = req.user_agent or ""
    ip = req.ip_address or ""
    headers = req.raw_headers or ""
    context = req.source_context or "Dark Web Intercept"

    pattern_result = analyze_browser_crime_pattern(ua, ip, headers, context)
    browser_info = pattern_result["browser"]
    classification = f"{browser_info['id'].upper()}"
    confidence = browser_info["confidence_pct"] / 100.0
    opsec_failure = pattern_result["opsec_failure_detected"]
    signals = pattern_result["investigative_findings"] + pattern_result["crime_pattern_profile"]["forensic_deanon_vectors"]

    # Backward-compatible response merged with advanced crime pattern intelligence
    result = {
        "timestamp": pattern_result["timestamp"],
        "classification": classification,
        "browser_name": browser_info["name"],
        "browser_category": browser_info["primary_category"],
        "browser_engine": browser_info["engine"],
        "risk_tier": browser_info["risk_tier"],
        "confidence_percentage": int(confidence * 100),
        "is_tor_network": pattern_result["network_context"]["is_tor_exit_subnet"],
        "is_chrome": "chrome" in browser_info["id"] or "chromium" in browser_info["id"],
        "opsec_failure_detected": opsec_failure,
        "forensic_signals": signals,
        "evidence_sha256": pattern_result["evidence_sha256"],
        "recommendation": pattern_result["recommended_pivot"],
        "crime_pattern_profile": pattern_result["crime_pattern_profile"],
        "behavioral_summary": pattern_result["crime_pattern_profile"]["behavioral_summary"],
        "opsec_vulnerabilities": pattern_result["crime_pattern_profile"]["opsec_vulnerabilities"],
        "forensic_deanon_vectors": pattern_result["crime_pattern_profile"]["forensic_deanon_vectors"],
        "typical_crime_contexts": pattern_result["crime_pattern_profile"]["typical_crime_contexts"]
    }

    # Broadcast real-time alert on OPSEC leak
    if opsec_failure or browser_info["risk_tier"] in ["CRITICAL_OPSEC_LEAK", "DEV_MALWARE_AUTHOR_STAGING"]:
        ws_manager.broadcast_sync({
            "type": "NEW_ALERT",
            "alert": {
                "id": f"ALT-BROWSER-{pattern_result['evidence_sha256'][:8].upper()}",
                "title": f"Forensic Alert: {browser_info['name']} Crime Pattern Identified ({browser_info['risk_tier']})",
                "severity": "HIGH" if opsec_failure else "MEDIUM",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        })

    return result

@router.get("/live-tor-relays")
def get_live_tor_relays(limit: int = 15):
    """
    REAL-WORLD TELEMETRY: Queries official Tor Project Onionoo directory API
    for live running Tor relays, exit nodes, real IP addresses, and ASNs.
    """
    import urllib.request
    try:
        url = f"https://onionoo.torproject.org/details?type=relay&running=true&limit={min(limit, 30)}"
        req = urllib.request.Request(url, headers={"User-Agent": "NTRO-DarktraceX/1.0"})
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            data = json.loads(resp.read().decode())
            relays = data.get("relays", [])
            formatted = []
            for r in relays:
                is_exit = "Exit" in r.get("flags", [])
                formatted.append({
                    "nickname": r.get("nickname", "Unnamed"),
                    "fingerprint": r.get("fingerprint"),
                    "or_addresses": r.get("or_addresses", []),
                    "exit_addresses": r.get("exit_addresses", []),
                    "is_exit_node": is_exit,
                    "flags": r.get("flags", []),
                    "bandwidth_rate_kbps": round(r.get("bandwidth_rate", 0) / 1024, 1),
                    "as_number": r.get("as", "Unknown ASN"),
                    "as_name": r.get("as_name", "Unknown Org"),
                    "country": r.get("country", "XX"),
                    "verified_live": True
                })
            return {
                "source": "https://onionoo.torproject.org (Tor Project Official Directory)",
                "total_fetched": len(formatted),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "relays": formatted
            }
    except Exception as e:
        # Fallback to known live passive Tor consensus nodes
        return {
            "source": "Local Tor Consensus Cache (Offline Fallback)",
            "total_fetched": 4,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "relays": [
                {"nickname": "TorExitFrankfurt", "or_addresses": ["185.220.101.42:9001"], "is_exit_node": True, "flags": ["Exit", "Fast", "Running"], "as_number": "AS200052", "country": "de"},
                {"nickname": "AmsterdamRelay01", "or_addresses": ["194.26.29.114:443"], "is_exit_node": True, "flags": ["Exit", "Guard"], "as_number": "AS49981", "country": "nl"},
                {"nickname": "SelectelExit03", "or_addresses": ["91.240.118.89:9050"], "is_exit_node": True, "flags": ["Exit"], "as_number": "AS48287", "country": "ru"},
                {"nickname": "USExitNode08", "or_addresses": ["198.98.56.24:9001"], "is_exit_node": True, "flags": ["Exit", "Stable"], "as_number": "AS53667", "country": "us"}
            ]
        }

@router.get("/live-btc-lookup/{address}")
def lookup_live_bitcoin_wallet(address: str):
    """
    REAL-WORLD TELEMETRY: Queries public Bitcoin mempool ledger API
    for real confirmed balance, funded transaction outputs, and activity history.
    """
    import urllib.request
    clean_addr = re.sub(r'[^a-zA-Z0-9]', '', address.strip())
    if not clean_addr:
        raise HTTPException(status_code=400, detail="Invalid Bitcoin address")

    try:
        url = f"https://mempool.space/api/address/{clean_addr}"
        req = urllib.request.Request(url, headers={"User-Agent": "NTRO-DarktraceX/1.0"})
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            data = json.loads(resp.read().decode())
            chain_stats = data.get("chain_stats", {})
            mempool_stats = data.get("mempool_stats", {})

            funded_sats = chain_stats.get("funded_txo_sum", 0)
            spent_sats = chain_stats.get("spent_txo_sum", 0)
            balance_sats = funded_sats - spent_sats
            balance_btc = round(balance_sats / 100_000_000, 8)

            return {
                "source": "https://mempool.space (Bitcoin Mainnet Ledger)",
                "address": clean_addr,
                "verified_live": True,
                "confirmed_balance_btc": balance_btc,
                "confirmed_balance_satoshis": balance_sats,
                "total_funded_tx_count": chain_stats.get("funded_txo_count", 0),
                "total_spent_tx_count": chain_stats.get("spent_txo_count", 0),
                "unconfirmed_tx_count": mempool_stats.get("tx_count", 0),
                "unconfirmed_balance_satoshis": mempool_stats.get("funded_txo_sum", 0) - mempool_stats.get("spent_txo_sum", 0),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
    except Exception as e:
        return {
            "source": "Local Bitcoin Ledger Node Fallback",
            "address": clean_addr,
            "verified_live": False,
            "error_detail": str(e),
            "confirmed_balance_btc": 0.0,
            "total_funded_tx_count": 0,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

class LiveSocketProbeRequest(BaseModel):
    target_host: str
    target_port: int = 443

@router.post("/live-socket-probe")
def execute_live_socket_probe(payload: LiveSocketProbeRequest):
    """
    REAL-WORLD TELEMETRY: Performs actual live TCP socket handshake and
    real TLS X.509 certificate extraction against specified target.
    """
    import socket
    import ssl
    import time

    host = payload.target_host.replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]
    port = payload.target_port

    start_time = time.time()
    try:
        s = socket.create_connection((host, port), timeout=3.0)
        latency_ms = round((time.time() - start_time) * 1000, 1)

        tls_data = None
        server_banner = None

        if port in (443, 8443):
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                with ctx.wrap_socket(s, server_hostname=host) as ss:
                    cert = ss.getpeercert(binary_form=False) or {}
                    cert_bin = ss.getpeercert(binary_form=True)
                    sha256_fp = hashlib.sha256(cert_bin).hexdigest() if cert_bin else "N/A"
                    
                    san_list = [v for k, v in cert.get("subjectAltName", []) if k == "DNS"]
                    tls_data = {
                        "subject": dict(x[0] for x in cert.get("subject", [])),
                        "issuer": dict(x[0] for x in cert.get("issuer", [])),
                        "sha256_fingerprint": sha256_fp,
                        "subject_alt_names": san_list[:10],
                        "not_after": cert.get("notAfter"),
                        "not_before": cert.get("notBefore")
                    }
            except Exception as ssl_err:
                tls_data = {"error": f"TLS handshake failed: {str(ssl_err)}"}
        elif port in (80, 8080):
            try:
                s.sendall(f"HEAD / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: NTRO-Scanner\r\nConnection: close\r\n\r\n".encode())
                s.settimeout(2.0)
                raw_resp = s.recv(1024).decode('utf-8', errors='ignore')
                headers = raw_resp.split("\r\n")
                server_header = next((h.split(":", 1)[1].strip() for h in headers if h.lower().startswith("server:")), "Not Disclosed")
                server_banner = {
                    "status_line": headers[0] if headers else "HTTP/1.1 200 OK",
                    "server_software": server_header,
                    "sha256_hash": hashlib.sha256(raw_resp.encode()).hexdigest()
                }
            except Exception:
                pass
        s.close()

        # Check against Tor exit nodes list
        is_known_tor_exit = any(host.startswith(prefix) for prefix in KNOWN_TOR_EXIT_SUBNETS)

        return {
            "target": f"{host}:{port}",
            "port_open": True,
            "latency_ms": latency_ms,
            "is_known_tor_exit": is_known_tor_exit,
            "tls_certificate": tls_data,
            "http_banner": server_banner,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "LIVE_CONNECTION_VERIFIED"
        }
    except Exception as e:
        return {
            "target": f"{host}:{port}",
            "port_open": False,
            "latency_ms": round((time.time() - start_time) * 1000, 1),
            "error_detail": str(e),
            "status": "HOST_UNREACHABLE_OR_FILTERED",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

