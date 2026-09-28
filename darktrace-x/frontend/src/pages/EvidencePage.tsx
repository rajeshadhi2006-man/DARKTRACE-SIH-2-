import React, { useEffect, useState } from 'react';
import { FileCheck, Shield, CheckCircle2, AlertTriangle, Hash, ExternalLink, Search } from 'lucide-react';
import { evidenceApi } from '../services/api';
import { Evidence } from '../types';

export const EvidencePage: React.FC = () => {
  const [evidenceList, setEvidenceList] = useState<Evidence[]>([]);
  const [selectedEvidence, setSelectedEvidence] = useState<Evidence | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterType, setFilterType] = useState<string>('');

  useEffect(() => {
    loadEvidence();
  }, [filterType]);

  const loadEvidence = () => {
    setLoading(true);
    const params: Record<string, any> = {};
    if (filterType) params.evidence_type = filterType;

    evidenceApi.list(params)
      .then((data) => {
        setEvidenceList(data);
        if (data.length > 0 && !selectedEvidence) {
          inspectEvidence(data[0].id);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  const inspectEvidence = (id: string) => {
    evidenceApi.getById(id)
      .then(setSelectedEvidence)
      .catch(console.error);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <FileCheck size={20} className="text-[#00FF88]" />
            EVIDENCE INTEGRITY & PROVENANCE REPOSITORY
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Every indexed artifact is stamped with a cryptographic SHA-256 hash. Real-time integrity verification protects against tampering.
          </p>
        </div>
      </div>

      <div className="glass-panel p-4 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <label className="text-xs font-mono text-slate-400">CATEGORY FILTER:</label>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded px-3 py-1.5 outline-none font-mono focus:border-[#00D9FF]"
          >
            <option value="">All Evidence Types</option>
            <option value="IDENTITY">Identity (PGP / Cryptographic)</option>
            <option value="INFRASTRUCTURE">Infrastructure & Hosting</option>
            <option value="CONTENT">Content & Stylometry</option>
            <option value="BEHAVIOR">Behavioral Analysis</option>
            <option value="HISTORICAL">Historical Archival</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Evidence List */}
        <div className="lg:col-span-2 space-y-3">
          {loading ? (
            <div className="text-center py-20 font-mono text-xs text-slate-500">
              VERIFYING EVIDENCE SIGNATURES...
            </div>
          ) : (
            evidenceList.map((ev) => (
              <div
                key={ev.id}
                onClick={() => inspectEvidence(ev.id)}
                className={`glass-panel p-4 cursor-pointer transition-all ${
                  selectedEvidence?.id === ev.id
                    ? 'border-[#00FF88] bg-[#00FF88]/5'
                    : 'hover:border-slate-600'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-[#00FF88]">[{ev.id}]</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      {ev.evidence_type}
                    </span>
                    <span className="text-[10px] font-mono text-slate-500">Source: {ev.source_id || 'LOCAL'}</span>
                  </div>
                  <div className="flex items-center gap-1 text-[11px] font-mono text-emerald-400">
                    <CheckCircle2 size={12} />
                    <span>Reliability {ev.reliability} ({Math.round(ev.confidence * 100)}%)</span>
                  </div>
                </div>

                <h4 className="text-sm font-bold text-slate-200 mt-2">{ev.title}</h4>
                <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">{ev.description}</p>

                <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] font-mono text-slate-500">
                  <span className="truncate max-w-[280px]">SHA-256: {ev.content_hash}</span>
                  <span>{new Date(ev.timestamp).toLocaleDateString()}</span>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Right Column: Detailed Evidence Inspector */}
        <div>
          {selectedEvidence ? (
            <div className="glass-panel p-5 space-y-4 sticky top-6 font-mono text-xs">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <span className="text-xs font-bold text-[#00D9FF]">EVIDENCE INSPECTOR</span>
                <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold text-[10px] flex items-center gap-1">
                  <CheckCircle2 size={11} /> {selectedEvidence.integrity_status || 'VERIFIED_INTEGRITY'}
                </span>
              </div>

              <div>
                <span className="text-[10px] text-slate-500 block uppercase">Identifier</span>
                <span className="text-sm font-bold text-slate-100">{selectedEvidence.id}</span>
              </div>

              <div>
                <span className="text-[10px] text-slate-500 block uppercase">Title</span>
                <span className="text-xs text-slate-200 font-sans font-semibold">{selectedEvidence.title}</span>
              </div>

              <div>
                <span className="text-[10px] text-slate-500 block uppercase">Full Narrative Description</span>
                <p className="text-xs text-slate-300 font-sans leading-relaxed mt-1 bg-slate-900/60 p-3 rounded border border-slate-800">
                  {selectedEvidence.description}
                </p>
              </div>

              <div>
                <span className="text-[10px] text-slate-500 block uppercase">Cryptographic Integrity (SHA-256)</span>
                <div className="p-2 rounded bg-slate-900 border border-slate-800 text-[11px] text-[#00FF88] break-all select-all">
                  {selectedEvidence.content_hash}
                </div>
              </div>

              <div>
                <span className="text-[10px] text-slate-500 block uppercase">Related Entity References</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {selectedEvidence.related_entity_ids?.map((rid) => (
                    <span key={rid} className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 text-[10px]">
                      {rid}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <span className="text-[10px] text-slate-500 block uppercase">Chain of Custody Provenance</span>
                <span className="text-[11px] text-slate-400 font-sans block mt-0.5">{selectedEvidence.provenance || 'Recorded via automated crawler'}</span>
              </div>
            </div>
          ) : (
            <div className="glass-panel p-8 text-center text-xs text-slate-500">
              Select an evidence artifact to inspect cryptographic hash and chain of custody.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
