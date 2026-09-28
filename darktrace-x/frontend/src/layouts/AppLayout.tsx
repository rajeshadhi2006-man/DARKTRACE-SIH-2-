import React, { useState, useEffect, useRef } from 'react';
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  ShieldAlert,
  Database,
  Network,
  CalendarDays,
  Server,
  FileCheck,
  Scale,
  Search,
  FileText,
  History,
  Settings,
  LogOut,
  User as UserIcon,
  Activity,
  ChevronRight,
  Filter,
  FolderGit2,
  Target,
  BellRing,
  Radio,
  Clock,
  Cpu,
  Globe2,
  Globe,
  Lock,
  Layers,
  Terminal,
  Shield,
  Cloud,
  Sparkles
} from 'lucide-react';
import { healthApi, supabaseApi } from '../services/api';
import { TorBrowserDetectionModal, ModalTab } from '../components/TorBrowserDetectionModal';
import { SupabaseCloudModal } from '../components/SupabaseCloudModal';

interface NavGroup {
  groupTitle: string;
  items: {
    name: string;
    path: string;
    icon: any;
    badge?: string;
  }[];
}

const navGroups: NavGroup[] = [
  {
    groupTitle: 'NTRO MISSION COMMAND',
    items: [
      { name: 'COMMAND WAR ROOM', path: '/dashboard', icon: LayoutDashboard },
      { name: 'THREAT ACTOR PROFILES', path: '/actors', icon: ShieldAlert },
    ]
  },
  {
    groupTitle: 'SIH CORE CAPABILITIES',
    items: [
      { name: '1. TOR CLEARED ORIGIN', path: '/infrastructure', icon: Server, badge: 'CAP 1' },
      { name: '2. CROSS-MARKET GRAPH', path: '/graph', icon: Network, badge: 'CAP 2' },
      { name: '3. AI STYLOMETRY & DE-ANON', path: '/ai-analysis', icon: Sparkles, badge: 'CAP 3' },
      { name: 'TEMPORAL DIURNAL TIMELINE', path: '/timeline', icon: CalendarDays },
    ]
  },
  {
    groupTitle: 'FORENSICS & EXPORTS',
    items: [
      { name: 'EVIDENCE VAULT (SEC. 65B)', path: '/evidence', icon: FileCheck },
      { name: 'INTELLIGENCE DOSSIERS & EXPORT', path: '/reports', icon: FileText, badge: 'EXPORT' },
    ]
  }
];

export const AppLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [globalSearch, setGlobalSearch] = useState('');
  const [healthStatus, setHealthStatus] = useState<string>('ONLINE');
  const [wsLive, setWsLive] = useState<boolean>(false);
  const [liveTicker, setLiveTicker] = useState<string | null>(null);
  const [utcTime, setUtcTime] = useState<string>('');
  const [showTorModal, setShowTorModal] = useState<boolean>(false);
  const [torModalTab, setTorModalTab] = useState<ModalTab>('LOCAL_DETECTION');
  const [showSupabaseModal, setShowSupabaseModal] = useState<boolean>(false);
  const [supabaseOnline, setSupabaseOnline] = useState<boolean>(true);
  const [supabaseLatency, setSupabaseLatency] = useState<number>(240);
  
  const storedUser = localStorage.getItem('darktrace_user');
  const user = storedUser ? JSON.parse(storedUser) : { username: 'investigator', role: 'ANALYST', full_name: 'Lead CTI Investigator' };

  // Supabase Heartbeat
  useEffect(() => {
    const checkSb = () => {
      supabaseApi.getStatus()
        .then((res: any) => {
          setSupabaseOnline(res.connected || res.status === 'HEALTHY');
          if (res.latency_ms) setSupabaseLatency(Math.round(res.latency_ms));
        })
        .catch(() => setSupabaseOnline(false));
    };
    checkSb();
    const sbInterval = setInterval(checkSb, 15000);
    return () => clearInterval(sbInterval);
  }, []);

  // Live UTC Clock
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setUtcTime(now.toUTCString().slice(17, 25) + ' UTC');
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    healthApi.check()
      .then(res => setHealthStatus(res.status))
      .catch(() => setHealthStatus('DEGRADED'));

    // Global Real-time WebSocket connection for topbar telemetry
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = (window.location.port === '3000' || window.location.port === '5173')
      ? `${window.location.hostname}:8000`
      : window.location.host;
    const wsUrl = `${protocol}//${host}/api/ws/telemetry`;

    let ws: WebSocket | null = null;
    let reconnectTimer: any = null;

    const connect = () => {
      try {
        ws = new WebSocket(wsUrl);
        ws.onopen = () => setWsLive(true);
        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);
            if (msg.type === 'NEW_DARKNET_INTERCEPT') {
              setLiveTicker(`[INTERCEPT] ${msg.author} @ ${msg.source}`);
              setTimeout(() => setLiveTicker(null), 4000);
            }
          } catch (e) {}
        };
        ws.onclose = () => {
          setWsLive(false);
          reconnectTimer = setTimeout(connect, 3000);
        };
        ws.onerror = () => setWsLive(false);
      } catch (e) {
        setWsLive(false);
      }
    };

    connect();

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (ws) ws.close();
    };
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (globalSearch.trim()) {
      navigate(`/search?q=${encodeURIComponent(globalSearch.trim())}`);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('darktrace_token');
    localStorage.removeItem('darktrace_user');
    navigate('/login');
  };

const AshokChakra: React.FC<{ size?: number; className?: string }> = ({ size = 22, className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    <circle cx="50" cy="50" r="46" stroke="#E2B857" strokeWidth="4" />
    <circle cx="50" cy="50" r="10" fill="#E2B857" />
    {Array.from({ length: 24 }).map((_, i) => (
      <line
        key={i}
        x1="50"
        y1="50"
        x2={50 + 44 * Math.cos((i * 15 * Math.PI) / 180)}
        y2={50 + 44 * Math.sin((i * 15 * Math.PI) / 180)}
        stroke="#E2B857"
        strokeWidth="2.5"
      />
    ))}
  </svg>
);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#080E1E] text-[#F1F5F9] font-sans selection:bg-[#38BDF8] selection:text-[#080E1E]">

      {/* ── Precision Sovereign Tiranga Accent Ribbon ── */}
      <div className="tiranga-ribbon flex-shrink-0 z-50" />

      {/* Main layout below ribbon */}
      <div className="flex flex-1 min-h-0 overflow-hidden">

        {/* ══════════════════════════════════════════════════════
            GOVERNMENT / MNC FUSION SIDEBAR
            ══════════════════════════════════════════════════════ */}
        <aside className="w-72 flex-shrink-0 flex flex-col border-r border-sky-500/15 bg-[#0A1329]/96 backdrop-blur-xl relative z-20">

          {/* ── Sidebar Cool Top Accent ── */}
          <div className="h-[2px] w-full bg-gradient-to-r from-transparent via-[#38BDF8]/60 to-transparent" />

          {/* ── Ministry / Brand Banner ── */}
          <div className="px-4 pt-4 pb-3 border-b border-sky-500/15 bg-[#0D1836]/75 relative overflow-hidden">
            {/* Subtle cyan radial glow behind brand */}
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_50%_0%,rgba(56,189,248,0.10),transparent_70%)] pointer-events-none" />

            {/* Government Seal + Brand */}
            <div className="flex items-center gap-3 relative">
              {/* Sovereign Ashoka Seal Emblem */}
              <div className="relative flex-shrink-0">
                <div className="ashoka-seal-badge h-12 w-12 rounded-full flex items-center justify-center relative">
                  <AshokChakra size={26} className="chakra-spin" />
                  {/* Live indicator */}
                  <div className="absolute -top-0.5 -right-0.5 h-3 w-3 rounded-full bg-[#10B981] border-2 border-[#0A1329] animate-ping opacity-70" />
                  <div className="absolute -top-0.5 -right-0.5 h-3 w-3 rounded-full bg-[#10B981] border-2 border-[#0A1329]" />
                </div>
              </div>

              <div className="overflow-hidden">
                <div className="flex items-center gap-2">
                  <h1 className="text-[13px] font-black tracking-[0.18em] text-[#38BDF8] font-mono glow-text-cyan">
                    DARKTRACE-X
                  </h1>
                  <span className="text-[8px] px-1.5 py-0.5 rounded bg-sky-500/15 text-sky-300 font-mono font-bold border border-sky-500/30 tracking-widest">
                    v2.4
                  </span>
                </div>
                <p className="text-[9px] text-slate-200 uppercase tracking-[0.18em] font-mono mt-0.5 font-bold">
                  NTRO CYBER RECON // NTRO-CTOC
                </p>
                <p className="text-[8px] text-[#E2B857] uppercase tracking-[0.12em] font-mono font-semibold">
                  राष्ट्रीय तकनीकी अनुसंधान संगठन • NTRO • SIH 2026
                </p>
              </div>
            </div>

            {/* Classification Clearance Badge */}
            <div className="mt-3 px-2.5 py-1.5 rounded-lg bg-[#0E1B3A] border border-sky-500/25 flex items-center justify-between text-[10px] font-mono shadow-sm">
              <div className="flex items-center gap-1.5 text-slate-300">
                <Lock size={10} className="text-[#38BDF8]" />
                <span>CLEARANCE: <strong className="text-white font-bold">TS // SCI // NTRO-CYBER-OPS</strong></span>
              </div>
              <span className="gov-status-pill">TLP:AMBER</span>
            </div>
          </div>

          {/* ── Navigation with Defense Grouping ── */}
          <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-5">
            {navGroups.map((group, gIdx) => (
              <div key={gIdx} className={`space-y-1 ${gIdx > 0 ? 'border-t border-sky-900/30 pt-4' : ''}`}>
                <div className="px-2 pb-2 text-[9px] font-mono font-black tracking-[0.2em] flex items-center justify-between">
                  <span className="text-slate-400 uppercase">{group.groupTitle}</span>
                  <span className="text-sky-400/60 border border-sky-800/40 bg-sky-950/30 px-1.5 py-0.5 rounded text-[8px]">0{gIdx + 1}</span>
                </div>

                {group.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path || (item.path !== '/dashboard' && location.pathname.startsWith(item.path));
                  return (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      className={`flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-semibold tracking-wider transition-all duration-150 group relative ${
                        isActive
                          ? 'bg-gradient-to-r from-sky-500/20 to-sky-500/5 text-[#38BDF8] border border-sky-500/35 shadow-[0_0_15px_rgba(56,189,248,0.15)] font-bold'
                          : 'text-slate-300 hover:text-white hover:bg-slate-800/50 border border-transparent hover:border-sky-500/20'
                      }`}
                    >
                      {/* Left active indicator */}
                      {isActive && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-4 bg-[#00E5FF] rounded-r-full shadow-[0_0_10px_#00E5FF]" />}
                      <Icon size={15} className={`transition-colors flex-shrink-0 ${isActive ? 'text-[#00E5FF]' : 'text-slate-400 group-hover:text-sky-300'}`} />
                      <span className="flex-1 truncate font-mono">{item.name}</span>
                      {item.badge && (
                        <span className="text-[8px] font-mono px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-200 border border-sky-500/35 font-bold">
                          {item.badge}
                        </span>
                      )}
                      <ChevronRight size={12} className={`opacity-0 group-hover:opacity-60 transition-opacity ${isActive ? 'opacity-80 text-[#38BDF8]' : ''}`} />
                    </NavLink>
                  );
                })}
              </div>
            ))}
          </nav>

          {/* ── User Session Card ── */}
          <div className="border-t border-sky-500/15 bg-[#081024]/95">
            {/* Gov footer watermark line */}
            <div className="gov-footer-bar text-center py-1 px-3 tracking-[0.15em] text-[8px]">
              NTRO CYBER RECON • SEC. 65B IT ACT COMPLIANT • TOP SECRET
            </div>
            <div className="flex items-center justify-between px-3 py-2.5">
              <div className="flex items-center gap-2.5 overflow-hidden">
                <div className="h-8 w-8 rounded-lg gov-emblem flex items-center justify-center text-[#38BDF8] font-mono font-bold">
                  <UserIcon size={14} />
                </div>
                <div className="overflow-hidden">
                  <p className="text-xs font-bold truncate text-white font-mono">{user.full_name || user.username}</p>
                  <div className="flex items-center gap-1.5">
                    <span className="gov-status-pill">{user.role}</span>
                    <span className="text-[8px] text-slate-400 font-mono">JWT/ARGON2</span>
                  </div>
                </div>
              </div>
              <button
                onClick={handleLogout}
                title="Terminate Secure Session"
                className="p-1.5 text-slate-400 hover:text-[#F43F5E] transition-colors rounded-lg hover:bg-slate-800/60"
              >
                <LogOut size={15} />
              </button>
            </div>
          </div>
        </aside>

        {/* ══════════════════════════════════════════════════════
            MAIN CONTENT VIEWPORT
            ══════════════════════════════════════════════════════ */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">

          {/* ── Gov/MNC Defense Topbar ── */}
          <header className="gov-topbar h-[58px] flex-shrink-0 px-6 flex items-center justify-between gap-4 relative z-10 bg-[#0B1630]/95 border-b border-sky-500/15 backdrop-blur-xl">
            {/* Left: Ministry identifier + search */}
            <div className="flex items-center gap-4 flex-1 min-w-0">
              {/* Ministry/Agency Stamp with Tiranga badge */}
              <div className="hidden lg:flex items-center gap-2.5 flex-shrink-0">
                <div className="h-8 w-8 rounded-lg ashoka-seal-badge flex items-center justify-center">
                  <AshokChakra size={18} className="chakra-spin" />
                </div>
                <div className="text-[9px] font-mono leading-tight">
                  <div className="text-[#38BDF8] font-black tracking-widest flex items-center gap-1">
                    <span>NTRO // CYBER RECON</span>
                    <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]"></span>
                  </div>
                  <div className="text-slate-300 font-semibold tracking-wider">राष्ट्रीय तकनीकी अनुसंधान संगठन • NTRO SIH-2026</div>
                </div>
                <div className="h-5 w-px bg-sky-800/40 mx-1" />
              </div>

              {/* Global Search */}
              <form onSubmit={handleSearchSubmit} className="relative w-60 lg:w-72 xl:w-80 flex-shrink-0">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search IOCs, wallets, PGP, onion, actors..."
                  value={globalSearch}
                  onChange={(e) => setGlobalSearch(e.target.value)}
                  className="w-full pl-9 pr-14 py-1.5 bg-[#0E1A36] border border-sky-900/40 hover:border-sky-500/40 rounded-lg text-xs text-white placeholder-slate-400 focus:outline-none focus:border-[#00E5FF] focus:ring-1 focus:ring-[#00E5FF]/20 transition-all font-mono"
                />
                <div className="absolute right-3 top-1/2 -translate-y-1/2 text-[9px] font-mono text-slate-400 px-1 py-0.5 rounded bg-slate-800/80 border border-slate-700/50">
                  ⌘K
                </div>
              </form>
            </div>

            {/* Right: Streamlined, Calm Status Cluster */}
            <div className="flex items-center gap-2.5 flex-shrink-0">
              {/* Consolidated Telemetry Group */}
              <div className="hidden md:flex items-center bg-[#091328] border border-sky-900/40 rounded-lg p-1 text-[10px] font-mono divide-x divide-sky-900/40 shadow-inner">
                {/* UTC Clock */}
                <div className="flex items-center gap-1.5 px-2.5 text-slate-300">
                  <Clock size={11} className="text-[#38BDF8]" />
                  <span className="font-semibold">{utcTime || 'UTC--:--:--'}</span>
                </div>

                {/* Radar Stream Status */}
                <div className="flex items-center gap-1.5 px-2.5">
                  <span className={`h-2 w-2 rounded-full ${wsLive ? 'bg-[#10B981] animate-pulse shadow-[0_0_8px_#10B981]' : 'bg-amber-400'}`} />
                  <span className="font-bold text-slate-300">{wsLive ? 'RADAR: LIVE' : 'CONNECTING'}</span>
                </div>

                {/* DEFCON Level */}
                <div className="hidden lg:flex items-center gap-1 px-2.5 text-amber-300 font-bold">
                  <span className="h-1.5 w-1.5 rounded-full bg-amber-400" />
                  <span>DEFCON 2</span>
                </div>
              </div>

              {/* Supabase Cloud Connection Status */}
              <button
                onClick={() => setShowSupabaseModal(true)}
                title="Supabase Cloud Bridge: Project surihwgxgymlgdxyghqx"
                className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0E1A36] hover:bg-[#38BDF8]/15 border border-sky-500/30 hover:border-sky-400/60 text-[10px] font-mono transition text-slate-200 btn-3d"
              >
                <Cloud size={12} className="text-[#38BDF8]" />
                <span className="font-bold text-[#38BDF8]">SUPABASE</span>
                <span className={`h-1.5 w-1.5 rounded-full ${supabaseOnline ? 'bg-[#00E5FF] shadow-[0_0_6px_#00E5FF]' : 'bg-red-400'}`} />
              </button>

              {/* 80+ Browser Crime Pattern Intelligence Matrix Button */}
              <button
                onClick={() => {
                  setTorModalTab('BROWSER_TAXONOMY');
                  setShowTorModal(true);
                }}
                title="80+ Browser Cybercrime Attribution Matrix & OPSEC Taxonomy"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-rose-600/30 via-pink-600/20 to-purple-600/30 hover:from-rose-600/45 hover:to-purple-600/40 border border-rose-500/50 hover:border-rose-400 text-[10px] font-mono font-bold text-rose-200 hover:text-white transition shadow-[0_0_12px_rgba(244,63,94,0.25)] btn-3d"
              >
                <ShieldAlert size={12} className="text-rose-400" />
                <span className="hidden sm:inline">CRIME MATRIX</span>
                <span className="px-1.5 py-0.5 rounded bg-rose-500/30 text-rose-300 text-[9px] font-extrabold border border-rose-500/50">80+</span>
              </button>

              {/* Quick Tor/Chrome Forensic Probe Button */}
              <button
                onClick={() => {
                  setTorModalTab('LOCAL_DETECTION');
                  setShowTorModal(true);
                }}
                title="Network Forensic Probe: Tor / Chrome Detection"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-sky-600/30 to-cyan-600/20 hover:from-sky-600/40 hover:to-cyan-600/30 border border-sky-400/40 text-[10px] font-mono font-bold text-sky-200 hover:text-white transition shadow-sm btn-3d"
              >
                <Globe size={12} className="text-[#38BDF8]" />
                <span>NTRO PROBE</span>
              </button>

              {/* System Health */}
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#091328] border border-sky-900/40 text-[10px] font-mono">
                <span className={`h-1.5 w-1.5 rounded-full ${healthStatus === 'ONLINE' || healthStatus === 'HEALTHY' ? 'bg-[#10B981]' : 'bg-amber-400'} animate-pulse`} />
                <span className="text-slate-300 font-semibold">{healthStatus}</span>
              </div>
            </div>
          </header>

          {/* ── Page Content ── */}
          <main className="flex-1 overflow-y-auto p-5 bg-[#080E1E] cyber-grid relative">
            <Outlet />
          </main>
        </div>
      </div>

      {/* Tor & Chrome Browser Forensic Detection Modal */}
      <TorBrowserDetectionModal
        isOpen={showTorModal}
        initialTab={torModalTab}
        onClose={() => setShowTorModal(false)}
        onPivotToDeanon={() => {
          setShowTorModal(false);
          navigate('/dashboard');
        }}
      />

      {/* Supabase Cloud Realtime Telemetry Modal */}
      <SupabaseCloudModal
        isOpen={showSupabaseModal}
        onClose={() => setShowSupabaseModal(false)}
      />
    </div>
  );
};