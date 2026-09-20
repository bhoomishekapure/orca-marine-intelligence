# ORCA Phased Implementation Plan (SIH 2026)

## 1. Phased Roadmap

This plan outlines the systematic engineering execution across 10 distinct phases. Each phase concludes with automated verification before advancing.

```
Phase 1: Project Setup & Scaffolding
   ↓
Phase 2: Database & Seed Geospatial Data
   ↓
Phase 3: Data Adapters (Live & Verified Fallback)
   ↓
Phase 4: Specialized Agents Implementation
   ↓
Phase 5: Planner & Agent Orchestrator
   ↓
Phase 6: Spatial, Temporal & Risk Reasoning
   ↓
Phase 7: Backend FastAPI Service & Endpoints
   ↓
Phase 8: Frontend Application (React + MapLibre GL)
   ↓
Phase 9: Comprehensive Testing & Verification
   ↓
Phase 10: Demo Mode, Documentation & Final Polish
```

---

## 2. Detailed Phase Specifications

### Phase 1: Project Setup & Environment Scaffolding
- **Objectives**:
  - Establish clean project directory structure (`backend/`, `frontend/`, `agents/`, `reasoning/`, `data/`, `tests/`, `docs/`).
  - Create `pyproject.toml` / `requirements.txt` with FastAPI, Pydantic, Uvicorn, Shapely, PyProj, httpx, pytest.
  - Setup `.env.example` and configuration loading module.
  - Create `docker-compose.yml` defining PostgreSQL 16 with PostGIS extension.
  - Ensure zero-dependency local fallback mode (SQLite + Shapely) so developers can run without Docker running.
- **Verification**:
  - Python virtual environment activates cleanly; dependencies install without conflicts.

### Phase 2: Database Schema & Seed Data Ingestion
- **Objectives**:
  - Implement relational and spatial models: `locations`, `marine_observations`, `weather_observations`, `pfz_zones`, `marine_advisories`, `restricted_zones`, `conversations`, `messages`, `evidence_records`.
  - Create GeoJSON data files for Maharashtra coast:
    - `landing_centres.geojson` (Ratnagiri Mirkarwada, Mirya Bandar, Jaigad, Devgad, Malvan).
    - `pfz_polygons.geojson` (Authentic INCOIS PFZ coordinates offshore Ratnagiri).
    - `restricted_zones.geojson` (Malvan Marine Sanctuary, port shipping fairway).
  - Seed database with verified baseline datasets.
- **Verification**:
  - Migration script initializes tables; seed script populates 5 landing centres, 3 PFZ zones, and 2 restricted zones.

### Phase 3: Marine Data Adapters
- **Objectives**:
  - Build `OpenMeteoMarineAdapter` for live wave height, period, swell, and SST.
  - Build `OpenMeteoWeatherAdapter` for live wind speed, direction, gusts, and rain.
  - Build `INCOISAdvisoryAdapter` for PFZ advisories and ocean state bulletins.
  - Build `IMDCoastalWarningAdapter` for squall and severe weather alerts.
  - Build `FallbackCachedAdapter` providing verified authentic snapshots when offline.
  - Build unified `DataProviderRegistry` managing failover with provenance tags (`LIVE_API` vs `VERIFIED_CACHE`).
- **Verification**:
  - Unit tests verify network fetch when online, and instant graceful fallback to cached data if network disconnected.

### Phase 4: Specialized Agents
- **Objectives**:
  - Implement `BaseAgent` with strict Pydantic schemas.
  - Implement `WeatherAgent`: queries weather adapter, normalizes units ($km/h$, $^\circ$, $mm$).
  - Implement `OceanAgent`: queries ocean adapter, normalizes wave height ($m$), period ($s$), SST ($^\circ C$).
  - Implement `PFZAgent`: parses active PFZ zones, water depth, and distance vectors.
  - Implement `GeospatialEngine`: calculates distances (Haversine/geodesic), bearing, point-in-polygon containment, and geofence alerts.
- **Verification**:
  - Agent test suite passes with mock inputs, asserting 100% adherence to schema contracts.

### Phase 5: Planner & Multi-Agent Orchestrator
- **Objectives**:
  - Create `LLMProvider` interface with implementations:
    - `GeminiProvider` (Google GenAI / Gemini API)
    - `OpenAIProvider` (OpenAI API compatibility)
    - `MockRuleBasedProvider` (deterministic local NLP parser for demo/offline resilience)
  - Implement `OrcaOrchestrator`:
    - Language detection (`en`, `mr`, `hi`).
    - Intent detection (`MARINE_SAFETY`, `PFZ_DISCOVERY`, `OCEAN_CONDITIONS`, `GENERAL_MARINE_QUERY`).
    - Entity extraction (location name, target date, target time).
    - Multi-turn conversation context manager.
    - Concurrent agent execution DAG via `asyncio.gather`.
- **Verification**:
  - Orchestrator tests correctly route Example 1 ("Is it safe..."), Example 2 ("Where is nearest PFZ..."), and Example 4 ("What about 9 AM...").

### Phase 6: Deterministic Reasoning & Evidence Aggregation
- **Objectives**:
  - Implement `RiskEngine`:
    - Evaluates marine threshold rules (wave height, wind speed, advisories, geofencing).
    - Generates risk level (`SAFE`, `CAUTION`, `UNSAFE`, `UNKNOWN`) and contributing factor list.
  - Implement `TemporalReasoning`:
    - Filters 24-48 hour forecasts to user's specified hour/time window (e.g., 06:00 vs 09:00).
  - Implement `EvidenceAggregator`:
    - Compiles immutable evidence trail linking each factor to source, timestamp, and agent.
  - Implement `ResponseSynthesizer`:
    - Assembles final localized natural language response strictly referencing aggregated evidence.
- **Verification**:
  - Risk engine unit tests verify threshold boundaries and boundary condition triggers.

### Phase 7: Backend FastAPI Service
- **Objectives**:
  - Build endpoints:
    - `POST /api/query`: Main conversational agentic query pipeline.
    - `GET /api/health`: Health status of agents and data providers.
    - `GET /api/locations`: List of supported coastal landing centres and coordinates.
    - `GET /api/map/layers`: GeoJSON features for map (PFZs, restricted zones, landing centres).
    - `GET /api/marine-conditions`: Direct tabular condition feed for a location.
  - Add CORS, request validation, structured logging, and error handling.
- **Verification**:
  - Pytest API tests verify HTTP 200 responses, schema validity, and error handling.

### Phase 8: Frontend Web Application
- **Objectives**:
  - Initialize React 19 + TypeScript + Vite + Tailwind CSS application.
  - Integrate MapLibre GL with dark oceanic theme and responsive layout.
  - Build UI Components:
    - `Header`: ORCA brand, Demo Mode badge, language selector, data freshness indicator.
    - `MarineMap`: Interactive MapLibre GL map rendering landing centres, PFZ polygons, hazard zones, and vessel vectors.
    - `ChatPanel`: Chat history, suggested queries, message bubbles with markdown support.
    - `AgentActivityTracker`: Live visual timeline of active agents (Understanding -> Weather -> Ocean -> Marine -> Geospatial -> Risk).
    - `RiskCard`: Prominent visual safety assessment (Green/Yellow/Red) with contributing factors.
    - `EvidenceInspector`: Collapsible drawer detailing parameters, values, sources, and timestamps.
- **Verification**:
  - Frontend builds with zero TypeScript errors; map renders layers; chat executes queries against FastAPI backend.

### Phase 9: Comprehensive Integration & Verification
- **Objectives**:
  - End-to-end integration tests verifying all 5 core demonstration flows.
  - Failure scenario tests: external API timeout, missing parameters, out-of-bounds coordinates.
  - Multi-language verification (English, Marathi, Hindi).
- **Verification**:
  - 100% automated test pass rate across backend, reasoning, agents, and API.

### Phase 10: Demo Mode, SIH Presentation & Documentation
- **Objectives**:
  - Create prominent "DEMO MODE" toggle for deterministic Hackathon presentations.
  - Document setup commands, environment variables, and architecture.
  - Prepare SIH 6-slide visual assets and executive briefing.
- **Verification**:
  - Clean startup from scratch using standard scripts.
