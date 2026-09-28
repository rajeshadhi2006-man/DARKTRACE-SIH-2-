import React, { useState, useEffect, useRef } from 'react';
import { BellRing, AlertTriangle, ShieldAlert, CheckCircle2, ArrowUpRight, Flame, Layers, Radio } from 'lucide-react';
import { alertsApi } from '../services/api';

export const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [liveStreamActive, setLiveStreamActive] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const fetchAlerts = () => {
    alertsApi.list()
      .then((data) => setAlerts(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAlerts();

    // Connect to WebSocket for real-time alerts
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/ws/telemetry`;
    let reconnectTimeout: any = null;

    const connect = () => {
      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => setLiveStreamActive(true);

        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);
            if (msg.type === 'NEW_ALERT' && msg.alert) {
              setAlerts((prev) => [msg.alert, ...prev]);
            }
          } catch (e) {
            console.error('Failed to parse alert stream packet:', e);
          }
        };

        ws.onclose = () => {
          setLiveStreamActive(false);
          reconnectTimeout = setTimeout(connect, 3000);
        };

        ws.onerror = () => setLiveStreamActive(false);
      } catch (err) {
        setLiveStreamActive(false);
      }
    };

    connect();

    return () => {
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const handleAcknowledge = async (id: string) => {
    try {
      await alertsApi.ack(id);
      fetchAlerts();
    } catch (err) {
      console.error(err);
    }
  };

  const handleAcknowledgeAll = async () => {
    try {
      await alertsApi.ackAll();
      fetchAlerts();
    } catch (err) {
      console.error(err);
    }
  };

  const unackCount = alerts.filter(a => a.status === 'NEW').length;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Banner */}
      <div className="border-b border-[#00D9FF]/20 pb-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <BellRing className="text-amber-400" size={28} />
            <h1 className="text-2xl font-black tracking-wider text-slate-100">
              THREAT INTELLIGENCE ALERTS & ANOMALY RADAR
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Automated alerts: Persona migration detection, infrastructure origin decloaking, identity collision, and diurnal contradictions.
          </p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          {/* Live WebSocket Status */}
          <div className="flex items-center gap-2 text-xs font-mono px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-slate-300">
            <Radio size={14} className={liveStreamActive ? 'text-[#00FF88] animate-pulse' : 'text-slate-500'} />
            <span>{liveStreamActive ? 'RADAR STREAM: LIVE' : 'CONNECTING...'}</span>
          </div>

          {unackCount > 0 ? (
            <>
              <div className="px-3 py-1.5 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 font-mono text-xs font-bold flex items-center gap-2">
                <Flame size={14} className="animate-pulse" />
                {unackCount} UNACKNOWLEDGED ALERTS
              </div>
              <button
                onClick={handleAcknowledgeAll}
                className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-[#00FF88] border border-[#00FF88]/40 text-xs font-mono font-bold transition shadow-sm active:scale-95 flex items-center gap-1.5"
              >
                <span>ACKNOWLEDGE ALL → 0</span>
              </button>
            </>
          ) : (
            <div className="px-3 py-1.5 rounded-full bg-emerald-500/15 border border-[#00FF88]/40 text-[#00FF88] font-mono text-xs font-bold flex items-center gap-2">
              <CheckCircle2 size={14} className="text-[#00FF88]" />
              ZERO UNACKNOWLEDGED (ALL 0)
            </div>
          )}
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-xs font-mono text-slate-500 animate-pulse">
          Loading alerts feed...
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alt, idx) => (
            <div
              key={alt.id}
              className={`p-5 rounded-2xl border transition-all ${
                alt.status === 'NEW'
                  ? 'bg-[#0A0F1A]/95 border-amber-500/40 shadow-[0_0_15px_rgba(245,158,11,0.1)]'
                  : 'bg-[#05070A]/80 border-slate-800 opacity-70'
              }`}
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span
                    className={`p-2 rounded-xl ${
                      alt.severity === 'CRITICAL'
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        : alt.severity === 'HIGH'
                        ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                        : 'bg-[#00D9FF]/20 text-[#00D9FF] border border-[#00D9FF]/30'
                    }`}
                  >
                    <AlertTriangle size={20} />
                  </span>

                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-[11px] font-mono text-slate-400">{alt.id}</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        {alt.event_type}
                      </span>
                      {alt.actor_name && (
                        <span className="text-[10px] font-mono text-[#00FF88] font-bold">
                          [Target: {alt.actor_name}]
                        </span>
                      )}
                      {idx === 0 && alt.status === 'NEW' && (
                        <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/40 font-bold animate-pulse">
                          NEW ARRIVAL
                        </span>
                      )}
                    </div>
                    <h3 className="text-base font-bold text-slate-100 mt-0.5">{alt.title}</h3>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono font-bold text-[#00FF88]">
                    {Math.round(alt.confidence * 100)}% Confidence
                  </span>
                  {alt.status === 'NEW' ? (
                    <button
                      onClick={() => handleAcknowledge(alt.id)}
                      className="px-3.5 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-400 border border-amber-500/40 text-xs font-mono font-bold transition shadow-sm active:scale-95"
                    >
                      Acknowledge
                    </button>
                  ) : (
                    <span className="flex items-center gap-1 text-xs font-mono text-slate-500">
                      <CheckCircle2 size={14} className="text-[#00FF88]" />
                      Acknowledged
                    </span>
                  )}
                </div>
              </div>

              <p className="text-xs text-slate-400 mt-3 pl-11">
                {alt.description}
              </p>

              <div className="mt-3 pl-11 flex items-center gap-4 text-[11px] font-mono text-slate-500">
                <span>Supporting Artifacts: {alt.supporting_evidence_count}</span>
                <span>Timestamp: {new Date(alt.created_at).toLocaleString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
