import React, { useState, useEffect } from 'react';
import { Target, Shield, Server, FileText, CheckCircle, ExternalLink, Calendar } from 'lucide-react';
import { campaignsApi } from '../services/api';

export const CampaignsPage: React.FC = () => {
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    campaignsApi.list()
      .then((data) => setCampaigns(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Banner */}
      <div className="border-b border-[#00D9FF]/20 pb-4">
        <div className="flex items-center gap-3">
          <Target className="text-[#00FF88]" size={28} />
          <h1 className="text-2xl font-black tracking-wider text-slate-100">
            CAMPAIGN CLUSTERING & THREAT OPERATIONS
          </h1>
        </div>
        <p className="text-xs text-slate-400 mt-1 font-mono">
          Correlated threat campaigns: Shared infrastructure, cross-platform aliases, weaponized malware stubs, and target industry clusters.
        </p>
      </div>

      {loading ? (
        <div className="p-12 text-center text-xs font-mono text-slate-500 animate-pulse">
          Loading campaign clusters...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {campaigns.map((cmp) => (
            <div
              key={cmp.id}
              className="bg-[#0A0F1A]/90 border border-slate-800 hover:border-[#00D9FF]/40 rounded-2xl p-5 space-y-4 shadow-xl transition-all"
            >
              {/* Header */}
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-[#00D9FF] font-bold">
                  {cmp.id}
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00FF88]/10 text-[#00FF88] border border-[#00FF88]/30 font-bold">
                  {Math.round(cmp.confidence * 100)}% CONFIDENCE
                </span>
              </div>

              <div>
                <h3 className="text-base font-bold text-slate-100">{cmp.name}</h3>
                <p className="text-xs text-slate-400 mt-1 line-clamp-2">{cmp.description}</p>
              </div>

              {/* Target Sectors */}
              <div className="space-y-1.5">
                <div className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">
                  Target Sectors
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {cmp.target_sectors?.map((sec: string, idx: number) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-mono"
                    >
                      {sec}
                    </span>
                  ))}
                </div>
              </div>

              {/* Associated Threat Actors */}
              <div className="space-y-1.5">
                <div className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">
                  Attributed Threat Actors
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {cmp.threat_actors?.map((act: any) => (
                    <span
                      key={act.id}
                      className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 text-[10px] font-mono font-bold"
                    >
                      {act.name} [{act.id}]
                    </span>
                  ))}
                </div>
              </div>

              {/* Infrastructure Indicators */}
              <div className="space-y-1.5">
                <div className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">
                  Linked Infrastructure
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {cmp.infrastructure_indicators?.map((inf: string, idx: number) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded bg-[#00D9FF]/10 text-[#00D9FF] text-[10px] font-mono"
                    >
                      {inf}
                    </span>
                  ))}
                </div>
              </div>

              {/* MITRE ATT&CK Techniques */}
              {cmp.mitre_techniques && cmp.mitre_techniques.length > 0 && (
                <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[11px] font-mono text-slate-400">
                  <span>MITRE ATT&CK:</span>
                  <span className="text-[#00FF88] font-bold">
                    {cmp.mitre_techniques.join(', ')}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
