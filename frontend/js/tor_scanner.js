// Tor Misconfiguration & Infrastructure Correlator Controller

document.addEventListener('DOMContentLoaded', () => {
  const scanBtn = document.getElementById('btn-scan-onion');
  const inputOnion = document.getElementById('input-onion-scan');

  if (scanBtn) {
    scanBtn.addEventListener('click', () => {
      const url = inputOnion.value.trim();
      if (!url) {
        alert('Please enter a Tor .onion service address.');
        return;
      }
      runOnionScan(url);
    });

    inputOnion.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') scanBtn.click();
    });
  }
});

window.loadReconTargets = async function() {
  const container = document.getElementById('recon-target-list');
  if (!container) return;

  try {
    const res = await fetch('/api/recon/targets');
    const targets = await res.json();

    container.innerHTML = '';
    targets.forEach((target, index) => {
      const card = document.createElement('div');
      card.className = `target-card ${index === 0 ? 'selected' : ''}`;
      card.innerHTML = `
        <div class="target-card-title">${escapeHtml(target.title)}</div>
        <div class="target-card-onion">${target.onion_address}</div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:6px; font-size:11px;">
          <span style="color:#fb923c; font-weight:600;"><i class="fa-solid fa-server"></i> ${target.correlated_clearnet_ip}</span>
          <span style="color:#34d399; font-weight:700;">${target.confidence_score}% Confidence</span>
        </div>
      `;
      card.addEventListener('click', () => {
        document.querySelectorAll('.target-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        document.getElementById('input-onion-scan').value = target.onion_address;
        runOnionScan(target.onion_address);
      });
      container.appendChild(card);
    });

    if (targets.length > 0) {
      document.getElementById('input-onion-scan').value = targets[0].onion_address;
      runOnionScan(targets[0].onion_address);
    }
  } catch (err) {
    console.error('Failed to load recon targets:', err);
  }
};

async function runOnionScan(onionUrl) {
  const resultBox = document.getElementById('recon-result-container');
  const scanBtn = document.getElementById('btn-scan-onion');

  scanBtn.disabled = true;
  scanBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Probing Onion Infrastructure...`;

  resultBox.innerHTML = `
    <div style="text-align:center; padding: 60px 20px;">
      <i class="fa-solid fa-radar fa-spin" style="font-size: 40px; color: var(--accent-cyan); margin-bottom: 16px;"></i>
      <h3>Inspecting Tor Hidden Service & Scanning Misconfigurations...</h3>
      <p style="font-size: 13px; color: var(--text-muted); margin-top: 6px;">Analyzing TLS certificates, verifying /server-status leaks, calculating MurmurHash3 favicon, and correlating clearnet host IP...</p>
    </div>
  `;

  try {
    const res = await fetch('/api/recon/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ onion_url: onionUrl, deep_scan: true })
    });

    if (!res.ok) throw new Error('Scan request failed');
    const data = await res.json();
    renderReconResults(data);
  } catch (err) {
    console.error(err);
    resultBox.innerHTML = `
      <div style="text-align:center; padding: 40px; color: #f87171;">
        <i class="fa-solid fa-triangle-exclamation" style="font-size: 36px; margin-bottom: 12px;"></i>
        <h3>Failed to execute reconnaissance scan</h3>
        <p style="font-size: 13px;">Error communicating with recon sensor.</p>
      </div>
    `;
  } finally {
    scanBtn.disabled = false;
    scanBtn.innerHTML = `<i class="fa-solid fa-radar"></i> De-Anonymize Hidden Service`;
  }
}

function renderReconResults(data) {
  const resultBox = document.getElementById('recon-result-container');
  const geo = data.geo_location || {};

  const misconfigHtml = (data.exposed_misconfigurations || []).map(m => `
    <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; border-left: 3px solid ${m.severity === 'CRITICAL' ? '#ef4444' : '#f59e0b'}; padding: 12px 16px; border-radius: 6px; margin-bottom: 10px;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-weight:700; font-size:13px; color:#f8fafc;">${escapeHtml(m.summary)}</span>
        <span class="badge ${m.severity === 'CRITICAL' ? 'badge-threat-CRITICAL' : 'badge-threat-HIGH'}">${m.severity}</span>
      </div>
      ${m.path ? `<div style="font-size:11px; color:var(--text-muted); margin-top:4px;">Endpoint: <code>${m.path}</code></div>` : ''}
      ${m.evidence ? `<blockquote style="background:#090d16; border-left:3px solid #38bdf8; margin-top:6px; padding:6px 10px; font-size:12px; color:#cbd5e1; font-family:var(--font-mono);">${escapeHtml(m.evidence)}</blockquote>` : ''}
      ${m.cert_serial ? `<div style="font-size:11px; color:#94a3b8; margin-top:4px;">Cert Serial: <code>${m.cert_serial}</code> | Subject: <code>${m.subject}</code></div>` : ''}
      ${m.sans ? `<div style="font-size:11px; color:#38bdf8; margin-top:2px;">Subject Alternative Names (SANs): <code>${m.sans.join(', ')}</code></div>` : ''}
    </div>
  `).join('') || '<p style="color:var(--text-dim); font-size:13px;">No explicit misconfigurations identified.</p>';

  const trailHtml = (data.attribution_trail || []).map((step, idx) => `
    <div style="display:flex; align-items:flex-start; gap:10px; font-size:12px; margin-bottom:8px;">
      <span style="background:var(--accent-cyan); color:#000; width:18px; height:18px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:800; font-size:10px; flex-shrink:0;">${idx+1}</span>
      <span style="color:#cbd5e1;">${escapeHtml(step)}</span>
    </div>
  `).join('');

  const wallets = data.extracted_indicators.wallets || [];
  const pgps = data.extracted_indicators.pgp_fingerprints || [];
  const emails = data.extracted_indicators.emails || [];

  resultBox.innerHTML = `
    <!-- Top Origin De-cloaked Highlight Banner -->
    <div class="origin-unmasked-banner">
      <div>
        <div style="font-size:12px; font-weight:800; text-transform:uppercase; color:#fb923c; letter-spacing:1px;">
          <i class="fa-solid fa-lock-open"></i> Origin Clearnet Server De-Anonymized
        </div>
        <div class="origin-ip-val">${data.correlated_clearnet_ip || 'Uncorrelated'}</div>
        <div style="font-size:13px; color:#fed7aa; margin-top:4px;">
          <strong>Domain:</strong> <code>${data.correlated_clearnet_domain || 'N/A'}</code> | 
          <strong>Hosting:</strong> ${escapeHtml(geo.asn || 'Unknown')} (${escapeHtml(geo.city || '')}, ${escapeHtml(geo.country || '')})
        </div>
      </div>
      <div style="text-align:right;">
        <div style="font-size:32px; font-weight:800; font-family:var(--font-mono); color:#34d399;">
          ${data.de_anonymization_confidence}%
        </div>
        <div style="font-size:11px; color:var(--text-muted); text-transform:uppercase;">Attribution Confidence</div>
      </div>
    </div>

    <!-- Target Details Metadata Grid -->
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:12px; margin-bottom:20px;">
      <div style="background:rgba(15,23,42,0.8); padding:10px 14px; border-radius:6px; border:1px solid #334155;">
        <span style="font-size:11px; color:var(--text-dim); text-transform:uppercase;">Hidden Service</span>
        <div style="font-size:11px; font-family:var(--font-mono); color:#38bdf8; word-break:break-all; margin-top:2px;">${data.onion_url}</div>
      </div>
      <div style="background:rgba(15,23,42,0.8); padding:10px 14px; border-radius:6px; border:1px solid #334155;">
        <span style="font-size:11px; color:var(--text-dim); text-transform:uppercase;">Exposed Web Server</span>
        <div style="font-size:12px; font-weight:600; color:#f8fafc; margin-top:2px;">${data.server_header || 'Unknown'}</div>
      </div>
      <div style="background:rgba(15,23,42,0.8); padding:10px 14px; border-radius:6px; border:1px solid #334155;">
        <span style="font-size:11px; color:var(--text-dim); text-transform:uppercase;">Favicon MurmurHash3</span>
        <div style="font-size:12px; font-family:var(--font-mono); color:#f59e0b; margin-top:2px;">${data.favicon_murmur3 || 'None'}</div>
      </div>
    </div>

    <!-- Identified Misconfigurations -->
    <div style="margin-bottom:20px;">
      <h4 style="font-size:13px; text-transform:uppercase; color:var(--accent-cyan); letter-spacing:1px; margin-bottom:10px;">
        <i class="fa-solid fa-bug"></i> Detected Server Misconfigurations & Leaks
      </h4>
      ${misconfigHtml}
    </div>

    <!-- Extracted Identifiers -->
    <div style="margin-bottom:20px; background:rgba(15,23,42,0.8); padding:16px; border-radius:8px; border:1px solid #334155;">
      <h4 style="font-size:13px; text-transform:uppercase; color:var(--text-muted); letter-spacing:1px; margin-bottom:10px;">
        <i class="fa-solid fa-fingerprint"></i> Intercepted Crypto & Identity Footprints
      </h4>
      <div style="font-size:12px; line-height:1.6;">
        <div><strong>Cryptocurrency Wallets:</strong> ${wallets.map(w => `<code>${w}</code>`).join(' ') || '<span style="color:var(--text-dim);">None</span>'}</div>
        <div style="margin-top:4px;"><strong>PGP Public Fingerprints:</strong> ${pgps.map(p => `<code>${p}</code>`).join(' ') || '<span style="color:var(--text-dim);">None</span>'}</div>
        <div style="margin-top:4px;"><strong>Associated Contacts:</strong> ${emails.map(e => `<code>${e}</code>`).join(' ') || '<span style="color:var(--text-dim);">None</span>'}</div>
      </div>
    </div>

    <!-- Attribution Evidentiary Chain -->
    <div>
      <h4 style="font-size:13px; text-transform:uppercase; color:var(--text-muted); letter-spacing:1px; margin-bottom:10px;">
        <i class="fa-solid fa-link"></i> Forensics Attribution Evidentiary Trail
      </h4>
      ${trailHtml}
    </div>
  `;
}
