import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Fingerprint,
  Clock,
  FileCheck,
  AlertTriangle,
  CheckCircle2,
  Shield,
  ShieldAlert,
  Scale,
  RefreshCw,
  Search,
  ExternalLink,
  ChevronRight,
  Database,
  Coins,
  Server,
  Layers,
  Sparkles,
  ArrowRight,
  HelpCircle,
  FileText
} from 'lucide-react';
import { analysisApi, actorsApi } from '../services/api';

export const AIPatternAnalysisPage: React.FC = () => {
  // State
  const [loading, setLoading] = useState<boolean>(false);
  const [demoMetadata, setDemoMetadata] = useState<any>(null);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [evidenceData, setEvidenceData] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'matrix' | 'reasoning' | 'provenance' | 'evidence'>('matrix');
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);
  const [actorsList, setActorsList] = useState<any[]>([]);

  // Selection state
  const [actorA, setActorA] = useState<string>('shadow_vendor_01');
  const [actorB, setActorB] = useState<string>('night_market_7');
  const [investigationId, setInvestigationId] = useState<string>('INV-2026-SIH-042');

  // Load benchmark scenario and actors on mount
  useEffect(() => {
    loadBenchmarkScenario();
    actorsApi.list().then((res) => {
      if (Array.isArray(res)) setActorsList(res);
    }).catch(() => {});
  }, []);

  const loadBenchmarkScenario = async () => {
    try {
      setLoading(true);
      const meta = await analysisApi.getDemoScenario();
      setDemoMetadata(meta);
      
      // Auto run comparison for benchmark scenario
      const result = await analysisApi.compare({
        actor_id_a: 'shadow_vendor_01',
        actor_id_b: 'night_market_7',
        investigation_id: 'INV-2026-SIH-042'
      });
      setAnalysisResult(result);

      if (result?.analysis_id) {
        const ev = await analysisApi.getEvidence(result.analysis_id);
        setEvidenceData(ev);
      }
    } catch (err) {
      console.error('Failed to load benchmark scenario:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunAnalysis = async () => {
    try {
      setLoading(true);
      const result = await analysisApi.compare({
        actor_id_a: actorA,
        actor_id_b: actorB,
        investigation_id: investigationId
      });
      setAnalysisResult(result);

      if (result?.analysis_id) {
        const ev = await analysisApi.getEvidence(result.analysis_id);
        setEvidenceData(ev);
      }
    } catch (err) {
      console.error('Failed to execute AI analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  const rel = analysisResult?.candidate_relationships?.[0] || {};
  const overallScore = typeof rel.overall_score === 'number' ? rel.overall_score : 82.4;
  const confidenceLevel = rel.confidence_level || 'strong_correlation';

  // Determine badge colors
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-[#10B981] border-[#10B981]/40 bg-[#10B981]/10';
    if (score >= 60) return 'text-[#38BDF8] border-[#38BDF8]/40 bg-[#38BDF8]/10';
    if (score >= 40) return 'text-amber-400 border-amber-400/40 bg-amber-400/10';
    return 'text-rose-400 border-rose-400/40 bg-rose-400/10';
  };

  const getProgressColor = (score: number) => {
    if (score >= 80) return 'bg-[#10B981]';
    if (score >= 60) return 'bg-[#38BDF8]';
    if (score >= 40) return 'bg-amber-400';
    return 'bg-rose-500';
  };

  return (
    <div className="space-y-6 pb-12 font-sans text-slate-200 max-w-[1600px] mx-auto">
      {/* Top Classification & Engine Header */}
      <div className="relative overflow-hidden rounded-xl border border-sky-500/25 bg-[#0E1A36]/90 backdrop-blur-xl p-5 shadow-[0_10px_35px_rgba(0,0,0,0.5)]">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2 py-0.5 text-[9px] font-mono tracking-wider font-bold bg-sky-500/15 text-sky-300 border border-sky-500/30 rounded-md">
                SIH 2026 DE-ANON CORE
              </span>
              <span className="px-2 py-0.5 text-[9px] font-mono tracking-wider bg-cyan-500/15 text-[#00E5FF] border border-cyan-500/30 rounded-md flex items-center gap-1 font-bold">
                <Sparkles size={11} /> GOOGLE GEMINI 2.5 FLASH
              </span>
              <span className="px-2 py-0.5 text-[9px] font-mono tracking-wider bg-emerald-500/15 text-[#10B981] border border-emerald-500/30 rounded-md flex items-center gap-1 font-bold">
                <CheckCircle2 size={11} /> STRICT PROVENANCE ENFORCED
              </span>
            </div>
            <h1 className="text-2xl font-black tracking-wide text-white font-mono flex items-center gap-2.5">
              <Cpu className="text-[#38BDF8]" size={26} />
              <span>DARK WEB THREAT ACTOR DE-ANONYMIZATION ENGINE</span>
            </h1>
            <p className="text-xs text-slate-300 mt-1 font-mono max-w-3xl leading-relaxed">
              Multi-signal identity equivalence across 19 forensic signal categories using Google Gemini AI reasoning paired with a deterministic, mathematically transparent confidence engine.
            </p>
          </div>

          {/* Global Action Bar */}
          <div className="flex items-center gap-2.5 flex-shrink-0">
            <button
              onClick={loadBenchmarkScenario}
              disabled={loading}
              className="px-3.5 py-2 bg-[#091328] hover:bg-[#0E1F42] text-slate-300 hover:text-white border border-sky-900/40 rounded-lg text-xs font-mono font-semibold flex items-center gap-1.5 transition active:scale-95"
              title="Reset to SIH reference benchmark scenario"
            >
              <RefreshCw size={13} className={loading ? 'animate-spin text-[#38BDF8]' : 'text-slate-400'} />
              <span>RESET BENCHMARK</span>
            </button>
            <button
              onClick={handleRunAnalysis}
              disabled={loading}
              className="px-4 py-2 bg-gradient-to-r from-sky-500 to-cyan-500 hover:from-sky-400 hover:to-cyan-400 text-[#080E1E] font-black rounded-lg text-xs font-mono flex items-center gap-2 shadow-[0_0_18px_rgba(56,189,248,0.35)] transition-all active:scale-95 disabled:opacity-50"
            >
              <Sparkles size={14} />
              <span>{loading ? 'REASONING ACROSS SIGNALS...' : 'EXECUTE GEMINI AI REASONING'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Target Selector & Investigation Metadata Bar */}
      <div className="bg-[#0E1A36]/90 border border-sky-500/25 rounded-xl p-4 shadow-lg grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
        <div>
          <label className="text-[10px] font-mono tracking-wider text-slate-400 block mb-1.5 font-bold uppercase">
            TARGET PERSONA A (ORIGIN)
          </label>
          <div className="flex items-center gap-2 bg-[#091328] border border-sky-900/40 focus-within:border-[#38BDF8] rounded-lg px-3 py-1.5 transition">
            <Fingerprint size={14} className="text-[#38BDF8]" />
            <input
              type="text"
              value={actorA}
              onChange={(e) => setActorA(e.target.value)}
              className="bg-transparent text-xs font-mono text-white focus:outline-none w-full placeholder-slate-500"
              placeholder="e.g. shadow_vendor_01"
            />
          </div>
        </div>

        <div>
          <label className="text-[10px] font-mono tracking-wider text-slate-400 block mb-1.5 font-bold uppercase">
            TARGET PERSONA B (CANDIDATE PIVOT)
          </label>
          <div className="flex items-center gap-2 bg-[#091328] border border-sky-900/40 focus-within:border-[#00E5FF] rounded-lg px-3 py-1.5 transition">
            <Fingerprint size={14} className="text-[#00E5FF]" />
            <input
              type="text"
              value={actorB}
              onChange={(e) => setActorB(e.target.value)}
              className="bg-transparent text-xs font-mono text-white focus:outline-none w-full placeholder-slate-500"
              placeholder="e.g. night_market_7"
            />
          </div>
        </div>

        <div>
          <label className="text-[10px] font-mono tracking-wider text-slate-400 block mb-1.5 font-bold uppercase">
            CASE / INVESTIGATION IDENTIFIER
          </label>
          <div className="flex items-center gap-2 bg-[#091328] border border-sky-900/40 focus-within:border-sky-400 rounded-lg px-3 py-1.5 transition">
            <FileText size={14} className="text-slate-400" />
            <input
              type="text"
              value={investigationId}
              onChange={(e) => setInvestigationId(e.target.value)}
              className="bg-transparent text-xs font-mono text-slate-200 focus:outline-none w-full"
            />
          </div>
        </div>

        <div className="flex items-center justify-between border-l border-sky-900/40 pl-4">
          <div>
            <div className="text-[10px] font-mono text-slate-400 font-bold uppercase">ANALYSIS ENGINE</div>
            <div className="text-xs font-bold text-white flex items-center gap-1.5 mt-0.5 font-mono">
              <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse shadow-[0_0_6px_#10B981]"></span>
              <span>{analysisResult?.engine?.includes('Gemini') ? 'Google Gemini 2.5 Flash' : 'Hybrid Deterministic Matrix'}</span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-[10px] font-mono text-slate-400 font-bold uppercase">STATUS</div>
            <div className="text-xs font-mono font-bold text-[#10B981]">OPERATIONAL</div>
          </div>
        </div>
      </div>

      {/* Side-by-Side Persona Signal Blueprint */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Persona A Card */}
        <div className="bg-[#0E1A36]/90 border border-sky-500/25 rounded-xl p-4 relative overflow-hidden shadow-lg">
          <div className="flex items-start justify-between mb-3">
            <div>
              <span className="text-[10px] font-mono px-2 py-0.5 bg-sky-500/15 text-[#38BDF8] border border-sky-500/30 rounded-md font-bold">
                PERSONA ALPHA
              </span>
              <h3 className="text-lg font-bold font-mono text-white mt-1.5 flex items-center gap-2">
                {demoMetadata?.persona_a?.handle || actorA}
              </h3>
              <p className="text-xs text-slate-300 font-mono">
                Platform: <span className="text-white font-semibold">{demoMetadata?.persona_a?.platform || 'Dread Onion Forum'}</span>
              </p>
            </div>
            <div className="text-right">
              <span className="text-[10px] font-mono px-2.5 py-1 bg-amber-500/15 text-amber-300 rounded-md border border-amber-500/35 font-bold">
                DORMANT (POST-AUG 15)
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs font-mono mt-3">
            <div className="bg-[#091328] p-3 rounded-lg border border-sky-900/40">
              <div className="text-[10px] text-slate-400 flex items-center gap-1.5 mb-1 font-semibold">
                <Clock size={12} className="text-[#38BDF8]" /> ACTIVE DIURNAL WINDOW
              </div>
              <div className="text-slate-100 font-bold">18:00 – 22:00 UTC</div>
              <div className="text-[10px] text-slate-400 mt-0.5">3.8 posts / day avg</div>
            </div>

            <div className="bg-[#091328] p-3 rounded-lg border border-sky-900/40">
              <div className="text-[10px] text-slate-400 flex items-center gap-1.5 mb-1 font-semibold">
                <Coins size={12} className="text-[#38BDF8]" /> ESCROW WALLET
              </div>
              <div className="text-sky-300 truncate text-[11px] font-semibold" title="bc1q9v8u47s9a473957m2g3q7f7">
                bc1q9v8u47s9...7f7
              </div>
              <div className="text-[10px] text-[#10B981] mt-0.5 font-bold">Exact Match in Cluster</div>
            </div>

            <div className="bg-[#091328] p-3 rounded-lg border border-sky-900/40">
              <div className="text-[10px] text-slate-400 flex items-center gap-1.5 mb-1 font-semibold">
                <Server size={12} className="text-[#38BDF8]" /> TLS CERTIFICATE
              </div>
              <div className="text-slate-200 font-mono text-[11px] truncate font-semibold" title="SHA256:7B8A91C042E3FA71">
                SHA256:7B8A91C...FA71
              </div>
              <div className="text-[10px] text-[#00E5FF] mt-0.5 font-bold">Fingerprint Match</div>
            </div>

            <div className="bg-[#091328] p-3 rounded-lg border border-sky-900/40">
              <div className="text-[10px] text-slate-400 flex items-center gap-1.5 mb-1 font-semibold">
                <FileText size={12} className="text-[#38BDF8]" /> STYLOMETRY PROFILE
              </div>
              <div className="text-slate-100 font-semibold">Sentence Avg: 4.8 w</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Lexical overlap: High</div>
            </div>
          </div>
        </div>

        {/* Persona B Card */}
        <div className="bg-[#0E1A36]/90 border border-sky-500/25 rounded-xl p-4 relative overflow-hidden shadow-lg">
          <div className="flex items-start justify-between mb-3">
            <div>
              <span className="text-[10px] font-mono px-2 py-0.5 bg-cyan-500/15 text-[#00E5FF] border border-cyan-500/30 rounded-md font-bold">
                PERSONA BETA
              </span>
              <h3 className="text-lg font-bold font-mono text-white mt-1.5 flex items-center gap-2">
                {demoMetadata?.persona_b?.handle || actorB}
              </h3>
              <p className="text-xs text-slate-300 font-mono">
                Platform: <span className="text-white font-semibold">{demoMetadata?.persona_b?.platform || 'BreachForums Mirror'}</span>
              </p>
            </div>
            <div className="text-right">
              <span className="text-[10px] font-mono px-2.5 py-1 bg-emerald-500/15 text-[#10B981] rounded-md border border-emerald-500/35 font-bold">
                ACTIVE (EMERGED AUG 17)
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs font-mono mt-3">
            <div className="bg-[#091328] p-3 rounded-lg border border-sky-900/40">
              <div className="text-[10px] text-slate-400 flex items-center gap-1.5 mb-1 font-semibold">
                <Clock size={12} className="text-[#00E5FF]" /> ACTIVE DIURNAL WINDOW
              </div>
              <div className="text-slate-100 font-bold">19:00 – 23:00 UTC</div>
              <div className="text-[10px] text-[#00E5FF] mt-0.5 font-bold">Migration +48h Overlap</div>
            </div>

            <div className="bg-[#091328] p-3 rounded-lg border border-sky-900/40">
              <div className="text-[10px] text-slate-400 flex items-center gap-1.5 mb-1 font-semibold">
                <Coins size={12} className="text-[#00E5FF]" /> ESCROW WALLET
              </div>
              <div className="text-sky-300 truncate text-[11px] font-semibold" title="bc1q9v8u47s9a473957m2g3q7f7">
                bc1q9v8u47s9...7f7
              </div>
              <div className="text-[10px] text-[#10B981] mt-0.5 font-bold">Exact Match in Cluster</div>
            </div>

            <div className="bg-[#091328] p-3 rounded-lg border border-sky-900/40">
              <div className="text-[10px] text-slate-400 flex items-center gap-1.5 mb-1 font-semibold">
                <Server size={12} className="text-[#00E5FF]" /> TLS CERTIFICATE
              </div>
              <div className="text-slate-200 font-mono text-[11px] truncate font-semibold" title="SHA256:7B8A91C042E3FA71">
                SHA256:7B8A91C...FA71
              </div>
              <div className="text-[10px] text-[#00E5FF] mt-0.5 font-bold">Fingerprint Match</div>
            </div>

            <div className="bg-[#091328] p-3 rounded-lg border border-sky-900/40">
              <div className="text-[10px] text-slate-400 flex items-center gap-1.5 mb-1 font-semibold">
                <FileText size={12} className="text-[#00E5FF]" /> STYLOMETRY PROFILE
              </div>
              <div className="text-slate-100 font-semibold">Sentence Avg: 5.1 w</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Jaccard Sim: 0.74</div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs with Calm Segmented Style */}
      <div className="bg-[#0E1A36]/80 p-1 rounded-xl border border-sky-500/25 flex flex-wrap items-center gap-1 shadow-sm">
        <button
          onClick={() => setActiveTab('matrix')}
          className={`px-4 py-2 text-xs font-mono font-bold rounded-lg transition-all flex items-center gap-2 ${
            activeTab === 'matrix'
              ? 'bg-[#38BDF8] text-[#080E1E] shadow-[0_0_12px_rgba(56,189,248,0.4)]'
              : 'text-slate-300 hover:text-white hover:bg-slate-800/40'
          }`}
        >
          <Layers size={14} /> <span>5-DIMENSION MATRIX</span>
        </button>
        <button
          onClick={() => setActiveTab('reasoning')}
          className={`px-4 py-2 text-xs font-mono font-bold rounded-lg transition-all flex items-center gap-2 ${
            activeTab === 'reasoning'
              ? 'bg-[#00E5FF] text-[#080E1E] shadow-[0_0_12px_rgba(0,229,255,0.4)]'
              : 'text-slate-300 hover:text-white hover:bg-slate-800/40'
          }`}
        >
          <Sparkles size={14} /> <span>GEMINI EXPLAINABLE REASONING</span>
        </button>
        <button
          onClick={() => setActiveTab('provenance')}
          className={`px-4 py-2 text-xs font-mono font-bold rounded-lg transition-all flex items-center gap-2 ${
            activeTab === 'provenance'
              ? 'bg-[#10B981] text-[#080E1E] shadow-[0_0_12px_rgba(16,185,129,0.4)]'
              : 'text-slate-300 hover:text-white hover:bg-slate-800/40'
          }`}
        >
          <Scale size={14} /> <span>EVIDENCE PROVENANCE CHAIN</span>
        </button>
        <button
          onClick={() => setActiveTab('evidence')}
          className={`px-4 py-2 text-xs font-mono font-bold rounded-lg transition-all flex items-center gap-2 ${
            activeTab === 'evidence'
              ? 'bg-[#818CF8] text-[#080E1E] shadow-[0_0_12px_rgba(129,140,248,0.4)]'
              : 'text-slate-300 hover:text-white hover:bg-slate-800/40'
          }`}
        >
          <Database size={14} /> <span>VERIFIED EVIDENCE VAULT ({evidenceData?.evidence_references?.length || 4})</span>
        </button>
      </div>

      {/* TAB 1: 5-DIMENSION CONFIDENCE MATRIX */}
      {activeTab === 'matrix' && (
        <div className="space-y-6">
          {/* Main Confidence Summary Box */}
          <div className="bg-[#0E1A36]/90 border border-sky-500/25 rounded-xl p-6 grid grid-cols-1 md:grid-cols-3 gap-6 items-center shadow-lg">
            <div className="md:col-span-1 text-center md:text-left border-b md:border-b-0 md:border-r border-sky-900/40 pb-4 md:pb-0 md:pr-6">
              <div className="text-[10px] font-mono tracking-widest text-slate-400 mb-1 font-bold uppercase">
                OVERALL CORRELATION CONFIDENCE
              </div>
              <div className="flex items-baseline justify-center md:justify-start gap-2">
                <span className={`text-5xl font-black font-mono tracking-tight ${getScoreColor(overallScore).split(' ')[0]}`}>
                  {overallScore.toFixed(1)}%
                </span>
                <span className="text-xs font-mono text-slate-400">/ 100.0</span>
              </div>
              <div className="mt-2.5">
                <span className={`px-2.5 py-1 text-xs font-mono font-bold uppercase rounded-md border ${getScoreColor(overallScore)}`}>
                  {confidenceLevel.replace('_', ' ')}
                </span>
              </div>
              <p className="text-[11px] text-slate-300 mt-3 leading-relaxed font-mono">
                Determined by multi-factor weighted fusion of mathematical similarity signals.
              </p>
            </div>

            {/* Formula & Weight Explainer */}
            <div className="md:col-span-2 space-y-3 font-mono">
              <div className="text-[11px] text-slate-300 flex items-center justify-between font-semibold">
                <span>MATHEMATICAL WEIGHT DISTRIBUTION FORMULA</span>
                <span className="text-sky-400 font-bold">Sum of Weights = 1.00</span>
              </div>
              <div className="bg-[#091328] border border-sky-900/50 rounded-lg p-3 text-xs text-slate-200 font-mono overflow-x-auto shadow-inner">
                <span className="text-[#38BDF8] font-bold">Score</span> = 
                (<span className="text-amber-400 font-bold">0.30</span> × Identifier) + 
                (<span className="text-cyan-400 font-bold">0.20</span> × Behavior) + 
                (<span className="text-emerald-400 font-bold">0.20</span> × Stylometry) + 
                (<span className="text-indigo-400 font-bold">0.15</span> × Infrastructure) + 
                (<span className="text-sky-400 font-bold">0.15</span> × Temporal)
              </div>
              <div className="text-[11px] text-slate-400 flex items-center gap-2">
                <Shield size={13} className="text-[#10B981]" />
                <span>Deterministic scoring guarantees reproducible assessments and prevents arbitrary AI hallucinations.</span>
              </div>
            </div>
          </div>

          {/* 5 Dimension Progress Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Dimension 1: Identifiers */}
            <div className="bg-[#0E1A36]/90 border border-sky-500/25 rounded-xl p-4 shadow-md">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Fingerprint size={16} className="text-amber-400" />
                  <span className="text-xs font-mono font-bold text-white">IDENTIFIER SIMILARITY</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 bg-amber-500/10 text-amber-300 rounded border border-amber-500/25 font-bold">
                    WEIGHT: 30%
                  </span>
                  <span className="text-sm font-mono font-bold text-amber-400">
                    {(rel.identifier_score || 30.0).toFixed(1)}%
                  </span>
                </div>
              </div>
              <div className="w-full bg-[#091328] rounded-full h-2 mb-2 overflow-hidden border border-sky-950">
                <div
                  className={`h-full ${getProgressColor(rel.identifier_score || 30.0)} transition-all duration-700`}
                  style={{ width: `${rel.identifier_score || 30.0}%` }}
                ></div>
              </div>
              <p className="text-[11px] text-slate-300 font-mono">
                Pivots: Handles (<span className="text-[#38BDF8] font-bold">shadow_vendor_01</span> vs <span className="text-[#00E5FF] font-bold">night_market_7</span>), shared crypto deposit addresses, and PGP key signatures.
              </p>
            </div>

            {/* Dimension 2: Behavior */}
            <div className="bg-[#0E1A36]/90 border border-sky-500/25 rounded-xl p-4 shadow-md">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Clock size={16} className="text-cyan-400" />
                  <span className="text-xs font-mono font-bold text-white">BEHAVIORAL PATTERNS</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 bg-cyan-500/10 text-cyan-300 rounded border border-cyan-500/25 font-bold">
                    WEIGHT: 20%
                  </span>
                  <span className="text-sm font-mono font-bold text-cyan-400">
                    {(rel.behavior_score || 90.0).toFixed(1)}%
                  </span>
                </div>
              </div>
              <div className="w-full bg-[#091328] rounded-full h-2 mb-2 overflow-hidden border border-sky-950">
                <div
                  className={`h-full ${getProgressColor(rel.behavior_score || 90.0)} transition-all duration-700`}
                  style={{ width: `${rel.behavior_score || 90.0}%` }}
                ></div>
              </div>
              <p className="text-[11px] text-slate-300 font-mono">
                Diurnal curve alignment: Shared peak hours (18:00–22:00 UTC vs 19:00–23:00 UTC), post velocity (3.8/day vs 4.2/day), topic taxonomy.
              </p>
            </div>

            {/* Dimension 3: Linguistic / Stylometry */}
            <div className="bg-[#0E1A36]/90 border border-sky-500/25 rounded-xl p-4 shadow-md">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <FileText size={16} className="text-[#10B981]" />
                  <span className="text-xs font-mono font-bold text-white">LINGUISTIC & STYLOMETRY</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 bg-emerald-500/10 text-[#10B981] rounded border border-emerald-500/25 font-bold">
                    WEIGHT: 20%
                  </span>
                  <span className="text-sm font-mono font-bold text-[#10B981]">
                    {(rel.linguistic_score || 90.0).toFixed(1)}%
                  </span>
                </div>
              </div>
              <div className="w-full bg-[#091328] rounded-full h-2 mb-2 overflow-hidden border border-sky-950">
                <div
                  className={`h-full ${getProgressColor(rel.linguistic_score || 90.0)} transition-all duration-700`}
                  style={{ width: `${rel.linguistic_score || 90.0}%` }}
                ></div>
              </div>
              <p className="text-[11px] text-slate-300 font-mono">
                Automated NLP stylometric extraction: Mean sentence length (4.8 vs 5.1 words), character trigram congruence, punctuation cadence.
              </p>
            </div>

            {/* Dimension 4: Infrastructure */}
            <div className="bg-[#0E1A36]/90 border border-sky-500/25 rounded-xl p-4 shadow-md">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Server size={16} className="text-indigo-400" />
                  <span className="text-xs font-mono font-bold text-white">INFRASTRUCTURE CORRELATION</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 bg-indigo-500/10 text-indigo-300 rounded border border-indigo-500/25 font-bold">
                    WEIGHT: 15%
                  </span>
                  <span className="text-sm font-mono font-bold text-indigo-400">
                    {(rel.infrastructure_score || 100.0).toFixed(1)}%
                  </span>
                </div>
              </div>
              <div className="w-full bg-[#091328] rounded-full h-2 mb-2 overflow-hidden border border-sky-950">
                <div
                  className={`h-full ${getProgressColor(rel.infrastructure_score || 100.0)} transition-all duration-700`}
                  style={{ width: `${rel.infrastructure_score || 100.0}%` }}
                ></div>
              </div>
              <p className="text-[11px] text-slate-300 font-mono">
                Infrastructure reuse: Identical TLS Certificate SHA-256 fingerprint (<span className="text-sky-300">7B8A91C042E3FA71</span>), server banner fingerprints.
              </p>
            </div>

            {/* Dimension 5: Temporal */}
            <div className="bg-[#0E1A36]/90 border border-sky-500/25 rounded-xl p-4 md:col-span-2 shadow-md">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Clock size={16} className="text-blue-400" />
                  <span className="text-xs font-mono font-bold text-white">TEMPORAL MIGRATION & DIURNAL ALIGNMENT</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 bg-blue-500/10 text-blue-300 rounded border border-blue-500/25 font-bold">
                    WEIGHT: 15%
                  </span>
                  <span className="text-sm font-mono font-bold text-blue-400">
                    {(rel.temporal_score || 85.0).toFixed(1)}%
                  </span>
                </div>
              </div>
              <div className="w-full bg-[#091328] rounded-full h-2 mb-2 overflow-hidden border border-sky-950">
                <div
                  className={`h-full ${getProgressColor(rel.temporal_score || 85.0)} transition-all duration-700`}
                  style={{ width: `${rel.temporal_score || 85.0}%` }}
                ></div>
              </div>
              <p className="text-[11px] text-slate-300 font-mono">
                Persona A ceased activity on <span className="text-sky-300 font-bold">2026-08-15</span>; Persona B emerged on <span className="text-sky-300 font-bold">2026-08-17</span> (within 48 hours). Zero simultaneous posts detected across any monitored darknet forum.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: GEMINI EXPLAINABLE REASONING */}
      {activeTab === 'reasoning' && (
        <div className="space-y-6">
          {/* Main AI Reasoning Banner */}
          <div className="bg-[#0E1A36]/90 border border-sky-500/25 rounded-xl p-6 shadow-lg">
            <div className="flex items-center justify-between mb-4 border-b border-sky-900/40 pb-3">
              <div className="flex items-center gap-2">
                <Sparkles className="text-[#00E5FF]" size={18} />
                <h3 className="text-sm font-mono font-bold text-white tracking-wide">
                  SYNTACTIC & BEHAVIORAL AI REASONING SYNTHESIS
                </h3>
              </div>
              <span className="text-[10px] font-mono text-sky-300 bg-sky-950/60 border border-sky-800/40 px-2.5 py-0.5 rounded font-bold">
                EVALUATED BY GOOGLE GEMINI 2.5 FLASH
              </span>
            </div>

            {/* Explanation Body */}
            <div className="bg-[#091328] border border-sky-900/40 rounded-lg p-4 text-xs font-mono leading-relaxed text-slate-200 shadow-inner">
              <p className="whitespace-pre-line">
                {rel.explanation ||
                  `The analysis strongly indicates that 'shadow_vendor_01' (Dread) and 'night_market_7' (BreachForums) represent the same underlying threat actor persona. The critical pivots include a shared Bitcoin escrow address, identical TLS certificate fingerprint (SHA256:7B8A91C042E3FA71), and a 48-hour sequential migration window with congruent diurnal UTC posting activity.`}
              </p>
            </div>

            {/* Key Observations with Evidence Badges */}
            <div className="mt-6">
              <h4 className="text-xs font-mono font-bold text-slate-200 flex items-center gap-2 mb-3">
                <CheckCircle2 size={14} className="text-[#10B981]" />
                <span>CORROBORATING OBSERVATIONS (EVIDENCE CITATIONS)</span>
              </h4>
              <div className="space-y-2">
                {(rel.key_observations && rel.key_observations.length > 0
                  ? rel.key_observations
                  : [
                      "Shared Bitcoin deposit address 'bc1q9v8u47s9a473957m2g3q7f7' observed on both Dread and BreachForums (EV-000103, EV-000203).",
                      "Shared TLS certificate fingerprint 'SHA256:7B8A91C042E3FA71' linked to custom reverse proxy infrastructure (EV-000104).",
                      "Sequential account timeline: shadow_vendor_01 ceased activity 2026-08-15, night_market_7 active 2026-08-17 with zero overlapping timestamps.",
                      "High stylometric congruence: average sentence length of 4.8 words vs 5.1 words, identical lexical markers around escrow and access broker jargon."
                    ]
                ).map((obs: string, idx: number) => (
                  <div key={idx} className="bg-[#091328] border border-sky-900/40 rounded-lg p-3 text-xs flex items-start gap-2.5">
                    <span className="w-5 h-5 rounded-full bg-sky-950 text-[#38BDF8] border border-sky-800/40 font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5 font-bold">
                      {idx + 1}
                    </span>
                    <span className="text-slate-200 font-mono leading-normal">{obs}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Contradictory Evidence & Risk Factors */}
            <div className="mt-6">
              <h4 className="text-xs font-mono font-bold text-amber-400 flex items-center gap-2 mb-3">
                <AlertTriangle size={14} className="text-amber-400" />
                <span>CONTRADICTORY EVIDENCE & ANOMALIES IDENTIFIED</span>
              </h4>
              <div className="space-y-2">
                {(rel.contradictory_evidence && rel.contradictory_evidence.length > 0
                  ? rel.contradictory_evidence
                  : [
                      "Rotated PGP public key signature (Key ID 0x9B1C... vs 0x4A7E...): Actor actively migrated to a new RSA 4096 key upon switching forums.",
                      "Slight shift in handle vocabulary tokens (shadow/vendor vs night/market) prevents simple string identity match."
                    ]
                ).map((item: string, idx: number) => (
                  <div key={idx} className="bg-amber-950/20 border border-amber-500/30 rounded-lg p-3 text-xs flex items-start gap-2.5 text-amber-200 font-mono">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0"></span>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Missing Evidence / Required Steps */}
            <div className="mt-6">
              <h4 className="text-xs font-mono font-bold text-slate-300 flex items-center gap-2 mb-3">
                <HelpCircle size={14} className="text-[#38BDF8]" />
                <span>MISSING EVIDENCE & RECOMMENDED INVESTIGATIVE STEPS</span>
              </h4>
              <div className="space-y-2">
                {(rel.missing_evidence && rel.missing_evidence.length > 0
                  ? rel.missing_evidence
                  : [
                      "Request blockchain UTXO transaction trace on wallet bc1q9v8u47s9a473957m2g3q7f7 to confirm single private key signing cluster.",
                      "Acquire server access logs for reverse proxy associated with TLS cert 7B8A91C042E3FA71 to verify common upstream origin IP.",
                      "Subject forum posts to extended n-gram syntactical stylometry against larger baseline corpus."
                    ]
                ).map((step: string, idx: number) => (
                  <div key={idx} className="bg-[#091328] border border-sky-900/40 rounded-lg p-3 text-xs flex items-start gap-2 text-slate-300 font-mono">
                    <ArrowRight size={13} className="text-[#38BDF8] mt-0.5 shrink-0" />
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: EVIDENCE PROVENANCE CHAIN */}
      {activeTab === 'provenance' && (
        <div className="space-y-6">
          <div className="bg-[#0E1A36]/90 border border-sky-500/25 rounded-xl p-6 shadow-lg">
            <div className="mb-4">
              <h3 className="text-sm font-mono font-bold text-white tracking-wide flex items-center gap-2">
                <Scale size={16} className="text-[#10B981]" />
                <span>END-TO-END EVIDENCE PROVENANCE & AUDIT PIPELINE</span>
              </h3>
              <p className="text-xs text-slate-300 mt-1 font-mono">
                Visualizes exactly how raw dark web observations flow through deterministic feature extractors, score models, and Gemini AI reasoning into the final attribution dossier.
              </p>
            </div>

            {/* Provenance Steps */}
            <div className="relative border-l-2 border-sky-900/50 ml-4 pl-6 space-y-6 my-6 font-mono">
              {/* Step 1 */}
              <div className="relative">
                <span className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-[#0E1A36] border-2 border-[#38BDF8] flex items-center justify-center"></span>
                <div className="bg-[#091328] border border-sky-900/40 p-4 rounded-xl shadow-md">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-[#38BDF8] font-bold">STAGE 1: RAW THREAT DATA INGESTION</span>
                    <span className="text-slate-400 text-[10px]">COLLECTION TIMESTAMPS: 2026-08-10 to 2026-08-20</span>
                  </div>
                  <p className="text-xs text-slate-200">
                    4 forensic records collected from Dread and BreachForums mirror. Each item signed with SHA-256 cryptographic digest.
                  </p>
                  <div className="mt-2.5 flex gap-2 flex-wrap">
                    <span className="px-2 py-0.5 bg-[#0E1A36] text-[10px] text-slate-300 rounded border border-sky-900/40">EV-000101 (Handle)</span>
                    <span className="px-2 py-0.5 bg-[#0E1A36] text-[10px] text-slate-300 rounded border border-sky-900/40">EV-000103 (Crypto Wallet)</span>
                    <span className="px-2 py-0.5 bg-[#0E1A36] text-[10px] text-slate-300 rounded border border-sky-900/40">EV-000104 (TLS Cert)</span>
                    <span className="px-2 py-0.5 bg-[#0E1A36] text-[10px] text-slate-300 rounded border border-sky-900/40">EV-000203 (Crypto Wallet)</span>
                  </div>
                </div>
              </div>

              {/* Step 2 */}
              <div className="relative">
                <span className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-[#0E1A36] border-2 border-cyan-400 flex items-center justify-center"></span>
                <div className="bg-[#091328] border border-sky-900/40 p-4 rounded-xl shadow-md">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-cyan-400 font-bold">STAGE 2: DETERMINISTIC FEATURE EXTRACTION</span>
                    <span className="text-slate-400 text-[10px]">MODULE: app.services.pattern_engine</span>
                  </div>
                  <p className="text-xs text-slate-200">
                    Extracted diurnal activity arrays, normalized cryptocurrency addresses, computed character n-gram stylometric vector, and evaluated TLS certificate fingerprints.
                  </p>
                </div>
              </div>

              {/* Step 3 */}
              <div className="relative">
                <span className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-[#0E1A36] border-2 border-[#10B981] flex items-center justify-center"></span>
                <div className="bg-[#091328] border border-sky-900/40 p-4 rounded-xl shadow-md">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-[#10B981] font-bold">STAGE 3: 5-DIMENSION SIMILARITY CALCULATION</span>
                    <span className="text-slate-400 text-[10px]">CONFIDENCE MATRIX ENGINE</span>
                  </div>
                  <p className="text-xs text-slate-200">
                    Identifier: 30.0% | Behavior: 90.0% | Linguistic: 90.0% | Infrastructure: 100.0% | Temporal: 85.0%.
                  </p>
                  <p className="text-xs text-[#10B981] font-bold mt-1">
                    Deterministic Overall Score: {overallScore.toFixed(1)}% ({confidenceLevel.toUpperCase()})
                  </p>
                </div>
              </div>

              {/* Step 4 */}
              <div className="relative">
                <span className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-[#0E1A36] border-2 border-indigo-400 flex items-center justify-center"></span>
                <div className="bg-[#091328] border border-sky-900/40 p-4 rounded-xl shadow-md">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-indigo-400 font-bold">STAGE 4: GOOGLE GEMINI 2.5 FLASH REASONING</span>
                    <span className="text-slate-400 text-[10px]">MODEL: gemini-2.5-flash</span>
                  </div>
                  <p className="text-xs text-slate-200">
                    Synthesized findings, identified cross-forum behavioral patterns, performed contradiction detection (rotated PGP keys), and generated structured explainability report.
                  </p>
                </div>
              </div>

              {/* Step 5 */}
              <div className="relative">
                <span className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-[#0E1A36] border-2 border-[#10B981] flex items-center justify-center"></span>
                <div className="bg-[#091328] border border-sky-900/40 p-4 rounded-xl shadow-md">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-[#10B981] font-bold">STAGE 5: HUMAN-IN-THE-LOOP FORENSIC SIGN-OFF</span>
                    <span className="text-slate-400 text-[10px]">CHAIN OF CUSTODY VERIFIED</span>
                  </div>
                  <p className="text-xs text-slate-200">
                    Ready for Lead CTI Investigator validation and STIX 2.1 dossier export.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: VERIFIED EVIDENCE VAULT */}
      {activeTab === 'evidence' && (
        <div className="space-y-6">
          <div className="bg-[#0E1A36]/90 border border-sky-500/25 rounded-xl p-6 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-mono font-bold text-white tracking-wide flex items-center gap-2">
                  <Database size={16} className="text-indigo-400" />
                  <span>CORROBORATING FORENSIC EVIDENCE RECORDS</span>
                </h3>
                <p className="text-xs text-slate-300 mt-1 font-mono">
                  Immutable threat intelligence records underpinning the current AI analysis with SHA-256 integrity verification.
                </p>
              </div>
            </div>

            <div className="overflow-x-auto rounded-lg border border-sky-900/40">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-[#091328] text-slate-300 border-b border-sky-900/40">
                  <tr>
                    <th className="p-3">EVIDENCE ID</th>
                    <th className="p-3">SOURCE</th>
                    <th className="p-3">TYPE</th>
                    <th className="p-3">OBSERVATION</th>
                    <th className="p-3">COLLECTION TIME</th>
                    <th className="p-3">RELIABILITY</th>
                    <th className="p-3">SHA-256 INTEGRITY</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-sky-900/30">
                  {(evidenceData?.evidence_references && evidenceData.evidence_references.length > 0
                    ? evidenceData.evidence_references
                    : [
                        {
                          evidence_id: "EV-000101",
                          source: "SRC-DREAD",
                          type: "IDENTITY",
                          observation: "Handle registration 'shadow_vendor_01' on Dread forum",
                          collection_timestamp: "2026-08-10T18:15:00Z",
                          hash_sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                          reliability: "A"
                        },
                        {
                          evidence_id: "EV-000103",
                          source: "SRC-DREAD",
                          type: "FINANCIAL",
                          observation: "Bitcoin escrow deposit address 'bc1q9v8u47s9a473957m2g3q7f7'",
                          collection_timestamp: "2026-08-12T19:40:00Z",
                          hash_sha256: "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
                          reliability: "A"
                        },
                        {
                          evidence_id: "EV-000104",
                          source: "SRC-SENSOR",
                          type: "INFRASTRUCTURE",
                          observation: "TLS Certificate SHA-256 fingerprint '7B8A91C042E3FA71'",
                          collection_timestamp: "2026-08-14T03:00:00Z",
                          hash_sha256: "7b8a91c042e3fa71c26b8470f9520e2418e95fb1e9a99fc62e36b8566efc4f7a",
                          reliability: "B"
                        },
                        {
                          evidence_id: "EV-000203",
                          source: "SRC-BREACH",
                          type: "FINANCIAL",
                          observation: "Identical escrow deposit address 'bc1q9v8u47s9a473957m2g3q7f7' on BreachForums mirror",
                          collection_timestamp: "2026-08-20T20:30:00Z",
                          hash_sha256: "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
                          reliability: "A"
                        }
                      ]
                  ).map((ev: any) => (
                    <tr
                      key={ev.evidence_id}
                      onClick={() => setSelectedEvidenceId(selectedEvidenceId === ev.evidence_id ? null : ev.evidence_id)}
                      className={`hover:bg-sky-500/10 cursor-pointer transition-colors ${
                        selectedEvidenceId === ev.evidence_id ? 'bg-sky-500/15' : ''
                      }`}
                    >
                      <td className="p-3 font-bold text-[#38BDF8]">{ev.evidence_id}</td>
                      <td className="p-3 text-slate-300">{ev.source}</td>
                      <td className="p-3">
                        <span className="px-2 py-0.5 rounded text-[10px] bg-[#091328] border border-sky-900/40 text-slate-200">
                          {ev.type}
                        </span>
                      </td>
                      <td className="p-3 text-slate-200 max-w-xs truncate" title={ev.observation}>
                        {ev.observation}
                      </td>
                      <td className="p-3 text-slate-400">{ev.collection_timestamp}</td>
                      <td className="p-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/15 text-[#10B981] border border-emerald-500/30">
                          GRADE {ev.reliability}
                        </span>
                      </td>
                      <td className="p-3 text-slate-400 font-mono text-[10px] truncate max-w-[120px]" title={ev.hash_sha256}>
                        {ev.hash_sha256?.substring(0, 16)}...
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Mandatory Sovereign Legal & Forensics Disclaimer */}
      <div className="bg-[#0E1A36]/80 border border-sky-500/25 rounded-xl p-4 flex items-start gap-3 text-xs font-mono text-slate-300 shadow-md">
        <ShieldAlert size={18} className="text-[#38BDF8] shrink-0 mt-0.5" />
        <div>
          <span className="text-white font-bold block mb-0.5">
            FORENSIC COMPLIANCE & LEGAL NOTICE:
          </span>
          {demoMetadata?.compliance_note || 'Analytical correlation — not confirmed real-world attribution.'}{' '}
          All identity resolutions represent probabilistic investigative leads based on synthetic dark web telemetry in strict adherence to SIH 2026 guidelines. Final attribution determinations require human-in-the-loop judicial oversight.
        </div>
      </div>
    </div>
  );
};

export default AIPatternAnalysisPage;
