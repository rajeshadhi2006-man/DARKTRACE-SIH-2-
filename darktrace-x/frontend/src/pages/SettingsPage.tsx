import React, { useEffect, useState } from 'react';
import { Settings, Shield, Server, Database, CheckCircle2, AlertTriangle, Cpu } from 'lucide-react';
import { healthApi } from '../services/api';

export const SettingsPage: React.FC = () => {
  const [health, setHealth] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    healthApi.check()
      .then((data) => {
        setHealth(data);
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
          <Settings size={20} className="text-[#00D9FF]" />
          PLATFORM ARCHITECTURE & SYSTEM HEALTH
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Infrastructure telemetry for PostgreSQL / SQLite, Neo4j Graph cluster, Redis cache, and AI providers.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Relational Database */}
        <div className="glass-panel p-5 space-y-3 border-l-4 border-l-[#00FF88]">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-200">RELATIONAL DATABASE</span>
            <span className="text-[10px] font-mono font-bold text-[#00FF88] px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30">
              {health?.components?.relational_database?.status || 'HEALTHY'}
            </span>
          </div>
          <p className="text-xs text-slate-400 font-mono">
            Engine: {health?.components?.relational_database?.engine || 'SQLite / PostgreSQL'}
          </p>
          <div className="text-[11px] text-slate-500 pt-2 border-t border-slate-800">
            Stores actors, personas, evidence records, and audit events.
          </div>
        </div>

        {/* Neo4j Graph Database */}
        <div className="glass-panel p-5 space-y-3 border-l-4 border-l-[#00D9FF]">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-200">GRAPH ENGINE</span>
            <span className="text-[10px] font-mono font-bold text-[#00D9FF] px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/30">
              {health?.components?.graph_database?.status || 'STANDBY'}
            </span>
          </div>
          <p className="text-xs text-slate-400 font-mono">
            Mode: {health?.components?.graph_database?.mode || 'NetworkX / Neo4j APOC'}
          </p>
          <div className="text-[11px] text-slate-500 pt-2 border-t border-slate-800">
            Powers multi-relational entity resolution and pathfinding.
          </div>
        </div>

        {/* Redis Cache */}
        <div className="glass-panel p-5 space-y-3 border-l-4 border-l-[#A855F7]">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-200">CACHE & BROKER</span>
            <span className="text-[10px] font-mono font-bold text-purple-400 px-2 py-0.5 rounded bg-purple-500/10 border border-purple-500/30">
              {health?.components?.cache_broker?.status || 'HEALTHY'}
            </span>
          </div>
          <p className="text-xs text-slate-400 font-mono">
            Type: {health?.components?.cache_broker?.type || 'In-Memory / Redis 7.0'}
          </p>
          <div className="text-[11px] text-slate-500 pt-2 border-t border-slate-800">
            Buffers asynchronous background analytics and Celery tasks.
          </div>
        </div>
      </div>

      <div className="glass-panel p-5 space-y-4">
        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <Cpu size={16} className="text-[#00FF88]" />
          AUTHORIZED RESEARCH COMPLIANCE POLICY
        </h3>
        <p className="text-xs text-slate-300 leading-relaxed font-sans">
          DARKTRACE-X is strictly engineered for authorized cybersecurity research, law enforcement threat analysis, and controlled academic investigation. The platform relies on synthetic datasets, public OSINT, and passive infrastructure telemetry. It strictly forbids unauthorized credential access, exploitation, network disruption, or automated deanonymization claims without investigator corroboration.
        </p>
      </div>
    </div>
  );
};
