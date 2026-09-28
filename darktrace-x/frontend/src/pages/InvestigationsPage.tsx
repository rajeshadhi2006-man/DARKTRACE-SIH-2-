import React, { useState, useEffect } from 'react';
import {
  FolderGit2,
  PlusCircle,
  PlayCircle,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ShieldAlert,
  Search,
  ArrowRight,
  Download,
  Fingerprint,
  Cpu,
  Layers,
  FileCheck,
  Eye,
  Clock
} from 'lucide-react';
import { investigationsApi, stixApi } from '../services/api';

interface InvestigationItem {
  id: string;
  case_id: string;
  title: string;
  description: string;
  analyst_name: string;
  status: string;
  priority: string;
  scope: string;
  seed_indicators: any[];
  actor_id: string | null;
  confidence_assessment: number;
  created_at: string;
}

export const InvestigationsPage: React.FC = () => {
  const [investigations, setInvestigations] = useState<InvestigationItem[]>([]);
  const [selectedInv, setSelectedInv] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [correlating, setCorrelating] = useState(false);
  const [correlationResults, setCorrelationResults] = useState<any>(null);

  // New Case Modal State
  const [showModal, setShowModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newCaseId, setNewCaseId] = useState('');
  const [newScope, setNewScope] = useState('Dark Web Threat Actor De-Anonymization');
  const [newSeedType, setNewSeedType] = useState('alias');
  const [newSeedValue, setNewSeedValue] = useState('nightfox_404');
  const [newPriority, setNewPriority] = useState('CRITICAL');

  const fetchInvestigations = async () => {
    try {
      setLoading(true);
      const data = await investigationsApi.list();
      setInvestigations(data);
      if (data.length > 0 && !selectedInv) {
        loadInvestigationDetails(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load investigations', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvestigations();
  }, []);

  const loadInvestigationDetails = async (id: string) => {
    try {
      const data = await investigationsApi.getById(id);
      setSelectedInv(data);
      setCorrelationResults(null);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle) return;
    try {
      await investigationsApi.create({
        title: newTitle,
        case_id: newCaseId || `CASE-SIH-${Math.floor(Math.random() * 900 + 100)}`,
        scope: newScope,
        priority: newPriority,
        seed_indicators: [{ type: newSeedType, value: newSeedValue }]
      });
      setShowModal(false);
      setNewTitle('');
      fetchInvestigations();
    } catch (err) {
      console.error(err);
    }
  };

  const handleStartCorrelation = async () => {
    if (!selectedInv) return;
    setCorrelating(true);
    setCorrelationResults(null);

    const seed = selectedInv.seed_indicators?.[0]?.value || 'nightfox_404';

    try {
      const res = await investigationsApi.correlate(selectedInv.id, 'alias', seed);
      setTimeout(() => {
        setCorrelationResults(res);
        setCorrelating(false);
        // Refresh details
        loadInvestigationDetails(selectedInv.id);
      }, 1200);
    } catch (err) {
      console.error(err);
      setCorrelating(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!selectedInv) return;
    try {
      await investigationsApi.updateStatus(selectedInv.id, newStatus, `Analyst marked status as ${newStatus}`);
      loadInvestigationDetails(selectedInv.id);
      fetchInvestigations();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#00D9FF]/20 pb-4">
        <div>
          <div className="flex items-center gap-3">
            <FolderGit2 className="text-[#00FF88]" size={28} />
            <h1 className="text-2xl font-black tracking-wider text-slate-100">
              INVESTIGATION WORKSPACE & CASE ENGINE
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Interactive de-anonymization workbench: Seed ingestion, automated correlation pipeline, and human-in-the-loop validation.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-[#00FF88] text-[#05070A] font-bold text-xs uppercase tracking-wider hover:bg-[#00FF88]/90 transition shadow-[0_0_15px_rgba(0,255,136,0.3)]"
        >
          <PlusCircle size={16} />
          New Investigation
        </button>
      </div>

      {/* Main Grid: Cases List on Left, Active Workbench on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Cases Sidebar (4 Cols) */}
        <div className="lg:col-span-4 space-y-3">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 px-1">
            <span>ACTIVE CASES ({investigations.length})</span>
            <span className="text-[#00FF88]">TLP:AMBER</span>
          </div>

          <div className="space-y-2.5 max-h-[720px] overflow-y-auto pr-1">
            {investigations.map((inv) => {
              const isSelected = selectedInv?.id === inv.id;
              return (
                <div
                  key={inv.id}
                  onClick={() => loadInvestigationDetails(inv.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-[#00D9FF]/10 border-[#00D9FF] shadow-[0_0_15px_rgba(0,217,255,0.2)]'
                      : 'bg-[#0A0F1A]/80 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono font-bold text-[#00D9FF]">
                      {inv.case_id}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        inv.priority === 'CRITICAL'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                      }`}
                    >
                      {inv.priority}
                    </span>
                  </div>

                  <h3 className="text-sm font-semibold text-slate-100 mt-2 line-clamp-1">
                    {inv.title}
                  </h3>

                  <div className="flex items-center justify-between mt-3 text-[11px] text-slate-400">
                    <span>{inv.status}</span>
                    <span className="font-mono text-[#00FF88]">
                      {inv.confidence_assessment ? `${Math.round(inv.confidence_assessment * 100)}% Confidence` : 'Pending'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Investigation Workbench Canvas (8 Cols) */}
        <div className="lg:col-span-8 space-y-5">
          {selectedInv ? (
            <div className="bg-[#0A0F1A]/90 border border-[#00D9FF]/20 rounded-2xl p-6 space-y-6 shadow-xl">
              {/* Case Header */}
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 border-b border-slate-800 pb-5">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-0.5 rounded bg-[#00D9FF]/20 text-[#00D9FF] font-mono text-xs font-bold border border-[#00D9FF]/30">
                      {selectedInv.case_id}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      Analyst: {selectedInv.analyst_name}
                    </span>
                  </div>
                  <h2 className="text-xl font-bold text-slate-100 mt-2">
                    {selectedInv.title}
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">
                    {selectedInv.description || 'Targeted de-anonymization investigation into underground activity.'}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  {selectedInv.actor_id && (
                    <button
                      onClick={() => stixApi.exportActor(selectedInv.actor_id)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-300 border border-slate-700"
                    >
                      <Download size={14} />
                      Export STIX 2.1
                    </button>
                  )}
                  <button
                    onClick={handleStartCorrelation}
                    disabled={correlating}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-[#00D9FF] to-[#00FF88] text-[#05070A] font-extrabold text-xs uppercase tracking-wider hover:opacity-90 shadow-[0_0_15px_rgba(0,255,136,0.3)] disabled:opacity-50"
                  >
                    <PlayCircle size={16} />
                    {correlating ? 'Correlating Pipeline...' : 'Start Correlation'}
                  </button>
                </div>
              </div>

              {/* Seed Indicators Box */}
              <div className="bg-[#05070A] border border-slate-800 rounded-xl p-4">
                <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-2">
                  <Fingerprint size={14} className="text-[#00FF88]" />
                  Active Seed Indicators
                </div>
                <div className="flex flex-wrap gap-2">
                  {selectedInv.seed_indicators && selectedInv.seed_indicators.length > 0 ? (
                    selectedInv.seed_indicators.map((seed: any, idx: number) => (
                      <div
                        key={idx}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#00FF88]/10 border border-[#00FF88]/30 text-xs font-mono text-[#00FF88]"
                      >
                        <span className="uppercase text-[10px] text-slate-400">[{seed.type}]</span>
                        <span className="font-bold">{seed.value}</span>
                      </div>
                    ))
                  ) : (
                    <div className="text-xs text-slate-500 font-mono">No seed indicators assigned.</div>
                  )}
                </div>
              </div>

              {/* Correlation Pipeline Progress or Telemetry */}
              {correlating && (
                <div className="p-6 rounded-xl border border-[#00D9FF]/40 bg-[#00D9FF]/5 space-y-4 animate-pulse">
                  <div className="flex items-center justify-between text-xs font-mono text-[#00D9FF]">
                    <span>RUNNING 7-STAGE ATTRIBUTION PIPELINE</span>
                    <span>PROCESSING...</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div className="bg-gradient-to-r from-[#00D9FF] to-[#00FF88] h-full w-3/4 animate-pulse"></div>
                  </div>
                  <p className="text-xs text-slate-400 font-mono">
                    Harvesting authorized intercepts → Entity Resolution → Passive TLS SAN match → AI Stylometric Writeprints → Diurnal variance check...
                  </p>
                </div>
              )}

              {/* Pipeline Results View */}
              {correlationResults && (
                <div className="space-y-4">
                  {/* Assessment Card */}
                  <div className="p-5 rounded-xl border border-[#00FF88]/40 bg-[#00FF88]/10 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-sm font-bold text-[#00FF88]">
                        <CheckCircle2 size={18} />
                        ATTRIBUTION ASSESSMENT RESULT
                      </div>
                      <span className="px-2.5 py-0.5 rounded bg-[#00FF88] text-[#05070A] font-black text-xs font-mono">
                        {correlationResults.actor?.confidence}% CONFIDENCE
                      </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2 text-xs font-mono">
                      <div className="bg-[#05070A]/60 p-2.5 rounded-lg border border-slate-800">
                        <span className="text-slate-400 text-[10px] block">TARGET THREAT ACTOR</span>
                        <span className="font-bold text-slate-100">{correlationResults.actor?.name}</span>
                      </div>
                      <div className="bg-[#05070A]/60 p-2.5 rounded-lg border border-slate-800">
                        <span className="text-slate-400 text-[10px] block">SUPPORTING EVIDENCE</span>
                        <span className="font-bold text-[#00FF88]">{correlationResults.supporting_evidence_count} Artifacts</span>
                      </div>
                      <div className="bg-[#05070A]/60 p-2.5 rounded-lg border border-slate-800">
                        <span className="text-slate-400 text-[10px] block">CONTRADICTING EVIDENCE</span>
                        <span className="font-bold text-amber-400">{correlationResults.contradicting_evidence_count} Detected</span>
                      </div>
                      <div className="bg-[#05070A]/60 p-2.5 rounded-lg border border-slate-800">
                        <span className="text-slate-400 text-[10px] block">STATUS</span>
                        <span className="font-bold text-rose-400">{correlationResults.actor?.status?.replace(/_/g, ' ')}</span>
                      </div>
                    </div>
                  </div>

                  {/* 7-Stage Pipeline Telemetry */}
                  <div className="space-y-2">
                    <div className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                      PIPELINE EXECUTION TRACE
                    </div>
                    <div className="space-y-1.5 font-mono text-xs">
                      {correlationResults.pipeline_steps?.map((step: any, idx: number) => (
                        <div
                          key={idx}
                          className="flex items-start gap-3 p-2.5 rounded-lg bg-[#05070A]/80 border border-slate-800"
                        >
                          <span className="text-[#00FF88] font-bold text-[10px] mt-0.5">[{idx + 1}]</span>
                          <div className="flex-1">
                            <span className="text-[#00D9FF] font-semibold">{step.stage}</span>
                            <p className="text-slate-400 text-[11px] mt-0.5">{step.detail}</p>
                          </div>
                          <span className="text-[#00FF88] text-[10px]">OK</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Human-In-The-Loop Validation Controls */}
              <div className="border-t border-slate-800 pt-5 space-y-3">
                <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                  <span>HUMAN-IN-THE-LOOP ANALYST ARBITRATION</span>
                  <span className="text-amber-400">MANDATORY SIGN-OFF</span>
                </div>

                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={() => handleStatusChange('CONFIRMED_BY_ANALYST')}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#00FF88]/20 hover:bg-[#00FF88]/30 text-[#00FF88] border border-[#00FF88]/40 text-xs font-bold transition"
                  >
                    <CheckCircle2 size={16} />
                    Confirm Attribution
                  </button>
                  <button
                    onClick={() => handleStatusChange('REJECTED_DISJOINT')}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-400 border border-rose-500/40 text-xs font-bold transition"
                  >
                    <XCircle size={16} />
                    Reject (Separate Personas)
                  </button>
                  <button
                    onClick={() => handleStatusChange('NEEDS_MORE_EVIDENCE')}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-400 border border-amber-500/40 text-xs font-bold transition"
                  >
                    <AlertTriangle size={16} />
                    Needs More Evidence
                  </button>
                  <button
                    onClick={() => handleStatusChange('CLOSED')}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold transition ml-auto"
                  >
                    Close Case
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl bg-[#0A0F1A]/50">
              <Layers className="mx-auto text-slate-600 mb-3" size={40} />
              <p className="text-sm font-semibold text-slate-400">Select an investigation to open workspace</p>
            </div>
          )}
        </div>
      </div>

      {/* New Investigation Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-[#0A0F1A] border border-[#00D9FF]/30 rounded-2xl p-6 max-w-lg w-full space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <PlusCircle className="text-[#00FF88]" size={20} />
              Create New Investigation Case
            </h3>

            <form onSubmit={handleCreateCase} className="space-y-4 text-xs font-mono">
              <div>
                <label className="text-slate-400 block mb-1">CASE TITLE</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. De-anonymization of Operator NightFox"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full bg-[#05070A] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:border-[#00FF88] outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">CASE ID (OPTIONAL)</label>
                  <input
                    type="text"
                    placeholder="CASE-SIH-001"
                    value={newCaseId}
                    onChange={(e) => setNewCaseId(e.target.value)}
                    className="w-full bg-[#05070A] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:border-[#00FF88] outline-none"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">PRIORITY</label>
                  <select
                    value={newPriority}
                    onChange={(e) => setNewPriority(e.target.value)}
                    className="w-full bg-[#05070A] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:border-[#00FF88] outline-none"
                  >
                    <option value="CRITICAL">CRITICAL</option>
                    <option value="HIGH">HIGH</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="LOW">LOW</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">INITIAL SEED INDICATOR</label>
                <div className="grid grid-cols-3 gap-2">
                  <select
                    value={newSeedType}
                    onChange={(e) => setNewSeedType(e.target.value)}
                    className="bg-[#05070A] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:border-[#00FF88] outline-none"
                  >
                    <option value="alias">Alias / Handle</option>
                    <option value="pgp">PGP Fingerprint</option>
                    <option value="wallet">Crypto Wallet</option>
                    <option value="domain">Onion / Domain</option>
                    <option value="ip">IP Address</option>
                  </select>
                  <input
                    type="text"
                    required
                    placeholder="e.g. nightfox_404"
                    value={newSeedValue}
                    onChange={(e) => setNewSeedValue(e.target.value)}
                    className="col-span-2 bg-[#05070A] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:border-[#00FF88] outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">SCOPE & OBJECTIVES</label>
                <input
                  type="text"
                  value={newScope}
                  onChange={(e) => setNewScope(e.target.value)}
                  className="w-full bg-[#05070A] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:border-[#00FF88] outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-lg bg-[#00FF88] text-[#05070A] font-bold shadow-[0_0_12px_rgba(0,255,136,0.3)]"
                >
                  Create Case
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
