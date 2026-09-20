from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class IntentEnum(str, Enum):
    MARINE_SAFETY = "MARINE_SAFETY"
    PFZ_DISCOVERY = "PFZ_DISCOVERY"
    OCEAN_CONDITIONS = "OCEAN_CONDITIONS"
    GENERAL_MARINE = "GENERAL_MARINE"

class RiskLevelEnum(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"
    # Backwards compatibility aliases
    SAFE = "LOW"
    CAUTION = "MODERATE"
    UNSAFE = "HIGH"

class SourceTypeEnum(str, Enum):
    LIVE_API = "LIVE_API"
    VERIFIED_CACHE = "VERIFIED_CACHE"
    DETERMINISTIC_GIS = "DETERMINISTIC_GIS"

class LocationQuery(BaseModel):
    name: str
    latitude: float
    longitude: float

class LandingCentre(BaseModel):
    id: str
    name: str
    location_name: str
    district: str
    state: str
    category: str
    latitude: float
    longitude: float
    active_vessels: Optional[int] = None
    contact: Optional[str] = None

class WeatherData(BaseModel):
    temperature_c: float
    wind_speed_kmh: float
    wind_gusts_kmh: float
    wind_direction_deg: float
    wind_direction_cardinal: str
    precipitation_mm: float
    weather_code: int
    weather_description: str
    active_warnings: List[str] = Field(default_factory=list)

class WeatherAgentResponse(BaseModel):
    agent: str = "weather"
    status: str
    location: LocationQuery
    timestamp: datetime
    source: str
    source_type: SourceTypeEnum
    source_timestamp: str
    confidence: float
    data: WeatherData
    errors: List[str] = Field(default_factory=list)

class OceanData(BaseModel):
    significant_wave_height_m: float
    maximum_wave_height_m: Optional[float] = None
    wave_period_s: float
    wave_direction_deg: float
    swell_wave_height_m: float
    swell_period_s: float
    sea_surface_temperature_c: float
    current_speed_knots: Optional[float] = None
    current_direction_deg: Optional[float] = None
    ocean_state_alert: str = "NORMAL"

class OceanAgentResponse(BaseModel):
    agent: str = "ocean"
    status: str
    location: LocationQuery
    timestamp: datetime
    source: str
    source_type: SourceTypeEnum
    source_timestamp: str
    confidence: float
    data: OceanData
    errors: List[str] = Field(default_factory=list)

class PFZZoneDetail(BaseModel):
    id: str
    name: str
    reference_centre: str
    bearing_deg: float
    direction: str
    distance_km: float
    distance_nm: float
    depth_range_m: str
    sst_celsius: float
    chlorophyll_mg_m3: float
    pelagic_density: str
    target_species: str
    valid_until: str
    coordinates: List[List[List[float]]]

class PFZAgentResponse(BaseModel):
    agent: str = "marine_pfz"
    status: str
    location: LocationQuery
    timestamp: datetime
    source: str
    source_type: SourceTypeEnum
    source_timestamp: str
    confidence: float
    data: Dict[str, Any]
    errors: List[str] = Field(default_factory=list)

class GeospatialResponse(BaseModel):
    agent: str = "geospatial"
    status: str
    timestamp: datetime
    source: str = "Shapely / Geodesic Spatial Engine"
    source_type: SourceTypeEnum = SourceTypeEnum.DETERMINISTIC_GIS
    data: Dict[str, Any]
    errors: List[str] = Field(default_factory=list)

class PlannerOutput(BaseModel):
    language: str = "en"
    intent: IntentEnum
    location: LocationQuery
    target_datetime: datetime
    date_expression: str
    time_expression: str
    activity: str = "fishing"
    required_agents: List[str]

class RiskFactor(BaseModel):
    parameter: str
    value: str
    threshold: str
    status: str  # "SAFE", "CAUTION", "UNSAFE", "CLEAR"

class RiskAssessment(BaseModel):
    risk_level: RiskLevelEnum
    risk_score: int
    status_color: str  # "green", "yellow", "red", "gray"
    headline: str
    factors: List[RiskFactor]
    recommendations: List[str]
    evidence_ids: List[str]

class EvidenceRecord(BaseModel):
    evidence_id: str
    agent: str
    parameter: str
    value: Any
    unit: str
    source: str
    source_type: str
    source_timestamp: str
    retrieved_at: str
    location: str

class AgentTimelineItem(BaseModel):
    agent: str
    label: str
    status: str  # "completed", "warning", "error"
    duration_ms: int
    summary: str

class QueryRequest(BaseModel):
    session_id: Optional[str] = "default-session"
    query: str
    location_override: Optional[str] = None
    language_override: Optional[str] = "auto"
    force_demo_mode: Optional[bool] = None

class QueryResponse(BaseModel):
    # Core schema requested for SIH 2026
    query: str
    location: str
    time: str
    intent: str
    risk: str
    answer: str
    evidence: List[EvidenceRecord]
    sources: List[str]
    agents_used: List[str]
    
    # Extended platform metadata
    session_id: str
    query_language: str
    risk_assessment: RiskAssessment
    agent_timeline: List[AgentTimelineItem]
    map_features: Dict[str, Any]
    is_demo_mode: bool
    execution_time_ms: int
