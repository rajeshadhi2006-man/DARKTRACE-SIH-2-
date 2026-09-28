import axios from 'axios';
import { DashboardStats, ActorSummary, GraphData, Evidence, AttributionAssessment, TimelineEvent, AuditLogItem } from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('darktrace_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response && err.response.status === 401) {
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem('darktrace_token');
        localStorage.removeItem('darktrace_user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(err);
  }
);

export const authApi = {
  login: async (username: string, password: string) => {
    const res = await api.post('/auth/login/json', { username, password });
    return res.data;
  },
  getMe: async () => {
    const res = await api.get('/auth/me');
    return res.data;
  }
};

export const dashboardApi = {
  getStats: async (): Promise<DashboardStats> => {
    const res = await api.get('/dashboard/stats');
    return res.data;
  }
};

export const actorsApi = {
  list: async (params?: Record<string, any>): Promise<ActorSummary[]> => {
    const res = await api.get('/actors', { params });
    return res.data;
  },
  getById: async (id: string) => {
    const res = await api.get(`/actors/${id}`);
    return res.data;
  },
  exportCsvUrl: '/api/actors/export/csv',
  exportJsonUrl: '/api/actors/export/json',
  exportCsv: () => {
    window.open('/api/actors/export/csv', '_blank');
  },
  exportJson: () => {
    window.open('/api/actors/export/json', '_blank');
  }
};

export const personasApi = {
  list: async (params?: Record<string, any>) => {
    const res = await api.get('/personas', { params });
    return res.data;
  },
  getById: async (id: string) => {
    const res = await api.get(`/personas/${id}`);
    return res.data;
  }
};

export const graphApi = {
  getActorGraph: async (actorId: string): Promise<GraphData> => {
    const res = await api.get(`/graph/${actorId}`);
    return res.data;
  }
};

export const timelineApi = {
  getActorTimeline: async (actorId: string, params?: Record<string, any>): Promise<TimelineEvent[]> => {
    const res = await api.get(`/timeline/${actorId}`, { params });
    return res.data;
  }
};

export const evidenceApi = {
  list: async (params?: Record<string, any>): Promise<Evidence[]> => {
    const res = await api.get('/evidence', { params });
    return res.data;
  },
  getById: async (id: string): Promise<Evidence> => {
    const res = await api.get(`/evidence/${id}`);
    return res.data;
  }
};

export const attributionApi = {
  getByActorId: async (actorId: string): Promise<AttributionAssessment[]> => {
    const res = await api.get(`/attribution/${actorId}`);
    return res.data;
  },
  review: async (assessmentId: string, isConfirmed: boolean, analystComment: string) => {
    const res = await api.post('/attribution/review', {
      assessment_id: assessmentId,
      is_confirmed: isConfirmed,
      analyst_comment: analystComment
    });
    return res.data;
  },
  correlateLive: async (payload: {
    persona_a: string;
    persona_b: string;
    target_actor_id?: string;
    crypto_wallets?: string[];
    onion_services?: string[];
    pgp_fingerprints?: string[];
    clearnet_ips?: string[];
    text_sample_a?: string;
    text_sample_b?: string;
    active_hours_a?: number[];
    active_hours_b?: number[];
    weights?: Record<string, number>;
    auto_save_as_assessment?: boolean;
    auto_create_actor?: boolean;
  }) => {
    const res = await api.post('/attribution/correlate-live', payload);
    return res.data;
  }
};

export const analyticsApi = {
  runJob: async (taskType: string, actorId?: string, parameters?: Record<string, any>) => {
    const res = await api.post('/analytics/run', { task_type: taskType, actor_id: actorId, parameters: parameters || {} });
    return res.data;
  },
  askAssistant: async (query: string, actorId?: string) => {
    const res = await api.post('/analytics/assistant', { query, actor_id: actorId });
    return res.data;
  },
  compareStylometry: async (textSample: string) => {
    const res = await api.post('/analytics/stylometry/compare', textSample, {
      headers: { 'Content-Type': 'text/plain' }
    });
    return res.data;
  }
};

export const intelligenceApi = {
  list: async (params?: Record<string, any>) => {
    const res = await api.get('/intelligence', { params });
    return res.data;
  },
  upload: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post('/intelligence/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },
  inject: async (data: { source_name: string; author: string; raw_text: string }) => {
    const res = await api.post('/intelligence/inject', data);
    return res.data;
  }
};

export const searchApi = {
  query: async (q: string, entityType?: string) => {
    const res = await api.get('/search', { params: { q, entity_type: entityType } });
    return res.data;
  }
};

export const reportsApi = {
  list: async () => {
    const res = await api.get('/reports');
    return res.data;
  },
  generate: async (actorId: string, format = 'PDF') => {
    const res = await api.post('/reports/generate', { actor_id: actorId, format });
    return res.data;
  }
};

export const auditApi = {
  list: async (params?: Record<string, any>): Promise<AuditLogItem[]> => {
    const res = await api.get('/audit', { params });
    return res.data;
  }
};

export const investigationsApi = {
  list: async () => {
    const res = await api.get('/investigations');
    return res.data;
  },
  getById: async (id: string) => {
    const res = await api.get(`/investigations/${id}`);
    return res.data;
  },
  create: async (data: { title: string; description?: string; case_id?: string; priority?: string; scope?: string; seed_indicators?: any[] }) => {
    const res = await api.post('/investigations', data);
    return res.data;
  },
  correlate: async (id: string, seedType = 'alias', seedValue = 'nightfox_404') => {
    const res = await api.post(`/investigations/${id}/correlate`, { seed_type: seedType, seed_value: seedValue });
    return res.data;
  },
  updateStatus: async (id: string, status: string, notes?: string) => {
    const res = await api.post(`/investigations/${id}/status`, { status, notes });
    return res.data;
  }
};

export const campaignsApi = {
  list: async () => {
    const res = await api.get('/campaigns');
    return res.data;
  },
  getById: async (id: string) => {
    const res = await api.get(`/campaigns/${id}`);
    return res.data;
  }
};

export const alertsApi = {
  list: async () => {
    const res = await api.get('/alerts');
    return res.data;
  },
  ack: async (id: string) => {
    const res = await api.post(`/alerts/${id}/ack`);
    return res.data;
  },
  ackAll: async () => {
    const res = await api.post('/alerts/ack-all');
    return res.data;
  }
};

export const stixApi = {
  exportActor: (actorId: string) => {
    window.open(`/api/stix/actor/${actorId}`, '_blank');
  }
};

export const mitreApi = {
  list: async () => {
    const res = await api.get('/mitre');
    return res.data;
  }
};

export const healthApi = {
  check: async () => {
    const res = await api.get('/health');
    return res.data;
  }
};

export const realtimeApi = {
  getStatus: async () => {
    const res = await api.get('/realtime/status');
    return res.data;
  },
  start: async () => {
    const res = await api.post('/realtime/start');
    return res.data;
  },
  stop: async () => {
    const res = await api.post('/realtime/stop');
    return res.data;
  },
  setConfig: async (interval_seconds: number) => {
    const res = await api.post('/realtime/config', { interval_seconds });
    return res.data;
  },
  trigger: async () => {
    const res = await api.post('/realtime/trigger');
    return res.data;
  },
  reset: async () => {
    const res = await api.post('/realtime/reset');
    return res.data;
  },
  clearAllToZero: async () => {
    const res = await api.post('/realtime/clear-all-to-zero');
    return res.data;
  },
  reseedDemoData: async () => {
    const res = await api.post('/realtime/reseed-demo-data');
    return res.data;
  }
};

export const networkDetectionApi = {
  getStatus: async () => {
    const res = await api.get('/network-detection/status');
    return res.data;
  },
  analyzeClient: async (payload: Record<string, any>) => {
    const res = await api.post('/network-detection/analyze-client', payload);
    return res.data;
  },
  classifyArtifact: async (payload: { user_agent?: string; ip_address?: string; raw_headers?: string; source_context?: string }) => {
    const res = await api.post('/network-detection/classify-artifact', payload);
    return res.data;
  },
  getLiveTorRelays: async (limit: number = 15) => {
    const res = await api.get('/network-detection/live-tor-relays', { params: { limit } });
    return res.data;
  },
  lookupLiveBtcWallet: async (address: string) => {
    const res = await api.get(`/network-detection/live-btc-lookup/${encodeURIComponent(address)}`);
    return res.data;
  },
  liveSocketProbe: async (target_host: string, target_port: number = 443) => {
    const res = await api.post('/network-detection/live-socket-probe', { target_host, target_port });
    return res.data;
  },
  getBrowserCatalog: async () => {
    const res = await api.get('/network-detection/browsers/catalog');
    return res.data;
  },
  identifyBrowserCrimePattern: async (payload: { user_agent?: string; ip_address?: string; raw_headers?: string; source_context?: string }) => {
    const res = await api.post('/network-detection/browsers/identify-crime-pattern', payload);
    return res.data;
  }
};

export const supabaseApi = {
  getStatus: async () => {
    const res = await api.get('/supabase/status');
    return res.data;
  },
  getConfig: async () => {
    const res = await api.get('/supabase/config');
    return res.data;
  },
  broadcastThreat: async (payload: { threat_type: string; severity?: string; source?: string; actor?: string; summary: string }) => {
    const res = await api.post('/supabase/broadcast', payload);
    return res.data;
  }
};

export const analysisApi = {
  compare: async (payload?: { actor_id_a?: string; actor_id_b?: string; investigation_id?: string; custom_persona_a?: any; custom_persona_b?: any }) => {
    const res = await api.post('/analysis/compare', payload || {});
    return res.data;
  },
  getDemoScenario: async () => {
    const res = await api.get('/analysis/demo-scenario');
    return res.data;
  },
  getAnalysis: async (id: string) => {
    const res = await api.get(`/analysis/${id}`);
    return res.data;
  },
  getEvidence: async (id: string) => {
    const res = await api.get(`/analysis/${id}/evidence`);
    return res.data;
  },
  patternAnalysis: async (payload: any) => {
    const res = await api.post('/analysis/pattern', payload);
    return res.data;
  },
  analyzeActor: async (actorId: string, params?: { compare_with?: string; investigation_id?: string }) => {
    const res = await api.post(`/analysis/actor/${actorId}`, null, { params });
    return res.data;
  }
};

export const infrastructureApi = {
  getFindings: async () => {
    const res = await api.get('/infrastructure/findings');
    return res.data;
  },
  probeSurface: async (payload: {
    target_onion_or_domain: string;
    tls_cert_san?: string;
    server_status_text?: string;
    favicon_murmur3?: number;
    target_ip?: string;
    source_context?: string;
  }) => {
    const res = await api.post('/infrastructure/probe', payload);
    return res.data;
  }
};

export { api };
export default api;
