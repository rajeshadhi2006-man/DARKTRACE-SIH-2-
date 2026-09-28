import React, { useEffect, useState } from 'react';
import { History, Shield, Clock } from 'lucide-react';
import { auditApi } from '../services/api';
import { AuditLogItem } from '../types';

export const AuditPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    auditApi.list()
      .then((data) => {
        setLogs(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <History size={20} className="text-[#00D9FF]" />
          IMMUTABLE INVESTIGATOR AUDIT LOG
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Complete forensic traceability of analyst logins, dossier views, search queries, and relationship review actions.
        </p>
      </div>

      <div className="glass-panel p-5">
        {loading ? (
          <div className="text-center py-10 font-mono text-xs text-slate-500">
            LOADING AUDIT LOGS...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="pb-3 font-semibold">ACTION</th>
                  <th className="pb-3 font-semibold">ANALYST</th>
                  <th className="pb-3 font-semibold">OBJECT TYPE</th>
                  <th className="pb-3 font-semibold">OBJECT ID</th>
                  <th className="pb-3 font-semibold">IP ADDRESS</th>
                  <th className="pb-3 font-semibold">TIMESTAMP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {logs.map((l) => (
                  <tr key={l.id} className="hover:bg-slate-900/40 transition-colors">
                    <td className="py-3">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#00FF88]/10 text-[#00FF88] border border-[#00FF88]/20">
                        {l.action}
                      </span>
                    </td>
                    <td className="py-3 text-slate-200 font-bold">{l.username || 'System'}</td>
                    <td className="py-3 text-slate-400">{l.object_type || '-'}</td>
                    <td className="py-3 text-[#00D9FF]">{l.object_id || '-'}</td>
                    <td className="py-3 text-slate-400">{l.ip_address || '127.0.0.1'}</td>
                    <td className="py-3 text-slate-400 text-[11px]">
                      {new Date(l.timestamp).toLocaleString()} UTC
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
