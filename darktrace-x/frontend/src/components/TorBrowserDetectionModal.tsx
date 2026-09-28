import React, { useEffect, useState } from 'react';
import {
  Globe,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Cpu,
  Terminal,
  Activity,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Copy,
  Check,
  Search,
  Sparkles,
  ExternalLink,
  X,
  Flame,
  Zap,
  Radio,
  RefreshCw,
  FolderGit2,
  Coins,
  Server,
  Lock,
  Network,
  Wifi
} from 'lucide-react';
import { networkDetectionApi } from '../services/api';

interface TorStatusData {
  timestamp: string;
  tor_detected_overall: boolean;
  local_proxies: {
    tor_browser_bundle_socks: {
      port: number;
      service_name: string;
      active: boolean;
      socks5_verified: boolean;
      status: string;
    };
    tor_system_daemon_socks: {
      port: number;
      service_name: string;
      active: boolean;
      socks5_verified: boolean;
      status: string;
    };
    tor_http_privoxy: {
      port: number;
      service_name: string;
      active: boolean;
      status: string;
    };
  };
  egress_network: {
    queried_successfully: boolean;
    is_tor: boolean;
    ip: string;
    source: string;
  };
  instructions: string;
}

interface ClientAnalysisData {
  primary_browser: string;
  engine: string;
  is_chrome: boolean;
  is_tor_browser: boolean;
  detected_classifications: string[];
  chrome_fingerprint_signals: string[];
  tor_fingerprint_signals: string[];
  opsec_leak_score: number;
  opsec_tier: string;
  forensic_findings: {
    vector: string;
    severity: string;
    detail: string;
  }[];
  client_network: {
    client_ip: string;
    is_tor_exit_node: boolean;
    accept_language: string;
  };
}

interface TorBrowserDetectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onPivotToDeanon?: (targetHandle: string, indicators?: any) => void;
  initialTab?: ModalTab;
}

export type ModalTab = 'LOCAL_DETECTION' | 'LIVE_TOR_RELAYS' | 'LIVE_BTC_EXPLORER' | 'LIVE_SOCKET_PROBE' | 'ARTIFACT_CLASSIFIER' | 'BROWSER_TAXONOMY';

export const TorBrowserDetectionModal: React.FC<TorBrowserDetectionModalProps> = ({
  isOpen,
  onClose,
  onPivotToDeanon,
  initialTab
}) => {
  const [activeTab, setActiveTab] = useState<ModalTab>(initialTab || 'LOCAL_DETECTION');
  const [loading, setLoading] = useState<boolean>(true);
  const [torStatus, setTorStatus] = useState<TorStatusData | null>(null);
  const [clientAnalysis, setClientAnalysis] = useState<ClientAnalysisData | null>(null);
  const [webrtcIps, setWebrtcIps] = useState<string[]>([]);

  // Classifier state
  const [classifierUa, setClassifierUa] = useState<string>('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36');
  const [classifierIp, setClassifierIp] = useState<string>('185.220.101.42');
  const [classifierHeaders, setClassifierHeaders] = useState<string>('Sec-CH-UA: "Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"\nSec-CH-UA-Platform: "Windows"');
  const [classifying, setClassifying] = useState<boolean>(false);
  const [artifactResult, setArtifactResult] = useState<any | null>(null);

  // Live Tor Relays state
  const [liveRelays, setLiveRelays] = useState<any[]>([]);
  const [relaysLoading, setRelaysLoading] = useState<boolean>(false);
  const [relaysSource, setRelaysSource] = useState<string>('');

  // Live BTC Explorer state
  const [btcAddress, setBtcAddress] = useState<string>('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa');
  const [btcResult, setBtcResult] = useState<any | null>(null);
  const [btcLoading, setBtcLoading] = useState<boolean>(false);

  // Live Socket Probe state
  const [socketHost, setSocketHost] = useState<string>('185.220.101.42');
  const [socketPort, setSocketPort] = useState<number>(443);
  const [socketResult, setSocketResult] = useState<any | null>(null);
  const [socketLoading, setSocketLoading] = useState<boolean>(false);

  // Browser Crime Matrix state (80+ Browsers across 8 Categories)
  const [browserCatalog, setBrowserCatalog] = useState<any | null>(null);
  const [catalogLoading, setCatalogLoading] = useState<boolean>(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [catalogSearch, setCatalogSearch] = useState<string>('');
  const [selectedBrowserCard, setSelectedBrowserCard] = useState<any | null>(null);

  const fetchBrowserCatalog = async () => {
    setCatalogLoading(true);
    try {
      const res = await networkDetectionApi.getBrowserCatalog();
      setBrowserCatalog(res);
      if (res.complete_registry && res.complete_registry.length > 0) {
        setSelectedBrowserCard(res.complete_registry[0]);
      }
    } catch (err) {
      console.error('Failed to load browser catalog', err);
    } finally {
      setCatalogLoading(false);
    }
  };

  // Probes local WebRTC for IP candidate leaks
  const probeWebRTC = (): Promise<string[]> => {
    return new Promise((resolve) => {
      const ips: string[] = [];
      try {
        const RTCPC = window.RTCPeerConnection || (window as any).webkitRTCPeerConnection || (window as any).mozRTCPeerConnection;
        if (!RTCPC) {
          resolve([]);
          return;
        }
        const pc = new RTCPC({ iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] });
        pc.createDataChannel('');
        pc.onicecandidate = (event) => {
          if (!event || !event.candidate) {
            pc.close();
            resolve(Array.from(new Set(ips)));
            return;
          }
          const candidate = event.candidate.candidate;
          const match = candidate.match(/([0-9]{1,3}(\.[0-9]{1,3}){3})/);
          if (match && match[1] && !match[1].startsWith('0.0.0.0')) {
            ips.push(match[1]);
          }
        };
        pc.createOffer().then((offer) => pc.setLocalDescription(offer)).catch(() => resolve([]));
        setTimeout(() => {
          try { pc.close(); } catch (e) {}
          resolve(Array.from(new Set(ips)));
        }, 1200);
      } catch (e) {
        resolve([]);
      }
    });
  };

  // Canvas fingerprint hash generator
  const getCanvasHash = (): string => {
    try {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (!ctx) return 'NO_2D_CONTEXT';
      canvas.width = 200;
      canvas.height = 50;
      ctx.textBaseline = 'top';
      ctx.font = '14px Arial';
      ctx.fillStyle = '#00FF88';
      ctx.fillRect(10, 10, 60, 20);
      ctx.fillStyle = '#00D9FF';
      ctx.fillText('DarktraceX//TorDetect', 15, 15);
      const dataUrl = canvas.toDataURL();
      let hash = 0;
      for (let i = 0; i < dataUrl.length; i++) {
        hash = ((hash << 5) - hash) + dataUrl.charCodeAt(i);
        hash |= 0;
      }
      return '0x' + Math.abs(hash).toString(16);
    } catch (e) {
      return 'CANVAS_BLOCKED';
    }
  };

  // Perform forensic scan
  const runForensicScan = async () => {
    setLoading(true);
    try {
      const status = await networkDetectionApi.getStatus();
      setTorStatus(status);

      const localIps = await probeWebRTC();
      setWebrtcIps(localIps);

      const canvasHash = getCanvasHash();
      const brands = (navigator as any).userAgentData?.brands || [];
      const hasUaData = Boolean((navigator as any).userAgentData);
      const hasWindowChrome = Boolean((window as any).chrome);

      let webglVendor = 'Unknown';
      let webglRenderer = 'Unknown';
      try {
        const glCanvas = document.createElement('canvas');
        const gl = glCanvas.getContext('webgl') || glCanvas.getContext('experimental-webgl');
        if (gl) {
          const debugInfo = (gl as any).getExtension('WEBGL_debug_renderer_info');
          if (debugInfo) {
            webglVendor = (gl as any).getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) || 'Unknown';
            webglRenderer = (gl as any).getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) || 'Unknown';
          }
        }
      } catch (e) {}

      const clientAnalysisRes = await networkDetectionApi.analyzeClient({
        user_agent: navigator.userAgent,
        platform: navigator.platform,
        vendor: navigator.vendor,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        timezone_offset: new Date().getTimezoneOffset(),
        screen_width: window.screen.width,
        screen_height: window.screen.height,
        inner_width: window.innerWidth,
        inner_height: window.innerHeight,
        has_window_chrome: hasWindowChrome,
        has_user_agent_data: hasUaData,
        brands: brands,
        webrtc_detected: localIps.length > 0,
        webrtc_local_ips: localIps,
        canvas_hash: canvasHash,
        webgl_vendor: webglVendor,
        webgl_renderer: webglRenderer
      });

      setClientAnalysis(clientAnalysisRes);
    } catch (err) {
      console.error('Forensic scan error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchLiveTorRelays = async () => {
    setRelaysLoading(true);
    try {
      const res = await networkDetectionApi.getLiveTorRelays(12);
      setLiveRelays(res.relays || []);
      setRelaysSource(res.source || 'Tor Project Onionoo Directory');
    } catch (err) {
      console.error(err);
    } finally {
      setRelaysLoading(false);
    }
  };

  const handleLookupBtc = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!btcAddress.trim()) return;
    setBtcLoading(true);
    try {
      const res = await networkDetectionApi.lookupLiveBtcWallet(btcAddress.trim());
      setBtcResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setBtcLoading(false);
    }
  };

  const handleRunSocketProbe = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!socketHost.trim()) return;
    setSocketLoading(true);
    try {
      const res = await networkDetectionApi.liveSocketProbe(socketHost.trim(), socketPort);
      setSocketResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setSocketLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      if (initialTab) {
        setActiveTab(initialTab);
      }
      runForensicScan();
      if ((initialTab === 'LIVE_TOR_RELAYS' || activeTab === 'LIVE_TOR_RELAYS') && liveRelays.length === 0) {
        fetchLiveTorRelays();
      }
      if ((initialTab === 'LIVE_BTC_EXPLORER' || activeTab === 'LIVE_BTC_EXPLORER') && !btcResult) {
        handleLookupBtc();
      }
      if ((initialTab === 'BROWSER_TAXONOMY' || activeTab === 'BROWSER_TAXONOMY') && !browserCatalog) {
        fetchBrowserCatalog();
      }
    }
  }, [isOpen, initialTab, activeTab]);

  const handleClassifyArtifact = async (e: React.FormEvent) => {
    e.preventDefault();
    setClassifying(true);
    try {
      const res = await networkDetectionApi.classifyArtifact({
        user_agent: classifierUa,
        ip_address: classifierIp,
        raw_headers: classifierHeaders,
        source_context: 'Dark Web Forum / Mirror Telemetry'
      });
      setArtifactResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setClassifying(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fadeIn">
      <div className="w-full max-w-5xl glass-panel p-6 border border-[#00D9FF]/40 shadow-[0_0_50px_rgba(0,217,255,0.2)] space-y-4 max-h-[92vh] overflow-y-auto">
        {/* Header Bar */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-[#00D9FF]/15 border border-[#00D9FF]/40 text-[#00D9FF]">
              <Globe size={22} className="animate-spin" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-extrabold font-mono text-slate-100 uppercase tracking-wide">
                  NTRO LIVE NETWORK RECONNAISSANCE & FORENSICS SUITE
                </h3>
                <span className="text-[10px] px-2 py-0.5 rounded bg-[#00FF88]/20 text-[#00FF88] border border-[#00FF88]/40 font-bold font-mono">
                  LIVE SOCKETS & REAL LEDGER
                </span>
              </div>
              <p className="text-[11px] font-mono text-slate-400">
                Official Tor Project Onionoo directory · Live Bitcoin mainnet ledger · Real active socket TLS handshakes · Client OPSEC classification
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
          >
            <X size={18} />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-2">
          <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
            <button
              onClick={() => setActiveTab('LOCAL_DETECTION')}
              className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 ${
                activeTab === 'LOCAL_DETECTION'
                  ? 'bg-[#00D9FF] text-black shadow-[0_0_12px_rgba(0,217,255,0.3)]'
                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              <Cpu size={13} />
              <span>THIS BROWSER</span>
            </button>
            <button
              onClick={() => { setActiveTab('LIVE_TOR_RELAYS'); fetchLiveTorRelays(); }}
              className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 ${
                activeTab === 'LIVE_TOR_RELAYS'
                  ? 'bg-[#00FF88] text-black shadow-[0_0_12px_rgba(0,255,136,0.3)]'
                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              <Wifi size={13} />
              <span>LIVE TOR NODES</span>
            </button>
            <button
              onClick={() => { setActiveTab('LIVE_BTC_EXPLORER'); if (!btcResult) handleLookupBtc(); }}
              className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 ${
                activeTab === 'LIVE_BTC_EXPLORER'
                  ? 'bg-amber-400 text-black shadow-[0_0_12px_rgba(251,191,36,0.3)]'
                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              <Coins size={13} />
              <span>BTC MAINNET</span>
            </button>
            <button
              onClick={() => { setActiveTab('LIVE_SOCKET_PROBE'); if (!socketResult) handleRunSocketProbe(); }}
              className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 ${
                activeTab === 'LIVE_SOCKET_PROBE'
                  ? 'bg-purple-400 text-black shadow-[0_0_12px_rgba(192,132,252,0.3)]'
                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              <Server size={13} />
              <span>LIVE TLS PROBE</span>
            </button>
            <button
              onClick={() => setActiveTab('ARTIFACT_CLASSIFIER')}
              className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 ${
                activeTab === 'ARTIFACT_CLASSIFIER'
                  ? 'bg-sky-400 text-black shadow-[0_0_12px_rgba(56,189,248,0.3)]'
                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              <Terminal size={13} />
              <span>OPSEC CLASSIFIER</span>
            </button>
            <button
              onClick={() => { setActiveTab('BROWSER_TAXONOMY'); if (!browserCatalog) fetchBrowserCatalog(); }}
              className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 ${
                activeTab === 'BROWSER_TAXONOMY'
                  ? 'bg-rose-500 text-white shadow-[0_0_12px_rgba(244,63,94,0.4)]'
                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              <ShieldAlert size={13} />
              <span>CRIME MATRIX (80+ BROWSERS)</span>
            </button>
          </div>

          <button
            onClick={runForensicScan}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1 rounded bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 text-xs font-mono disabled:opacity-50"
          >
            <RefreshCw size={12} className={loading ? 'animate-spin text-[#00D9FF]' : ''} />
            <span>{loading ? 'PROBING...' : 'RE-SCAN ENVIRONMENT'}</span>
          </button>
        </div>

        {/* TAB 1: LOCAL BROWSER & TOR PROXY INSPECTION */}
        {activeTab === 'LOCAL_DETECTION' && (
          <div className="space-y-4 font-mono text-xs">
            {loading ? (
              <div className="p-12 flex flex-col items-center justify-center gap-3">
                <RefreshCw size={28} className="animate-spin text-[#00D9FF]" />
                <span className="text-slate-400">PROBING SOCKS5 PORTS 9150/9050 & EXTRACTING BROWSER FINGERPRINTS...</span>
              </div>
            ) : (
              <>
                {/* Status Hero Tile */}
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-3 rounded-lg border ${
                      torStatus?.tor_detected_overall
                        ? 'bg-emerald-500/20 text-[#00FF88] border-emerald-500/40'
                        : 'bg-slate-900 text-slate-400 border-slate-700'
                    }`}>
                      {torStatus?.tor_detected_overall ? <ShieldCheck size={26} /> : <ShieldAlert size={26} />}
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-bold">TOR CONNECTION STATUS:</span>
                      <h4 className="text-sm font-black text-slate-100 mt-0.5">
                        {torStatus?.tor_detected_overall ? 'TOR PROXY / SERVICE IDENTIFIED' : 'NO ACTIVE TOR PROXY RUNNING'}
                      </h4>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        Egress Node: <span className="text-slate-200 font-bold">{torStatus?.egress_network?.ip}</span> · Source: <span className="text-[#00D9FF]">{torStatus?.egress_network?.source}</span>
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-slate-400 uppercase block">BROWSER ARCHITECTURE:</span>
                    <span className="text-xs font-bold text-[#00D9FF]">{clientAnalysis?.primary_browser || 'Detecting...'}</span>
                  </div>
                </div>

                {/* SOCKS5 Local Ports & Fingerprint Signals */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                    <h4 className="text-xs font-bold text-slate-200 flex items-center gap-2">
                      <Terminal size={14} className="text-[#00D9FF]" />
                      LOCAL PROXY LISTENERS (SOCKET HANDSHAKE)
                    </h4>
                    <div className="space-y-2 text-[11px]">
                      {torStatus?.local_proxies && Object.entries(torStatus.local_proxies).map(([k, p]: [string, any]) => (
                        <div key={k} className="p-2.5 rounded bg-slate-900 border border-slate-800 flex items-center justify-between">
                          <div>
                            <span className="font-bold text-slate-200 block">{p.service_name}</span>
                            <span className="text-slate-500 text-[10px]">Port: 127.0.0.1:{p.port}</span>
                          </div>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            p.active ? 'bg-emerald-500/20 text-[#00FF88] border border-emerald-500/40' : 'bg-slate-800 text-slate-500'
                          }`}>
                            {p.status}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                    <h4 className="text-xs font-bold text-slate-200 flex items-center gap-2">
                      <Cpu size={14} className="text-[#00FF88]" />
                      CLIENT HARDWARE FINGERPRINT & WEBRTC
                    </h4>
                    <div className="space-y-2 text-[11px]">
                      <div className="p-2 rounded bg-slate-900 flex items-center justify-between">
                        <span className="text-slate-400">WebRTC Candidates:</span>
                        <span className="text-slate-200 font-bold">{webrtcIps.length ? webrtcIps.join(', ') : 'None Leaked (Protected)'}</span>
                      </div>
                      <div className="p-2 rounded bg-slate-900 flex items-center justify-between">
                        <span className="text-slate-400">Screen Resolution:</span>
                        <span className="text-slate-200">{window.screen.width} × {window.screen.height}</span>
                      </div>
                      <div className="p-2 rounded bg-slate-900 flex items-center justify-between">
                        <span className="text-slate-400">Timezone Offset:</span>
                        <span className="text-slate-200">{Intl.DateTimeFormat().resolvedOptions().timeZone} ({new Date().getTimezoneOffset()} min)</span>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* TAB 2: LIVE REAL-TIME TOR NODES (ONIONOO API) */}
        {activeTab === 'LIVE_TOR_RELAYS' && (
          <div className="space-y-4 font-mono text-xs">
            <div className="p-3.5 rounded-xl bg-slate-950 border border-emerald-500/30 flex items-center justify-between gap-4">
              <div>
                <span className="text-[10px] text-emerald-400 font-bold tracking-widest uppercase block">
                  GENUINE TOR PROJECT TELEMETRY
                </span>
                <p className="text-xs text-slate-200 font-bold mt-0.5">
                  Live Tor Consensus Directory · Real Running Relays & Exit Nodes
                </p>
                <p className="text-[10px] text-slate-400 mt-0.5">
                  Direct API Feed: <span className="text-emerald-400">{relaysSource}</span>
                </p>
              </div>
              <button
                onClick={fetchLiveTorRelays}
                disabled={relaysLoading}
                className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs font-bold flex items-center gap-1.5 transition"
              >
                <RefreshCw size={12} className={relaysLoading ? 'animate-spin' : ''} />
                <span>REFRESH LIVE RELAYS</span>
              </button>
            </div>

            {relaysLoading ? (
              <div className="p-12 text-center text-slate-400 flex flex-col items-center justify-center gap-2">
                <RefreshCw size={24} className="animate-spin text-emerald-400" />
                <span>QUERYING ONIONOO.TORPROJECT.ORG IN REAL TIME...</span>
              </div>
            ) : (
              <div className="overflow-x-auto rounded-xl border border-slate-800">
                <table className="w-full text-left text-[11px] divide-y divide-slate-800">
                  <thead className="bg-slate-900 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="px-3 py-2">Relay Nickname</th>
                      <th className="px-3 py-2">OR Address (Real IP)</th>
                      <th className="px-3 py-2">Exit Flag</th>
                      <th className="px-3 py-2">ASN / Organization</th>
                      <th className="px-3 py-2">Bandwidth</th>
                      <th className="px-3 py-2">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 bg-slate-950">
                    {liveRelays.map((r, i) => (
                      <tr key={i} className="hover:bg-slate-900/40 transition">
                        <td className="px-3 py-2 font-bold text-slate-200 flex items-center gap-1.5">
                          <span className={`h-2 w-2 rounded-full ${r.is_exit_node ? 'bg-amber-400 animate-pulse' : 'bg-emerald-400'}`} />
                          <span>{r.nickname}</span>
                        </td>
                        <td className="px-3 py-2 text-slate-300 font-mono">
                          {r.or_addresses?.[0] || 'Unknown'}
                        </td>
                        <td className="px-3 py-2">
                          <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                            r.is_exit_node
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                              : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                          }`}>
                            {r.is_exit_node ? 'TOR EXIT NODE' : 'GUARD / RELAY'}
                          </span>
                        </td>
                        <td className="px-3 py-2 text-slate-400 truncate max-w-[180px]">
                          {r.as_number} ({r.as_name})
                        </td>
                        <td className="px-3 py-2 text-[#00D9FF]">
                          {r.bandwidth_rate_kbps ? `${r.bandwidth_rate_kbps} KB/s` : 'Active'}
                        </td>
                        <td className="px-3 py-2">
                          <button
                            onClick={() => {
                              const ip = (r.or_addresses?.[0] || '').split(':')[0];
                              setSocketHost(ip);
                              setActiveTab('LIVE_SOCKET_PROBE');
                            }}
                            className="px-2 py-0.5 rounded bg-slate-900 hover:bg-slate-800 border border-slate-700 text-[#00D9FF] text-[10px]"
                          >
                            Probe IP
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* TAB 3: LIVE BITCOIN MAINNET LEDGER LOOKUP */}
        {activeTab === 'LIVE_BTC_EXPLORER' && (
          <div className="space-y-4 font-mono text-xs">
            <div className="p-3.5 rounded-xl bg-slate-950 border border-amber-500/30">
              <span className="text-[10px] text-amber-400 font-bold tracking-widest uppercase block">
                LIVE BITCOIN BLOCKCHAIN EXPLORER
              </span>
              <p className="text-xs text-slate-200 font-bold mt-0.5">
                Real-Time Mainnet Ledger Query · Confirmed Balances & Mempool Verifications
              </p>
              <p className="text-[10px] text-slate-400 mt-0.5">
                Querying official public node API (<span className="text-amber-300">mempool.space</span>).
              </p>
            </div>

            <form onSubmit={handleLookupBtc} className="flex gap-2">
              <input
                type="text"
                placeholder="Enter BTC address (e.g. 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa or bc1q...)"
                value={btcAddress}
                onChange={(e) => setBtcAddress(e.target.value)}
                className="flex-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 outline-none focus:border-amber-400"
              />
              <button
                type="submit"
                disabled={btcLoading}
                className="px-5 py-2 rounded-lg bg-amber-400 hover:bg-amber-300 text-black font-bold flex items-center gap-1.5 transition disabled:opacity-50"
              >
                <Search size={13} />
                <span>{btcLoading ? 'QUERYING LEDGER...' : 'LOOKUP MAINNET'}</span>
              </button>
            </form>

            {btcResult && (
              <div className="p-4 rounded-xl bg-slate-950 border border-amber-500/40 space-y-3 animate-fadeIn">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase block">ADDRESS IDENTIFIED:</span>
                    <span className="text-sm font-bold text-slate-200 select-all font-mono">{btcResult.address}</span>
                  </div>
                  <span className="px-2.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold text-[10px]">
                    {btcResult.verified_live ? 'CONFIRMED ON MAINNET' : 'OFFLINE FALLBACK'}
                  </span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-[11px]">
                  <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Confirmed Balance (BTC):</span>
                    <span className="text-sm font-black text-amber-300">{btcResult.confirmed_balance_btc} BTC</span>
                  </div>
                  <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Total Satoshis:</span>
                    <span className="text-slate-200 font-bold">{Number(btcResult.confirmed_balance_satoshis).toLocaleString()} sats</span>
                  </div>
                  <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Funded TX Count:</span>
                    <span className="text-slate-200 font-bold">{btcResult.total_funded_tx_count} Transactions</span>
                  </div>
                  <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Unconfirmed Mempool:</span>
                    <span className="text-slate-200 font-bold">{btcResult.unconfirmed_tx_count} pending</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 4: LIVE ACTIVE TCP/TLS SOCKET PROBE */}
        {activeTab === 'LIVE_SOCKET_PROBE' && (
          <div className="space-y-4 font-mono text-xs">
            <div className="p-3.5 rounded-xl bg-slate-950 border border-purple-500/30">
              <span className="text-[10px] text-purple-400 font-bold tracking-widest uppercase block">
                ACTIVE TCP SOCKET & TLS X.509 HANDSHAKE ENGINE
              </span>
              <p className="text-xs text-slate-200 font-bold mt-0.5">
                Direct Host Port Prober · Real TLS Certificate Extraction · Origin Server Banners
              </p>
              <p className="text-[10px] text-slate-400 mt-0.5">
                Performs a genuine TCP socket connection from backend server and parses live response.
              </p>
            </div>

            <form onSubmit={handleRunSocketProbe} className="flex gap-2">
              <input
                type="text"
                placeholder="Target Host / IP (e.g. 185.220.101.42 or cloudflare.com)"
                value={socketHost}
                onChange={(e) => setSocketHost(e.target.value)}
                className="flex-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 outline-none focus:border-purple-400"
              />
              <input
                type="number"
                placeholder="Port"
                value={socketPort}
                onChange={(e) => setSocketPort(Number(e.target.value))}
                className="w-24 px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 outline-none focus:border-purple-400"
              />
              <button
                type="submit"
                disabled={socketLoading}
                className="px-5 py-2 rounded-lg bg-purple-400 hover:bg-purple-300 text-black font-bold flex items-center gap-1.5 transition disabled:opacity-50"
              >
                <Zap size={13} />
                <span>{socketLoading ? 'PROBING...' : 'CONNECT & EXTRACT'}</span>
              </button>
            </form>

            {socketResult && (
              <div className="p-4 rounded-xl bg-slate-950 border border-purple-500/40 space-y-3 animate-fadeIn">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <div className="flex items-center gap-2">
                    <span className={`h-2.5 w-2.5 rounded-full ${socketResult.port_open ? 'bg-emerald-400' : 'bg-red-400'}`} />
                    <span className="text-sm font-bold text-slate-200">{socketResult.target}</span>
                    <span className="text-slate-500 text-[10px]">({socketResult.latency_ms} ms RTT)</span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    socketResult.port_open
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                      : 'bg-red-500/20 text-red-300 border border-red-500/40'
                  }`}>
                    {socketResult.status}
                  </span>
                </div>

                {socketResult.tls_certificate && !socketResult.tls_certificate.error && (
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-2">
                    <span className="text-[10px] text-purple-400 font-bold block uppercase">EXTRACTED TLS X.509 CERTIFICATE:</span>
                    <div className="text-[11px] space-y-1">
                      <div><span className="text-slate-400">Subject:</span> <span className="text-slate-200">{JSON.stringify(socketResult.tls_certificate.subject)}</span></div>
                      <div><span className="text-slate-400">Issuer:</span> <span className="text-slate-200">{JSON.stringify(socketResult.tls_certificate.issuer)}</span></div>
                      <div><span className="text-slate-400">SHA-256 Fingerprint:</span> <span className="text-[#00D9FF] font-mono select-all">{socketResult.tls_certificate.sha256_fingerprint}</span></div>
                      <div><span className="text-slate-400">SAN Domains:</span> <span className="text-emerald-300 font-mono">{socketResult.tls_certificate.subject_alt_names?.join(', ') || 'None'}</span></div>
                    </div>
                  </div>
                )}

                {socketResult.http_banner && (
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1 text-[11px]">
                    <span className="text-[10px] text-[#00D9FF] font-bold block uppercase">HTTP SERVER BANNER:</span>
                    <div><span className="text-slate-400">Status:</span> <span className="text-slate-200">{socketResult.http_banner.status_line}</span></div>
                    <div><span className="text-slate-400">Software:</span> <span className="text-amber-300 font-bold">{socketResult.http_banner.server_software}</span></div>
                    <div><span className="text-slate-400">Header SHA-256:</span> <span className="text-slate-300 font-mono">{socketResult.http_banner.sha256_hash}</span></div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB 5: THREAT ACTOR ARTIFACT CLASSIFIER */}
        {activeTab === 'ARTIFACT_CLASSIFIER' && (
          <div className="space-y-4 font-mono text-xs">
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-[11px] text-slate-300">
              Paste HTTP headers, User-Agent strings, or egress IPs extracted from darknet leaks, forums, or staging mirrors.
              The AI classifier detects whether the operator preserved Tor anonymity or made a fatal OPSEC leak by using Google Chrome.
            </div>

            {/* Quick Presets */}
            <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
              <span className="text-slate-500 font-bold">PRESETS:</span>
              <button
                type="button"
                onClick={() => {
                  setClassifierUa('Mozilla/5.0 (Windows NT 10.0; rv:128.0) Gecko/20100101 Firefox/128.0');
                  setClassifierIp('185.220.101.42');
                  setClassifierHeaders('Accept-Language: en-US,en;q=0.5');
                }}
                className="px-2 py-0.5 rounded bg-slate-900 border border-emerald-500/40 text-[#00FF88] hover:bg-emerald-900/30 transition text-[10px]"
              >
                Tor Browser (Standard ESR)
              </button>
              <button
                type="button"
                onClick={() => {
                  setClassifierUa('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36');
                  setClassifierIp('195.123.246.77');
                  setClassifierHeaders('Sec-CH-UA: "Chromium";v="126", "Google Chrome";v="126"\nSec-CH-UA-Platform: "Windows"');
                }}
                className="px-2 py-0.5 rounded bg-slate-900 border border-blue-500/40 text-blue-400 hover:bg-blue-900/30 transition text-[10px]"
              >
                Chrome (Fatal OPSEC Leak)
              </button>
              <button
                type="button"
                onClick={() => {
                  setClassifierUa('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Zen/1.0.0-a.30');
                  setClassifierIp('185.220.101.42');
                  setClassifierHeaders('Accept-Language: en-US,en;q=0.5');
                }}
                className="px-2 py-0.5 rounded bg-slate-900 border border-purple-500/40 text-purple-300 hover:bg-purple-900/30 transition text-[10px]"
              >
                Zen Browser (Privacy Evasion)
              </button>
              <button
                type="button"
                onClick={() => {
                  setClassifierUa('Mozilla/5.0 (Linux; Android 14; 2201123G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36 Kiwi Chrome/124.0.6367.82');
                  setClassifierIp('195.123.246.77');
                  setClassifierHeaders('User-Agent: Kiwi Chrome/124.0\nSec-CH-UA-Mobile: ?1');
                }}
                className="px-2 py-0.5 rounded bg-slate-900 border border-amber-500/40 text-amber-300 hover:bg-amber-900/30 transition text-[10px]"
              >
                Kiwi Browser (Mobile Carding)
              </button>
              <button
                type="button"
                onClick={() => {
                  setClassifierUa('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15 Safari/Technology Preview');
                  setClassifierIp('91.240.118.89');
                  setClassifierHeaders('User-Agent: Safari/Technology Preview');
                }}
                className="px-2 py-0.5 rounded bg-slate-900 border border-rose-500/40 text-rose-300 hover:bg-rose-900/30 transition text-[10px]"
              >
                Safari Tech Preview (WebKit 0-Day)
              </button>
              <button
                type="button"
                onClick={() => {
                  setClassifierUa('IBM WebExplorer /v1.2');
                  setClassifierIp('194.26.29.114');
                  setClassifierHeaders('User-Agent: IBM WebExplorer /v1.2');
                }}
                className="px-2 py-0.5 rounded bg-slate-900 border border-red-500/40 text-red-400 hover:bg-red-900/30 transition text-[10px]"
              >
                IBM WebExplorer (Mainframe Breach)
              </button>
              <button
                type="button"
                onClick={() => {
                  setClassifierUa('python-requests/2.31.0');
                  setClassifierIp('91.215.85.17');
                  setClassifierHeaders('User-Agent: python-requests/2.31.0\nAccept: */*');
                }}
                className="px-2 py-0.5 rounded bg-slate-900 border border-cyan-500/40 text-cyan-300 hover:bg-cyan-900/30 transition text-[10px]"
              >
                Automated Bot (Python Script)
              </button>
            </div>

            <form onSubmit={handleClassifyArtifact} className="space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] text-slate-400 mb-1 uppercase font-bold">
                    User-Agent String:
                  </label>
                  <input
                    type="text"
                    required
                    value={classifierUa}
                    onChange={(e) => setClassifierUa(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 outline-none focus:border-[#00FF88]"
                  />
                </div>
                <div>
                  <label className="block text-[10px] text-slate-400 mb-1 uppercase font-bold">
                    Egress IP Address:
                  </label>
                  <input
                    type="text"
                    required
                    value={classifierIp}
                    onChange={(e) => setClassifierIp(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 outline-none focus:border-[#00FF88]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[10px] text-slate-400 mb-1 uppercase font-bold">
                  Raw HTTP Request Headers:
                </label>
                <textarea
                  rows={2}
                  value={classifierHeaders}
                  onChange={(e) => setClassifierHeaders(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 outline-none focus:border-[#00FF88]"
                />
              </div>

              <div className="flex justify-end pt-1">
                <button
                  type="submit"
                  disabled={classifying}
                  className="px-6 py-2 rounded-lg bg-[#00FF88] hover:bg-[#00e67a] text-black font-extrabold flex items-center gap-1.5 shadow-[0_0_15px_rgba(0,255,136,0.3)] disabled:opacity-50"
                >
                  <Cpu size={14} />
                  <span>{classifying ? 'CLASSIFYING FORENSIC ARTIFACT...' : 'EXECUTE FORENSIC CLASSIFICATION'}</span>
                </button>
              </div>
            </form>

            {/* Artifact Result Card */}
            {artifactResult && (
              <div className="p-4 rounded-xl bg-slate-950 border border-[#00FF88]/40 space-y-3 animate-fadeIn">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-2">
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase block">IDENTIFIED BROWSER PROFILE:</span>
                    <h4 className="text-base font-extrabold text-slate-100 flex flex-wrap items-center gap-2">
                      <span className={artifactResult.opsec_failure_detected ? 'text-rose-400' : 'text-[#00FF88]'}>
                        {artifactResult.browser_name || artifactResult.classification}
                      </span>
                      {artifactResult.browser_category && (
                        <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-bold border border-slate-700">
                          {artifactResult.browser_category}
                        </span>
                      )}
                      {artifactResult.browser_engine && (
                        <span className="text-[10px] px-2 py-0.5 rounded bg-[#00D9FF]/20 text-[#00D9FF] font-bold border border-[#00D9FF]/40">
                          {artifactResult.browser_engine}
                        </span>
                      )}
                      <span className="text-slate-400 text-xs font-normal">
                        ({artifactResult.confidence_percentage}% Confidence)
                      </span>
                    </h4>
                  </div>
                  {artifactResult.risk_tier && (
                    <span className={`px-2.5 py-1 rounded text-[10px] font-bold border ${
                      artifactResult.risk_tier === 'CRITICAL_OPSEC_LEAK' ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse' :
                      artifactResult.risk_tier === 'DEV_MALWARE_AUTHOR_STAGING' ? 'bg-purple-500/20 text-purple-300 border-purple-500/40' :
                      artifactResult.risk_tier === 'ENTERPRISE_INSIDER_RISK' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
                      artifactResult.risk_tier === 'HIGH_ANONYMITY_EVASION' ? 'bg-emerald-500/20 text-[#00FF88] border-emerald-500/40' :
                      'bg-sky-500/20 text-sky-300 border-sky-500/40'
                    }`}>
                      {artifactResult.risk_tier.replace(/_/g, ' ')}
                    </span>
                  )}
                </div>

                {/* Behavioral Crime Pattern Summary */}
                {artifactResult.behavioral_summary && (
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-[11px] space-y-1">
                    <span className="text-[10px] text-amber-400 uppercase font-bold block">CRIME PATTERN BEHAVIOR:</span>
                    <p className="text-slate-200">{artifactResult.behavioral_summary}</p>
                  </div>
                )}

                {/* OPSEC Vulnerabilities & De-anonymization */}
                {artifactResult.opsec_vulnerabilities && (
                  <div className="p-3 rounded-lg bg-rose-950/20 border border-rose-500/30 text-[11px] space-y-1">
                    <span className="text-[10px] text-rose-400 uppercase font-bold block">FORENSIC OPSEC VULNERABILITIES:</span>
                    <p className="text-slate-300">{artifactResult.opsec_vulnerabilities}</p>
                  </div>
                )}

                {/* Forensic Signals */}
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">
                    CORROBORATING FORENSIC SIGNALS & DE-ANON VECTORS:
                  </span>
                  <ul className="space-y-1 text-[11px] text-slate-300">
                    {artifactResult.forensic_signals?.map((sig: string, idx: number) => (
                      <li key={idx} className="flex items-center gap-1.5">
                        <span className="h-1.5 w-1.5 rounded-full bg-[#00D9FF]" />
                        <span>{sig}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Typical Crime Contexts */}
                {artifactResult.typical_crime_contexts && artifactResult.typical_crime_contexts.length > 0 && (
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">
                      ASSOCIATED UNDERGROUND CRIME PATTERNS:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {artifactResult.typical_crime_contexts.map((ctx: string, i: number) => (
                        <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-300">
                          {ctx}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Evidence SHA-256 */}
                {artifactResult.evidence_sha256 && (
                  <div className="p-2.5 rounded bg-slate-900 border border-slate-800 flex items-center justify-between text-[11px]">
                    <span className="text-slate-500">SHA-256 EVIDENCE CHAIN:</span>
                    <span className="text-slate-300 font-mono select-all">{artifactResult.evidence_sha256}</span>
                  </div>
                )}

                {/* Recommendation */}
                <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px] text-slate-300">
                  <strong className="text-[#00D9FF]">INVESTIGATIVE RECOMMENDATION:</strong>{' '}
                  {artifactResult.recommendation}
                </div>

                {/* Pivot Actions */}
                {onPivotToDeanon && (
                  <div className="flex justify-end gap-2 pt-2 border-t border-slate-800">
                    <button
                      onClick={() => {
                        onClose();
                        onPivotToDeanon('Suspect_From_Artifact', {
                          ip: classifierIp,
                          ua: classifierUa
                        });
                      }}
                      className="px-4 py-1.5 rounded-lg bg-[#00D9FF]/20 hover:bg-[#00D9FF]/30 text-[#00D9FF] border border-[#00D9FF]/40 text-xs font-bold"
                    >
                      PIVOT TO DE-ANONYMIZATION STUDIO
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB 6: COMPLETE BROWSER CRIME PATTERN TAXONOMY (80+ BROWSERS) */}
        {activeTab === 'BROWSER_TAXONOMY' && (
          <div className="space-y-4 font-mono text-xs">
            {/* Header Hero Banner */}
            <div className="p-3.5 rounded-xl bg-slate-950 border border-rose-500/30 flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div>
                <span className="text-[10px] text-rose-400 font-bold tracking-widest uppercase block">
                  FORENSIC BROWSER CRIME PATTERN INTELLIGENCE MATRIX
                </span>
                <h4 className="text-sm font-extrabold text-slate-100 mt-0.5">
                  Comprehensive Registry: 8 Categories · 109 Indexed Browsers
                </h4>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Exhaustive behavioral profiling mapping client architectures to threat actor modus operandi, OPSEC risks, and legal de-anonymization attack surfaces.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 rounded-lg bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold text-xs">
                  {browserCatalog?.total_browsers_indexed || 109} BROWSERS INDEXED
                </span>
              </div>
            </div>

            {/* Category Selector Pills */}
            <div className="flex flex-wrap items-center gap-1.5 pb-1">
              <button
                onClick={() => setSelectedCategory('ALL')}
                className={`px-2.5 py-1 rounded-lg text-xs font-bold transition ${
                  selectedCategory === 'ALL'
                    ? 'bg-rose-500 text-white shadow-[0_0_10px_rgba(244,63,94,0.4)]'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                ALL BROWSERS ({browserCatalog?.total_browsers_indexed || 109})
              </button>
              {browserCatalog?.categories_list?.map((cat: string) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition ${
                    selectedCategory === cat
                      ? 'bg-[#00D9FF] text-black shadow-[0_0_10px_rgba(0,217,255,0.4)]'
                      : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
                  }`}
                >
                  {cat} ({browserCatalog?.catalog_by_category?.[cat]?.length || 0})
                </button>
              ))}
            </div>

            {/* Search Input Filter */}
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Search browsers by name, engine (Blink/Gecko/WebKit), risk tier, or cybercrime vector..."
                value={catalogSearch}
                onChange={(e) => setCatalogSearch(e.target.value)}
                className="flex-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 outline-none focus:border-rose-400 text-xs"
              />
              {catalogSearch && (
                <button
                  onClick={() => setCatalogSearch('')}
                  className="px-3 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-400 text-xs"
                >
                  Clear
                </button>
              )}
            </div>

            {/* Main Master-Detail Split Screen */}
            {catalogLoading ? (
              <div className="p-12 flex flex-col items-center justify-center gap-2 text-slate-400">
                <RefreshCw size={24} className="animate-spin text-rose-400" />
                <span>INDEXING 100+ BROWSER PROFILES & FORENSIC ATTRIBUTION MATRICES...</span>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
                {/* Left Column: Browser List */}
                <div className="lg:col-span-5 max-h-[460px] overflow-y-auto space-y-1.5 pr-1 border border-slate-800 rounded-xl p-2 bg-slate-950/60">
                  {(() => {
                    const list: any[] = selectedCategory === 'ALL'
                      ? (browserCatalog?.complete_registry || [])
                      : (browserCatalog?.catalog_by_category?.[selectedCategory] || []);

                    const filtered = list.filter((b: any) => {
                      if (!catalogSearch.trim()) return true;
                      const q = catalogSearch.toLowerCase();
                      return (
                        b.name.toLowerCase().includes(q) ||
                        b.engine?.toLowerCase().includes(q) ||
                        b.risk_tier?.toLowerCase().includes(q) ||
                        b.crime_behavior?.toLowerCase().includes(q) ||
                        b.typical_crime_contexts?.some((ctx: string) => ctx.toLowerCase().includes(q))
                      );
                    });

                    if (filtered.length === 0) {
                      return <div className="p-6 text-center text-slate-500">No browsers match query.</div>;
                    }

                    return filtered.map((b: any) => {
                      const isSelected = selectedBrowserCard?.id === b.id;
                      return (
                        <div
                          key={b.id}
                          onClick={() => setSelectedBrowserCard(b)}
                          className={`p-2.5 rounded-lg cursor-pointer transition border text-left flex items-center justify-between ${
                            isSelected
                              ? 'bg-slate-900 border-[#00D9FF] shadow-[0_0_12px_rgba(0,217,255,0.2)]'
                              : 'bg-slate-950/80 hover:bg-slate-900/60 border-slate-800/80'
                          }`}
                        >
                          <div>
                            <span className="font-extrabold text-slate-200 block text-xs">{b.name}</span>
                            <span className="text-[10px] text-slate-500 font-mono">{b.engine} · {b.primary_category || selectedCategory}</span>
                          </div>
                          <span className={`px-2 py-0.5 rounded text-[9px] font-bold border ${
                            b.risk_tier === 'CRITICAL_OPSEC_LEAK' ? 'bg-rose-500/20 text-rose-300 border-rose-500/40' :
                            b.risk_tier === 'DEV_MALWARE_AUTHOR_STAGING' ? 'bg-purple-500/20 text-purple-300 border-purple-500/40' :
                            b.risk_tier === 'ENTERPRISE_INSIDER_RISK' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
                            b.risk_tier === 'HIGH_ANONYMITY_EVASION' ? 'bg-emerald-500/20 text-[#00FF88] border-emerald-500/40' :
                            b.risk_tier === 'AUTOMATION_BOTNET' ? 'bg-orange-500/20 text-orange-300 border-orange-500/40' :
                            'bg-slate-800 text-slate-400 border-slate-700'
                          }`}>
                            {b.risk_tier.replace(/_/g, ' ')}
                          </span>
                        </div>
                      );
                    });
                  })()}
                </div>

                {/* Right Column: In-Depth Selected Browser Forensic Dossier */}
                <div className="lg:col-span-7">
                  {selectedBrowserCard ? (
                    <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                      {/* Title & Tier Header */}
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                        <div>
                          <span className="text-[10px] text-slate-500 uppercase block">FORENSIC ATTRIBUTION PROFILE:</span>
                          <h4 className="text-base font-black text-slate-100 flex items-center gap-2">
                            <span>{selectedBrowserCard.name}</span>
                            <span className="text-[10px] px-2 py-0.5 rounded bg-[#00D9FF]/20 text-[#00D9FF] font-bold border border-[#00D9FF]/40">
                              {selectedBrowserCard.engine}
                            </span>
                          </h4>
                          <span className="text-[11px] text-slate-400">
                            Category: <strong className="text-slate-300">{selectedBrowserCard.primary_category || selectedCategory}</strong>
                          </span>
                        </div>
                        <span className={`px-2.5 py-1 rounded text-[10px] font-bold border self-start sm:self-auto ${
                          selectedBrowserCard.risk_tier === 'CRITICAL_OPSEC_LEAK' ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse' :
                          selectedBrowserCard.risk_tier === 'DEV_MALWARE_AUTHOR_STAGING' ? 'bg-purple-500/20 text-purple-300 border-purple-500/40' :
                          selectedBrowserCard.risk_tier === 'ENTERPRISE_INSIDER_RISK' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
                          selectedBrowserCard.risk_tier === 'HIGH_ANONYMITY_EVASION' ? 'bg-emerald-500/20 text-[#00FF88] border-emerald-500/40' :
                          'bg-sky-500/20 text-sky-300 border-sky-500/40'
                        }`}>
                          {selectedBrowserCard.risk_tier.replace(/_/g, ' ')}
                        </span>
                      </div>

                      {/* Modus Operandi & Crime Behavior */}
                      <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
                        <span className="text-[10px] text-amber-400 uppercase font-bold block">
                          CYBERCRIME MODUS OPERANDI & BEHAVIORAL PATTERN:
                        </span>
                        <p className="text-slate-200 text-[11px] leading-relaxed">
                          {selectedBrowserCard.crime_behavior}
                        </p>
                      </div>

                      {/* OPSEC Vulnerabilities */}
                      <div className="p-3 rounded-lg bg-rose-950/20 border border-rose-500/30 space-y-1">
                        <span className="text-[10px] text-rose-400 uppercase font-bold block">
                          OPSEC VULNERABILITIES & EXPLOITABLE DISCLOSURES:
                        </span>
                        <p className="text-slate-300 text-[11px] leading-relaxed">
                          {selectedBrowserCard.opsec_vulnerabilities}
                        </p>
                      </div>

                      {/* Forensic De-Anonymization Vectors */}
                      <div className="space-y-1">
                        <span className="text-[10px] text-[#00D9FF] uppercase font-bold block">
                          LAW ENFORCEMENT & FORENSIC DE-ANONYMIZATION PIVOTS:
                        </span>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-[11px]">
                          {selectedBrowserCard.deanon_vectors?.map((vec: string, idx: number) => (
                            <div key={idx} className="p-2 rounded bg-slate-900 border border-slate-800 text-slate-300 flex items-center gap-1.5">
                              <span className="h-1.5 w-1.5 rounded-full bg-[#00FF88]" />
                              <span>{vec}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Typical Crime Contexts */}
                      {selectedBrowserCard.typical_crime_contexts && (
                        <div>
                          <span className="text-[10px] text-slate-500 uppercase font-bold block mb-1">
                            TYPICAL UNDERGROUND OFFENSES & CONTEXTS:
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {selectedBrowserCard.typical_crime_contexts.map((ctx: string, i: number) => (
                              <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                                {ctx}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Sample User-Agent with 1-Click Load into Classifier */}
                      <div className="p-2.5 rounded bg-slate-900 border border-slate-800 space-y-1.5">
                        <span className="text-[10px] text-slate-400 uppercase font-bold block">SAMPLE SIGNATURE:</span>
                        <code className="text-[10px] font-mono text-slate-300 block select-all break-all bg-black/40 p-1.5 rounded">
                          {selectedBrowserCard.sample_ua}
                        </code>
                        <div className="flex justify-end pt-1">
                          <button
                            type="button"
                            onClick={() => {
                              setClassifierUa(selectedBrowserCard.sample_ua);
                              setClassifierIp('185.220.101.42');
                              setActiveTab('ARTIFACT_CLASSIFIER');
                            }}
                            className="px-3 py-1 rounded bg-[#00FF88]/20 hover:bg-[#00FF88]/30 text-[#00FF88] border border-[#00FF88]/40 font-bold text-xs flex items-center gap-1 transition"
                          >
                            <Terminal size={12} />
                            <span>TEST IN OPSEC CLASSIFIER</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="p-12 border border-slate-800 rounded-xl bg-slate-950 text-center text-slate-500">
                      Select any browser on the left to view its forensic attribution dossier.
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
