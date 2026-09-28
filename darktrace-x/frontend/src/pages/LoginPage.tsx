import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, User, ArrowRight, AlertCircle, Key, Cpu, Radio, CheckCircle2, Terminal } from 'lucide-react';
import { authApi } from '../services/api';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('investigator');
  const [password, setPassword] = useState('Investigator2026!');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await authApi.login(username, password);
      localStorage.setItem('darktrace_token', data.access_token);
      localStorage.setItem('darktrace_user', JSON.stringify(data.user));
      navigate('/dashboard');
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const setDemoAccount = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
  };

  return (
    <div className="min-h-screen w-screen bg-[#04060A] cyber-grid flex items-center justify-center p-4 relative overflow-hidden font-sans">
      {/* Background radial glow effects */}
      <div className="absolute top-1/4 left-1/3 w-[500px] h-[500px] bg-[#00D9FF]/8 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/3 w-[500px] h-[500px] bg-[#00FF88]/8 rounded-full blur-[120px] pointer-events-none" />

      <div className="w-full max-w-lg relative z-10 space-y-6">
        {/* Brand Banner */}
        <div className="text-center space-y-3">
          <div className="relative inline-flex items-center justify-center">
            <div className="absolute -inset-2 rounded-2xl bg-gradient-to-r from-[#00D9FF] to-[#00FF88] opacity-30 blur-lg animate-pulse" />
            <div className="relative h-14 w-14 rounded-2xl bg-gradient-to-br from-[#00D9FF] via-[#00B4D8] to-[#00FF88] text-[#04060A] font-black text-2xl flex items-center justify-center shadow-[0_0_30px_rgba(0,255,136,0.4)]">
              DX
            </div>
          </div>
          <div>
            <h1 className="text-3xl font-black tracking-widest bg-gradient-to-r from-[#00D9FF] via-[#38BDF8] to-[#00FF88] bg-clip-text text-transparent font-mono">
              DARKTRACE-X
            </h1>
            <p className="text-xs font-mono text-slate-400 uppercase tracking-widest mt-1">
              DEFENSE INTELLIGENCE & THREAT ACTOR DE-ANONYMIZATION
            </p>
          </div>
        </div>

        {/* Tactical MNC Login Card */}
        <div className="glass-panel p-8 space-y-6 border border-[#00D9FF]/20 shadow-2xl relative">
          <div className="border-b border-slate-800/80 pb-4 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-mono flex items-center gap-2">
                <Terminal size={15} className="text-[#00FF88]" />
                SECURE OPERATOR ACCESS PORTAL
              </h2>
              <p className="text-[11px] text-slate-400 mt-0.5 font-mono">
                MIL-SPEC RBAC // ARGON2 & JWT ENCRYPTED SESSION
              </p>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00D9FF]/10 text-[#00D9FF] border border-[#00D9FF]/30">
              TLS 1.3
            </span>
          </div>

          {error && (
            <div className="p-3.5 bg-red-950/30 border border-red-900/60 rounded-xl text-xs text-[#FF4D6D] flex items-center gap-2.5 font-mono">
              <AlertCircle size={15} className="flex-shrink-0 text-[#FF4D6D]" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1.5 uppercase font-medium">
                Investigator Identity ID
              </label>
              <div className="relative">
                <User size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-xs text-slate-200 outline-none focus:border-[#00FF88] focus:ring-1 focus:ring-[#00FF88] font-mono transition-all"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1.5 uppercase font-medium">
                Cryptographic Keyphrase
              </label>
              <div className="relative">
                <Lock size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-xs text-slate-200 outline-none focus:border-[#00FF88] focus:ring-1 focus:ring-[#00FF88] font-mono transition-all"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-[#00D9FF] to-[#00FF88] text-[#04060A] font-extrabold text-xs rounded-xl hover:opacity-95 transition-opacity flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(0,255,136,0.35)] disabled:opacity-50 tracking-wider font-mono uppercase"
            >
              <span>{loading ? 'AUTHENTICATING OPERATOR...' : 'ENTER SECURE COMMAND CENTER'}</span>
              <ArrowRight size={15} />
            </button>
          </form>

          {/* Quick Demo Credentials Selector */}
          <div className="pt-4 border-t border-slate-800/80 space-y-2.5">
            <span className="text-[10px] font-mono text-slate-500 uppercase block text-center font-bold tracking-wider">
              AUTHORIZATION PRESETS (CLICK TO LOAD ROLE):
            </span>
            <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
              <button
                type="button"
                onClick={() => setDemoAccount('investigator', 'Investigator2026!')}
                className="p-2 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-300 hover:border-[#00FF88] text-center hover:bg-slate-850 transition flex flex-col items-center"
              >
                <span className="font-bold text-[#00FF88]">Lead Analyst</span>
                <span className="text-[9px] text-slate-500">SI-TK Clearance</span>
              </button>
              <button
                type="button"
                onClick={() => setDemoAccount('admin', 'DarktraceAdmin2026!')}
                className="p-2 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-300 hover:border-[#00D9FF] text-center hover:bg-slate-850 transition flex flex-col items-center"
              >
                <span className="font-bold text-[#00D9FF]">Administrator</span>
                <span className="text-[9px] text-slate-500">Root Governance</span>
              </button>
              <button
                type="button"
                onClick={() => setDemoAccount('supervisor', 'Supervisor2026!')}
                className="p-2 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-300 hover:border-[#FFB020] text-center hover:bg-slate-850 transition flex flex-col items-center"
              >
                <span className="font-bold text-amber-400">SOC Supervisor</span>
                <span className="text-[9px] text-slate-500">Case Sign-Off</span>
              </button>
              <button
                type="button"
                onClick={() => setDemoAccount('viewer', 'Viewer2026!')}
                className="p-2 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-300 hover:border-slate-600 text-center hover:bg-slate-850 transition flex flex-col items-center"
              >
                <span className="font-bold text-slate-400">Observer</span>
                <span className="text-[9px] text-slate-500">Read-Only Audit</span>
              </button>
            </div>
          </div>
        </div>

        {/* Security Compliance Footer */}
        <div className="flex items-center justify-center gap-4 text-[10px] text-slate-500 font-mono">
          <span>NIST SP 800-53 COMPLIANT</span>
          <span>•</span>
          <span>TLP:AMBER SENSITIVE</span>
          <span>•</span>
          <span>IMMUTABLE EVIDENCE CHAIN</span>
        </div>
      </div>
    </div>
  );
};
