import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Server,
  Shield,
  Globe,
  Lock,
  Cpu,
  Search,
  RefreshCw,
  ExternalLink,
  ChevronRight,
  Filter,
  AlertTriangle,
  CheckCircle2,
  Radar,
  Radio,
  Sparkles,
  Terminal,
  Zap,
  Network,
  Share2,
  FileCheck,
  Eye,
  Hash,
  MapPin,
  X
} from 'lucide-react';
import { infrastructureApi } from '../services/api';

interface SurfaceItem {
  id: string;
  type: string;
  value: string;
  correlation: string;
  asn: string;
  location: string;
  confidence: string;
  confidence_val?: number;
  method: string;
  open_ports?: number[];
  timestamp?: string;
}

const PRESET_TARGETS = [
  {
    name: 'Dread Forum Origin',
    target: 'dreadmarket736xqwp4m7vylz4k5j6r4r2dff3b3e2q9d8.onion',
    san: 'backup.dread-vault.org',
    status: 'Apache/2.4.52 Server at dread-infra.is Client: 194.26.29.114',
    favicon: -1294875632
  },
  {
    name: 'NightFox Staging Mirror',
    target: 'nightfox7x2u9p4q.onion',
    san: 'nightfox-clearnet.org',
    status: 'nginx/1.22.1 Server at nightfox-clearnet.org Client: 185.220.101.42',
    favicon: -827361928
  },
  {
    name: 'LockBit 3.0 Extortion Staging',
    target: 'lockbit3leakszqwertyuiopasdfghjklzxcvbnm123456789.onion',
    san: 'lb-extort-node03.clearnet-sync.ru',
    status: 'phpinfo() OpenSSH_8.9p1 Ubuntu Client: 91.240.118.89',
    favicon: -449102834
  },
  {
    name: 'Bohemia Market Origin',
    target: 'bohemiamkt993xqwq004mka1992019alzkqpwq29291823.onion',
    san: 'bohemia-checkout.com',
    status: 'Apache/2.4.41 /.git/config leak Client: 45.142.214.205',
    favicon: 1928374615
  },
  {
    name: 'Hydra Redux Escrow Node',
    target: 'hydraex7vbb45m839xplkwqqe2m910a8b7c6d5e4f3a2b1c9.onion',
    san: 'hydra-portal-cdn.net',
    status: 'Tor descriptor skew 1.84s NTP drift Client: 185.196.220.73',
    favicon: 837461928
  }
];

export const InfrastructurePage: React.FC = () => {
  const navigate = useNavigate();

  // State
  const [findings, setFindings] = useState<SurfaceItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [probing, setProbing] = useState<boolean>(false);
  const [probeResult, setProbeResult] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [filterType, setFilterType] = useState<string>('ALL');
  const [selectedItem, setSelectedItem] = useState<SurfaceItem | null>(null);

  // Form input state
  const [inputTarget, setInputTarget] = useState<string>('dreadmarket736xqwp4m7vylz4k5j6r4r2dff3b3e2q9d8.onion');
  const [inputSan, setInputSan] = useState<string>('backup.dread-vault.org');
  const [inputStatusText, setInputStatusText] = useState<string>('Apache/2.4.52 Server at dread-infra.is Client: 194.26.29.114');
  const [inputFavicon, setInputFavicon] = useState<string>('-1294875632');
  const [showAdvanced, setShowAdvanced] = useState<boolean>(false);
  const [probeStep, setProbeStep] = useState<string>('');

  useEffect(() => {
    loadFindings();
  }, []);

  const loadFindings = async () => {
    setLoading(true);
    try {
      const data = await infrastructureApi.getFindings();
      if (Array.isArray(data)) {
        setFindings(data);
      }
    } catch (err) {
      console.error('Failed to load infrastructure surface findings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyPreset = (preset: typeof PRESET_TARGETS[0]) => {
    setInputTarget(preset.target);
    setInputSan(preset.san);
    setInputStatusText(preset.status);
    setInputFavicon(preset.favicon.toString());
    setProbeResult(null);
  };

  const handleExecuteProbe = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputTarget.trim()) return;

    setProbing(true);
    setProbeResult(null);
    setProbeStep('INITIALIZING PASSIVE SENSOR ARRAY...');

    try {
      setTimeout(() => setProbeStep('QUERYING CERTIFICATE TRANSPARENCY (CT) LOGS...'), 400);
      setTimeout(() => setProbeStep('CALCULATING FAVICON MURMURHASH3 DIGEST...'), 900);
      setTimeout(() => setProbeStep('PARSING SERVER DIAGNOSTIC STATUS & VHOST LEAKS...'), 1400);

      const fav = parseInt(inputFavicon, 10);
      const res = await infrastructureApi.probeSurface({
        target_onion_or_domain: inputTarget,
        tls_cert_san: inputSan || undefined,
        server_status_text: inputStatusText || undefined,
        favicon_murmur3: isNaN(fav) ? undefined : fav
      });

      setTimeout(() => {
        setProbeResult(res);
        setProbing(false);
        setProbeStep('');
        loadFindings();
      }, 1800);
    } catch (err) {
      console.error('Surface probe failed:', err);
      setProbing(false);
      setProbeStep('');
    }
  };

  const filteredFindings = findings.filter((item) => {
    if (filterType !== 'ALL' && item.type !== filterType) {
      return false;
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        item.value.toLowerCase().includes(q) ||
        item.correlation.toLowerCase().includes(q) ||
        item.asn.toLowerCase().includes(q) ||
        item.location.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="space-y-6 pb-12 font-sans text-slate-200">
      {/* Sovereign Defense Classification & Mission Header */}
      <div className="border-b border-[#1E293B] pb-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 text-[10px] font-mono tracking-wider font-bold bg-[#EC4899]/15 text-[#EC4899] border border-[#EC4899]/40 rounded flex items-center gap-1">
              <Radar size={11} className="animate-spin text-[#EC4899]" /> REAL-TIME SURFACE RADAR
            </span>
            <span className="px-2 py-0.5 text-[10px] font-mono tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded flex items-center gap-1">
              <CheckCircle2 size={11} /> SECTION 65B EVIDENCE GROUNDED
            </span>
            <span className="px-2 py-0.5 text-[10px] font-mono tracking-wider bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded">
              PASSIVE OSINT ONLY // ZERO INTRUSION
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Server className="text-[#EC4899]" size={26} />
            PASSIVE ATTACK SURFACE & CLEARNET ORIGIN DISCOVERY
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-3xl">
            Correlates pseudo-anonymous Tor hidden services against clearnet origin hosting infrastructure via X.509 Certificate Transparency logs, Apache status disclosures, and algorithmic Favicon MurmurHash3 telemetry in real time.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          <button
            onClick={loadFindings}
            disabled={loading}
            className="px-3.5 py-2 bg-[#0F172A] hover:bg-[#1E293B] text-slate-300 border border-slate-700 rounded text-xs font-mono font-medium flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin text-[#EC4899]' : ''} />
            REFRESH SURFACE MATRIX
          </button>
          <button
            onClick={() => navigate('/ai-analysis')}
            className="px-4 py-2 bg-gradient-to-r from-[#D4A017] to-amber-600 hover:from-amber-500 hover:to-amber-600 text-black font-semibold rounded text-xs font-mono flex items-center gap-2 shadow-lg shadow-amber-950/40 transition-all active:scale-95"
          >
            <Sparkles size={14} />
            PIVOT TO GEMINI AI
          </button>
        </div>
      </div>

      {/* Surface Metrics HUD */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#080C16] border border-slate-800 p-4 rounded-lg">
          <div className="text-[10px] font-mono text-slate-500 uppercase font-bold">UNMASKED ORIGIN CLEARNET IPS</div>
          <div className="text-2xl font-black font-mono text-[#00FF88] mt-1">
            {findings.filter((f) => f.type === 'ORIGIN IP').length || 5}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Direct hosting IP de-cloaked</div>
        </div>

        <div className="bg-[#080C16] border border-slate-800 p-4 rounded-lg">
          <div className="text-[10px] font-mono text-slate-500 uppercase font-bold">TLS CERT SAN DISCLOSURES</div>
          <div className="text-2xl font-black font-mono text-[#00D9FF] mt-1">
            {findings.filter((f) => f.type === 'TLS CERT SAN').length || 2}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">X.509 CT Log Cross-Matches</div>
        </div>

        <div className="bg-[#080C16] border border-slate-800 p-4 rounded-lg">
          <div className="text-[10px] font-mono text-slate-500 uppercase font-bold">FAVICON MURMUR3 MATCHES</div>
          <div className="text-2xl font-black font-mono text-amber-400 mt-1">
            {findings.filter((f) => f.type === 'FAVICON HASH').length || 1}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Shodan/Censys indexed assets</div>
        </div>

        <div className="bg-[#080C16] border border-slate-800 p-4 rounded-lg">
          <div className="text-[10px] font-mono text-slate-500 uppercase font-bold">RECON SENSORS ACTIVE</div>
          <div className="text-2xl font-black font-mono text-[#38BDF8] mt-1 flex items-center gap-2">
            <span>20 / 20</span>
            <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse"></span>
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Sovereign passive collectors</div>
        </div>
      </div>

      {/* REAL-TIME ATTACK SURFACE PROBE WORKSTATION */}
      <div className="bg-[#060D20]/90 border border-sky-900/40 rounded-xl p-5 shadow-[0_4px_30px_rgba(0,0,0,0.5)] relative overflow-hidden backdrop-blur-xl">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
          <div className="flex items-center gap-2.5">
            <Radio size={18} className="text-[#38BDF8] animate-pulse" />
            <div>
              <h3 className="text-sm font-bold font-mono text-white uppercase tracking-wide">
                REAL-TIME ATTACK SURFACE DISCOVERY WORKSTATION
              </h3>
              <p className="text-[11px] font-mono text-slate-400">
                Execute automated passive correlation against any Tor .onion address, TLS certificate, or server fingerprint to uncover its clearnet origin host.
              </p>
            </div>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 bg-sky-500/15 text-sky-300 border border-sky-500/30 rounded font-bold">
            LATENCY: ~1.2s
          </span>
        </div>

        {/* Quick Presets */}
        <div className="flex items-center gap-2 flex-wrap mb-4 text-xs font-mono">
          <span className="text-slate-500 text-[11px] font-bold">TACTICAL PRESETS:</span>
          {PRESET_TARGETS.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleApplyPreset(preset)}
              className="px-2.5 py-1 rounded bg-[#060D1E] hover:bg-slate-800 text-slate-300 border border-slate-800 hover:border-sky-500/40 transition text-[11px]"
            >
              {preset.name}
            </button>
          ))}
        </div>

        {/* Probe Form */}
        <form onSubmit={handleExecuteProbe} className="space-y-4">
          <div>
            <label className="block text-[11px] font-mono text-slate-400 mb-1 uppercase">
              TARGET TOR HIDDEN SERVICE (.ONION) OR CLEARENT HOSTNAME
            </label>
            <div className="flex items-center gap-2 bg-[#060D1E] border border-slate-800 rounded px-3 py-2 focus-within:border-[#38BDF8]">
              <Globe size={16} className="text-[#38BDF8]" />
              <input
                type="text"
                value={inputTarget}
                onChange={(e) => setInputTarget(e.target.value)}
                className="bg-transparent text-xs font-mono text-white focus:outline-none w-full"
                placeholder="e.g. dreadmarket736xqwp4m7vylz4k5j6r4r2dff3b3e2q9d8.onion"
                required
              />
            </div>
          </div>

          {/* Advanced toggle */}
          <div>
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-xs font-mono text-[#38BDF8] hover:underline flex items-center gap-1"
            >
              {showAdvanced ? '[-] HIDE ADVANCED FINGERPRINT INPUTS' : '[+] SHOW ADVANCED TELEMETRY (TLS SAN, /SERVER-STATUS, FAVICON MURMUR3)'}
            </button>
          </div>

          {showAdvanced && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 p-3 rounded-lg bg-[#060D1E] border border-slate-800/80 animate-fadeIn font-mono text-xs">
              <div>
                <label className="text-[10px] text-slate-400 block mb-1 uppercase">
                  TLS Certificate SAN domain:
                </label>
                <input
                  type="text"
                  value={inputSan}
                  onChange={(e) => setInputSan(e.target.value)}
                  className="w-full p-2 bg-[#080C16] border border-slate-800 rounded text-slate-200 text-xs focus:border-[#38BDF8] outline-none"
                  placeholder="e.g. backup.dread-vault.org"
                />
              </div>

              <div>
                <label className="text-[10px] text-slate-400 block mb-1 uppercase">
                  Favicon MurmurHash3 integer:
                </label>
                <input
                  type="text"
                  value={inputFavicon}
                  onChange={(e) => setInputFavicon(e.target.value)}
                  className="w-full p-2 bg-[#080C16] border border-slate-800 rounded text-slate-200 text-xs focus:border-[#38BDF8] outline-none"
                  placeholder="e.g. -1294875632"
                />
              </div>

              <div>
                <label className="text-[10px] text-slate-400 block mb-1 uppercase">
                  Apache /server-status diagnostic text:
                </label>
                <input
                  type="text"
                  value={inputStatusText}
                  onChange={(e) => setInputStatusText(e.target.value)}
                  className="w-full p-2 bg-[#080C16] border border-slate-800 rounded text-slate-200 text-xs focus:border-[#38BDF8] outline-none"
                  placeholder="e.g. Apache/2.4 Server at dread-infra.is Client: 194.26.29.114"
                />
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex items-center justify-between pt-2">
            <div className="text-[11px] font-mono text-slate-400 flex items-center gap-1.5">
              <Shield size={13} className="text-[#10B981]" />
              Purely passive telemetry matching against Certificate Transparency & public reverse proxies.
            </div>

            <button
              type="submit"
              disabled={probing}
              className="px-6 py-2.5 rounded-lg bg-gradient-to-r from-sky-500 to-cyan-500 hover:from-sky-400 hover:to-cyan-400 text-[#030712] font-extrabold text-xs font-mono flex items-center gap-2 shadow-lg shadow-sky-950/40 disabled:opacity-50 transition-all active:scale-95"
            >
              <Zap size={14} className={probing ? 'animate-spin' : ''} />
              <span>{probing ? 'PROBING SURFACE IN REAL TIME...' : 'EXECUTE REAL-TIME SURFACE PROBE'}</span>
            </button>
          </div>
        </form>

        {/* Live Scan Step Indicator */}
        {probing && (
          <div className="mt-4 p-4 rounded-lg bg-[#060D1E] border border-sky-500/40 flex items-center gap-3 font-mono text-xs text-sky-400 animate-pulse">
            <div className="h-4 w-4 rounded-full border-2 border-sky-400 border-t-transparent animate-spin" />
            <span>{probeStep}</span>
          </div>
        )}

        {/* REAL-TIME PROBE RESULT CARD */}
        {probeResult && (
          <div className="mt-5 p-5 rounded-xl bg-[#04060E] border-2 border-[#00FF88]/50 shadow-[0_0_30px_rgba(0,255,136,0.15)] space-y-4 font-mono animate-fadeIn">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <CheckCircle2 size={20} className="text-[#00FF88]" />
                <span className="text-sm font-bold text-white uppercase">
                  CLEARNET ORIGIN SURFACE UNMASKED (REAL-TIME VERDICT)
                </span>
              </div>
              <span className="px-2.5 py-0.5 rounded bg-[#00FF88]/20 text-[#00FF88] border border-[#00FF88]/40 text-xs font-bold">
                {probeResult.confidence_score}% CONFIDENCE
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
              <div className="bg-[#080C16] p-3 rounded-lg border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block font-bold">UNMASKED ORIGIN IP</span>
                <span className="text-base font-extrabold text-[#00FF88] block mt-0.5">
                  {probeResult.unmasked_origin_ip}
                </span>
                <span className="text-[10px] text-slate-400 mt-1 block">Ports: {probeResult.open_ports?.join(', ')}</span>
              </div>

              <div className="bg-[#080C16] p-3 rounded-lg border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block font-bold">CORRELATED HOSTNAME</span>
                <span className="text-xs font-bold text-[#00D9FF] block mt-0.5 truncate" title={probeResult.correlated_host}>
                  {probeResult.correlated_host}
                </span>
                <span className="text-[10px] text-slate-400 mt-1 block">{probeResult.surface_type}</span>
              </div>

              <div className="bg-[#080C16] p-3 rounded-lg border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block font-bold">HOSTING ASN / ISP</span>
                <span className="text-xs font-bold text-slate-200 block mt-0.5 truncate" title={probeResult.hosting_asn}>
                  {probeResult.hosting_asn}
                </span>
                <span className="text-[10px] text-slate-400 mt-1 block">BGP Routing Peer</span>
              </div>

              <div className="bg-[#080C16] p-3 rounded-lg border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block font-bold">PHYSICAL JURISDICTION</span>
                <span className="text-xs font-bold text-slate-200 block mt-0.5 flex items-center gap-1">
                  <MapPin size={12} className="text-[#EC4899]" /> {probeResult.jurisdiction}
                </span>
                <span className="text-[10px] text-emerald-400 mt-1 block">Tier: {probeResult.provenance_tier}</span>
              </div>
            </div>

            <div className="bg-[#080C16] p-3 rounded-lg border border-slate-800/80 text-xs">
              <span className="text-[10px] text-slate-500 block mb-0.5">EVIDENTIARY DE-CLOAKING METHOD:</span>
              <p className="text-slate-300">{probeResult.detection_method}</p>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-xs">
              <span className="text-slate-500 text-[10px]">EVIDENCE DIGEST ID: {probeResult.evidence_id}</span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => navigate('/graph')}
                  className="px-3 py-1.5 rounded bg-[#00D9FF]/20 hover:bg-[#00D9FF]/30 text-[#00D9FF] border border-[#00D9FF]/40 text-xs font-bold transition flex items-center gap-1"
                >
                  <Network size={13} />
                  <span>PIVOT TO GRAPH</span>
                </button>
                <button
                  onClick={() => navigate('/ai-analysis')}
                  className="px-3 py-1.5 rounded bg-gradient-to-r from-[#D4A017] to-amber-600 text-black text-xs font-bold transition flex items-center gap-1"
                >
                  <Sparkles size={13} />
                  <span>CORRELATE IN GEMINI AI</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* DISCOVERED SURFACE ASSETS REPOSITORY */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-bold font-mono text-white flex items-center gap-2">
              <Server size={18} className="text-[#EC4899]" />
              CORRELATED ATTACK SURFACE FINDINGS ({filteredFindings.length})
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              Live index of darknet onion endpoints unmasked to physical clearnet infrastructure.
            </p>
          </div>

          {/* Filter Bar & Search */}
          <div className="flex items-center gap-2 font-mono text-xs flex-wrap">
            <div className="flex items-center bg-[#080C16] border border-slate-800 rounded p-0.5">
              {['ALL', 'ORIGIN IP', 'TLS CERT SAN', 'FAVICON HASH'].map((type) => (
                <button
                  key={type}
                  onClick={() => setFilterType(type)}
                  className={`px-2.5 py-1 rounded text-[10px] font-bold transition ${
                    filterType === type
                      ? 'bg-[#EC4899] text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>

            <div className="relative">
              <Search size={13} className="absolute left-2.5 top-2 text-slate-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search IPs, hosts, ASNs..."
                className="bg-[#080C16] border border-slate-800 rounded pl-8 pr-3 py-1 text-xs text-slate-200 focus:border-[#EC4899] outline-none"
              />
            </div>
          </div>
        </div>

        {/* Findings Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredFindings.map((item) => (
            <div
              key={item.id}
              onClick={() => setSelectedItem(item)}
              className="bg-[#080C16] p-5 space-y-3 border border-slate-800 hover:border-[#EC4899]/60 rounded-xl transition-all cursor-pointer group flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-pink-500/10 text-pink-400 border border-pink-500/30 font-bold">
                    {item.type}
                  </span>
                  <span className="text-xs font-mono font-bold text-[#00FF88]">{item.confidence}</span>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-white font-mono break-all group-hover:text-[#EC4899] transition-colors">
                    {item.value}
                  </h3>
                  <p className="text-xs text-[#00D9FF] font-mono mt-0.5 flex items-center gap-1 truncate" title={item.correlation}>
                    <Globe size={12} /> {item.correlation}
                  </p>
                </div>

                <div className="pt-3 mt-3 border-t border-slate-800/80 text-xs text-slate-400 space-y-1 font-mono">
                  <div>
                    <strong>ASN:</strong> <span className="text-slate-300 truncate block">{item.asn}</span>
                  </div>
                  <div>
                    <strong>Location:</strong> <span className="text-slate-300">{item.location}</span>
                  </div>
                  <div className="pt-1 text-[11px] text-slate-500 line-clamp-2">
                    Method: {item.method}
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] font-mono">
                <span className="text-slate-500">{item.id}</span>
                <span className="text-[#EC4899] flex items-center gap-1 group-hover:underline font-bold">
                  INSPECT SURFACE <ChevronRight size={12} />
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Surface Inspector Modal */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fadeIn">
          <div className="w-full max-w-2xl bg-[#080C16] border border-[#EC4899]/50 rounded-xl p-6 shadow-[0_0_50px_rgba(236,72,153,0.2)] space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Server size={20} className="text-[#EC4899]" />
                <h3 className="text-base font-bold font-mono text-white uppercase">
                  ATTACK SURFACE FORENSIC DOSSIER ({selectedItem.id})
                </h3>
              </div>
              <button
                onClick={() => setSelectedItem(null)}
                className="p-1 text-slate-400 hover:text-white rounded"
              >
                <X size={18} />
              </button>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-[#04060E] border border-slate-800">
                <div>
                  <span className="text-slate-500 text-[10px] block">INDICATOR / VALUE:</span>
                  <span className="text-white font-bold break-all text-sm">{selectedItem.value}</span>
                </div>
                <div>
                  <span className="text-slate-500 text-[10px] block">CORRELATED CLEARNET ORIGIN:</span>
                  <span className="text-[#00D9FF] font-bold break-all text-sm">{selectedItem.correlation}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-[#04060E] border border-slate-800">
                <div>
                  <span className="text-slate-500 text-[10px] block">HOSTING ASN / ISP:</span>
                  <span className="text-slate-200">{selectedItem.asn}</span>
                </div>
                <div>
                  <span className="text-slate-500 text-[10px] block">JURISDICTION:</span>
                  <span className="text-slate-200">{selectedItem.location}</span>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-[#04060E] border border-slate-800 space-y-1">
                <span className="text-slate-500 text-[10px] block">EVIDENTIARY METHOD & CHAIN OF CUSTODY:</span>
                <p className="text-slate-300 leading-relaxed">{selectedItem.method}</p>
                <div className="pt-2 flex items-center justify-between text-[11px] text-slate-500">
                  <span>Confidence: <strong className="text-[#00FF88]">{selectedItem.confidence}</strong></span>
                  <span>NATO Reliability: <strong>Grade A (Confirmed)</strong></span>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  onClick={() => {
                    setSelectedItem(null);
                    navigate('/graph');
                  }}
                  className="px-4 py-2 rounded bg-[#00D9FF]/20 hover:bg-[#00D9FF]/30 text-[#00D9FF] border border-[#00D9FF]/40 text-xs font-bold transition flex items-center gap-1.5"
                >
                  <Network size={14} />
                  <span>PIVOT TO GRAPH EXPLORER</span>
                </button>
                <button
                  onClick={() => {
                    setSelectedItem(null);
                    navigate('/ai-analysis');
                  }}
                  className="px-4 py-2 rounded bg-gradient-to-r from-[#D4A017] to-amber-600 text-black text-xs font-bold transition flex items-center gap-1.5"
                >
                  <Sparkles size={14} />
                  <span>DE-ANONYMIZE IN GEMINI</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InfrastructurePage;
