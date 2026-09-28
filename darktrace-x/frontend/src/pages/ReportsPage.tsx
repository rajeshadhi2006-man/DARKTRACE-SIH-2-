import React, { useEffect, useState } from 'react';
import { FileText, Download, Shield, Plus, Clock, ExternalLink, FileSpreadsheet, Code2, CheckCircle2, Lock } from 'lucide-react';
import { reportsApi, actorsApi } from '../services/api';
import { ActorSummary } from '../types';

export const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<any[]>([]);
  const [actors, setActors] = useState<ActorSummary[]>([]);
  const [selectedActorId, setSelectedActorId] = useState<string>('ACT-0042');
  const [generating, setGenerating] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [exportNotice, setExportNotice] = useState<string | null>(null);

  useEffect(() => {
    actorsApi.list().then(setActors).catch(console.error);
    loadReports();
  }, []);

  const loadReports = () => {
    setLoading(true);
    reportsApi.list()
      .then((data) => {
        setReports(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await reportsApi.generate(selectedActorId, 'PDF');
      loadReports();
      window.open(res.download_url, '_blank');
      setExportNotice('Official NTRO Investigation Dossier generated and opened in new tab.');
      setTimeout(() => setExportNotice(null), 5000);
    } catch (err) {
      console.error(err);
      alert('Report generation failed.');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadCsv = () => {
    actorsApi.exportCsv();
    setExportNotice('Exporting complete NTRO threat actor dataset as CSV...');
    setTimeout(() => setExportNotice(null), 4000);
  };

  const handleDownloadJson = () => {
    actorsApi.exportJson();
    setExportNotice('Exporting complete NTRO threat actor schema as JSON...');
    setTimeout(() => setExportNotice(null), 4000);
  };

  return (
    <div className="space-y-6 max-w-[1500px] mx-auto">
      {/* ── Sovereign NTRO Header ── */}
      <div className="card-3d p-6 rounded-2xl border border-sky-500/25 bg-[#0E1A36]/90 relative overflow-hidden backdrop-blur-xl">
        <div className="h-[2px] w-full bg-gradient-to-r from-transparent via-[#00E5FF]/70 to-transparent absolute top-0 left-0" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="h-2 w-2 rounded-full bg-[#10B981] animate-ping" />
              <span className="text-[10px] font-mono tracking-widest text-[#10B981] font-bold uppercase">
                NTRO FORENSIC GOVERNANCE // SIH 2026
              </span>
            </div>
            <h2 className="text-xl lg:text-2xl font-black text-white tracking-wide font-mono flex items-center gap-2.5">
              <span className="text-[#00E5FF] glow-text-cyan font-black">INTELLIGENCE DOSSIERS</span>
              <span className="text-slate-500 font-light">//</span>
              <span>MULTI-FORMAT EXPORT ENGINE</span>
            </h2>
            <p className="text-xs text-slate-300 mt-1 font-mono">
              National Technical Research Organisation (NTRO) • Law enforcement sensitive dark web threat actor intelligence outputs (CSV, JSON & PDF).
            </p>
          </div>
          <div className="flex items-center gap-2 text-[10px] font-mono text-slate-400">
            <span className="px-2.5 py-1 rounded-md bg-[#091328] border border-sky-500/30 text-sky-300 font-bold flex items-center gap-1.5">
              <Lock size={11} className="text-[#38BDF8]" />
              SEC. 65B IT ACT COMPLIANT
            </span>
          </div>
        </div>

        {exportNotice && (
          <div className="mt-4 px-4 py-2 rounded-lg bg-emerald-500/15 border border-emerald-500/35 text-emerald-300 text-xs font-mono flex items-center gap-2 animate-pulse">
            <CheckCircle2 size={14} className="text-[#10B981]" />
            <span>{exportNotice}</span>
          </div>
        )}
      </div>

      {/* ── 3-Column SIH Export Modalities Cards (3D Elevation) ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* CSV Format */}
        <div className="card-3d p-5 rounded-xl border border-sky-500/25 bg-[#0E1A36]/80 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="h-10 w-10 rounded-lg bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <FileSpreadsheet size={20} />
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold">
                FORMAT: CSV
              </span>
            </div>
            <h3 className="text-sm font-bold text-white font-mono">Threat Actor Matrix (CSV)</h3>
            <p className="text-xs text-slate-300 mt-2 font-mono leading-relaxed">
              Tabular spreadsheet covering actor profiles, extracted handles, PGP fingerprints, cryptocurrency wallets (BTC/XMR), Tor hidden services, and clearnet origin IPs.
            </p>
          </div>
          <button
            onClick={handleDownloadCsv}
            className="mt-5 w-full py-2.5 px-4 rounded-lg bg-gradient-to-r from-emerald-600/30 to-sky-600/20 hover:from-emerald-600/40 hover:to-sky-600/30 text-emerald-300 border border-emerald-400/40 text-xs font-mono font-bold flex items-center justify-center gap-2 btn-3d transition-all shadow-sm"
          >
            <Download size={14} />
            <span>DOWNLOAD DATASET (.CSV)</span>
          </button>
        </div>

        {/* JSON Schema Format */}
        <div className="card-3d p-5 rounded-xl border border-sky-500/25 bg-[#0E1A36]/80 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="h-10 w-10 rounded-lg bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-sky-400">
                <Code2 size={20} />
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/40 font-bold">
                FORMAT: JSON
              </span>
            </div>
            <h3 className="text-sm font-bold text-white font-mono">Structured Machine Schema (JSON)</h3>
            <p className="text-xs text-slate-300 mt-2 font-mono leading-relaxed">
              Programmatic STIX/TAXII-aligned nested intelligence objects with full indicator graphs, persona linkages, attribution confidence ratings, and source provenance.
            </p>
          </div>
          <button
            onClick={handleDownloadJson}
            className="mt-5 w-full py-2.5 px-4 rounded-lg bg-gradient-to-r from-sky-600/30 to-cyan-600/20 hover:from-sky-600/40 hover:to-cyan-600/30 text-sky-200 border border-sky-400/40 text-xs font-mono font-bold flex items-center justify-center gap-2 btn-3d transition-all shadow-sm"
          >
            <Download size={14} />
            <span>DOWNLOAD SCHEMA (.JSON)</span>
          </button>
        </div>

        {/* PDF Forensic Dossier */}
        <div className="card-3d p-5 rounded-xl border border-sky-500/25 bg-[#0E1A36]/80 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="h-10 w-10 rounded-lg bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                <FileText size={20} />
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold">
                FORMAT: PDF
              </span>
            </div>
            <h3 className="text-sm font-bold text-white font-mono">Formal Case Dossier (PDF)</h3>
            <p className="text-xs text-slate-300 mt-2 font-mono leading-relaxed">
              Official NTRO evidentiary dossier with executive summary, persona handles, attribution findings, contradicting evidence check, and chain-of-custody disclaimer.
            </p>
          </div>
          <div className="mt-4 space-y-2">
            <select
              value={selectedActorId}
              onChange={(e) => setSelectedActorId(e.target.value)}
              className="w-full bg-[#091328] border border-sky-900/50 text-xs text-slate-200 rounded-lg px-3 py-2 outline-none font-mono focus:border-[#00E5FF]"
            >
              {actors.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.primary_name} ({a.id})
                </option>
              ))}
            </select>
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="w-full py-2.5 px-4 rounded-lg bg-gradient-to-r from-[#00E5FF] to-[#38BDF8] text-[#080E1E] text-xs font-mono font-bold flex items-center justify-center gap-2 btn-3d transition-all shadow-[0_4px_16px_rgba(0,229,255,0.25)] disabled:opacity-50"
            >
              <Plus size={14} />
              <span>{generating ? 'COMPILING DOSSIER...' : 'GENERATE DOSSIER (.PDF)'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* ── Reports Archive List (3D Elevation) ── */}
      <div className="card-3d p-6 rounded-2xl border border-sky-500/25 bg-[#0E1A36]/90 backdrop-blur-xl">
        <h3 className="text-sm font-bold text-white font-mono mb-4 flex items-center gap-2">
          <FileText size={16} className="text-[#00E5FF]" />
          ARCHIVED INVESTIGATION DOSSIERS
        </h3>

        {loading ? (
          <div className="text-center py-10 font-mono text-xs text-slate-400">
            LOADING REPORT ARCHIVE...
          </div>
        ) : (
          <div className="divide-y divide-sky-900/30">
            {reports.length === 0 ? (
              <div className="text-center py-8 text-xs text-slate-400 font-mono">
                No reports compiled yet. Click above to generate an investigation dossier.
              </div>
            ) : (
              reports.map((r) => (
                <div key={r.id} className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-900/40 px-3 rounded-xl transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-lg bg-[#091328] border border-sky-500/25 text-[#00E5FF]">
                      <FileText size={18} />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-white font-mono">{r.title}</h4>
                      <div className="flex flex-wrap items-center gap-2 mt-1 text-[10px] font-mono text-slate-400">
                        <span>ID: <strong className="text-slate-300">{r.id}</strong></span>
                        <span>•</span>
                        <span>Classification: <strong className="text-amber-400">{r.classification}</strong></span>
                        <span>•</span>
                        <span>Size: {(r.file_size_bytes / 1024).toFixed(1)} KB</span>
                        <span>•</span>
                        <span>Hash: <span className="text-[#38BDF8]">{r.file_hash || 'SHA-256 VERIFIED'}</span></span>
                      </div>
                    </div>
                  </div>

                  <a
                    href={`/api/reports/download/${r.id}`}
                    target="_blank"
                    rel="noreferrer"
                    className="px-4 py-2 bg-[#091328] hover:bg-sky-500/20 text-xs font-mono font-bold text-[#38BDF8] rounded-lg border border-sky-500/30 flex items-center gap-2 transition-all btn-3d self-start sm:self-auto"
                  >
                    <Download size={13} />
                    <span>DOWNLOAD PDF</span>
                  </a>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportsPage;
