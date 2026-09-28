import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  Shield,
  Key,
  Database,
  GitFork,
  Link,
  Server,
  AlertTriangle,
  FileCheck,
  TrendingUp,
  ExternalLink,
  Clock,
  Radio,
  Zap,
  Activity,
  CheckCircle2,
  Play,
  Pause,
  RotateCcw,
  CheckCheck,
  Sliders,
  Flame,
  BellRing,
  Timer,
  Trash2,
  RefreshCw,
  Terminal,
  Crosshair,
  Lock,
  Layers,
  ArrowUpRight,
  Volume2,
  VolumeX,
  Send,
  Copy,
  Check,
  SearchCode,
  Eye,
  X,
  Sparkles,
  Cpu,
  Pin,
  PinOff,
  Filter,
  Search,
  FolderGit2,
  Share2,
  Globe,
  FileSpreadsheet,
  Code2
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';
import { dashboardApi, api, realtimeApi, alertsApi, intelligenceApi, attributionApi, actorsApi } from '../services/api';
import { DashboardStats } from '../types';
import { TorBrowserDetectionModal } from '../components/TorBrowserDetectionModal';

interface LiveTelemetryEvent {
  type: string;
  event_title: string;
  source: string;
  author: string;
  timestamp: string;
  pinned?: boolean;
  data?: {
    record_id?: string;
    evidence_id?: string;
    extracted_indicators?: {
      btc_wallets?: string[];
      xmr_wallets?: string[];
      clearnet_ips?: string[];
      pgp_fingerprints?: string[];
      onion_services?: string[];
    };
    content_hash?: string;
  };
}

interface RealtimeStatus {
  is_running: boolean;
  interval_seconds: number;
  cycle_count: number;
  last_run: string | null;
  active_ws_subscribers: number;
}

const PRESET_TEMPLATES = [
  {
    title: 'Financial Breach & Monero Escrow',
    source: 'BreachForums v4',
    author: 'DarkSpecter_X',
    text: 'Exclusive database leak: Financial services portal in Southeast Asia breached. 1.8M KYC records. Escrow bids in XMR: 888tNkZrPN6JsEgekjMnABU4TBzc2Dt29EPAvkFxbTNsLTGnqFTv28RcyR44FKa6KN22gqEBCPr4FnElzqY2R44FKa6KN22. PGP Key: 8A7B6C5D4E3F2A1B0C9D8E7F6A5B4C3D2E1F0A9B. Jabber: darkspecter@xmpp.is'
  },
  {
    title: 'FUD Crypter & Tor Staging Mirror',
    source: 'Dread Underground',
    author: 'CipherGhost_007',
    text: 'FUD Crypter updated for Defender bypass. 0/72 Detections on DynCheck. Hidden service at http://cipherghost7x2u9p4q.onion. Clearnet staging mirror detected at IP 185.220.101.42. Payment BTC: bc1q8w7x6y5z4a3b2c1d0e9f8g7h6i5j4k3l2m1n0. Tox: 76A28E3490BCDF21984712093847120938471209384712093847120938471209'
  },
  {
    title: 'VPN Gateway 0-day Exploit Broker',
    source: 'Exploit.in Mirror',
    author: 'KernelPanik_0day',
    text: 'Priv8 RCE weaponized exploit targeting enterprise VPN gateway appliances (CVE-2026-9812). Full unauthenticated root interactive reverse shell. Staging server IP: 91.215.85.17. Price: $80,000 USDT.'
  }
];

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState<boolean>(false);
  const [liveEvents, setLiveEvents] = useState<LiveTelemetryEvent[]>([]);
  const [crawling, setCrawling] = useState<boolean>(false);
  const [crawlNotice, setCrawlNotice] = useState<string | null>(null);
  const [latestAlert, setLatestAlert] = useState<any | null>(null);
  const [countdown, setCountdown] = useState<number>(5);
  const [audioEnabled, setAudioEnabled] = useState<boolean>(false);
  const [selectedIntercept, setSelectedIntercept] = useState<LiveTelemetryEvent | null>(null);
  const [copiedHash, setCopiedHash] = useState<boolean>(false);

  // Live Threat Injection Console State
  const [showInjector, setShowInjector] = useState<boolean>(false);
  const [injectSource, setInjectSource] = useState<string>('BreachForums v4');
  const [injectAuthor, setInjectAuthor] = useState<string>('DarkSpecter_X');
  const [injectText, setInjectText] = useState<string>(PRESET_TEMPLATES[0].text);
  const [injecting, setInjecting] = useState<boolean>(false);

  // Real-Time Interactive De-Anonymization Studio State
  const [showDeanonStudio, setShowDeanonStudio] = useState<boolean>(false);
  const [deanonPersonaA, setDeanonPersonaA] = useState<string>('DarkSpecter_X');
  const [deanonPersonaB, setDeanonPersonaB] = useState<string>('darkspecter_dev');
  const [deanonWallets, setDeanonWallets] = useState<string>('888tNkZrPN6JsEgekjMnABU4TBzc2Dt29EPAvkFxbTNsLTGnqFTv28RcyR44FKa6KN22gqEBCPr4FnElzqY2R44FKa6KN22');
  const [deanonOnions, setDeanonOnions] = useState<string>('http://specter7x2u9p4q.onion');
  const [deanonPgp, setDeanonPgp] = useState<string>('8A7B6C5D4E3F2A1B0C9D8E7F6A5B4C3D2E1F0A9B');
  const [deanonIps, setDeanonIps] = useState<string>('185.220.101.42');
  const [deanonTextA, setDeanonTextA] = useState<string>('Exclusive leak available. PM on jabber darkspecter@xmpp.is for escrow details. No lowballers.');
  const [deanonTextB, setDeanonTextB] = useState<string>('Check my GitHub repo for recent kernel bypass. Contact darkspecter@xmpp.is if issues found.');
  const [deanonCorrelating, setDeanonCorrelating] = useState<boolean>(false);
  const [deanonResult, setDeanonResult] = useState<any | null>(null);
  const [autoSaveAssessment, setAutoSaveAssessment] = useState<boolean>(true);
  const [autoCreateActor, setAutoCreateActor] = useState<boolean>(false);

  // Interactive Weight Sliders
  const [weightStylometry, setWeightStylometry] = useState<number>(20);
  const [weightCrypto, setWeightCrypto] = useState<number>(20);
  const [weightInfra, setWeightInfra] = useState<number>(20);
  const [weightPgp, setWeightPgp] = useState<number>(15);
  const [weightTemporal, setWeightTemporal] = useState<number>(15);

  // Live Wire Stream Controls
  const [wirePaused, setWirePaused] = useState<boolean>(false);
  const [wireSearch, setWireSearch] = useState<string>('');
  const [wireFilter, setWireFilter] = useState<'ALL' | 'CRYPTO' | 'ONION' | 'IP' | 'PGP'>('ALL');
  const [showTorModal, setShowTorModal] = useState<boolean>(false);

  const [realtimeStatus, setRealtimeStatus] = useState<RealtimeStatus>({
    is_running: true,
    interval_seconds: 5.0,
    cycle_count: 0,
    last_run: null,
    active_ws_subscribers: 1
  });

  const wsRef = useRef<WebSocket | null>(null);

  // Synthesize tactical audio blips with Web Audio API
  const playTacticalSound = (type: 'beep' | 'alert' | 'pulse' = 'beep') => {
    if (!audioEnabled) return;
    try {
      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      
      if (type === 'beep') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.04, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.12);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.12);
      } else if (type === 'alert') {
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(520, audioCtx.currentTime);
        osc.frequency.setValueAtTime(740, audioCtx.currentTime + 0.08);
        gain.gain.setValueAtTime(0.06, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.25);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.25);
      }
    } catch (e) {}
  };

  const fetchStats = () => {
    dashboardApi.getStats()
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError('Failed to fetch real-time intelligence telemetry.');
        setLoading(false);
      });
  };

  const fetchRealtimeStatus = () => {
    realtimeApi.getStatus()
      .then((res) => {
        if (res) setRealtimeStatus(res);
      })
      .catch(() => {});
  };

  // Real-Time Countdown Timer that counts down to 0 every cycle
  useEffect(() => {
    if (!realtimeStatus.is_running) return;

    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          return Math.round(realtimeStatus.interval_seconds);
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [realtimeStatus.is_running, realtimeStatus.interval_seconds]);

  useEffect(() => {
    fetchStats();
    fetchRealtimeStatus();

    // Establish Resilient WebSocket Connection
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = (window.location.port === '3000' || window.location.port === '5173')
      ? `${window.location.hostname}:8000`
      : window.location.host;
    const wsUrl = `${protocol}//${host}/api/ws/telemetry`;
    
    let reconnectTimeout: any = null;

    const connectWs = () => {
      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          setWsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);
            
            // 1. LIVE DARKNET INTERCEPT
            if (msg.type === 'NEW_DARKNET_INTERCEPT') {
              playTacticalSound('beep');
              if (!wirePaused) {
                setLiveEvents((prev) => [msg, ...prev.slice(0, 15)]);
              }
              setRealtimeStatus((prev) => ({
                ...prev,
                cycle_count: prev.cycle_count + 1,
                last_run: msg.timestamp
              }));
              setCountdown(Math.round(realtimeStatus.interval_seconds));
              setStats((prev) => prev ? {
                ...prev,
                total_intelligence_records: prev.total_intelligence_records + 1,
                evidence_items: prev.evidence_items + 1
              } : prev);
            }

            // 2. LIVE KPI TELEMETRY UPDATE
            if (msg.type === 'KPI_TELEMETRY_UPDATE' && msg.metrics) {
              setStats((prev) => prev ? {
                ...prev,
                total_intelligence_records: msg.metrics.total_intelligence_records,
                evidence_items: msg.metrics.evidence_items,
                pending_reviews: msg.metrics.unresolved_alerts ?? prev.pending_reviews
              } : prev);
            }

            // 3. LIVE ALERT BROADCAST
            if (msg.type === 'NEW_ALERT' && msg.alert) {
              playTacticalSound('alert');
              setLatestAlert(msg.alert);
              setTimeout(() => setLatestAlert(null), 8000);
            }

            // 4. ATTRIBUTION CORRELATED BROADCAST
            if (msg.type === 'ATTRIBUTION_CORRELATED') {
              playTacticalSound('alert');
              fetchStats();
            }

          } catch (e) {
            console.error('Failed to parse telemetry packet:', e);
          }
        };

        ws.onclose = () => {
          setWsConnected(false);
          reconnectTimeout = setTimeout(connectWs, 3000);
        };

        ws.onerror = () => {
          setWsConnected(false);
        };
      } catch (err) {
        setWsConnected(false);
      }
    };

    connectWs();

    // Regular polling fallback every 4 seconds
    const statusInterval = setInterval(() => {
      fetchRealtimeStatus();
      fetchStats();
    }, 4000);

    return () => {
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (statusInterval) clearInterval(statusInterval);
      if (wsRef.current) wsRef.current.close();
    };
  }, [realtimeStatus.interval_seconds, audioEnabled, wirePaused]);

  const handleTriggerLiveCrawl = async () => {
    setCrawling(true);
    setCrawlNotice(null);
    try {
      const res = await realtimeApi.trigger();
      const d = res.intercept;
      playTacticalSound('beep');
      setCrawlNotice(`[INTERCEPT AT 0s] Intercepted ${d.source} packet from ${d.author}! SHA: ${d.content_hash?.slice(0, 14)}...`);
      setCountdown(Math.round(realtimeStatus.interval_seconds));
      setTimeout(() => setCrawlNotice(null), 5000);
      fetchStats();
      fetchRealtimeStatus();
    } catch (e) {
      console.error(e);
      setCrawlNotice('Live sensor sweep initiated.');
    } finally {
      setCrawling(false);
    }
  };

  const handleToggleDaemon = async () => {
    try {
      if (realtimeStatus.is_running) {
        await realtimeApi.stop();
        setRealtimeStatus((prev) => ({ ...prev, is_running: false }));
      } else {
        await realtimeApi.start();
        setRealtimeStatus((prev) => ({ ...prev, is_running: true }));
        setCountdown(Math.round(realtimeStatus.interval_seconds));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleChangeCadence = async (seconds: number) => {
    try {
      await realtimeApi.setConfig(seconds);
      setRealtimeStatus((prev) => ({ ...prev, interval_seconds: seconds }));
      setCountdown(seconds);
    } catch (err) {
      console.error(err);
    }
  };

  const handleResetToZero = async () => {
    try {
      await realtimeApi.reset();
      setLiveEvents([]);
      setRealtimeStatus((prev) => ({ ...prev, cycle_count: 0 }));
      setCountdown(Math.round(realtimeStatus.interval_seconds));
      setCrawlNotice('Cycle counter & telemetry stream reset to 0! Watch new intercepts start from 0 in real time.');
      setTimeout(() => setCrawlNotice(null), 5000);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAcknowledgeAll = async () => {
    try {
      await alertsApi.ackAll();
      setStats((prev) => prev ? { ...prev, pending_reviews: 0 } : prev);
      setCrawlNotice('All threat alerts acknowledged! Pending reviews count is now 0.');
      setTimeout(() => setCrawlNotice(null), 5000);
    } catch (err) {
      console.error(err);
    }
  };

  const handleClearAllToZero = async () => {
    try {
      await realtimeApi.clearAllToZero();
      setStats({
        total_actors: 0,
        total_personas: 0,
        total_handles: 0,
        total_intelligence_records: 0,
        total_relationships: 0,
        potential_persona_links: 0,
        infrastructure_relationships: 0,
        pending_reviews: 0,
        evidence_items: 0,
        source_distribution: {},
        confidence_distribution: {},
        activity_over_time: [],
        recent_findings: []
      });
      setLiveEvents([]);
      setRealtimeStatus((prev) => ({ ...prev, cycle_count: 0 }));
      setCountdown(Math.round(realtimeStatus.interval_seconds));
      setCrawlNotice('ALL VALUES SET TO 0! System is in zero-state. Real-time sensor is actively streaming data from 0.');
      setTimeout(() => setCrawlNotice(null), 6000);
    } catch (e) {
      console.error(e);
    }
  };

  const handleReseedDemoData = async () => {
    try {
      await realtimeApi.reseedDemoData();
      fetchStats();
      fetchRealtimeStatus();
      setCrawlNotice('Full 21 threat actor demo dataset restored successfully!');
      setTimeout(() => setCrawlNotice(null), 5000);
    } catch (e) {
      console.error(e);
    }
  };

  // Analyst Real-Time Threat Packet Injection
  const handleDispatchCustomPacket = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!injectText.trim()) return;
    setInjecting(true);
    try {
      const res = await intelligenceApi.inject({
        source_name: injectSource,
        author: injectAuthor,
        raw_text: injectText.trim()
      });
      playTacticalSound('alert');
      setCrawlNotice(`[ANALYST INJECTION EXECUTED] Ingested packet from ${res.author} on ${res.source}! SHA: ${res.content_hash.slice(0, 14)}...`);
      fetchStats();
      fetchRealtimeStatus();
      setShowInjector(false);
      setTimeout(() => setCrawlNotice(null), 6000);
    } catch (err) {
      console.error(err);
      setCrawlNotice('Failed to dispatch packet. Verify backend status.');
    } finally {
      setInjecting(false);
    }
  };

  // Real-Time Interactive De-Anonymization Handler
  const handleRunLiveDeanon = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setDeanonCorrelating(true);
    try {
      const wallets = deanonWallets.split(/[\n, ]+/).filter(Boolean);
      const onions = deanonOnions.split(/[\n, ]+/).filter(Boolean);
      const pgps = deanonPgp.split(/[\n, ]+/).filter(Boolean);
      const ips = deanonIps.split(/[\n, ]+/).filter(Boolean);

      const totalWeights = (weightStylometry + weightCrypto + weightInfra + weightPgp + weightTemporal) || 100;
      const customWeights = {
        stylometric_similarity: weightStylometry / totalWeights,
        behavior_similarity: weightCrypto / totalWeights,
        infrastructure_correlation: weightInfra / totalWeights,
        pgp_correlation: weightPgp / totalWeights,
        temporal_correlation: weightTemporal / totalWeights,
        identifier_match: 0.15,
        independent_corroboration: 0.05
      };

      const res = await attributionApi.correlateLive({
        persona_a: deanonPersonaA,
        persona_b: deanonPersonaB,
        crypto_wallets: wallets,
        onion_services: onions,
        pgp_fingerprints: pgps,
        clearnet_ips: ips,
        text_sample_a: deanonTextA,
        text_sample_b: deanonTextB,
        active_hours_a: [10, 11, 12, 13, 14, 15, 16, 17, 18],
        active_hours_b: [11, 12, 13, 14, 15, 16, 17],
        weights: customWeights,
        auto_save_as_assessment: autoSaveAssessment,
        auto_create_actor: autoCreateActor
      });

      setDeanonResult(res);
      playTacticalSound('alert');
      setCrawlNotice(`[REAL-TIME DE-ANONYMIZATION EXECUTED] Correlation Confidence: ${res.confidence_percentage}% (${res.confidence_rating})`);
      fetchStats();
      setTimeout(() => setCrawlNotice(null), 6000);
    } catch (err) {
      console.error(err);
      setCrawlNotice('De-anonymization analysis failed. Verify inputs.');
    } finally {
      setDeanonCorrelating(false);
    }
  };

  // Quick Pivot from Wire Intercept to De-anonymization Studio
  const handlePivotToDeanon = (intercept: LiveTelemetryEvent) => {
    setDeanonPersonaA(intercept.author);
    setDeanonPersonaB(`${intercept.author}_clearnet_candidate`);
    const ind = intercept.data?.extracted_indicators || {};
    setDeanonWallets([...(ind.btc_wallets || []), ...(ind.xmr_wallets || [])].join('\n'));
    setDeanonOnions((ind.onion_services || []).join('\n'));
    setDeanonPgp((ind.pgp_fingerprints || []).join('\n'));
    setDeanonIps((ind.clearnet_ips || []).join('\n'));
    setDeanonTextA(intercept.event_title);
    setDeanonResult(null);
    setSelectedIntercept(null);
    setShowDeanonStudio(true);
  };

  // Toggle Pin on Wire Intercept
  const handleTogglePin = (index: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setLiveEvents(prev => prev.map((ev, i) => i === index ? { ...ev, pinned: !ev.pinned } : ev));
  };

  const handleCopyHash = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2500);
  };

  if (loading) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <div className="text-center space-y-4 font-mono">
          <div className="relative h-14 w-14 mx-auto flex items-center justify-center">
            <div className="absolute inset-0 rounded-full border-2 border-[#00D9FF]/20 animate-ping" />
            <div className="h-10 w-10 animate-spin rounded-full border-2 border-[#00FF88] border-t-transparent" />
          </div>
          <div>
            <p className="text-xs text-slate-300 font-bold tracking-widest">CONNECTING TO G-CTOC THREAT REPOSITORY</p>
            <p className="text-[10px] text-slate-500 mt-1">INITIALIZING MULTI-SIGNAL TELEMETRY BUS...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="p-6 text-center text-sm text-[#FF4D6D] bg-red-950/20 border border-red-900 rounded-xl">
        {error || 'Unable to load dashboard metrics.'}
      </div>
    );
  }

  const kpiCards = [
    { label: 'TOTAL ACTORS', value: stats.total_actors, hex: '0x01', icon: Shield, color: '#10B981', sub: 'Indexed Threat Groups' },
    { label: 'TOTAL PERSONAS', value: stats.total_personas, hex: '0x02', icon: Users, color: '#38BDF8', sub: 'Tracked Identities' },
    { label: 'TOTAL HANDLES', value: stats.total_handles, hex: '0x03', icon: Key, color: '#818CF8', sub: 'Extracted Underground Aliases' },
    { label: 'INTEL RECORDS', value: stats.total_intelligence_records, hex: '0x04', icon: Database, color: '#00D9FF', sub: 'Continuous Sensor Stream' },
    { label: 'RELATIONSHIPS', value: stats.total_relationships, hex: '0x05', icon: GitFork, color: '#34D399', sub: 'Correlated Network Links' },
    { label: 'POTENTIAL LINKS', value: stats.potential_persona_links, hex: '0x06', icon: Link, color: '#F59E0B', sub: 'Arbitration Queue' },
    { label: 'INFRASTRUCTURE', value: stats.infrastructure_relationships, hex: '0x07', icon: Server, color: '#22D3EE', sub: 'Clearnet Origin Pivots' },
    {
      label: 'PENDING REVIEWS',
      value: stats.pending_reviews,
      hex: '0x08',
      icon: AlertTriangle,
      color: stats.pending_reviews === 0 ? '#10B981' : '#F43F5E',
      sub: stats.pending_reviews === 0 ? 'Zero Backlog ✓' : 'Analyst Action Needed'
    },
    { label: 'EVIDENCE ITEMS', value: stats.evidence_items, hex: '0x09', icon: FileCheck, color: '#60A5FA', sub: 'SHA-256 Chain of Custody' },
  ];

  const sourceData = Object.entries(stats.source_distribution).map(([name, count]) => ({
    name: name.replace(' Underground Community', '').replace(' Underground Forum', ''),
    count
  }));

  // Filtered live wire events
  const filteredEvents = liveEvents.filter(ev => {
    if (wireSearch.trim()) {
      const q = wireSearch.toLowerCase();
      const match = ev.author.toLowerCase().includes(q) ||
                    ev.source.toLowerCase().includes(q) ||
                    ev.event_title.toLowerCase().includes(q);
      if (!match) return false;
    }
    if (wireFilter === 'CRYPTO') {
      const ind = ev.data?.extracted_indicators;
      return (ind?.btc_wallets?.length || 0) > 0 || (ind?.xmr_wallets?.length || 0) > 0;
    }
    if (wireFilter === 'ONION') {
      return (ev.data?.extracted_indicators?.onion_services?.length || 0) > 0;
    }
    if (wireFilter === 'IP') {
      return (ev.data?.extracted_indicators?.clearnet_ips?.length || 0) > 0;
    }
    if (wireFilter === 'PGP') {
      return (ev.data?.extracted_indicators?.pgp_fingerprints?.length || 0) > 0;
    }
    return true;
  });

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">      {/* ═══════════════════════════════════════════════════════════
          SOVEREIGN WAR ROOM COMMAND CENTER — G-CTOC TACTICAL HQ
          ═══════════════════════════════════════════════════════════ */}
      <div className="card-3d relative overflow-hidden rounded-2xl border border-sky-500/25 bg-[#0E1A36]/90 backdrop-blur-2xl">
        {/* Subtle top edge highlight */}
        <div className="h-[2px] w-full bg-gradient-to-r from-transparent via-[#00E5FF]/70 to-transparent" />

        {/* Main Command Bar */}
        <div className="p-6">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5 relative z-10">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="h-2 w-2 rounded-full bg-[#10B981] animate-ping" />
                <span className="text-[10px] font-mono tracking-widest text-[#10B981] font-bold uppercase">
                  OPERATIONAL COMMAND // REAL-TIME SENSORS
                </span>
              </div>
              <h2 className="text-xl lg:text-2xl font-black text-white tracking-wide font-mono flex items-center gap-2.5">
                <span className="text-[#00E5FF] glow-text-cyan font-black whitespace-nowrap">DARKTRACE-X</span>
                <span className="text-slate-500 font-light">//</span>
                <span className="whitespace-nowrap">NTRO CYBER RECON COMMAND</span>
              </h2>
              <p className="text-xs text-slate-300 mt-1 font-mono">
                Continuous darknet telemetry · multi-signal identity equivalence · explainable threat actor de-anonymization
              </p>
              <div className="flex items-center gap-3 mt-2 text-[10px] font-mono text-slate-400">
                <span className="px-2.5 py-0.5 rounded-md bg-sky-500/15 text-sky-300 border border-sky-500/30 font-bold">CASE: NTRO-SIH-2026</span>
                <span className="text-slate-600">•</span>
                <span className="text-emerald-400 font-semibold tracking-wider">TS // NTRO-CYBER-OPS</span>
                <span className="text-slate-600">•</span>
                <span className="text-slate-400">NATIONAL TECHNICAL RESEARCH ORGANISATION</span>
              </div>
            </div>

            {/* Primary Investigation Actions Suite with 3D Depth */}
            <div className="flex items-center gap-2.5 flex-shrink-0 flex-wrap">
              {/* DE-ANONYMIZATION STUDIO */}
              <button
                onClick={() => setShowDeanonStudio(true)}
                className="flex items-center gap-2 bg-gradient-to-r from-emerald-600/30 to-sky-600/20 hover:from-emerald-600/40 hover:to-sky-600/30 text-emerald-300 border border-emerald-400/40 text-xs font-mono font-bold px-3.5 py-2 rounded-xl transition-all shadow-[0_4px_16px_rgba(16,185,129,0.2)] active:scale-95 btn-3d"
              >
                <Crosshair size={14} className="text-[#10B981]" />
                <span>DE-ANON STUDIO</span>
              </button>

              {/* TOR & CHROME DETECTION PROBE */}
              <button
                onClick={() => setShowTorModal(true)}
                className="flex items-center gap-2 bg-gradient-to-r from-sky-600/30 to-cyan-600/20 hover:from-sky-600/40 hover:to-cyan-600/30 text-sky-200 border border-sky-400/40 text-xs font-mono font-bold px-3.5 py-2 rounded-xl transition-all shadow-[0_4px_16px_rgba(56,189,248,0.2)] active:scale-95 btn-3d"
              >
                <Globe size={14} className="text-[#38BDF8]" />
                <span>TOR/CHROME PROBE</span>
              </button>

              {/* SIH MANDATE: ONE-CLICK EXPORT SUITE */}
              <div className="flex items-center bg-[#091328] border border-sky-500/30 rounded-xl p-0.5 shadow-sm">
                <button
                  onClick={() => actorsApi.exportCsv()}
                  title="Export complete NTRO threat actor dataset as CSV"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-emerald-300 hover:bg-emerald-500/15 text-xs font-mono font-bold transition btn-3d"
                >
                  <FileSpreadsheet size={13} className="text-emerald-400" />
                  <span>CSV</span>
                </button>
                <div className="h-4 w-px bg-sky-900/50" />
                <button
                  onClick={() => actorsApi.exportJson()}
                  title="Export complete NTRO threat actor schema as JSON"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sky-300 hover:bg-sky-500/15 text-xs font-mono font-bold transition btn-3d"
                >
                  <Code2 size={13} className="text-[#38BDF8]" />
                  <span>JSON</span>
                </button>
                <div className="h-4 w-px bg-sky-900/50" />
                <button
                  onClick={() => navigate('/reports')}
                  title="Navigate to Dossiers & Report generator"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-cyan-300 hover:bg-cyan-500/15 text-xs font-mono font-bold transition btn-3d"
                >
                  <FileCheck size={13} className="text-cyan-400" />
                  <span>DOSSIER</span>
                </button>
              </div>

              {/* LIVE PACKET INJECTOR */}
              <button
                onClick={() => setShowInjector(!showInjector)}
                className={`flex items-center gap-1.5 text-xs font-mono font-bold px-3 py-2 rounded-xl border transition-all active:scale-95 btn-3d ${
                  showInjector
                    ? 'bg-indigo-500/30 text-indigo-200 border-indigo-400 shadow-[0_4px_16px_rgba(99,102,241,0.3)]'
                    : 'bg-[#091328] hover:bg-indigo-950/40 text-indigo-300 border-indigo-500/35'
                }`}
              >
                <Terminal size={14} className="text-indigo-400" />
                <span>{showInjector ? 'CLOSE' : 'INJECTOR'}</span>
              </button>

              {/* Tactical Audio Mute/Unmute */}
              <button
                onClick={() => setAudioEnabled(!audioEnabled)}
                title={audioEnabled ? 'Mute tactical audio alerts' : 'Enable tactical audio blips on packet arrival'}
                className="p-2 rounded-xl border text-xs font-mono transition-all btn-3d bg-[#091328] text-slate-300 border-sky-900/40 hover:text-white"
              >
                {audioEnabled ? <Volume2 size={15} className="text-emerald-400" /> : <VolumeX size={15} className="text-slate-400" />}
              </button>
            </div>
          </div>
        </div>

        {/* Lower Tier: Calm Telemetry & Sensor Control Strip with 3D Depth */}
        <div className="border-t border-sky-500/15 bg-[#091328]/95 px-6 py-3 flex flex-wrap items-center justify-between gap-4 relative z-10 font-mono text-xs shadow-inner">
          {/* Left: Sensor Cadence & Ingestion Engine */}
          <div className="flex flex-wrap items-center gap-3">
            {/* Sweep Countdown Timer */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#0E1A36] border border-sky-500/30 text-slate-300 shadow-inner">
              <Timer size={13} className="text-[#00E5FF] animate-spin" />
              <span className="text-[10px] text-slate-400 font-semibold uppercase">SWEEP:</span>
              <span className={`font-black text-xs px-1.5 py-0.5 rounded transition-all ${
                countdown <= 1
                  ? 'bg-[#10B981] text-[#080E1E] font-black shadow-[0_0_10px_#10B981]'
                  : 'text-[#38BDF8]'
              }`}>
                0{countdown}s
              </span>
              <span className="text-[10px] text-slate-500">→ 0s</span>
            </div>

            {/* WebSocket Bus Status */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0E1A36] border border-sky-900/40">
              <span className={`h-2 w-2 rounded-full ${wsConnected ? 'bg-[#10B981] animate-pulse shadow-[0_0_8px_#10B981]' : 'bg-amber-400'}`} />
              <span className="text-slate-300 text-[11px] font-semibold">
                {wsConnected ? 'WSS: LIVE' : 'CONNECTING...'}
              </span>
            </div>

            {/* Daemon State Toggle */}
            <button
              onClick={handleToggleDaemon}
              title={realtimeStatus.is_running ? 'Pause ingestion daemon' : 'Resume ingestion daemon'}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-bold border transition-all btn-3d ${
                realtimeStatus.is_running
                  ? 'bg-emerald-500/15 text-emerald-300 border-emerald-400/35 hover:bg-emerald-500/25'
                  : 'bg-amber-500/15 text-amber-300 border-amber-400/35 hover:bg-amber-500/25'
              }`}
            >
              {realtimeStatus.is_running ? (
                <><Pause size={12} className="text-emerald-400" /><span>ACTIVE ({realtimeStatus.interval_seconds}s)</span></>
              ) : (
                <><Play size={12} className="text-amber-400" /><span>PAUSED</span></>
              )}
            </button>

            {/* Cadence Interval Selector */}
            <div className="flex items-center bg-[#0E1A36] border border-sky-900/40 rounded-lg p-0.5 text-[10px]">
              <span className="px-2 text-slate-500 uppercase text-[9px] font-semibold">CADENCE:</span>
              {[3, 5, 10].map((sec) => (
                <button
                  key={sec}
                  onClick={() => handleChangeCadence(sec)}
                  className={`px-2.5 py-0.5 rounded transition font-bold ${
                    realtimeStatus.interval_seconds === sec
                      ? 'bg-[#38BDF8] text-[#080E1E] shadow-sm'
                      : 'text-slate-300 hover:text-white'
                  }`}
                >
                  {sec}s
                </button>
              ))}
            </div>
          </div>

          {/* Right: Tactical Stream Operations Toolbar */}
          <div className="flex items-center gap-2">
            {/* RESTORE DEMO */}
            <button
              onClick={handleReseedDemoData}
              title="Restore full 21 threat actor demo dataset"
              className="flex items-center gap-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[11px] font-semibold px-3 py-1.5 rounded-lg transition-all btn-3d"
            >
              <RefreshCw size={12} className="text-emerald-400" />
              <span>RESTORE DEMO</span>
            </button>

            {/* ACK ALL ALERTS */}
            <button
              onClick={handleAcknowledgeAll}
              title="Acknowledge and clear active alerts"
              className="flex items-center gap-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[11px] font-semibold px-3 py-1.5 rounded-lg transition-all btn-3d"
            >
              <CheckCheck size={12} className="text-amber-400" />
              <span>ACK ALERTS</span>
            </button>

            {/* RESET STREAM */}
            <button
              onClick={handleResetToZero}
              title="Reset the live wire intercept stream buffer"
              className="flex items-center gap-1.5 bg-[#0E1A36] hover:bg-slate-800 text-slate-300 border border-sky-900/40 text-[11px] font-semibold px-3 py-1.5 rounded-lg transition-all btn-3d"
            >
              <RotateCcw size={12} />
              <span>RESET WIRE</span>
            </button>
          </div>
        </div>
      </div>


      {/* ANALYST REAL-TIME THREAT PACKET INJECTION WORKSTATION */}
      {showInjector && (
        <div className="glass-panel p-5 border border-purple-500/40 bg-purple-950/15 shadow-[0_0_30px_rgba(168,85,247,0.15)] animate-fadeIn">
          <div className="flex items-center justify-between border-b border-purple-500/30 pb-3 mb-4">
            <div className="flex items-center gap-2.5">
              <Terminal size={18} className="text-purple-400" />
              <div>
                <h3 className="text-sm font-bold font-mono text-purple-200 uppercase tracking-wide">
                  ANALYST REAL-TIME THREAT PACKET INJECTION WORKSTATION
                </h3>
                <p className="text-[11px] font-mono text-slate-400">
                  Transmit authorized intercepted payloads directly into the live ingestion and entity extraction pipeline.
                </p>
              </div>
            </div>
            <button
              onClick={() => setShowInjector(false)}
              className="p-1 rounded text-slate-400 hover:text-slate-200"
            >
              <X size={16} />
            </button>
          </div>

          <form onSubmit={handleDispatchCustomPacket} className="space-y-4">
            <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
              <Sparkles size={13} className="text-purple-400" />
              <span>QUICK TEMPLATES:</span>
              {PRESET_TEMPLATES.map((tpl, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setInjectSource(tpl.source);
                    setInjectAuthor(tpl.author);
                    setInjectText(tpl.text);
                  }}
                  className="px-2.5 py-1 rounded bg-slate-900 border border-purple-500/30 text-purple-300 hover:bg-purple-900/30 transition text-[11px]"
                >
                  {tpl.title}
                </button>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1 uppercase">
                  Target Darknet Source
                </label>
                <input
                  type="text"
                  value={injectSource}
                  onChange={(e) => setInjectSource(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950/80 border border-slate-700 rounded-lg text-xs font-mono text-slate-200 focus:border-purple-400 outline-none"
                  placeholder="e.g. BreachForums v4, Dread, Telegram"
                  required
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1 uppercase">
                  Suspect Author Handle / Persona
                </label>
                <input
                  type="text"
                  value={injectAuthor}
                  onChange={(e) => setInjectAuthor(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950/80 border border-slate-700 rounded-lg text-xs font-mono text-slate-200 focus:border-purple-400 outline-none"
                  placeholder="e.g. NightStalker_99"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-mono text-slate-400 mb-1 uppercase">
                Underground Message Body / Intercepted Payload (Contains Crypto Wallets, IPs, Onions, PGP)
              </label>
              <textarea
                rows={3}
                value={injectText}
                onChange={(e) => setInjectText(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950/80 border border-slate-700 rounded-lg text-xs font-mono text-slate-200 focus:border-purple-400 outline-none leading-relaxed"
                placeholder="Paste or write raw intercepted darknet message..."
                required
              />
            </div>

            <div className="flex items-center justify-between pt-2">
              <span className="text-[11px] font-mono text-slate-500">
                Indicators are parsed, SHA-256 hashed, logged to audit ledger, and broadcasted over WebSocket instantly.
              </span>
              <button
                type="submit"
                disabled={injecting}
                className="flex items-center gap-2 px-5 py-2 rounded-lg bg-gradient-to-r from-purple-500 to-indigo-500 text-white text-xs font-mono font-bold hover:opacity-95 shadow-[0_0_15px_rgba(168,85,247,0.3)] disabled:opacity-50"
              >
                <Send size={13} />
                <span>{injecting ? 'PARSING & DISPATCHING...' : 'TRANSMIT LIVE PACKET'}</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* REAL-TIME DE-ANONYMIZATION STUDIO MODAL */}
      {showDeanonStudio && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fadeIn">
          <div className="w-full max-w-4xl glass-panel p-6 border border-[#00FF88]/40 shadow-[0_0_50px_rgba(0,255,136,0.2)] space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2.5">
                <Crosshair size={20} className="text-[#00FF88]" />
                <div>
                  <h3 className="text-base font-bold font-mono text-slate-100 uppercase">
                    REAL-TIME THREAT ACTOR DE-ANONYMIZATION STUDIO
                  </h3>
                  <p className="text-[11px] font-mono text-slate-400">
                    Live multi-vector correlation across stylometry, infrastructure, PGP fingerprints, and blockchain graphs.
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowDeanonStudio(false)}
                className="p-1 text-slate-400 hover:text-slate-200 rounded"
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleRunLiveDeanon} className="space-y-4 font-mono text-xs">
              {/* Target Candidate Inputs */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[11px] text-[#00D9FF] font-bold block uppercase">
                    TARGET A: UNDERGROUND PERSONA / HANDLE
                  </label>
                  <input
                    type="text"
                    required
                    value={deanonPersonaA}
                    onChange={(e) => setDeanonPersonaA(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-200 outline-none focus:border-[#00D9FF]"
                    placeholder="e.g. DarkSpecter_X"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[11px] text-[#00FF88] font-bold block uppercase">
                    TARGET B: CLEARNET CANDIDATE / SUSPECT
                  </label>
                  <input
                    type="text"
                    required
                    value={deanonPersonaB}
                    onChange={(e) => setDeanonPersonaB(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-200 outline-none focus:border-[#00FF88]"
                    placeholder="e.g. darkspecter_dev"
                  />
                </div>
              </div>

              {/* Multi-Indicator Inputs */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-[10px] text-slate-400 block mb-1 uppercase">
                    CRYPTO WALLETS (BTC / XMR):
                  </label>
                  <textarea
                    rows={2}
                    value={deanonWallets}
                    onChange={(e) => setDeanonWallets(e.target.value)}
                    className="w-full p-2 bg-slate-900 border border-slate-800 rounded text-slate-300 text-[11px] outline-none focus:border-[#00D9FF]"
                    placeholder="One address per line or comma-separated..."
                  />
                </div>
                <div>
                  <label className="text-[10px] text-slate-400 block mb-1 uppercase">
                    ONION SERVICES & CLEARNET IPS:
                  </label>
                  <textarea
                    rows={2}
                    value={`${deanonOnions}\n${deanonIps}`}
                    onChange={(e) => {
                      const lines = e.target.value.split('\n');
                      setDeanonOnions(lines.filter(l => l.includes('.onion')).join('\n'));
                      setDeanonIps(lines.filter(l => !l.includes('.onion')).join('\n'));
                    }}
                    className="w-full p-2 bg-slate-900 border border-slate-800 rounded text-slate-300 text-[11px] outline-none focus:border-[#00D9FF]"
                    placeholder="e.g. http://specter.onion or 185.220.101.42"
                  />
                </div>
              </div>

              {/* Text Samples for Stylometric Analysis */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-[10px] text-slate-400 block mb-1 uppercase">
                    TARGET A COMMUNICATION SAMPLE:
                  </label>
                  <textarea
                    rows={2}
                    value={deanonTextA}
                    onChange={(e) => setDeanonTextA(e.target.value)}
                    className="w-full p-2 bg-slate-900 border border-slate-800 rounded text-slate-300 text-[11px] outline-none focus:border-[#00D9FF]"
                    placeholder="Paste forum post, ransom note, or chat sample..."
                  />
                </div>
                <div>
                  <label className="text-[10px] text-slate-400 block mb-1 uppercase">
                    TARGET B COMMUNICATION SAMPLE:
                  </label>
                  <textarea
                    rows={2}
                    value={deanonTextB}
                    onChange={(e) => setDeanonTextB(e.target.value)}
                    className="w-full p-2 bg-slate-900 border border-slate-800 rounded text-slate-300 text-[11px] outline-none focus:border-[#00FF88]"
                    placeholder="Paste GitHub commit msg, issue, or clearnet text..."
                  />
                </div>
              </div>

              {/* Interactive Evidentiary Weight Sliders */}
              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 space-y-2">
                <span className="text-[10px] font-bold text-slate-400 block uppercase">
                  ADJUST REAL-TIME EVIDENTIARY FACTOR WEIGHTS
                </span>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-[10px]">
                  <div>
                    <div className="flex justify-between text-slate-400 mb-0.5">
                      <span>Stylometry</span>
                      <strong className="text-[#00D9FF]">{weightStylometry}%</strong>
                    </div>
                    <input
                      type="range"
                      min={0}
                      max={50}
                      value={weightStylometry}
                      onChange={(e) => setWeightStylometry(Number(e.target.value))}
                      className="w-full accent-[#00D9FF]"
                    />
                  </div>
                  <div>
                    <div className="flex justify-between text-slate-400 mb-0.5">
                      <span>Crypto</span>
                      <strong className="text-[#10B981]">{weightCrypto}%</strong>
                    </div>
                    <input
                      type="range"
                      min={0}
                      max={50}
                      value={weightCrypto}
                      onChange={(e) => setWeightCrypto(Number(e.target.value))}
                      className="w-full accent-[#10B981]"
                    />
                  </div>
                  <div>
                    <div className="flex justify-between text-slate-400 mb-0.5">
                      <span>Network</span>
                      <strong className="text-[#EC4899]">{weightInfra}%</strong>
                    </div>
                    <input
                      type="range"
                      min={0}
                      max={50}
                      value={weightInfra}
                      onChange={(e) => setWeightInfra(Number(e.target.value))}
                      className="w-full accent-[#EC4899]"
                    />
                  </div>
                  <div>
                    <div className="flex justify-between text-slate-400 mb-0.5">
                      <span>PGP Key</span>
                      <strong className="text-[#FFB020]">{weightPgp}%</strong>
                    </div>
                    <input
                      type="range"
                      min={0}
                      max={50}
                      value={weightPgp}
                      onChange={(e) => setWeightPgp(Number(e.target.value))}
                      className="w-full accent-[#FFB020]"
                    />
                  </div>
                  <div>
                    <div className="flex justify-between text-slate-400 mb-0.5">
                      <span>Temporal</span>
                      <strong className="text-[#A855F7]">{weightTemporal}%</strong>
                    </div>
                    <input
                      type="range"
                      min={0}
                      max={50}
                      value={weightTemporal}
                      onChange={(e) => setWeightTemporal(Number(e.target.value))}
                      className="w-full accent-[#A855F7]"
                    />
                  </div>
                </div>
              </div>

              {/* Action Controls & Options */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-800">
                <div className="flex items-center gap-4 text-[11px] text-slate-400">
                  <label className="flex items-center gap-1.5 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={autoSaveAssessment}
                      onChange={(e) => setAutoSaveAssessment(e.target.checked)}
                      className="rounded accent-[#00FF88]"
                    />
                    <span>Commit Official Assessment to DB</span>
                  </label>
                  <label className="flex items-center gap-1.5 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={autoCreateActor}
                      onChange={(e) => setAutoCreateActor(e.target.checked)}
                      className="rounded accent-[#00D9FF]"
                    />
                    <span>Instantiate New Threat Actor Group</span>
                  </label>
                </div>

                <button
                  type="submit"
                  disabled={deanonCorrelating}
                  className="px-6 py-2.5 rounded-lg bg-[#00FF88] hover:bg-[#00e67a] text-black font-extrabold text-xs flex items-center gap-2 shadow-[0_0_20px_rgba(0,255,136,0.3)] disabled:opacity-50 transition-all active:scale-95"
                >
                  <Cpu size={15} />
                  <span>{deanonCorrelating ? 'CORRELATING MULTI-SIGNALS...' : 'EXECUTE REAL-TIME CORRELATION'}</span>
                </button>
              </div>
            </form>

            {/* Real-Time Correlation Output Verdict */}
            {deanonResult && (
              <div className="p-4 rounded-xl bg-slate-900/90 border border-[#00FF88]/40 space-y-3 font-mono text-xs animate-fadeIn mt-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase block">ATTRIBUTION DECISION VERDICT:</span>
                    <h4 className="text-base font-extrabold text-slate-100 flex items-center gap-2">
                      <span className="text-[#00FF88]">{deanonResult.confidence_rating}</span>
                      <span className="text-slate-400 font-normal">({deanonResult.confidence_percentage}% Confidence Score)</span>
                    </h4>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-1 rounded bg-[#00FF88]/20 text-[#00FF88] border border-[#00FF88]/40 font-bold text-[11px]">
                      {deanonResult.recommendation}
                    </span>
                  </div>
                </div>

                {/* Factor Breakdown Bars */}
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-bold block mb-2">
                    EVIDENTIARY VECTOR BREAKDOWN:
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                    {deanonResult.factor_breakdown?.map((fb: any, idx: number) => (
                      <div key={idx} className="p-2.5 rounded bg-slate-950 border border-slate-800 flex flex-col justify-between">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-slate-300 font-semibold text-[11px]">{fb.factor_label}</span>
                          <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${
                            fb.status === 'STRONG'
                              ? 'bg-emerald-500/20 text-[#00FF88]'
                              : fb.status === 'MODERATE'
                              ? 'bg-amber-500/20 text-amber-400'
                              : 'bg-slate-800 text-slate-500'
                          }`}>
                            {fb.status}
                          </span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-1">
                          <div
                            className="bg-[#00D9FF] h-full rounded-full transition-all"
                            style={{ width: `${Math.round(fb.raw_score * 100)}%` }}
                          />
                        </div>
                        <div className="flex justify-between text-[10px] text-slate-500">
                          <span>Raw: {fb.raw_score}</span>
                          <span>Weighted: {fb.weighted_contribution}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* AI Forensic Narrative */}
                <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
                  <span className="text-[10px] text-[#00D9FF] uppercase font-bold block mb-1 flex items-center gap-1.5">
                    <Sparkles size={12} />
                    <span>AI FORENSIC NARRATIVE & HYPOTHESIS:</span>
                  </span>
                  <p className="text-slate-300 text-[11px] leading-relaxed">
                    {deanonResult.forensic_narrative}
                  </p>
                </div>

                {/* Evidence Artifacts */}
                {deanonResult.supporting_evidence?.length > 0 && (
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">
                      SUPPORTING EVIDENCE CHAIN (SHA-256):
                    </span>
                    <div className="space-y-1 max-h-32 overflow-y-auto">
                      {deanonResult.supporting_evidence.map((ev: any, idx: number) => (
                        <div key={idx} className="p-2 rounded bg-slate-950 border border-slate-800 text-[11px] flex justify-between items-center">
                          <div>
                            <strong className="text-[#00FF88]">{ev.vector}:</strong>{' '}
                            <span className="text-slate-300">{ev.description}</span>
                          </div>
                          {ev.hash && (
                            <span className="text-slate-600 font-mono text-[9px] ml-2">
                              {ev.hash.slice(0, 10)}...
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Action Buttons to Pivot */}
                <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
                  <button
                    onClick={() => {
                      setShowDeanonStudio(false);
                      navigate('/graph');
                    }}
                    className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-[#00D9FF] text-xs font-bold flex items-center gap-1.5"
                  >
                    <GitFork size={13} />
                    <span>EXPLORE IN GRAPH</span>
                  </button>
                  <button
                    onClick={() => {
                      setShowDeanonStudio(false);
                      navigate('/investigations');
                    }}
                    className="px-3 py-1.5 rounded bg-[#00FF88]/20 hover:bg-[#00FF88]/30 text-[#00FF88] border border-[#00FF88]/40 text-xs font-bold flex items-center gap-1.5"
                  >
                    <FolderGit2 size={13} />
                    <span>CREATE CASE</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Calm Notification Banner for Inbound Real-Time Alerts */}
      {latestAlert && (
        <div
          onClick={() => navigate('/alerts')}
          className="p-3 bg-[#0E1A36]/90 border border-sky-500/30 rounded-xl text-xs font-mono text-slate-200 flex items-center justify-between cursor-pointer hover:border-sky-400/60 transition shadow-lg card-3d"
        >
          <div className="flex items-center gap-3">
            <span className="h-2.5 w-2.5 rounded-full bg-[#38BDF8] animate-pulse shadow-[0_0_8px_#38BDF8] flex-shrink-0" />
            <div>
              <span className="text-[#38BDF8] font-bold">[INTEL UPDATE]</span>{' '}
              <span className="text-slate-200 font-semibold">{latestAlert.title}</span>
            </div>
          </div>
          <span className="text-[11px] text-[#38BDF8] font-bold flex items-center gap-1 hover:underline">
            Inspect Feed <ExternalLink size={12} />
          </span>
        </div>
      )}

      {/* Live Notice Banner */}
      {crawlNotice && (
        <div className="p-3 bg-[#0E1A36]/90 border border-[#00E5FF]/30 rounded-xl text-xs font-mono text-[#00E5FF] flex items-center gap-2.5 shadow-md">
          <CheckCircle2 size={15} className="text-[#10B981]" />
          <span>{crawlNotice}</span>
        </div>
      )}

      {/* 3D Physical HUD KPI Grid (9 Tactile Elevated Metric Tiles) */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-3 gap-4">
        {kpiCards.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div
              key={kpi.label}
              className="card-3d p-5 flex flex-col justify-between group cursor-pointer"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-sky-400/70 font-semibold">{kpi.hex}</span>
                    <span className="text-[11px] font-mono uppercase tracking-wider text-slate-300 font-bold">
                      {kpi.label}
                    </span>
                  </div>
                  <div className="h-8 w-8 rounded-lg bg-[#091328] border border-sky-900/40 flex items-center justify-center text-slate-300 group-hover:border-sky-500/50 shadow-inner transition">
                    <Icon size={16} style={{ color: kpi.color }} />
                  </div>
                </div>

                <div className="flex items-baseline gap-2 mt-1">
                  <p className="text-3xl font-black font-mono tracking-tight" style={{ color: kpi.color }}>
                    {kpi.value.toLocaleString()}
                  </p>
                  {kpi.label === 'PENDING REVIEWS' && kpi.value === 0 && (
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-md bg-emerald-500/20 text-[#10B981] border border-emerald-500/40">
                      ZERO BACKLOG ✓
                    </span>
                  )}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-sky-900/30 flex items-center justify-between text-[10px] font-mono text-slate-400">
                <span>{kpi.sub}</span>
                <span className="text-[#38BDF8] opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-0.5 font-bold">
                  AUDIT <ArrowUpRight size={10} />
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Real-Time Live Darknet Intercept Wire Feed with Triage Toolbar */}
      <div className="card-3d p-6 border border-sky-500/25 bg-[#0E1A36]/90 rounded-2xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div className="flex items-center gap-2.5">
            <div className="relative h-4 w-4 flex items-center justify-center">
              <span className="h-3 w-3 rounded-full bg-[#10B981] animate-ping" />
              <Radio size={15} className="text-[#10B981] relative z-10" />
            </div>
            <h3 className="text-sm font-bold font-mono text-white uppercase tracking-wider flex items-center gap-2">
              <span className="text-[#00E5FF]">CIPHER WIRE</span>
              <span className="text-slate-500">//</span>
              <span>LIVE DARKNET TELEMETRY FEED</span>
            </h3>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-[11px] font-mono">
            {/* Stream Pause / Resume */}
            <button
              onClick={() => setWirePaused(!wirePaused)}
              className={`px-3 py-1.5 rounded-lg border flex items-center gap-1.5 transition font-bold btn-3d ${
                wirePaused
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                  : 'bg-[#091328] text-slate-300 border-sky-900/40 hover:text-white'
              }`}
            >
              {wirePaused ? <Play size={12} /> : <Pause size={12} />}
              <span>{wirePaused ? 'RESUME WIRE' : 'PAUSE WIRE'}</span>
            </button>

            {/* Single Step Packet Sweep */}
            <button
              onClick={handleTriggerLiveCrawl}
              disabled={crawling}
              className="px-3 py-1.5 rounded-lg bg-sky-500/20 text-[#38BDF8] border border-sky-500/40 hover:bg-sky-500/30 transition font-bold flex items-center gap-1.5 btn-3d"
            >
              <Zap size={12} />
              <span>{crawling ? 'SWEEPING...' : 'STEP 1 PKT'}</span>
            </button>

            <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
              Cycles: <strong className="text-slate-200">#{realtimeStatus.cycle_count}</strong>
            </span>
            <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[#00D9FF]">
              Timer: 0{countdown}s → 0s
            </span>
          </div>
        </div>

        {/* Wire Filter and Search Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-3 pb-3 border-b border-slate-800/80 font-mono text-xs">
          <div className="flex items-center gap-1.5">
            <Filter size={13} className="text-slate-500" />
            {(['ALL', 'CRYPTO', 'ONION', 'IP', 'PGP'] as const).map(f => (
              <button
                key={f}
                onClick={() => setWireFilter(f)}
                className={`px-2 py-0.5 rounded text-[10px] font-bold border transition ${
                  wireFilter === f
                    ? 'bg-[#00D9FF] text-black border-[#00D9FF]'
                    : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                {f}
              </button>
            ))}
          </div>

          <div className="relative w-full sm:w-64">
            <Search className="absolute left-2.5 top-2 text-slate-500" size={13} />
            <input
              type="text"
              value={wireSearch}
              onChange={(e) => setWireSearch(e.target.value)}
              placeholder="Search wire packets..."
              className="w-full bg-slate-900/90 border border-slate-800 rounded-lg pl-8 pr-3 py-1 text-xs text-slate-200 outline-none focus:border-[#00D9FF] placeholder-slate-600"
            />
          </div>
        </div>

        {filteredEvents.length === 0 ? (
          <div className="p-6 text-center text-xs font-mono text-slate-400 bg-slate-950/70 rounded-xl border border-slate-800/80 flex flex-col items-center justify-center gap-2.5">
            <div className="flex items-center gap-2.5 text-[#00FF88]">
              <div className="h-4 w-4 rounded-full border-2 border-[#00FF88] border-t-transparent animate-spin" />
              <span className="font-bold tracking-wide">
                MONITORING PASSIVE DARKNET SENSORS (CADENCE: {realtimeStatus.interval_seconds}s)
              </span>
            </div>
            <p className="text-[11px] text-slate-500">
              When the timer reaches 0s, autonomous crawlers ingest underground forum transmissions and extract indicators live.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {filteredEvents.map((ev, i) => (
              <div
                key={i}
                onClick={() => setSelectedIntercept(ev)}
                className={`p-3 rounded-xl bg-slate-950/90 border flex flex-col md:flex-row md:items-center justify-between text-xs font-mono gap-3 transition-all cursor-pointer group hover:border-[#00D9FF]/70 ${
                  ev.pinned
                    ? 'border-amber-500/60 bg-amber-950/20'
                    : i === 0
                    ? 'border-[#00FF88]/60 bg-[#00FF88]/10 shadow-[0_0_20px_rgba(0,255,136,0.12)]'
                    : 'border-slate-800'
                }`}
              >
                <div className="flex items-center gap-2.5 flex-wrap">
                  {ev.pinned ? (
                    <span className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 font-bold text-[9px] border border-amber-500/40">
                      PINNED
                    </span>
                  ) : i === 0 ? (
                    <span className="px-1.5 py-0.5 rounded bg-[#00FF88]/20 text-[#00FF88] font-bold text-[9px] border border-[#00FF88]/40 animate-pulse">
                      NEW (0s PULSE)
                    </span>
                  ) : null}

                  <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30 text-[10px] font-bold">
                    {ev.source}
                  </span>
                  <span className="text-slate-100 font-extrabold group-hover:text-[#00FF88] transition-colors">{ev.author}</span>
                  <span className="text-slate-400 text-[11px] hidden md:inline truncate max-w-md">
                    {ev.event_title}
                  </span>
                </div>

                <div className="flex items-center gap-2 text-[11px] text-slate-400">
                  <span className="text-slate-300 font-bold">{new Date(ev.timestamp).toLocaleTimeString()}</span>
                  
                  {/* Pin Button */}
                  <button
                    onClick={(e) => handleTogglePin(i, e)}
                    className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-amber-400 transition"
                    title={ev.pinned ? 'Unpin packet' : 'Pin packet to top'}
                  >
                    {ev.pinned ? <PinOff size={12} className="text-amber-400" /> : <Pin size={12} />}
                  </button>

                  {/* De-Anonymize Pivot Button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handlePivotToDeanon(ev);
                    }}
                    className="px-2 py-0.5 rounded bg-emerald-500/20 hover:bg-emerald-500/30 text-[#00FF88] border border-[#00FF88]/40 transition flex items-center gap-1 text-[10px] font-bold"
                    title="Launch Real-Time De-Anonymization on this suspect"
                  >
                    <Crosshair size={11} />
                    <span>DE-ANON</span>
                  </button>

                  {/* Inspect Button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedIntercept(ev);
                    }}
                    className="p-1 rounded text-[#00D9FF] hover:bg-[#00D9FF]/20 transition flex items-center gap-1 text-[10px]"
                  >
                    <Eye size={12} />
                    <span>INSPECT</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Forensic Intercept Inspector Modal (When an Intercept is clicked) */}
      {selectedIntercept && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
          <div className="w-full max-w-2xl glass-panel p-6 border border-[#00D9FF]/40 shadow-[0_0_40px_rgba(0,217,255,0.2)] space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <SearchCode size={18} className="text-[#00D9FF]" />
                <h3 className="text-base font-bold font-mono text-slate-100 uppercase">
                  FORENSIC INTERCEPT INSPECTOR
                </h3>
              </div>
              <button
                onClick={() => setSelectedIntercept(null)}
                className="p-1 text-slate-400 hover:text-slate-200 rounded"
              >
                <X size={18} />
              </button>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <div>
                  <span className="text-slate-500 block text-[10px]">SUSPECT IDENTIFIER:</span>
                  <span className="text-slate-200 font-bold text-sm text-[#00FF88]">{selectedIntercept.author}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">ORIGIN SENSOR:</span>
                  <span className="text-slate-200 font-bold text-sm text-[#00D9FF]">{selectedIntercept.source}</span>
                </div>
              </div>

              <div>
                <span className="text-slate-500 block text-[10px] mb-1">INTERCEPTED TELEMETRY PAYLOAD:</span>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 leading-relaxed max-h-36 overflow-y-auto">
                  {selectedIntercept.event_title}
                </div>
              </div>

              {selectedIntercept.data?.content_hash && (
                <div>
                  <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1">
                    <span>EVIDENCE CRYPTOGRAPHIC INTEGRITY (SHA-256):</span>
                    <button
                      onClick={() => handleCopyHash(selectedIntercept.data!.content_hash!)}
                      className="text-[#00FF88] hover:underline flex items-center gap-1"
                    >
                      {copiedHash ? <Check size={11} /> : <Copy size={11} />}
                      <span>{copiedHash ? 'COPIED' : 'COPY HASH'}</span>
                    </button>
                  </div>
                  <div className="p-2 rounded bg-slate-950 border border-slate-800 text-slate-400 break-all select-all text-[11px]">
                    {selectedIntercept.data.content_hash}
                  </div>
                </div>
              )}

              {selectedIntercept.data?.extracted_indicators && (
                <div>
                  <span className="text-slate-500 block text-[10px] mb-1">EXTRACTED THREAT INDICATORS:</span>
                  <div className="grid grid-cols-2 gap-2 text-[11px]">
                    <div className="p-2 rounded bg-slate-900 border border-slate-800">
                      <span className="text-amber-400 block font-bold">Bitcoin Wallets:</span>
                      <span className="text-slate-300 break-all">
                        {selectedIntercept.data.extracted_indicators.btc_wallets?.join(', ') || 'None extracted'}
                      </span>
                    </div>
                    <div className="p-2 rounded bg-slate-900 border border-slate-800">
                      <span className="text-orange-400 block font-bold">Monero Wallets:</span>
                      <span className="text-slate-300 break-all">
                        {selectedIntercept.data.extracted_indicators.xmr_wallets?.join(', ') || 'None extracted'}
                      </span>
                    </div>
                    <div className="p-2 rounded bg-slate-900 border border-slate-800">
                      <span className="text-[#00D9FF] block font-bold">Clearnet IP Mirrors:</span>
                      <span className="text-slate-300 break-all">
                        {selectedIntercept.data.extracted_indicators.clearnet_ips?.join(', ') || 'None extracted'}
                      </span>
                    </div>
                    <div className="p-2 rounded bg-slate-900 border border-slate-800">
                      <span className="text-[#00FF88] block font-bold">PGP Fingerprints:</span>
                      <span className="text-slate-300 break-all">
                        {selectedIntercept.data.extracted_indicators.pgp_fingerprints?.join(', ') || 'None extracted'}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  onClick={() => handlePivotToDeanon(selectedIntercept)}
                  className="px-3.5 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-[#00FF88] border border-[#00FF88]/40 text-xs font-bold transition flex items-center gap-1.5"
                >
                  <Crosshair size={13} />
                  <span>DE-ANONYMIZE IN REAL TIME</span>
                </button>
                <button
                  onClick={() => {
                    setSelectedIntercept(null);
                    navigate('/graph');
                  }}
                  className="px-3.5 py-1.5 rounded-lg bg-[#00D9FF]/20 hover:bg-[#00D9FF]/30 text-[#00D9FF] border border-[#00D9FF]/40 text-xs font-bold transition flex items-center gap-1.5"
                >
                  <GitFork size={13} />
                  <span>PIVOT TO GRAPH EXPLORER</span>
                </button>
                <button
                  onClick={() => {
                    setSelectedIntercept(null);
                    navigate('/investigations');
                  }}
                  className="px-3.5 py-1.5 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/40 text-xs font-bold transition flex items-center gap-1.5"
                >
                  <FolderGit2 size={13} />
                  <span>SPAWN INVESTIGATION CASE</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts Section: Activity Timeline + Source Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activity Over Time */}
        <div className="glass-panel p-5 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2 font-mono">
              <TrendingUp size={16} className="text-[#00D9FF]" />
              INTELLIGENCE OBSERVATIONS & CORRELATIONS OVER TIME
            </h3>
            <span className="text-[11px] font-mono text-slate-500">Live DB Monthly Aggregations</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats.activity_over_time} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorObs" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00D9FF" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#00D9FF" stopOpacity={0.0}/>
                  </linearGradient>
                  <linearGradient id="colorRel" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#F59E0B" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="period" stroke="#475569" tick={{ fontSize: 11, fill: '#94A3B8' }} />
                <YAxis stroke="#475569" tick={{ fontSize: 11, fill: '#94A3B8' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0A0F1A', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                />
                <Area type="monotone" dataKey="observations" stroke="#00D9FF" fillOpacity={1} fill="url(#colorObs)" name="Observations" />
                <Area type="monotone" dataKey="relationships" stroke="#F59E0B" fillOpacity={1} fill="url(#colorRel)" name="Relationships" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Source Distribution */}
        <div className="glass-panel p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2 font-mono">
              <Database size={16} className="text-[#00FF88]" />
              SOURCE TELEMETRY DISTRIBUTION
            </h3>
            <span className="text-[11px] font-mono text-slate-500">Monitored Ingestion</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sourceData} layout="vertical" margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                <XAxis type="number" stroke="#475569" tick={{ fontSize: 10, fill: '#94A3B8' }} />
                <YAxis type="category" dataKey="name" stroke="#475569" tick={{ fontSize: 9, fill: '#94A3B8' }} width={90} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0A0F1A', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                />
                <Bar dataKey="count" fill="#00FF88" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Dynamic Database-Driven Findings */}
      <div className="glass-panel p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2 font-mono">
              <AlertTriangle size={16} className="text-[#FFB020]" />
              HIGH-PRIORITY ATTRIBUTION FINDINGS & CORRELATIONS
            </h3>
            <p className="text-xs text-slate-400 mt-0.5 font-mono">
              Dynamically retrieved from active database attribution assessments and infrastructure correlations.
            </p>
          </div>
        </div>

        {stats.recent_findings.length === 0 ? (
          <div className="p-6 text-center text-xs font-mono text-slate-500 bg-slate-900/40 rounded-xl border border-slate-800">
            No active attribution findings in zero-state. Click <strong>RESTORE DEMO DATA</strong> or run an investigation to generate live correlations.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {stats.recent_findings.map((item) => (
              <div
                key={item.id}
                onClick={() => navigate(`/actors/${item.actor_id}`)}
                className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-[#00D9FF]/50 transition-all cursor-pointer group flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold ${
                      item.type === 'POTENTIAL_PERSONA_RELATIONSHIP'
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                        : 'bg-[#00D9FF]/10 text-[#00D9FF] border border-[#00D9FF]/30'
                    }`}>
                      {item.type.replace(/_/g, ' ')}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      Target: <strong className="text-slate-200">{item.actor_id}</strong>
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-slate-200 group-hover:text-[#00FF88] transition-colors">
                    {item.title}
                  </h4>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                    {item.description}
                  </p>
                </div>

                <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-800 text-xs">
                  <span className="text-slate-500 font-mono text-[11px]">
                    Confidence: <strong className="text-[#00FF88]">{item.confidence}</strong>
                  </span>
                  <span className="flex items-center gap-1 text-[#00D9FF] font-semibold text-[11px] group-hover:underline">
                    Inspect Dossier <ExternalLink size={12} />
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Tor Network & Chrome Browser Forensic Detection Console Modal */}
      <TorBrowserDetectionModal
        isOpen={showTorModal}
        onClose={() => setShowTorModal(false)}
        onPivotToDeanon={(handle, ind) => {
          setDeanonPersonaA(handle);
          if (ind?.ip) setDeanonIps(ind.ip);
          setShowTorModal(false);
          setShowDeanonStudio(true);
        }}
      />
    </div>
  );
};
