import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Calendar, Filter, Clock, ChevronRight, Shield, Layers } from 'lucide-react';
import { timelineApi, actorsApi } from '../services/api';
import { TimelineEvent, ActorSummary } from '../types';

export const TimelinePage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const initialActorId = searchParams.get('actor_id') || 'ACT-0042';

  const [actors, setActors] = useState<ActorSummary[]>([]);
  const [selectedActorId, setSelectedActorId] = useState<string>(initialActorId);
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [eventTypeFilter, setEventTypeFilter] = useState<string>('');

  useEffect(() => {
    actorsApi.list().then(setActors).catch(console.error);
  }, []);

  useEffect(() => {
    if (selectedActorId) {
      loadTimeline(selectedActorId);
    }
  }, [selectedActorId, eventTypeFilter]);

  const loadTimeline = (actorId: string) => {
    setLoading(true);
    const params: Record<string, any> = {};
    if (eventTypeFilter) params.event_type = eventTypeFilter;

    timelineApi.getActorTimeline(actorId, params)
      .then((data) => {
        setEvents(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  const getEventBadgeColor = (type: string) => {
    switch (type) {
      case 'ACCOUNT_CREATION': return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      case 'PGP_OBSERVED': return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'WALLET_OBSERVED': return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'PERSONA_MIGRATION': return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
      default: return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Calendar size={20} className="text-[#00D9FF]" />
            INVESTIGATION ACTIVITY TIMELINE
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Chronological footprint of account creations, key announcements, wallet activity, and persona migration events.
          </p>
        </div>
      </div>

      {/* Selector & Filters */}
      <div className="glass-panel p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <label className="text-xs font-mono text-slate-400">TARGET ACTOR:</label>
          <select
            value={selectedActorId}
            onChange={(e) => setSelectedActorId(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded px-3 py-1.5 outline-none font-mono focus:border-[#00D9FF]"
          >
            {actors.map((a) => (
              <option key={a.id} value={a.id}>
                {a.primary_name} ({a.id})
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-3">
          <label className="text-xs font-mono text-slate-400">EVENT TYPE:</label>
          <select
            value={eventTypeFilter}
            onChange={(e) => setEventTypeFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded px-3 py-1.5 outline-none font-mono focus:border-[#00D9FF]"
          >
            <option value="">All Chronological Events</option>
            <option value="ACCOUNT_CREATION">Account Creation</option>
            <option value="PGP_OBSERVED">PGP Key Observation</option>
            <option value="WALLET_OBSERVED">Wallet Activity</option>
            <option value="PERSONA_MIGRATION">Persona Migration</option>
            <option value="FORUM_ACTIVITY">Forum & Marketplace Posts</option>
          </select>
        </div>
      </div>

      {/* Timeline List */}
      {loading ? (
        <div className="text-center py-20 font-mono text-xs text-slate-500">
          RECONSTRUCTING CHRONOLOGICAL CHAIN OF EVENTS...
        </div>
      ) : (
        <div className="relative border-l border-slate-800 ml-4 pl-6 space-y-6">
          {events.map((ev, idx) => (
            <div key={ev.id} className="relative group">
              {/* Dot */}
              <div className="absolute -left-[31px] top-1 h-4 w-4 rounded-full bg-slate-900 border-2 border-[#00D9FF] flex items-center justify-center group-hover:border-[#00FF88] transition-colors">
                <div className="h-1.5 w-1.5 rounded-full bg-[#00D9FF] group-hover:bg-[#00FF88]" />
              </div>

              {/* Event Card */}
              <div className="glass-panel p-4 space-y-2 hover:border-[#00D9FF]/40 transition-all">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${getEventBadgeColor(ev.event_type)}`}>
                      {ev.event_type.replace(/_/g, ' ')}
                    </span>
                    <span className="text-xs font-mono text-slate-400 font-bold">[{ev.id}]</span>
                    {ev.persona_id && <span className="text-[11px] font-mono text-slate-300">Persona: {ev.persona_id}</span>}
                  </div>
                  <span className="text-xs font-mono text-slate-400 flex items-center gap-1">
                    <Clock size={12} className="text-slate-500" />
                    {new Date(ev.event_timestamp).toLocaleString()} UTC
                  </span>
                </div>

                <h4 className="text-sm font-bold text-slate-200">{ev.title}</h4>
                <p className="text-xs text-slate-300 leading-relaxed font-sans">{ev.description}</p>

                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
                  <span>Source: {ev.source_id || 'LOCAL SENSOR'}</span>
                  <span>Confidence: <strong className="text-[#00FF88]">{Math.round(ev.confidence * 100)}%</strong></span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
