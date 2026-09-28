import React, { useEffect, useState } from 'react';
import { Users, Search, ExternalLink } from 'lucide-react';
import { personasApi } from '../services/api';
import { Persona } from '../types';

export const PersonasPage: React.FC = () => {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [search, setSearch] = useState<string>('');

  useEffect(() => {
    personasApi.list()
      .then((data) => {
        setPersonas(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const filtered = personas.filter(p =>
    p.canonical_handle.toLowerCase().includes(search.toLowerCase()) ||
    p.platform.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Users size={20} className="text-[#00D9FF]" />
            TRACKED PERSONAS & UNDERGROUND HANDLES
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Normalized digital identities across dark web marketplaces and cyber forums.
          </p>
        </div>
      </div>

      <div className="glass-panel p-4 max-w-md">
        <div className="relative">
          <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search handle or platform..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 outline-none focus:border-[#00D9FF]"
          />
        </div>
      </div>

      {loading ? (
        <div className="text-center py-20 font-mono text-xs text-slate-500">
          LOADING PERSONA IDENTITIES...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((p) => (
            <div key={p.id} className="glass-panel p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-[#00D9FF]">{p.canonical_handle}</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                  {p.platform}
                </span>
              </div>

              <div className="text-xs text-slate-400 space-y-1">
                <div>Actor Parent: <strong className="text-slate-200 font-mono">{p.actor_id || 'Unlinked'}</strong></div>
                <div>Activity Volume: <span className="text-[#00FF88] font-bold font-mono">{p.activity_count} records</span></div>
                <div>Confidence: <span className="text-slate-200 font-mono">{Math.round(p.confidence * 100)}%</span></div>
              </div>

              <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[11px] font-mono text-slate-500">
                <span>Observed: {p.first_seen ? new Date(p.first_seen).toLocaleDateString() : 'N/A'}</span>
                <span>ID: {p.id}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
