# ORCA Data & API Contract Specifications

## 1. Overview
To ensure complete modularity, reliability, and testability, all communication between the web frontend, backend API, orchestrator, specialized agents, and reasoning engines is governed by strict Pydantic schemas. 

Unstructured natural-language blobs are prohibited between internal subsystems.

---

## 2. Agent Data Contracts

### 2.1. Base Agent Schemas
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class LocationQuery(BaseModel):
    name: str
    latitude: float
    longitude: float

class BaseAgentResponse(BaseModel):
    agent: str
    status: str = Field(..., description="'success' | 'warning' | 'error'")
    location: LocationQuery
    timestamp: datetime
    source: str
    source_type: str = Field(..., description="'LIVE_API' | 'VERIFIED_CACHE'")
    source_timestamp: str
    confidence: Optional[float] = None
    data: Dict[str, Any]
    errors: List[str] = Field(default_factory=list)
```

### 2.2. Weather Agent Response Contract
```json
{
  "agent": "weather",
  "status": "success",
  "location": {
    "name": "Ratnagiri Offshore",
    "latitude": 16.99,
    "longitude": 73.30
  },
  "timestamp": "2026-09-20T12:00:00Z",
  "source": "Open-Meteo Weather / IMD Marine Bulletin",
  "source_type": "LIVE_API",
  "source_timestamp": "2026-09-20T11:00:00Z",
  "confidence": 0.94,
  "data": {
    "temperature_c": 29.2,
    "wind_speed_kmh": 24.5,
    "wind_gusts_kmh": 32.1,
    "wind_direction_deg": 260,
    "wind_direction_cardinal": "WSW",
    "precipitation_mm": 0.0,
    "weather_code": 1,
    "weather_description": "Mainly clear",
    "active_warnings": []
  },
  "errors": []
}
```

### 2.3. Ocean Agent Response Contract
```json
{
  "agent": "ocean",
  "status": "success",
  "location": {
    "name": "Ratnagiri Coastal Waters",
    "latitude": 16.99,
    "longitude": 73.30
  },
  "timestamp": "2026-09-20T12:00:00Z",
  "source": "Open-Meteo Marine / INCOIS OSF",
  "source_type": "LIVE_API",
  "source_timestamp": "2026-09-20T11:00:00Z",
  "confidence": 0.92,
  "data": {
    "significant_wave_height_m": 1.4,
    "wave_period_s": 8.2,
    "wave_direction_deg": 250,
    "swell_wave_height_m": 1.1,
    "swell_period_s": 10.5,
    "sea_surface_temperature_c": 28.6,
    "current_speed_knots": 0.8,
    "ocean_state_alert": "NORMAL"
  },
  "errors": []
}
```

### 2.4. Marine / PFZ Agent Response Contract
```json
{
  "agent": "marine_pfz",
  "status": "success",
  "location": {
    "name": "Ratnagiri Mirya Bandar",
    "latitude": 17.01,
    "longitude": 73.28
  },
  "timestamp": "2026-09-20T12:00:00Z",
  "source": "INCOIS PFZ Advisory Bulletin",
  "source_type": "VERIFIED_CACHE",
  "source_timestamp": "2026-09-20T06:00:00Z",
  "confidence": 0.90,
  "data": {
    "active_advisories_count": 3,
    "primary_zone": {
      "id": "PFZ-MH-RTG-01",
      "landing_centre": "Mirya Bandar, Ratnagiri",
      "bearing_deg": 240,
      "direction": "WSW",
      "distance_km": 22.5,
      "distance_nm": 12.15,
      "depth_range_m": [35, 50],
      "chlorophyll_mg_m3": 0.85,
      "sst_c": 28.4,
      "valid_until": "2026-09-22T18:00:00Z",
      "coordinates": [73.08, 16.90]
    },
    "general_advisory": "Good pelagic fish aggregation observed along 40m thermal front."
  },
  "errors": []
}
```

### 2.5. Geospatial Engine Response Contract
```json
{
  "agent": "geospatial",
  "status": "success",
  "timestamp": "2026-09-20T12:00:00Z",
  "source": "PostGIS / Shapely Spatial Engine",
  "source_type": "DETERMINISTIC_GIS",
  "data": {
    "origin_location": "Ratnagiri (Mirkarwada)",
    "target_location": "PFZ-MH-RTG-01",
    "geodesic_distance_km": 22.48,
    "geodesic_distance_nm": 12.14,
    "compass_bearing_deg": 239.8,
    "compass_direction": "WSW",
    "is_inside_restricted_zone": false,
    "nearest_restricted_zone": {
      "name": "Malvan Marine Sanctuary",
      "distance_km": 78.4,
      "status": "OUTSIDE"
    },
    "geojson_features": {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": {
            "type": "LineString",
            "coordinates": [[73.28, 17.01], [73.08, 16.90]]
          },
          "properties": {
            "feature_type": "navigation_vector",
            "distance_km": 22.5,
            "bearing": "240° WSW"
          }
        }
      ]
    }
  },
  "errors": []
}
```

---

## 3. Orchestrator & Reasoning Contracts

### 3.1. Planner Output Schema
```json
{
  "language": "en",
  "intent": "MARINE_SAFETY",
  "location": {
    "name": "Ratnagiri",
    "latitude": 16.99,
    "longitude": 73.30
  },
  "target_datetime": "2026-09-21T06:00:00",
  "date_expression": "tomorrow",
  "time_expression": "06:00",
  "activity": "fishing",
  "required_agents": [
    "weather",
    "ocean",
    "marine_pfz",
    "geospatial"
  ]
}
```

### 3.2. Deterministic Risk Engine Output Schema
```json
{
  "risk_level": "LOW",
  "risk_score": 18,
  "status_color": "green",
  "headline": "Conditions Favourable for Artisanal & Mechanized Fishing",
  "factors": [
    {
      "parameter": "Significant Wave Height",
      "value": "1.4 m",
      "threshold": "< 1.8 m",
      "status": "SAFE"
    },
    {
      "parameter": "Wind Speed",
      "value": "24.5 km/h",
      "threshold": "< 30 km/h",
      "status": "SAFE"
    },
    {
      "parameter": "Marine Sanctuary Geofence",
      "value": "78.4 km away",
      "threshold": "Outside boundary",
      "status": "CLEAR"
    }
  ],
  "recommendations": [
    "Proceed with standard safety equipment.",
    "Monitor afternoon wind shifts as onshore breeze develops."
  ],
  "evidence_ids": ["EVID-001", "EVID-002", "EVID-003"]
}
```

### 3.3. Evidence Record Schema
```json
{
  "evidence_id": "EVID-001",
  "agent": "ocean",
  "parameter": "Significant Wave Height",
  "value": 1.4,
  "unit": "meters",
  "source": "Open-Meteo Marine (ECMWF Model)",
  "source_type": "LIVE_API",
  "source_timestamp": "2026-09-21T06:00:00Z",
  "retrieved_at": "2026-09-20T12:00:00Z",
  "location": "Ratnagiri Offshore (16.99° N, 73.30° E)"
}
```

---

## 4. Frontend-Backend REST API Contracts

### 4.1. `POST /api/query`
Main conversational query endpoint.

#### Request Body:
```json
{
  "session_id": "session-xyz-123",
  "query": "Is it safe to go fishing tomorrow at 6 AM near Ratnagiri?",
  "location_override": null,
  "language_override": "auto"
}
```

#### Response Body:
```json
{
  "session_id": "session-xyz-123",
  "query_language": "en",
  "intent": "MARINE_SAFETY",
  "answer": "Yes, conditions near Ratnagiri tomorrow at 6:00 AM are generally safe for fishing. The significant wave height is 1.4 m with wind speeds of 24.5 km/h from the WSW. No active cyclone or squall warnings are in effect for the Konkan coast.",
  "risk_assessment": { ... },
  "agent_timeline": [
    {"agent": "orchestrator", "status": "completed", "duration_ms": 32},
    {"agent": "weather", "status": "completed", "duration_ms": 110},
    {"agent": "ocean", "status": "completed", "duration_ms": 115},
    {"agent": "marine_pfz", "status": "completed", "duration_ms": 45},
    {"agent": "geospatial", "status": "completed", "duration_ms": 12},
    {"agent": "risk_engine", "status": "completed", "duration_ms": 5}
  ],
  "evidence": [ ... ],
  "map_features": {
    "type": "FeatureCollection",
    "features": [ ... ]
  },
  "is_demo_mode": false,
  "execution_time_ms": 319
}
```

### 4.2. `GET /api/locations`
Returns recognized coastal landing centres.
```json
[
  {
    "id": "mirkarwada_ratnagiri",
    "name": "Ratnagiri (Mirkarwada Harbour)",
    "latitude": 17.002,
    "longitude": 73.284,
    "district": "Ratnagiri",
    "state": "Maharashtra",
    "type": "Major Fishing Harbour"
  }
]
```

### 4.3. `GET /api/map/layers`
Returns static and dynamic GeoJSON map layers for base display.
- Layer `landing_centres`
- Layer `pfz_polygons`
- Layer `restricted_zones`
- Layer `bathymetry_contours`
