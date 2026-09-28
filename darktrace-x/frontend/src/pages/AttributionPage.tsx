import React, { useEffect, useState } from 'react';
import { Scale, CheckCircle2, AlertTriangle, ArrowRight, Shield, UserCheck, MessageSquare } from 'lucide-react';
import { attributionApi } from '../services/api';
import { AttributionAssessment } from '../types';

export const AttributionPage: React.FC = () => {
  const [assessments, setAssessments] = useState<AttributionAssessment[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [reviewingId, setReviewingId] = useState<string | null>(null);
  const [analystComment, setAnalystComment] = useState<string>('');

  useEffect(() => {
    loadAssessments();
  }, []);

  const loadAssessments = () => {
    setLoading(true);
    attributionApi.getByActorId('ACT-0042')
      .then((data) => {
        setAssessments(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  const handleReview = async (assessmentId: string, isConfirmed: boolean) => {
    try {
      await attributionApi.review(assessmentId, isConfirmed, analystComment || 'Reviewed by lead CTI investigator.');
      alert(isConfirmed ? 'Attribution relationship confirmed with human-in-the-loop validation.' : 'Attribution marked as unconfirmed pending further corroboration.');
      setReviewingId(null);
      setAnalystComment('');
      loadAssessments();
    } catch (err) {
      console.error(err);
      alert('Failed to submit assessment review.');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Scale size={20} className="text-[#FFB020]" />
          ATTRIBUTION & CONTRADICTION REVIEW
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Evidence fusion engine outputs paired with automated contradiction detection. Automated identity assertions are prohibited; human investigator review is required.
        </p>
      </div>

      {loading ? (
        <div className="text-center py-20 font-mono text-xs text-slate-500">
          LOADING ATTRIBUTION ASSESSMENTS...
        </div>
      ) : (
        <div className="space-y-6">
          {assessments.map((ass) => (
            <div key={ass.id} className="glass-panel p-6 space-y-5 border-l-4 border-l-[#FFB020]">
              <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30">
                      {ass.assessment_type.replace(/_/g, ' ')}
                    </span>
                    <span className="text-xs font-mono text-slate-400">ID: {ass.id}</span>
                  </div>
                  <h3 className="text-lg font-bold text-slate-100 mt-2">
                    {ass.candidate_persona_a} &harr; {ass.candidate_persona_b}
                  </h3>
                </div>

                <div className="text-right font-mono">
                  <span className="text-sm font-bold text-[#00FF88]">
                    Confidence: {ass.analytical_confidence} ({Math.round(ass.confidence_score * 100)}%)
                  </span>
                  <div className="mt-1">
                    {ass.is_confirmed_by_analyst ? (
                      <span className="text-xs font-bold text-emerald-400 flex items-center gap-1 justify-end">
                        <CheckCircle2 size={13} /> CONFIRMED BY ANALYST
                      </span>
                    ) : (
                      <span className="text-xs font-bold text-amber-400 flex items-center gap-1 justify-end">
                        <AlertTriangle size={13} /> {ass.recommendation}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Reasoning Summary */}
              <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-800 text-xs text-slate-300 leading-relaxed font-sans">
                <strong className="text-slate-100 block mb-1 font-mono uppercase text-[10px] text-[#00D9FF]">
                  Attribution Analysis Reasoning:
                </strong>
                {ass.reasoning_summary}
              </div>

              {/* Evidence Grid: Supporting vs Contradicting */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Supporting */}
                <div className="p-4 rounded-lg bg-emerald-950/10 border border-emerald-900/40 space-y-3">
                  <h4 className="text-xs font-mono font-bold text-[#00FF88] uppercase tracking-wider flex items-center gap-1.5">
                    <CheckCircle2 size={14} />
                    SUPPORTING EVIDENCE SIGNALS ({ass.supporting_evidence?.length || 3})
                  </h4>
                  <div className="space-y-2 text-xs">
                    {ass.supporting_evidence ? ass.supporting_evidence.map((s) => (
                      <div key={s.id} className="p-2.5 rounded bg-slate-900/70 border border-slate-800">
                        <div className="flex justify-between font-mono text-[11px]">
                          <span className="text-[#00FF88] font-bold">[{s.id}] {s.title}</span>
                          <span className="text-slate-400">{s.evidence_type}</span>
                        </div>
                        <p className="text-slate-300 mt-1 text-[11px] leading-relaxed">{s.description}</p>
                      </div>
                    )) : (
                      <>
                        <div className="p-2 rounded bg-slate-900/70 text-[11px] font-mono text-slate-300">[EVID-0001] Shared PGP 4096-bit Public Key Signature</div>
                        <div className="p-2 rounded bg-slate-900/70 text-[11px] font-mono text-slate-300">[EVID-0002] Origin Clearnet IP via Apache Status Leak (194.26.29.114)</div>
                        <div className="p-2 rounded bg-slate-900/70 text-[11px] font-mono text-slate-300">[EVID-0003] AI Stylometric Persona Similarity Match (88.4%)</div>
                      </>
                    )}
                  </div>
                </div>

                {/* Contradicting */}
                <div className="p-4 rounded-lg bg-red-950/10 border border-red-900/40 space-y-3">
                  <h4 className="text-xs font-mono font-bold text-[#FF4D6D] uppercase tracking-wider flex items-center gap-1.5">
                    <AlertTriangle size={14} />
                    CONTRADICTING EVIDENCE SIGNALS ({ass.contradicting_evidence?.length || 1})
                  </h4>
                  <div className="space-y-2 text-xs">
                    {ass.contradicting_evidence ? ass.contradicting_evidence.map((c) => (
                      <div key={c.id} className="p-2.5 rounded bg-slate-900/70 border border-slate-800">
                        <div className="flex justify-between font-mono text-[11px]">
                          <span className="text-[#FF4D6D] font-bold">[{c.id}] {c.title}</span>
                          <span className="text-slate-400">{c.evidence_type}</span>
                        </div>
                        <p className="text-slate-300 mt-1 text-[11px] leading-relaxed">{c.description}</p>
                      </div>
                    )) : (
                      <div className="p-2.5 rounded bg-slate-900/70 text-[11px] font-mono text-slate-300">
                        [EVID-0004] Divergent Operational Activity Timelines: Non-overlapping activity periods and 4-hour variance in peak UTC posting distributions.
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Review Actions */}
              <div className="pt-4 border-t border-slate-800 flex flex-wrap items-center justify-between gap-4">
                <span className="text-xs font-mono text-slate-400">
                  Principle: Fused evidence with active contradiction check requires investigator sign-off.
                </span>

                <div className="flex items-center gap-3">
                  {reviewingId === ass.id ? (
                    <div className="flex items-center gap-2">
                      <input
                        type="text"
                        placeholder="Add analyst validation rationale..."
                        value={analystComment}
                        onChange={(e) => setAnalystComment(e.target.value)}
                        className="bg-slate-900 border border-slate-700 text-xs px-3 py-1.5 rounded text-slate-200 outline-none font-mono"
                      />
                      <button
                        onClick={() => handleReview(ass.id, true)}
                        className="px-3 py-1.5 bg-[#00FF88] text-[#05070A] font-bold text-xs rounded hover:opacity-90"
                      >
                        Confirm Link
                      </button>
                      <button
                        onClick={() => handleReview(ass.id, false)}
                        className="px-3 py-1.5 bg-red-600 text-white font-bold text-xs rounded hover:opacity-90"
                      >
                        Reject Link
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setReviewingId(ass.id)}
                      className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded border border-slate-700 flex items-center gap-1.5"
                    >
                      <UserCheck size={14} className="text-[#00D9FF]" />
                      Conduct Investigator Review
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
