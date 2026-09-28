export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: 'ADMIN' | 'SUPERVISOR' | 'ANALYST' | 'VIEWER';
}

export interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
}

export interface ActorSummary {
  id: string;
  primary_name: string;
  threat_category: string;
  threat_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: string;
  analytical_confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  confidence_score: number;
  first_observed?: string;
  last_observed?: string;
  persona_count: number;
  evidence_count: number;
}

export interface Persona {
  id: string;
  canonical_handle: string;
  platform: string;
  actor_id?: string;
  first_seen?: string;
  last_seen?: string;
  activity_count: number;
  confidence: number;
  reliability: string;
  handles?: string[];
  provenance?: string;
}

export interface Evidence {
  id: string;
  source_id?: string;
  evidence_type: 'IDENTITY' | 'INFRASTRUCTURE' | 'CONTENT' | 'BEHAVIOR' | 'HISTORICAL';
  title: string;
  description: string;
  content_hash: string;
  integrity_status?: string;
  timestamp: string;
  reliability: string;
  confidence: number;
  related_entity_ids: string[];
  provenance?: string;
}

export interface AttributionAssessment {
  id: string;
  actor_id: string;
  candidate_persona_a: string;
  candidate_persona_b: string;
  assessment_type: string;
  analytical_confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  confidence_score: number;
  reasoning_summary: string;
  recommendation: string;
  is_confirmed_by_analyst: boolean;
  confirmed_by_user_id?: string;
  confirmed_at?: string;
  supporting_evidence?: Evidence[];
  contradicting_evidence?: Evidence[];
}

export interface TimelineEvent {
  id: string;
  actor_id?: string;
  persona_id?: string;
  event_type: string;
  title: string;
  description?: string;
  event_timestamp: string;
  source_id?: string;
  evidence_id?: string;
  confidence: number;
}

export interface DashboardStats {
  total_actors: number;
  total_personas: number;
  total_handles: number;
  total_intelligence_records: number;
  total_relationships: number;
  potential_persona_links: number;
  infrastructure_relationships: number;
  pending_reviews: number;
  evidence_items: number;
  source_distribution: Record<string, number>;
  confidence_distribution: Record<string, number>;
  activity_over_time: Array<{ period: string; observations: number; relationships: number; evidence: number }>;
  recent_findings: Array<{
    id: string;
    type: string;
    title: string;
    description: string;
    confidence: string;
    actor_id: string;
    requires_review: boolean;
  }>;
}

export interface AuditLogItem {
  id: string;
  user_id?: string;
  username?: string;
  action: string;
  object_type?: string;
  object_id?: string;
  details?: Record<string, any>;
  ip_address?: string;
  timestamp: string;
}

export interface GraphNode {
  data: {
    id: string;
    label: string;
    type: string;
    [key: string]: any;
  };
}

export interface GraphEdge {
  data: {
    id: string;
    source: string;
    target: string;
    label: string;
    confidence: number;
    evidence_id?: string;
  };
}

export interface GraphData {
  actor_id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  total_nodes: number;
  total_edges: number;
}
