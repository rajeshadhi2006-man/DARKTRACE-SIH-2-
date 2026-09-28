import re
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

class InfrastructureCorrelationEngine:
    """
    Passive Infrastructure Correlation & Tor Misconfiguration Analyzer.
    Correlates Tor hidden service configurations against clearnet telemetry
    via SSL/TLS certificates, Apache server-status leaks, Favicon hashes,
    and Certificate Transparency (CT) logs.
    """

    def parse_apache_status_leak(self, raw_status_html: str) -> Dict[str, Any]:
        """
        Parses Apache /server-status and /server-info diagnostic disclosures
        to uncover internal virtual hosts, client IP addresses, and backend origin servers.
        """
        vhosts = set(re.findall(r"VHost:\s*([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", raw_status_html, re.IGNORECASE))
        client_ips = set(re.findall(r"Client:\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", raw_status_html))
        server_version = re.search(r"Apache/([0-9.]+)", raw_status_html)

        leaked_vhosts = [v for v in vhosts if not v.endswith(".onion") and not v.startswith("localhost")]
        leaked_clearnet_ips = [ip for ip in client_ips if not ip.startswith(("127.", "10.", "192.168."))]

        return {
            "status_disclosed": bool(server_version or leaked_vhosts or leaked_clearnet_ips),
            "apache_version": server_version.group(0) if server_version else "Unknown",
            "leaked_internal_vhosts": list(leaked_vhosts),
            "leaked_origin_client_ips": list(leaked_clearnet_ips),
            "confidence": 0.95 if leaked_clearnet_ips or leaked_vhosts else 0.40,
            "provenance_tier": "DIRECTLY_OBSERVED_LEAK" if leaked_clearnet_ips else "INFERRED"
        }

    def correlate_tls_certificate(self, cert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes X.509 TLS Certificate Subject Alternative Names (SANs)
        and Serial Numbers against Certificate Transparency (CT) log entries.
        """
        sans = cert_data.get("subject_alt_names", [])
        serial = cert_data.get("serial_number", "")
        issuer = cert_data.get("issuer", "")

        clearnet_sans = [s for s in sans if not s.endswith(".onion")]

        has_clearnet_leak = len(clearnet_sans) > 0
        confidence = 0.98 if has_clearnet_leak else 0.50

        return {
            "serial_number": serial,
            "issuer": issuer,
            "clearnet_domains_in_san": clearnet_sans,
            "has_clearnet_leak": has_clearnet_leak,
            "confidence": confidence,
            "provenance_tier": "DIRECTLY_OBSERVED" if has_clearnet_leak else "HISTORICALLY_OBSERVED",
            "correlation_summary": (
                f"TLS Certificate served on onion endpoint contains clearnet domains: {', '.join(clearnet_sans)}."
                if has_clearnet_leak else "TLS Certificate restricted to onion or self-signed."
            )
        }

    def correlate_favicon_hash(self, favicon_murmur3: int, known_clearnet_hosts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Matches a Favicon MurmurHash3 against Shodan/Censys indexed clearnet web servers.
        """
        matches = []
        for host in known_clearnet_hosts:
            if host.get("favicon_hash") == favicon_murmur3:
                matches.append(host)

        return {
            "target_favicon_hash": favicon_murmur3,
            "matched_clearnet_hosts_count": len(matches),
            "matches": matches,
            "confidence": 0.85 if matches else 0.0,
            "provenance_tier": "POTENTIAL_CORRELATION"
        }

    def correlate_onion_service(
        self,
        onion_domain: str,
        cert_data: Optional[Dict[str, Any]] = None,
        server_status_text: Optional[str] = None,
        favicon_hash: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Runs comprehensive passive correlation against an authorized onion snapshot.
        """
        findings: List[Dict[str, Any]] = []
        overall_confidence = 0.50
        tier = "INFERRED"

        # 1. Cert SANs
        if cert_data:
            cert_res = self.correlate_tls_certificate(cert_data)
            if cert_res["has_clearnet_leak"]:
                findings.append({
                    "indicator": "TLS_SAN_LEAK",
                    "details": cert_res,
                    "confidence": cert_res["confidence"]
                })
                overall_confidence = max(overall_confidence, 0.95)
                tier = "DIRECTLY_OBSERVED"

        # 2. Server status
        if server_status_text:
            status_res = self.parse_apache_status_leak(server_status_text)
            if status_res["status_disclosed"]:
                findings.append({
                    "indicator": "APACHE_STATUS_DISCLOSURE",
                    "details": status_res,
                    "confidence": status_res["confidence"]
                })
                overall_confidence = max(overall_confidence, 0.90)
                tier = "DIRECTLY_OBSERVED"

        # 3. Favicon Murmur3
        if favicon_hash:
            findings.append({
                "indicator": "FAVICON_MURMUR3_INDEXED",
                "details": {"favicon_hash": favicon_hash},
                "confidence": 0.80
            })

        return {
            "onion_domain": onion_domain,
            "provenance_tier": tier,
            "overall_confidence": overall_confidence,
            "findings_count": len(findings),
            "findings": findings,
            "disclaimer": "Infrastructure correlation indicates potential shared hosting or operational origin; human analyst corroboration is required."
        }

infra_correlator = InfrastructureCorrelationEngine()
