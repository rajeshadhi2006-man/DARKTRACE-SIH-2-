import React, { useState, useEffect } from 'react';
import { Database, UploadCloud, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import { intelligenceApi } from '../services/api';

export const IntelligencePage: React.FC = () => {
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadResult, setUploadResult] = useState<any | null>(null);

  useEffect(() => {
    loadIntel();
  }, []);

  const loadIntel = () => {
    setLoading(true);
    intelligenceApi.list({ limit: 50 })
      .then((data) => {
        setRecords(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadResult(null);

    try {
      const res = await intelligenceApi.upload(file);
      setUploadResult(res);
      loadIntel();
    } catch (err: any) {
      console.error(err);
      alert('Upload failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Database size={20} className="text-[#00D9FF]" />
            INTELLIGENCE INGESTION & OBSERVATIONS
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Import structured CSV, JSON, and authorized research datasets. Complete workflow: UPLOAD &rarr; VALIDATE &rarr; PARSE &rarr; NORMALIZE &rarr; EXTRACT &rarr; STORE.
          </p>
        </div>
      </div>

      {/* Upload Zone */}
      <div className="glass-panel p-6 border-dashed border-2 border-[#00D9FF]/30 hover:border-[#00FF88] transition-all text-center">
        <UploadCloud size={36} className="mx-auto text-[#00D9FF] mb-2" />
        <h3 className="text-sm font-bold text-slate-200">Upload Intelligence Datasets</h3>
        <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
          Supported formats: <strong className="text-slate-200">CSV, JSON</strong>. Maximum size: 50MB. All ingested records are hashed and normalized.
        </p>

        <label className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#00D9FF] to-[#00FF88] text-[#05070A] text-xs font-bold rounded-lg cursor-pointer hover:opacity-90 transition-opacity">
          <span>{uploading ? 'Processing & Ingesting Dataset...' : 'Choose File to Ingest'}</span>
          <input
            type="file"
            accept=".csv,.json"
            onChange={handleFileUpload}
            disabled={uploading}
            className="hidden"
          />
        </label>

        {uploadResult && (
          <div className="mt-4 p-3 bg-emerald-950/20 border border-emerald-900/50 rounded-lg text-xs text-[#00FF88] max-w-lg mx-auto flex items-center justify-between font-mono">
            <span>[SUCCESS] Ingested {uploadResult.records_ingested} records from {uploadResult.filename}</span>
            <CheckCircle2 size={16} />
          </div>
        )}
      </div>

      {/* Intelligence Records Table */}
      <div className="glass-panel p-5">
        <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
          <FileText size={16} className="text-[#00FF88]" />
          INGESTED OBSERVATIONS & TELEMETRY ({records.length})
        </h3>

        {loading ? (
          <div className="text-center py-10 font-mono text-xs text-slate-500">
            FETCHING INTELLIGENCE OBSERVATIONS...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="pb-3 font-semibold">ID</th>
                  <th className="pb-3 font-semibold">SOURCE</th>
                  <th className="pb-3 font-semibold">TYPE</th>
                  <th className="pb-3 font-semibold">RAW TEXT PREVIEW</th>
                  <th className="pb-3 font-semibold">CONFIDENCE</th>
                  <th className="pb-3 font-semibold">TIMESTAMP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {records.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-900/40 transition-colors">
                    <td className="py-3 font-bold text-[#00D9FF]">{r.id}</td>
                    <td className="py-3 text-slate-300">{r.source_id}</td>
                    <td className="py-3">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">
                        {r.record_type}
                      </span>
                    </td>
                    <td className="py-3 text-slate-300 max-w-xs truncate font-sans text-xs">
                      {r.content_preview}
                    </td>
                    <td className="py-3 text-[#00FF88] font-bold">
                      {Math.round(r.confidence * 100)}%
                    </td>
                    <td className="py-3 text-slate-400 text-[11px]">
                      {new Date(r.timestamp).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
