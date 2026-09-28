import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Filter, Search, ChevronRight, AlertTriangle, Users, FileCheck } from 'lucide-react';
import { actorsApi } from '../services/api';
import { ActorSummary } from '../types';

export const ActorsPage: React.FC = () => {
  const navigate = useNavigate();
  const [actors, setActors] = useState<ActorSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [search, setSearch] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  useEffect(() => {
    loadActors();
  }, [selectedCategory]);

  const loadActors = () => {
    setLoading(true);
    const params: Record<string, any> = {};
    if (search.trim()) params.query = search.trim();
    if (selectedCategory) params.category = selectedCategory;

    actorsApi.list(params)
      .then((data) => {
        setActors(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadActors();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Shield size={20} className="text-[#00FF88]" />
            THREAT ACTOR DIRECTORY
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Indexed underground threat groups, extortion cartels, and initial access syndicates.
          </p>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="glass-panel p-4 flex flex-wrap items-center justify-between gap-4">
        <form onSubmit={handleSearchSubmit} className="relative flex-1 min-w-[280px]">
          <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Filter actors by handle, name, or summary..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-900/80 border border-slate-700/60 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-[#00D9FF]"
          />
        </form>

        <div className="flex items-center gap-3">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-3 py-2 outline-none focus:border-[#00D9FF]"
          >
            <option value="">All Threat Categories</option>
            <option value="Initial Access">Initial Access Brokers</option>
            <option value="Ransomware">Ransomware Cartels</option>
            <option value="Darknet Vendor">Darknet Vendors</option>
            <option value="Money Laundering">Money Laundering</option>
            <option value="Exploit Kit">Exploit Kit & Weaponization</option>
            <option value="Carding">Carding Syndicates</option>
          </select>
        </div>
      </div>

      {/* Actors Table / Cards */}
      {loading ? (
        <div className="text-center py-12 font-mono text-xs text-slate-500">
          LOADING THREAT ACTOR DOSSIERS...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {actors.map((actor) => (
            <div
              key={actor.id}
              onClick={() => navigate(`/actors/${actor.id}`)}
              className="glass-panel p-5 cursor-pointer hover:border-[#00FF88]/40 transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-mono font-bold text-[#00D9FF] bg-[#00D9FF]/10 px-2 py-0.5 rounded border border-[#00D9FF]/20">
                    {actor.id}
                  </span>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                    actor.threat_level === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border border-red-500/40' :
                    actor.threat_level === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40' :
                    'bg-blue-500/20 text-blue-400 border border-blue-500/40'
                  }`}>
                    {actor.threat_level}
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-200 group-hover:text-[#00FF88] transition-colors">
                  {actor.primary_name}
                </h3>
                <p className="text-xs text-slate-400 mt-1 font-mono">{actor.threat_category}</p>

                <div className="mt-4 grid grid-cols-2 gap-2 text-xs border-t border-slate-800/80 pt-3">
                  <div className="flex items-center gap-1.5 text-slate-400">
                    <Users size={13} className="text-[#00D9FF]" />
                    <span>{actor.persona_count} Personas</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-400">
                    <FileCheck size={13} className="text-[#00FF88]" />
                    <span>{actor.evidence_count} Evidence</span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-mono text-slate-500 block">Analytical Confidence</span>
                  <span className="text-xs font-mono font-bold text-[#00FF88]">
                    {actor.analytical_confidence} ({Math.round(actor.confidence_score * 100)}%)
                  </span>
                </div>
                <button className="text-xs font-semibold text-[#00D9FF] flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                  View Dossier <ChevronRight size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
