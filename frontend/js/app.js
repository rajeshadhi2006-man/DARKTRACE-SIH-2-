// State Management
const state = {
  currentTab: 'tab-dashboard',
  stats: {},
  actors: [],
  telemetryFeed: [],
  selectedActor: null,
  filters: {
    query: '',
    category: '',
    source: '',
    startDate: '',
    endDate: ''
  }
};

const API_BASE = ''; // Same origin

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initFilterListeners();
  initCrawlerButton();
  initModalListeners();
  
  // Initial API loads
  loadStats();
  loadActors();
  loadTelemetry();

  // Periodically refresh telemetry
  setInterval(loadTelemetry, 15000);
});

// Tab Navigation
function initTabs() {
  const tabs = document.querySelectorAll('.nav-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetId = tab.getAttribute('data-tab');
      switchTab(targetId);
    });
  });
}

function switchTab(tabId) {
  state.currentTab = tabId;

  document.querySelectorAll('.nav-tab').forEach(t => {
    t.classList.toggle('active', t.getAttribute('data-tab') === tabId);
  });

  document.querySelectorAll('.tab-pane').forEach(p => {
    p.classList.toggle('active', p.id === tabId);
  });

  // Trigger sub-module updates on tab switch
  if (tabId === 'tab-graph' && window.refreshNetworkGraph) {
    window.refreshNetworkGraph();
  } else if (tabId === 'tab-recon' && window.loadReconTargets) {
    window.loadReconTargets();
  } else if (tabId === 'tab-dossiers') {
    renderDossierCards();
  }
}

// Stats Loader
async function loadStats() {
  try {
    const res = await fetch(`${API_BASE}/api/stats`);
    const data = await res.json();
    state.stats = data;

    document.getElementById('stat-actors').textContent = data.total_actors || 0;
    document.getElementById('stat-wallets').textContent = data.total_crypto_wallets || 0;
    document.getElementById('stat-pgp').textContent = data.total_pgp_keys || 0;
    document.getElementById('stat-onions').textContent = data.monitored_onion_services || 0;
    document.getElementById('stat-suspects').textContent = data.unmasked_real_world_suspects || 0;
  } catch (err) {
    console.error('Failed to load stats:', err);
  }
}

// Actor Directory Loader & Query
async function loadActors() {
  try {
    const params = new URLSearchParams();
    if (state.filters.query) params.append('query', state.filters.query);
    if (state.filters.category) params.append('category', state.filters.category);
    if (state.filters.source) params.append('source', state.filters.source);
    if (state.filters.startDate) params.append('start_date', state.filters.startDate);
    if (state.filters.endDate) params.append('end_date', state.filters.endDate);

    const res = await fetch(`${API_BASE}/api/actors?${params.toString()}`);
    const data = await res.json();
    state.actors = data;

    renderActorTable(data);
    updateActorFilterDropdowns(data);
    
    if (state.currentTab === 'tab-dossiers') {
      renderDossierCards();
    }
  } catch (err) {
    console.error('Failed to load actors:', err);
  }
}

function renderActorTable(actors) {
  const tbody = document.getElementById('actor-table-body');
  const countLabel = document.getElementById('actor-count-label');
  tbody.innerHTML = '';
  countLabel.textContent = `Showing ${actors.length} actors`;

  if (actors.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 30px; color: var(--text-dim);">No threat actors matched the active search filters.</td></tr>`;
    return;
  }

  actors.forEach(actor => {
    const suspect = actor.real_world_suspect || {};
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>
        <div style="font-weight: 700; color: #f8fafc; font-size: 14px;">${escapeHtml(actor.primary_handle)}</div>
        <div style="font-size: 11px; color: var(--text-dim);">ID: <code>${actor.id}</code></div>
      </td>
      <td>
        <span class="badge badge-threat-${actor.threat_level}">${escapeHtml(actor.category)}</span>
      </td>
      <td>
        <div class="confidence-meter">
          <div class="meter-bar">
            <div class="meter-fill" style="width: ${actor.attribution_confidence}%"></div>
          </div>
          <span style="font-weight: 700; font-family: var(--font-mono); font-size: 12px; color: #34d399;">${actor.attribution_confidence}%</span>
        </div>
      </td>
      <td>
        <div style="font-weight: 600; color: #ec4899; font-size: 13px;">${escapeHtml(suspect.probable_legal_name || 'Under Active Analysis')}</div>
        <div style="font-size: 11px; color: var(--text-muted);">${suspect.probable_timezone || 'Timezone pending'}</div>
      </td>
      <td>
        <div><code>${(suspect.associated_ips && suspect.associated_ips[0]) || 'Tor Hidden'}</code></div>
        <div style="font-size: 11px; color: var(--text-dim);">${escapeHtml(suspect.suspected_city || '')} ${escapeHtml(suspect.suspected_country || '')}</div>
      </td>
      <td>
        <div style="font-size: 12px; color: var(--text-muted); font-family: var(--font-mono);">${actor.last_seen}</div>
        <div>${actor.sources.map(s => `<span class="source-tag">${s}</span>`).join('')}</div>
      </td>
      <td>
        <div style="display:flex; gap:6px;">
          <button class="btn btn-outline" style="padding: 4px 8px; font-size: 11px;" onclick="viewActorModal('${actor.id}')">
            <i class="fa-solid fa-eye"></i> Dossier
          </button>
          <a class="btn btn-primary" style="padding: 4px 8px; font-size: 11px;" href="${API_BASE}/api/export/report/${actor.id}" target="_blank">
            <i class="fa-solid fa-print"></i> Report
          </a>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function updateActorFilterDropdowns(actors) {
  const select = document.getElementById('graph-focus-actor');
  if (!select) return;
  const currentVal = select.value;
  select.innerHTML = '<option value="">Full Underground Graph</option>';
  actors.forEach(a => {
    const opt = document.createElement('option');
    opt.value = a.id;
    opt.textContent = `${a.primary_handle} (${a.id})`;
    select.appendChild(opt);
  });
  select.value = currentVal;
}

// Telemetry Feed Loader
async function loadTelemetry() {
  try {
    const res = await fetch(`${API_BASE}/api/telemetry/feed`);
    const feed = await res.json();
    state.telemetryFeed = feed;
    renderTelemetryFeed(feed);
  } catch (err) {
    console.error('Failed to load telemetry:', err);
  }
}

function renderTelemetryFeed(items) {
  const container = document.getElementById('telemetry-feed-container');
  if (!container) return;
  container.innerHTML = '';

  items.forEach(item => {
    const timeFormatted = item.timestamp ? item.timestamp.replace('T', ' ').replace('Z', '') : '';
    const div = document.createElement('div');
    div.className = 'feed-item';
    div.innerHTML = `
      <div class="feed-meta">
        <span class="feed-author"><i class="fa-solid fa-terminal"></i> ${escapeHtml(item.author)}</span>
        <span>${escapeHtml(item.source)} • ${timeFormatted}</span>
      </div>
      <div class="feed-text">${escapeHtml(item.summary)}</div>
      <div style="margin-top:6px; display:flex; justify-content:space-between; align-items:center; font-size:11px;">
        <span style="color:var(--text-dim);">Correlated: <code>${item.correlated_actor_id}</code></span>
        <span style="color:#10b981; font-weight:600;">${item.confidence}% Match</span>
      </div>
    `;
    container.appendChild(div);
  });
}

// Autonomous Crawl Trigger
function initCrawlerButton() {
  const btn = document.getElementById('btn-trigger-crawler');
  btn.addEventListener('click', async () => {
    btn.disabled = true;
    const originalText = btn.innerHTML;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Crawling Darknet...`;

    try {
      const res = await fetch(`${API_BASE}/api/crawler/trigger`, { method: 'POST' });
      const result = await res.json();
      
      // Reload stats, telemetry, actors
      await Promise.all([loadStats(), loadActors(), loadTelemetry()]);
      
      alert(`Autonomous Ingestion Round Completed!\n\nSources Scanned: ${result.monitored_sources_scanned.join(', ')}\nNew Footprint Intercepted: ${result.new_event.summary}`);
    } catch (err) {
      alert('Error triggering crawl round');
      console.error(err);
    } finally {
      btn.disabled = false;
      btn.innerHTML = originalText;
    }
  });
}

// Filter Listeners
function initFilterListeners() {
  const searchInput = document.getElementById('filter-search');
  const catSelect = document.getElementById('filter-category');
  const srcSelect = document.getElementById('filter-source');
  const startDate = document.getElementById('filter-date-start');
  const endDate = document.getElementById('filter-date-end');
  const resetBtn = document.getElementById('btn-reset-filters');

  let debounceTimer;
  searchInput.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      state.filters.query = e.target.value.trim();
      loadActors();
    }, 300);
  });

  catSelect.addEventListener('change', (e) => {
    state.filters.category = e.target.value;
    loadActors();
  });

  srcSelect.addEventListener('change', (e) => {
    state.filters.source = e.target.value;
    loadActors();
  });

  startDate.addEventListener('change', (e) => {
    state.filters.startDate = e.target.value;
    loadActors();
  });

  endDate.addEventListener('change', (e) => {
    state.filters.endDate = e.target.value;
    loadActors();
  });

  resetBtn.addEventListener('click', () => {
    searchInput.value = '';
    catSelect.value = '';
    srcSelect.value = '';
    startDate.value = '';
    endDate.value = '';
    state.filters = { query: '', category: '', source: '', startDate: '', endDate: '' };
    loadActors();
  });
}

// Modal Handlers
function initModalListeners() {
  const closeBtn = document.getElementById('btn-close-modal');
  const overlay = document.getElementById('actor-modal');

  closeBtn.addEventListener('click', () => {
    overlay.classList.remove('active');
  });

  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
      overlay.classList.remove('active');
    }
  });
}

window.viewActorModal = function(actorId) {
  const actor = state.actors.find(a => a.id === actorId);
  if (!actor) return;

  const suspect = actor.real_world_suspect || {};
  const content = document.getElementById('modal-content');
  
  content.innerHTML = `
    <div style="border-bottom: 2px solid var(--accent-cyan); padding-bottom: 16px; margin-bottom: 20px;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
          <h2 style="color:var(--text-main); font-size:24px;">${escapeHtml(actor.primary_handle)} <span style="font-size:16px; color:var(--text-dim);">(${actor.id})</span></h2>
          <div style="margin-top:6px; display:flex; gap:8px;">
            <span class="badge badge-threat-${actor.threat_level}">${actor.threat_level} THREAT</span>
            <span class="badge" style="background:rgba(16,185,129,0.2); color:#34d399; border:1px solid #10b981;">${actor.attribution_confidence}% ATTRIBUTION CONFIDENCE</span>
            <span class="badge" style="background:rgba(56,189,248,0.2); color:#38bdf8; border:1px solid #38bdf8;">${actor.status}</span>
          </div>
        </div>
        <a href="${API_BASE}/api/export/report/${actor.id}" target="_blank" class="btn btn-primary">
          <i class="fa-solid fa-file-pdf"></i> Official Law Enforcement Dossier
        </a>
      </div>
    </div>

    <!-- Suspect attribution highlight -->
    <div class="suspect-identity-box" style="margin-bottom:20px;">
      <div style="font-size:12px; font-weight:700; color:#ec4899; text-transform:uppercase;">
        <i class="fa-solid fa-user-check"></i> Suspected Physical Identity Link (${suspect.confidence_level || 'High'} Confidence)
      </div>
      <div style="font-size:20px; font-weight:700; color:#f8fafc; margin-top:4px;">
        ${escapeHtml(suspect.probable_legal_name || 'Under Active Attribution')}
      </div>
      <div style="font-size:13px; color:var(--text-muted); margin-top:6px; line-height:1.5;">
        <strong>Location:</strong> ${escapeHtml(suspect.suspected_city || 'Unknown')}, ${escapeHtml(suspect.suspected_country || 'Unknown')}<br>
        <strong>Probable Operating Timezone:</strong> ${escapeHtml(suspect.probable_timezone || 'Undetermined')}<br>
        <strong>Correlated Clearnet IPs:</strong> <code>${(suspect.associated_ips || []).join(', ') || 'None'}</code><br>
        <strong>Clearnet Digital Accounts:</strong> <code>${(suspect.clearnet_accounts || []).join(', ') || 'None'}</code>
      </div>
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:20px;">
      <div style="background:rgba(10,15,29,0.8); padding:14px; border-radius:8px; border:1px solid #334155;">
        <h4 style="font-size:12px; text-transform:uppercase; color:var(--text-dim); margin-bottom:8px;">Cryptographic Keys (PGP)</h4>
        ${actor.pgp_keys && actor.pgp_keys.length > 0 ? actor.pgp_keys.map(p => `
          <div style="margin-bottom:8px;">
            <div style="font-size:12px; font-weight:600; color:#facc15;">Key ID: ${p.key_id} (${p.bits} bits)</div>
            <div style="font-size:11px; font-family:var(--font-mono); color:#cbd5e1; word-break:break-all;">Fingerprint: ${p.fingerprint}</div>
            <div style="font-size:11px; color:var(--text-dim);">Identity: ${p.email_identity || 'N/A'}</div>
          </div>
        `).join('') : '<span style="color:var(--text-dim); font-size:12px;">No PGP keys registered</span>'}
      </div>

      <div style="background:rgba(10,15,29,0.8); padding:14px; border-radius:8px; border:1px solid #334155;">
        <h4 style="font-size:12px; text-transform:uppercase; color:var(--text-dim); margin-bottom:8px;">Monitored Crypto Wallets</h4>
        ${actor.crypto_wallets && actor.crypto_wallets.length > 0 ? actor.crypto_wallets.map(w => `
          <div style="margin-bottom:8px;">
            <div style="font-size:12px; font-weight:700; color:#34d399;">${w.currency} (Volume: ${w.total_received || 'N/A'})</div>
            <code style="word-break:break-all; font-size:11px;">${w.address}</code>
            <div style="font-size:10px; color:var(--text-dim); margin-top:2px;">Tags: ${w.cluster_tags.join(', ')}</div>
          </div>
        `).join('') : '<span style="color:var(--text-dim); font-size:12px;">No wallets recorded</span>'}
      </div>
    </div>

    <div style="background:rgba(10,15,29,0.8); padding:14px; border-radius:8px; border:1px solid #334155; margin-bottom:20px;">
      <h4 style="font-size:12px; text-transform:uppercase; color:var(--text-dim); margin-bottom:8px;">Associated Tor Hidden Services (.onion)</h4>
      ${actor.associated_onions && actor.associated_onions.length > 0 ? actor.associated_onions.map(o => `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <code>${o}</code>
          <button class="btn btn-outline" style="padding:2px 8px; font-size:10px;" onclick="switchTab('tab-recon'); document.getElementById('input-onion-scan').value='${o}'; document.getElementById('btn-scan-onion').click(); document.getElementById('actor-modal').classList.remove('active');">
            Scan Origin IP
          </button>
        </div>
      `).join('') : '<span style="color:var(--text-dim); font-size:12px;">None indexed</span>'}
    </div>

    <div style="background:rgba(10,15,29,0.8); padding:14px; border-radius:8px; border:1px solid #334155;">
      <h4 style="font-size:12px; text-transform:uppercase; color:var(--text-dim); margin-bottom:8px;">Underground Activity Summary</h4>
      <p style="font-size:13px; color:#cbd5e1; line-height:1.5;">${escapeHtml(actor.summary)}</p>
    </div>
  `;

  document.getElementById('actor-modal').classList.add('active');
};

function renderDossierCards() {
  const container = document.getElementById('dossiers-container');
  if (!container) return;
  container.innerHTML = '';

  state.actors.forEach(actor => {
    const suspect = actor.real_world_suspect || {};
    const card = document.createElement('div');
    card.className = 'glass-panel dossier-card';
    card.innerHTML = `
      <div class="dossier-header">
        <div>
          <h4 style="font-size:18px; font-weight:700; color:var(--text-main);">${escapeHtml(actor.primary_handle)}</h4>
          <span style="font-size:11px; color:var(--text-dim);">ID: <code>${actor.id}</code></span>
        </div>
        <span class="badge badge-threat-${actor.threat_level}">${actor.threat_level}</span>
      </div>

      <div class="suspect-identity-box">
        <div style="font-size:11px; font-weight:700; color:#ec4899; text-transform:uppercase;">
          Unmasked Legal Identity (${suspect.confidence_level || 'High'})
        </div>
        <div style="font-size:16px; font-weight:700; color:#f8fafc; margin-top:2px;">
          ${escapeHtml(suspect.probable_legal_name || 'Under Active Analysis')}
        </div>
        <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">
          Jurisdiction: <strong>${escapeHtml(suspect.suspected_city || '')}, ${escapeHtml(suspect.suspected_country || '')}</strong>
        </div>
      </div>

      <div style="font-size:12px; color:var(--text-muted); display:flex; flex-direction:column; gap:6px;">
        <div><strong>Specialization:</strong> ${escapeHtml(actor.category)}</div>
        <div><strong>Aliases:</strong> ${escapeHtml(actor.aliases.join(', ') || 'None')}</div>
        <div><strong>Sources:</strong> ${actor.sources.map(s => `<span class="source-tag">${s}</span>`).join('')}</div>
        <div><strong>Confidence:</strong> <span style="color:#34d399; font-weight:700;">${actor.attribution_confidence}%</span></div>
      </div>

      <div style="margin-top:auto; padding-top:12px; border-top:1px solid #334155; display:flex; justify-content:space-between; align-items:center;">
        <button class="btn btn-outline" style="padding:6px 12px;" onclick="viewActorModal('${actor.id}')">
          <i class="fa-solid fa-list-check"></i> Inspect
        </button>
        <a href="${API_BASE}/api/export/report/${actor.id}" target="_blank" class="btn btn-primary" style="padding:6px 12px;">
          <i class="fa-solid fa-file-shield"></i> Law Enforcement Report
        </a>
      </div>
    `;
    container.appendChild(card);
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
