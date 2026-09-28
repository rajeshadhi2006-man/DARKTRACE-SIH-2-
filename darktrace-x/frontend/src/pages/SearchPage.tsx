import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Search, Shield, Users, Key, Wallet, Server, FileCheck, ArrowRight } from 'lucide-react';
import { searchApi } from '../services/api';

export const SearchPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const queryParam = searchParams.get('q') || '';
  const [searchTerm, setSearchTerm] = useState<string>(queryParam);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (queryParam) {
      setSearchTerm(queryParam);
      runSearch(queryParam);
    }
  }, [queryParam]);

  const runSearch = (term: string) => {
    if (!term.trim()) return;
    setLoading(true);
    searchApi.query(term.trim())
      .then((data) => {
        setResults(data.results || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchTerm.trim())}`);
      runSearch(searchTerm);
    }
  };

  const getEntityIcon = (type: string) => {
    switch (type) {
      case 'Actor': return <Shield size={16} className="text-[#00FF88]" />;
      case 'Persona': return <Users size={16} className="text-[#00D9FF]" />;
      case 'PGPKey': return <Key size={16} className="text-[#FFB020]" />;
      case 'Wallet': return <Wallet size={16} className="text-[#10B981]" />;
      case 'Infrastructure': return <Server size={16} className="text-[#EC4899]" />;
      default: return <FileCheck size={16} className="text-slate-400" />;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Search size={20} className="text-[#00D9FF]" />
          GLOBAL CROSS-ENTITY INTELLIGENCE SEARCH
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Search across threat actors, handles, PGP key IDs, cryptocurrency wallets, infrastructure indicators, and evidence artifacts.
        </p>
      </div>

      <form onSubmit={handleSearchSubmit} className="glass-panel p-4 flex gap-3">
        <input
          type="text"
          placeholder="Search by handle (e.g. ShadowX), PGP key, wallet address, IP, or Actor ID..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-xs text-slate-200 outline-none focus:border-[#00D9FF] font-mono"
        />
        <button
          type="submit"
          className="px-6 py-2.5 bg-gradient-to-r from-[#00D9FF] to-[#00FF88] text-[#05070A] font-bold text-xs rounded-lg hover:opacity-90"
        >
          Search
        </button>
      </form>

      {loading ? (
        <div className="text-center py-20 font-mono text-xs text-slate-500">
          SCANNING INDEXED ENTITIES...
        </div>
      ) : (
        <div className="space-y-3">
          <div className="text-xs font-mono text-slate-400">
            {results.length > 0 ? `Found ${results.length} correlated intelligence matches:` : (searchTerm ? 'No matching entities found in intelligence repository.' : 'Enter a query above to search.')}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {results.map((r, idx) => (
              <div
                key={idx}
                onClick={() => navigate(r.url)}
                className="glass-panel p-4 cursor-pointer hover:border-[#00FF88]/40 transition-all flex items-center justify-between group"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded bg-slate-900 border border-slate-800">
                    {getEntityIcon(r.type)}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                        {r.type}
                      </span>
                      <h4 className="text-xs font-bold text-slate-200 group-hover:text-[#00FF88] transition-colors">
                        {r.title}
                      </h4>
                    </div>
                    <p className="text-[11px] text-slate-400 font-mono mt-0.5 truncate max-w-sm">
                      {r.subtitle}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono text-[#00FF88]">
                    {r.confidence ? `${Math.round(r.confidence * 100)}%` : ''}
                  </span>
                  <ArrowRight size={14} className="text-slate-500 group-hover:text-[#00D9FF] group-hover:translate-x-1 transition-all" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
