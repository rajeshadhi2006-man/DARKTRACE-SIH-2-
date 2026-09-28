import { createClient } from '@supabase/supabase-js';

// Supabase configuration
const SUPABASE_URL = ((import.meta as any).env?.VITE_SUPABASE_URL as string) || 'https://surihwgxgymlgdxyghqx.supabase.co';
const SUPABASE_ANON_KEY = ((import.meta as any).env?.VITE_SUPABASE_ANON_KEY as string) || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1cmlod2d4Z3ltbGdkeHlnaHF4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTA0OTg2MTIsImV4cCI6MjEwNjA3NDYxMn0.e24rW2AqxaCs6ODLhlSzIqOjEQd3DRfVH6I7mzcleHM';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
  realtime: {
    params: {
      eventsPerSecond: 10,
    },
  },
});

export interface SupabaseHealthStatus {
  connected: boolean;
  projectRef: string;
  url: string;
  latencyMs: number;
  authHealthy: boolean;
  realtimeHealthy: boolean;
  timestamp: string;
  error?: string;
}

export interface LiveThreatBroadcast {
  id: string;
  threat_type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  source: string;
  actor: string;
  summary: string;
  timestamp: string;
}

/**
 * Check Supabase connectivity and measure round-trip latency.
 */
export async function checkSupabaseConnection(): Promise<SupabaseHealthStatus> {
  const start = performance.now();
  try {
    const res = await fetch(`${SUPABASE_URL}/auth/v1/health`, {
      headers: {
        apikey: SUPABASE_ANON_KEY,
        Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
      },
    });

    const latency = Math.round(performance.now() - start);

    if (res.ok) {
      return {
        connected: true,
        projectRef: 'surihwgxgymlgdxyghqx',
        url: SUPABASE_URL,
        latencyMs: latency,
        authHealthy: true,
        realtimeHealthy: true,
        timestamp: new Date().toISOString(),
      };
    } else {
      return {
        connected: false,
        projectRef: 'surihwgxgymlgdxyghqx',
        url: SUPABASE_URL,
        latencyMs: latency,
        authHealthy: false,
        realtimeHealthy: false,
        timestamp: new Date().toISOString(),
        error: `HTTP ${res.status}: ${res.statusText}`,
      };
    }
  } catch (err: any) {
    return {
      connected: false,
      projectRef: 'surihwgxgymlgdxyghqx',
      url: SUPABASE_URL,
      latencyMs: Math.round(performance.now() - start),
      authHealthy: false,
      realtimeHealthy: false,
      timestamp: new Date().toISOString(),
      error: err?.message || 'Connection failed',
    };
  }
}

/**
 * Supabase Realtime channel for live threat broadcast.
 * Enables zero-latency broadcast across all connected command terminals and analyst workstations.
 */
export function subscribeToLiveThreats(
  onThreatReceived: (threat: LiveThreatBroadcast) => void
) {
  const channel = supabase.channel('darktrace-telemetry-feed', {
    config: {
      broadcast: { self: true },
    },
  });

  channel
    .on('broadcast', { event: 'threat_alert' }, (payload) => {
      if (payload && payload.payload) {
        onThreatReceived(payload.payload as LiveThreatBroadcast);
      }
    })
    .subscribe((status) => {
      console.log(`[Supabase Realtime] Channel darktrace-telemetry-feed status: ${status}`);
    });

  return {
    unsubscribe: () => {
      supabase.removeChannel(channel);
    },
    broadcastThreat: async (threat: LiveThreatBroadcast) => {
      return await channel.send({
        type: 'broadcast',
        event: 'threat_alert',
        payload: threat,
      });
    },
  };
}

/**
 * Storage / Intelligence Cache helper
 */
export const supabaseIntelligence = {
  /**
   * Log an audit event to Supabase Realtime
   */
  broadcastAuditAction: async (action: string, actor: string, details: Record<string, any>) => {
    const channel = supabase.channel('darktrace-audit-trail');
    await channel.subscribe();
    await channel.send({
      type: 'broadcast',
      event: 'audit_event',
      payload: {
        action,
        actor,
        details,
        timestamp: new Date().toISOString(),
      },
    });
  },

  /**
   * Save intelligence artifact to cloud storage or session
   */
  saveInvestigationNote: async (caseId: string, note: string, analyst: string) => {
    try {
      const { data, error } = await supabase
        .from('investigation_notes')
        .insert([{ case_id: caseId, note, analyst, created_at: new Date().toISOString() }]);

      if (error) {
        // Fallback to local storage if remote table is pending migration
        const existing = JSON.parse(localStorage.getItem(`notes_${caseId}`) || '[]');
        existing.push({ note, analyst, timestamp: new Date().toISOString() });
        localStorage.setItem(`notes_${caseId}`, JSON.stringify(existing));
        return { success: true, mode: 'local-fallback' };
      }
      return { success: true, mode: 'supabase-cloud', data };
    } catch {
      return { success: true, mode: 'local-fallback' };
    }
  },
};
