import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Shield, Users, Key, Wallet, Server, Network,
  Calendar, FileText, AlertTriangle, Scale, CheckCircle2,
  Clock, ArrowRight, Download, Brain
} from 'lucide-react';
import { actorsApi, reportsApi, attributionApi } from '../services/api';

export const ActorDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [actor, setActor] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [reportGenerating, setReportGenerating] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'OVERVIEW' | 'PERSONAS' | 'ATTRIBUTION' | 'NOTES'>('OVERVIEW');

  useEffect(() => {
    if (id) {
      actorsApi.getById(id)
        .then((data) => {
          setActor(data);
          setLoading(false);
        })
        .catch((err) => {
          console.error(err);
          setLoading(false);
        });
    }
  }, [id]);

  const handleGenerateReport = async () => {
    if (!id) return;
    setReportGenerating(true);
    try {
      const res = await reportsApi.generate(id, 'PDF');
      window.open(res.download_url, '_blank');
    } catch (err) {
      console.error(err);
      alert('Failed to generate forensic report.');
    } finally {
      setReportGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-20 font-mono text-xs text-slate-500">
        LOADING FORENSIC DOSSIER FOR {id}...
      </div>
    );
  }

  if (!actor) {
    return (
      <div className="p-6 text-center text-sm text-[#FF4D6D]">
        Threat Actor {id} not found in the intelligence repository.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Actor Header Banner */}
      <div className="glass-panel p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold text-[#00D9FF] bg-[#00D9FF]/10 px-2.5 py-1 rounded border border-[#00D9FF]/30">
                {actor.id}
              </span>
              <span className="text-xs font-mono font-bold text-red-400 bg-red-500/10 px-2.5 py-1 rounded border border-red-500/30">
                {actor.threat_level} THREAT
              </span>
              <span className="text-xs font-mono font-bold text-[#00FF88] bg-[#00FF88]/10 px-2.5 py-1 rounded border border-[#00FF88]/30">
                CONFIDENCE: {actor.analytical_confidence} ({Math.round(actor.confidence_score * 100)}%)
              </span>
            </div>

            <h1 className="text-2xl font-extrabold text-slate-100 mt-2 tracking-wide">
              {actor.primary_name}
            </h1>
            <p className="text-xs font-mono text-slate-400 mt-0.5">
              Category: <strong className="text-slate-200">{actor.threat_category}</strong> • Status: <strong className="text-emerald-400">{actor.status}</strong>
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate(`/graph?actor_id=${actor.id}`)}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-semibold rounded-lg border border-slate-700 flex items-center gap-2 transition-colors"
            >
              <Network size={14} className="text-[#00D9FF]" />
              Explore Graph
            </button>
            <button
              onClick={() => navigate(`/timeline?actor_id=${actor.id}`)}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-semibold rounded-lg border border-slate-700 flex items-center gap-2 transition-colors"
            >
              <Calendar size={14} className="text-[#00FF88]" />
              Timeline
            </button>
            <button
              onClick={handleGenerateReport}
              disabled={reportGenerating}
              className="px-4 py-2 bg-gradient-to-r from-[#00D9FF] to-[#00FF88] text-[#05070A] text-xs font-bold rounded-lg shadow-[0_0_15px_rgba(0,255,136,0.3)] hover:opacity-90 flex items-center gap-2 transition-all disabled:opacity-50"
            >
              <Download size={14} />
              {reportGenerating ? 'Generating PDF...' : 'Export Dossier PDF'}
            </button>
          </div>
        </div>

        {/* Dossier Tabs */}
        <div className="flex gap-4 border-t border-slate-800/80 mt-6 pt-3 text-xs font-semibold">
          {['OVERVIEW', 'PERSONAS', 'ATTRIBUTION', 'NOTES'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`pb-2 px-1 border-b-2 tracking-wider transition-colors ${
                activeTab === tab
                  ? 'border-[#00FF88] text-[#00FF88]'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Tab: OVERVIEW */}
      {activeTab === 'OVERVIEW' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {/* Executive Summary */}
            <div className="glass-panel p-5">
              <h3 className="text-sm font-bold text-slate-200 mb-2 flex items-center gap-2">
                <FileText size={16} className="text-[#00D9FF]" />
                FORENSIC SUMMARY & OBSERVATIONAL PROVENANCE
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed font-sans">
                {actor.summary}
              </p>
              <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] font-mono text-slate-500">
                Provenance: <span className="text-slate-400">{actor.provenance}</span>
              </div>
            </div>

            {/* Candidate Attribution Highlight */}
            {actor.attribution_assessments && actor.attribution_assessments.length > 0 && (
              <div className="glass-panel p-5 border-l-4 border-l-[#FFB020]">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-mono font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30 flex items-center gap-1.5">
                    <AlertTriangle size={12} />
                    {actor.attribution_assessments[0].assessment_type.replace(/_/g, ' ')}
                  </span>
                  <span className="text-xs font-mono text-[#00FF88]">
                    Confidence: {actor.attribution_assessments[0].analytical_confidence}
                  </span>
                </div>

                <h4 className="text-sm font-bold text-slate-200">
                  {actor.attribution_assessments[0].candidate_persona_a} &harr; {actor.attribution_assessments[0].candidate_persona_b}
                </h4>
                <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                  {actor.attribution_assessments[0].reasoning_summary}
                </p>

                <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-400">
                    Recommendation: <strong className="text-amber-400">{actor.attribution_assessments[0].recommendation}</strong>
                  </span>
                  <button
                    onClick={() => setActiveTab('ATTRIBUTION')}
                    className="text-xs font-semibold text-[#00D9FF] flex items-center gap-1 hover:underline"
                  >
                    Review Supporting & Contradicting Evidence <ArrowRight size={13} />
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Quick Details Sidebar */}
          <div className="space-y-6">
            <div className="glass-panel p-5">
              <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider mb-4">
                OBSERVATION TIMELINE
              </h3>
              <div className="space-y-3 text-xs font-mono">
                <div>
                  <span className="text-slate-500 block text-[10px]">First Observed</span>
                  <span className="text-slate-200 font-semibold">{actor.first_observed ? new Date(actor.first_observed).toLocaleDateString() : 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">Last Observed</span>
                  <span className="text-slate-200 font-semibold">{actor.last_observed ? new Date(actor.last_observed).toLocaleDateString() : 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">Active Tracked Personas</span>
                  <span className="text-[#00D9FF] font-semibold">{actor.personas.length} Personas</span>
                </div>
              </div>
            </div>

            <div className="glass-panel p-5">
              <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider mb-4">
                ANALYST ACTIONS
              </h3>
              <div className="space-y-2">
                <button
                  onClick={() => navigate(`/attribution`)}
                  className="w-full py-2 px-3 text-left text-xs rounded bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 flex items-center justify-between"
                >
                  <span>Attribution Review Queue</span>
                  <Scale size={14} className="text-[#FFB020]" />
                </button>
                <button
                  onClick={() => navigate(`/graph?actor_id=${actor.id}`)}
                  className="w-full py-2 px-3 text-left text-xs rounded bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 flex items-center justify-between"
                >
                  <span>Interactive Node Expansion</span>
                  <Network size={14} className="text-[#00D9FF]" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab: PERSONAS */}
      {activeTab === 'PERSONAS' && (
        <div className="space-y-4">
          {actor.personas.map((p: any) => (
            <div key={p.id} className="glass-panel p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="text-base font-bold text-[#00D9FF]">{p.canonical_handle}</h4>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                    {p.platform}
                  </span>
                  <span className="text-[10px] font-mono text-slate-500">ID: {p.id}</span>
                </div>
                <div className="mt-2 text-xs text-slate-400 space-y-1">
                  <div>Known Aliases / Handles: {p.handles && p.handles.length > 0 ? p.handles.map((h: string) => <code key={h} className="text-[#00FF88] mr-2">{h}</code>) : 'None'}</div>
                  <div>Provenance: {p.provenance}</div>
                </div>
              </div>

              <div className="text-right">
                <span className="text-xs font-mono font-bold text-[#00FF88] block">Activity Count: {p.activity_count}</span>
                <span className="text-[10px] font-mono text-slate-500">Confidence: {Math.round(p.confidence * 100)}%</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab: ATTRIBUTION */}
      {activeTab === 'ATTRIBUTION' && (
        <div className="space-y-6">
          {actor.attribution_assessments.map((ass: any) => (
            <div key={ass.id} className="glass-panel p-6 space-y-5">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div>
                  <span className="text-xs font-mono font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30">
                    {ass.assessment_type.replace(/_/g, ' ')}
                  </span>
                  <h3 className="text-lg font-bold text-slate-100 mt-2">
                    {ass.candidate_persona_a} &harr; {ass.candidate_persona_b}
                  </h3>
                </div>
                <div className="text-right font-mono">
                  <span className="text-sm font-bold text-[#00FF88]">Confidence: {ass.analytical_confidence} ({Math.round(ass.confidence_score * 100)}%)</span>
                  <span className="text-[11px] text-slate-400 block mt-0.5">Status: {ass.is_confirmed ? 'CONFIRMED BY ANALYST' : 'MANUAL REVIEW REQUIRED'}</span>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed font-sans">
                {ass.reasoning_summary}
              </p>

              {/* Supporting Evidence */}
              <div>
                <h4 className="text-xs font-mono font-bold text-[#00FF88] uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <CheckCircle2 size={13} />
                  SUPPORTING EVIDENCE ({ass.supporting_evidence_ids.length})
                </h4>
                <div className="space-y-2">
                  {ass.supporting_evidence_ids.map((eid: string) => (
                    <div key={eid} className="p-3 rounded bg-slate-900/60 border border-emerald-950 flex items-center justify-between text-xs">
                      <div>
                        <span className="font-mono font-bold text-[#00FF88] mr-2">[{eid}]</span>
                        <span className="text-slate-300">Correlated identity / infrastructure artifact</span>
                      </div>
                      <button onClick={() => navigate(`/evidence/${eid}`)} className="text-[#00D9FF] hover:underline font-mono text-[11px]">
                        Inspect Hash &rarr;
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Contradicting Evidence */}
              <div>
                <h4 className="text-xs font-mono font-bold text-[#FF4D6D] uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <AlertTriangle size={13} />
                  CONTRADICTING EVIDENCE ({ass.contradicting_evidence_ids.length})
                </h4>
                <div className="space-y-2">
                  {ass.contradicting_evidence_ids.map((eid: string) => (
                    <div key={eid} className="p-3 rounded bg-red-950/20 border border-red-900/50 flex items-center justify-between text-xs">
                      <div>
                        <span className="font-mono font-bold text-[#FF4D6D] mr-2">[{eid}]</span>
                        <span className="text-slate-300">Divergent diurnal activity and absence of temporal overlap</span>
                      </div>
                      <button onClick={() => navigate(`/evidence/${eid}`)} className="text-[#00D9FF] hover:underline font-mono text-[11px]">
                        Inspect Hash &rarr;
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab: NOTES */}
      {activeTab === 'NOTES' && (
        <div className="space-y-4">
          {actor.analyst_notes.map((note: any) => (
            <div key={note.id} className="glass-panel p-5 space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-bold text-slate-200">{note.title}</h4>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
                  {note.classification}
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed font-sans">{note.content}</p>
              <div className="text-[10px] font-mono text-slate-500 pt-2 border-t border-slate-800">
                Created: {new Date(note.created_at).toLocaleString()} UTC
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
