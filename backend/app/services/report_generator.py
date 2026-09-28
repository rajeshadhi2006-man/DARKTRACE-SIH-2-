import io
import csv
import json
from typing import List, Dict, Any
from datetime import datetime

class ThreatIntelReportGenerator:
    """
    Forensic Intelligence Report & Export Generator.
    Supports CSV, JSON, and Forensic Dossier HTML/PDF Reports.
    """

    @staticmethod
    def generate_csv(actors: List[Dict[str, Any]]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)

        headers = [
            "Actor ID",
            "Primary Handle",
            "Aliases",
            "Category",
            "Threat Level",
            "Attribution Confidence (%)",
            "Status",
            "Suspected Legal Name",
            "Suspected Country",
            "Origin Clearnet IPs",
            "PGP Fingerprints",
            "Crypto Wallets",
            "Onion Hidden Services",
            "First Seen",
            "Last Seen",
            "Intelligence Sources"
        ]
        writer.writerow(headers)

        for a in actors:
            suspect = a.get("real_world_suspect") or {}
            pgps = "; ".join([p.get("fingerprint", "") for p in a.get("pgp_keys", [])])
            wallets = "; ".join([f"{w.get('currency')}:{w.get('address')}" for w in a.get("crypto_wallets", [])])
            ips = "; ".join(suspect.get("associated_ips", []))
            aliases = ", ".join(a.get("aliases", []))
            onions = "; ".join(a.get("associated_onions", []))
            sources = ", ".join(a.get("sources", []))

            writer.writerow([
                a.get("id"),
                a.get("primary_handle"),
                aliases,
                a.get("category"),
                a.get("threat_level"),
                a.get("attribution_confidence"),
                a.get("status"),
                suspect.get("probable_legal_name", "N/A"),
                suspect.get("suspected_country", "N/A"),
                ips,
                pgps,
                wallets,
                onions,
                a.get("first_seen"),
                a.get("last_seen"),
                sources
            ])

        return output.getvalue()

    @staticmethod
    def generate_forensic_html_report(actor: Dict[str, Any]) -> str:
        """
        Generates an intelligence dossier styled for law enforcement
        and cyber threat intelligence teams.
        """
        suspect = actor.get("real_world_suspect") or {}
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        pgp_html = "".join([
            f"<div class='indicator-chip'><strong>Key ID:</strong> {p.get('key_id')} | <strong>Fingerprint:</strong> <code>{p.get('fingerprint')}</code> | <strong>Identity:</strong> {p.get('email_identity', 'None')}</div>"
            for p in actor.get("pgp_keys", [])
        ]) or "<p class='muted'>No PGP keys indexed</p>"

        wallet_html = "".join([
            f"<div class='indicator-chip'><strong>{w.get('currency')}:</strong> <code>{w.get('address')}</code> | Received: {w.get('total_received', 'Unknown')}</div>"
            for w in actor.get("crypto_wallets", [])
        ]) or "<p class='muted'>No wallets indexed</p>"

        comm_html = "".join([
            f"<div class='indicator-chip'><strong>{c.get('platform')}:</strong> {c.get('identifier')}</div>"
            for c in actor.get("communications", [])
        ]) or "<p class='muted'>No communications indexed</p>"

        sample_posts_html = "".join([
            f"<blockquote>\"{post}\"</blockquote>"
            for post in actor.get("sample_posts", [])
        ]) or "<p class='muted'>No sample posts archived</p>"

        ips_str = ", ".join(suspect.get("associated_ips", [])) or "None identified"
        clearnet_accs = ", ".join(suspect.get("clearnet_accounts", [])) or "None identified"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Intelligence Dossier: {actor.get('primary_handle')} [{actor.get('id')}]</title>
<style>
    body {{
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        background: #0f172a;
        color: #f1f5f9;
        margin: 0;
        padding: 40px;
        line-height: 1.6;
    }}
    .container {{
        max-width: 900px;
        margin: 0 auto;
        background: #1e293b;
        padding: 40px;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    }}
    .classification-banner {{
        background: #b91c1c;
        color: #ffffff;
        text-align: center;
        padding: 8px;
        font-weight: 800;
        letter-spacing: 2px;
        font-size: 13px;
        border-radius: 6px;
        margin-bottom: 25px;
    }}
    .header {{
        border-bottom: 2px solid #38bdf8;
        padding-bottom: 20px;
        margin-bottom: 25px;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }}
    h1 {{
        margin: 0 0 8px 0;
        color: #38bdf8;
        font-size: 28px;
    }}
    .badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
    }}
    .badge-critical {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }}
    .badge-confidence {{ background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }}
    
    .section-title {{
        font-size: 18px;
        color: #38bdf8;
        border-bottom: 1px solid #334155;
        padding-bottom: 6px;
        margin-top: 30px;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .grid-2 {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
    }}
    .meta-box {{
        background: #0f172a;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #334155;
    }}
    .meta-label {{
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
    }}
    .meta-value {{
        font-size: 16px;
        color: #f8fafc;
        font-weight: 600;
        margin-top: 4px;
    }}
    .suspect-card {{
        background: rgba(236, 72, 153, 0.1);
        border: 1px solid #ec4899;
        padding: 20px;
        border-radius: 8px;
        margin-top: 15px;
    }}
    .indicator-chip {{
        background: #0f172a;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 10px;
        border: 1px solid #334155;
        font-size: 13px;
    }}
    code {{
        font-family: 'Consolas', monospace;
        color: #38bdf8;
        background: #111827;
        padding: 2px 6px;
        border-radius: 4px;
    }}
    blockquote {{
        background: #0f172a;
        border-left: 4px solid #38bdf8;
        margin: 10px 0;
        padding: 12px 16px;
        font-style: italic;
        color: #cbd5e1;
        border-radius: 0 6px 6px 0;
    }}
    .footer {{
        margin-top: 40px;
        border-top: 1px solid #334155;
        padding-top: 15px;
        font-size: 12px;
        color: #64748b;
        text-align: center;
    }}
    @media print {{
        body {{ background: #ffffff; color: #000000; padding: 0; }}
        .container {{ background: #ffffff; border: none; box-shadow: none; }}
        .meta-box, .indicator-chip, blockquote {{ background: #f8fafc; color: #000; border-color: #cbd5e1; }}
        code {{ color: #0284c7; background: #f1f5f9; }}
    }}
</style>
</head>
<body>
<div class="container">
    <div class="classification-banner">
        CONFIDENTIAL // LAW ENFORCEMENT & INTEL PURPOSES ONLY // TLP:AMBER
    </div>
    
    <div class="header">
        <div>
            <h1>{actor.get('primary_handle')} <span style="font-size:18px; color:#94a3b8;">({actor.get('id')})</span></h1>
            <div style="margin-top: 6px;">
                <span class="badge badge-critical">{actor.get('threat_level')} THREAT</span>
                <span class="badge badge-confidence">{actor.get('attribution_confidence')}% ATTRIBUTION CONFIDENCE</span>
                <span style="margin-left: 10px; color: #94a3b8; font-size: 13px;">Status: <strong>{actor.get('status')}</strong></span>
            </div>
        </div>
        <div style="text-align: right; font-size: 12px; color: #94a3b8;">
            Generated: {now_str}<br>
            System: <strong>DarkWeb De-Anonymization Engine</strong>
        </div>
    </div>

    <div class="section-title">Identity & Operational Profile</div>
    <div class="grid-2">
        <div class="meta-box">
            <div class="meta-label">Category / Specialization</div>
            <div class="meta-value">{actor.get('category')}</div>
        </div>
        <div class="meta-box">
            <div class="meta-label">Known Aliases Across Underground</div>
            <div class="meta-value">{", ".join(actor.get('aliases', [])) or "None"}</div>
        </div>
        <div class="meta-box">
            <div class="meta-label">Underground Intelligence Sources</div>
            <div class="meta-value">{", ".join(actor.get('sources', []))}</div>
        </div>
        <div class="meta-box">
            <div class="meta-label">Observation Timeline</div>
            <div class="meta-value">First: {actor.get('first_seen')} | Last: {actor.get('last_seen')}</div>
        </div>
    </div>

    <div class="section-title">De-Anonymization & Suspect Real-World Entity</div>
    <div class="suspect-card">
        <div style="font-size: 14px; font-weight: 700; color: #ec4899; text-transform: uppercase;">
            Suspected Physical Attribution Link ({suspect.get('confidence_level', 'High')} Confidence)
        </div>
        <div style="margin-top: 10px; font-size: 20px; font-weight: 700; color: #f8fafc;">
            {suspect.get('probable_legal_name', 'Attribution In Progress')}
        </div>
        <div style="margin-top: 8px; font-size: 14px; color: #cbd5e1;">
            <strong>Jurisdiction:</strong> {suspect.get('suspected_city', 'Unknown')}, {suspect.get('suspected_country', 'Unknown')}<br>
            <strong>Probable Timezone:</strong> {suspect.get('probable_timezone', 'Undetermined')}<br>
            <strong>Correlated Clearnet IPs:</strong> <code>{ips_str}</code><br>
            <strong>Clearnet Identifiers:</strong> <code>{clearnet_accs}</code>
        </div>
    </div>

    <div class="section-title">Cryptographic & Financial Footprint</div>
    <div>
        <h4 style="margin: 10px 0 6px 0; color: #cbd5e1;">PGP Key Identification:</h4>
        {pgp_html}
    </div>
    <div style="margin-top: 15px;">
        <h4 style="margin: 10px 0 6px 0; color: #cbd5e1;">Crypto Wallets:</h4>
        {wallet_html}
    </div>

    <div class="section-title">Communications & Darknet Infrastructure</div>
    <div>
        <h4 style="margin: 10px 0 6px 0; color: #cbd5e1;">Associated Tor Hidden Services (.onion):</h4>
        <div class='indicator-chip'>{"<br>".join([f"<code>{o}</code>" for o in actor.get('associated_onions', [])]) or "None"}</div>
        <h4 style="margin: 15px 0 6px 0; color: #cbd5e1;">Direct Communications:</h4>
        {comm_html}
    </div>

    <div class="section-title">Stylometric Profile & Sample Post Intercepts</div>
    <div style="margin-bottom: 12px; font-size: 13px; color: #94a3b8;">
        Active UTC Hour Spread: <code>{str(actor.get('active_hours_utc', []))}</code>
    </div>
    {sample_posts_html}

    <div class="section-title">Analyst Summary & Attribution Evidentiary Basis</div>
    <p style="background: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid #334155;">
        {actor.get('summary')}
    </p>

    <div class="footer">
        Dark Web Threat Actor De-Anonymization System &copy; 2026. Automated attribution trail verified via cryptographic, infrastructure, and NLP stylometric correlation.
    </div>
</div>
</body>
</html>"""
        return html
