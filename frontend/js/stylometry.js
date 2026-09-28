// AI Stylometric Persona Identification Controller
let radarChartInstance = null;

const sampleCorpora = {
  sample1: "WTS fresh corporate domain admin access. Fortune 500 healthcare provider. Domain controller compromised, backup servers mapped. Starting bid 5 BTC. Escrow via Dread staff only!! Contact jabber with PGP.",
  sample2: "ATTENTION: All management of Target Corporation. Your data has been encrypted using military grade AES-256. If ransom of 2,500,000 USD is not paid within 72 hours, all customer PII, executive emails, and financial audits will be published on our mirror!!",
  sample3: "0day RCE in popular enterprise firewall appliances (FortiGate / Palo Alto). Remote unauthenticated root shell over SSL VPN port 443. PoC video available for serious buyers. Asking price: 80,000 USD. Priv8 FUD stub included."
};

document.addEventListener('DOMContentLoaded', () => {
  const textarea = document.getElementById('stylometry-input-text');
  const analyzeBtn = document.getElementById('btn-analyze-stylometry');
  const charCount = document.getElementById('stylometry-char-count');

  // Sample Loaders
  document.getElementById('btn-load-sample-1')?.addEventListener('click', () => {
    textarea.value = sampleCorpora.sample1;
    updateCharCount();
  });
  document.getElementById('btn-load-sample-2')?.addEventListener('click', () => {
    textarea.value = sampleCorpora.sample2;
    updateCharCount();
  });
  document.getElementById('btn-load-sample-3')?.addEventListener('click', () => {
    textarea.value = sampleCorpora.sample3;
    updateCharCount();
  });

  textarea?.addEventListener('input', updateCharCount);

  function updateCharCount() {
    const len = textarea.value.length;
    charCount.textContent = `${len} characters`;
  }

  analyzeBtn?.addEventListener('click', async () => {
    const text = textarea.value.trim();
    if (!text) {
      alert('Please enter or load a text sample for stylometric analysis.');
      return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Analyzing Stylometry...`;

    try {
      const res = await fetch('/api/stylometry/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });

      if (!res.ok) throw new Error('Stylometry request failed');
      const data = await res.json();

      renderStylometryResults(data);
    } catch (err) {
      console.error(err);
      alert('Failed to analyze stylometry');
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = `<i class="fa-solid fa-fingerprint"></i> Compute AI Stylometric Attribution`;
    }
  });

  // Init empty radar chart
  initRadarChart();
});

function renderStylometryResults(data) {
  const f = data.features;
  
  // Update feature pills
  document.getElementById('feat-sent-len').textContent = f.avg_sentence_length || 0;
  document.getElementById('feat-word-len').textContent = f.avg_word_length || 0;
  document.getElementById('feat-lexical').textContent = f.lexical_richness || 0;
  document.getElementById('feat-punct').textContent = f.punctuation_entropy || 0;
  document.getElementById('feat-upper').textContent = f.uppercase_ratio || 0;

  // Render candidates
  const container = document.getElementById('stylometry-candidates-container');
  container.innerHTML = '';

  const candidates = data.candidate_matches || [];
  if (candidates.length === 0) {
    container.innerHTML = `<div style="text-align:center; padding: 20px; color: var(--text-dim);">No significant stylometric correlation found.</div>`;
    return;
  }

  candidates.forEach((cand, idx) => {
    const isTop = idx === 0;
    const card = document.createElement('div');
    card.style.background = isTop ? 'rgba(6, 182, 212, 0.12)' : 'rgba(15, 23, 42, 0.7)';
    card.style.border = isTop ? '1px solid var(--accent-cyan)' : '1px solid #334155';
    card.style.borderRadius = '8px';
    card.style.padding = '14px';

    const levelBadge = cand.attribution_level === 'CONFIRMED_MATCH' 
      ? '<span class="badge" style="background:#10b981; color:#000;">CONFIRMED PERSONA LINK</span>'
      : (cand.attribution_level === 'HIGH_PROBABILITY' 
        ? '<span class="badge" style="background:rgba(56,189,248,0.2); color:#38bdf8; border:1px solid #38bdf8;">HIGH PROBABILITY</span>'
        : '<span class="badge" style="background:rgba(245,158,11,0.2); color:#fbbf24;">MODERATE CORRELATION</span>');

    const markersHtml = cand.matching_markers.map(m => `<li>${escapeHtml(m)}</li>`).join('');

    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <span style="font-size:16px; font-weight:700; color:#f8fafc;">${escapeHtml(cand.primary_handle)}</span>
          <span style="font-size:12px; color:var(--text-dim); margin-left:6px;">(${cand.actor_id})</span>
        </div>
        <div style="text-align:right;">
          <span style="font-size:22px; font-weight:800; font-family:var(--font-mono); color:${isTop ? '#06b6d4' : '#34d399'};">
            ${cand.confidence_percentage}%
          </span>
          <div style="font-size:10px; color:var(--text-dim); text-transform:uppercase;">Attribution Score</div>
        </div>
      </div>

      <div style="margin-top:6px; display:flex; align-items:center; gap:8px;">
        ${levelBadge}
        <span style="font-size:11px; color:var(--text-muted);">${escapeHtml(cand.category)}</span>
      </div>

      <div style="margin-top:8px; font-size:11px; color:var(--text-dim);">
        <i class="fa-regular fa-clock"></i> Estimated Active Timezone: <strong style="color:#cbd5e1;">${cand.estimated_timezone}</strong>
      </div>

      <div style="margin-top:10px; font-size:11px; color:#cbd5e1;">
        <strong style="color:var(--text-muted);">Attribution Stylistic Evidence:</strong>
        <ul style="margin: 4px 0 0 16px; line-height: 1.4;">${markersHtml}</ul>
      </div>
    `;
    container.appendChild(card);
  });

  // Update Radar Chart with top match comparison
  if (candidates.length > 0) {
    updateRadarChart(f, candidates[0].confidence_percentage);
  }
}

function initRadarChart() {
  const ctx = document.getElementById('stylometryRadarChart')?.getContext('2d');
  if (!ctx) return;

  radarChartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['Sentence Length', 'Word Complexity', 'Lexical Diversity', 'Punctuation Density', 'Uppercase Frequency', 'Dark Jargon Match'],
      datasets: [
        {
          label: 'Target Text Sample',
          data: [50, 60, 70, 40, 20, 80],
          backgroundColor: 'rgba(6, 182, 212, 0.25)',
          borderColor: '#06b6d4',
          pointBackgroundColor: '#06b6d4',
          borderWidth: 2
        },
        {
          label: 'Baseline Actor Corpus',
          data: [45, 65, 68, 38, 22, 75],
          backgroundColor: 'rgba(236, 72, 153, 0.15)',
          borderColor: '#ec4899',
          pointBackgroundColor: '#ec4899',
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
          grid: { color: 'rgba(255, 255, 255, 0.1)' },
          pointLabels: {
            color: '#94a3b8',
            font: { size: 10, family: 'Inter, sans-serif' }
          },
          ticks: { display: false }
        }
      },
      plugins: {
        legend: {
          labels: { color: '#f8fafc', font: { size: 11 } }
        }
      }
    }
  });
}

function updateRadarChart(features, topConfidence) {
  if (!radarChartInstance) return;

  const sLenNorm = Math.min(100, (features.avg_sentence_length / 25) * 100);
  const wLenNorm = Math.min(100, (features.avg_word_length / 8) * 100);
  const lexNorm = Math.min(100, features.lexical_richness * 100);
  const punctNorm = Math.min(100, (features.punctuation_entropy / 0.15) * 100);
  const upNorm = Math.min(100, (features.uppercase_ratio / 0.1) * 100);
  const jargonNorm = Math.min(100, features.detected_slang_jargon.length * 25);

  radarChartInstance.data.datasets[0].data = [sLenNorm, wLenNorm, lexNorm, punctNorm, upNorm, jargonNorm];
  
  // Baseline simulated curve
  const delta = (100 - topConfidence) * 0.15;
  radarChartInstance.data.datasets[1].data = [
    Math.max(10, sLenNorm - delta),
    Math.max(10, wLenNorm + delta * 0.5),
    Math.max(10, lexNorm - delta * 0.8),
    Math.max(10, punctNorm + delta),
    Math.max(10, upNorm - delta * 0.5),
    Math.max(10, jargonNorm - delta)
  ];

  radarChartInstance.update();
}
