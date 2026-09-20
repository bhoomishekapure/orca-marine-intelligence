export type RiskLevel = 'SAFE' | 'CAUTION' | 'UNSAFE' | 'UNKNOWN';

export interface LandingCentre {
  id: string;
  name: string;
  location_name: string;
  district: string;
  state: string;
  category: string;
  latitude: float;
  longitude: float;
  active_vessels?: number;
  contact?: string;
}

export type float = number;

export interface RiskFactor {
  parameter: string;
  value: string;
  threshold: string;
  status: string;
}

export interface RiskAssessment {
  risk_level: RiskLevel;
  risk_score: number;
  status_color: string;
  headline: string;
  factors: RiskFactor[];
  recommendations: string[];
  evidence_ids: string[];
}

export interface EvidenceRecord {
  evidence_id: string;
  agent: string;
  parameter: string;
  value: any;
  unit: string;
  source: string;
  source_type: string;
  source_timestamp: string;
  retrieved_at: string;
  location: string;
}

export interface AgentTimelineItem {
  agent: string;
  label: string;
  status: string;
  duration_ms: number;
  summary: string;
}

export interface QueryResponse {
  query: string;
  location: string;
  time: string;
  intent: string;
  risk: string;
  answer: string;
  evidence: EvidenceRecord[];
  sources: string[];
  agents_used: string[];
  session_id: string;
  query_language: string;
  risk_assessment: RiskAssessment;
  agent_timeline: AgentTimelineItem[];
  map_features: any;
  is_demo_mode: boolean;
  execution_time_ms: number;
}

export interface MapLayers {
  landing_centres: any;
  pfz_polygons: any;
  restricted_zones: any;
}

export interface MarineConditions {
  location: {
    name: string;
    latitude: number;
    longitude: number;
  };
  timestamp: string;
  weather: {
    temperature_c: number;
    wind_speed_kmh: number;
    wind_gusts_kmh: number;
    wind_direction_deg: number;
    wind_direction_cardinal: string;
    precipitation_mm: number;
    weather_description: string;
    active_warnings: string[];
  };
  ocean: {
    significant_wave_height_m: number;
    maximum_wave_height_m?: number;
    wave_period_s: number;
    wave_direction_deg: number;
    swell_wave_height_m: number;
    swell_period_s: number;
    sea_surface_temperature_c: number;
    current_speed_knots?: number;
    ocean_state_alert: string;
  };
  source_marine: string;
  source_weather: string;
  source_type: string;
}

export interface HealthStatus {
  status: string;
  app_name: string;
  environment: string;
  demo_mode: boolean;
  llm_provider: string;
  focus_geography: {
    region: string;
    default_lat: number;
    default_lon: number;
  };
  providers: Array<{
    name: string;
    type: string;
    healthy: boolean;
    coverage: string;
    last_error?: string;
  }>;
}
