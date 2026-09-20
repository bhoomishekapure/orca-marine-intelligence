# ORCA — Marine Ecosystem Reasoning with Collaborative Agents
## Technical Architecture & System Design Document

### 1. Executive Summary & System Vision
**ORCA (Oceanic Reasoning with Collaborative Agents)** is an agentic marine intelligence and decision-support platform engineered for coastal communities, artisanal and mechanized fishermen, maritime authorities, and port operators.

Built specifically for the **Smart India Hackathon 2026**, ORCA solves a critical maritime problem: coastal stakeholders must navigate fragmented, high-latency information across ocean forecasts, weather alerts, fisheries advisories, and navigational safety zones. ORCA provides an intuitive, conversational, and multilingual interface that translates natural language queries (in English, Marathi, and Hindi) into multi-agent workflows, performs deterministic geospatial and temporal reasoning, evaluates maritime risk thresholds, and presents an explainable, evidence-backed response alongside an interactive MapLibre GL map.

---

### 2. Core Architectural Principles
1. **Zero Hallucinated Metrics**: The Large Language Model (LLM) NEVER invents, estimates, or computes marine parameters (wave height, wind speed, SST, coordinates, or distances).
2. **Separation of LLM and Deterministic Logic**:
   - **LLM Responsibility**: Intent detection, entity extraction (location, date/time, activity), agent task planning, synthesis of retrieved evidence into human-intelligible prose, and multilingual localization.
   - **Deterministic Code / GIS Responsibility**: Haversine/geodesic distance calculations, point-in-polygon checks, spatial geofence intersections, temporal timestamp filtering, and numeric safety risk scoring based on configurable rules.
3. **Pluggable LLM Provider Abstraction**: The core system interacts with an abstract `LLMProvider` interface (`generate`, `structured_output`, `tool_selection`). Adapters exist for Google Gemini, OpenAI, Anthropic, or an offline rule-based Mock LLM provider for zero-API-key demonstrations.
4. **Resilient Data Ingestion & Graceful Degradation**:
   - Live external APIs (e.g., Open-Meteo Marine / Weather APIs) are queried when network connectivity permits.
   - Authoritative official datasets (INCOIS Ocean State Forecasts, INCOIS PFZ Advisories, IMD Coastal Bulletins) are ingested through dedicated adapters with verified caching.
   - Every metric preserves its provenance (`source`, `retrieved_at`, `timestamp`, `units`, `location`, `quality_flag`).
5. **Full Evidence Trail & Explainability**: Every assessment lists the exact parameters, values, units, timestamps, and reporting agencies that justified the advice.

---

### 3. End-to-End Conceptual Architecture

```
                                      +-----------------------------------+
                                      |         End User / Web UI         |
                                      |  (React 19 + Vite + MapLibre GL)  |
                                      +-----------------+-----------------+
                                                        |
                                       Natural Language Query (EN / MR / HI)
                                                        |
                                                        v
                                      +-----------------------------------+
                                      |       FastAPI Gateway / API       |
                                      |      (/api/query, /api/map)       |
                                      +-----------------+-----------------+
                                                        |
                                                        v
                                      +-----------------------------------+
                                      |      ORCA Planner / Orchestrator  |
                                      |  - Intent Detection               |
                                      |  - Entity Extraction              |
                                      |  - Multilingual Normalization     |
                                      |  - Execution DAG Builder          |
                                      +-----------------+-----------------+
                                                        |
                     +------------------+---------------+------------------+
                     |                  |               |                  |
                     v                  v               v                  v
             +---------------+  +---------------+  +----------+  +-------------------+
             | Weather Agent |  |  Ocean Agent  |  | PFZ Agent|  | Geospatial Engine |
             +-------+-------+  +-------+-------+  +----+-----+  +---------+---------+
                     |                  |               |                  |
             (Wind, Rain, GFS)   (Waves, SST, OSF)  (PFZ, Chl)     (PostGIS / GeoJSON)
                     |                  |               |                  |
                     +------------------+---------------+------------------+
                                                        |
                                            Normalized Agent Results
                                                        |
                                                        v
                                      +-----------------------------------+
                                      |     Temporal & Spatial Filter     |
                                      |  (Matches query target date/time) |
                                      +-----------------+-----------------+
                                                        |
                                                        v
                                      +-----------------------------------+
                                      |   Deterministic Risk Engine       |
                                      |  - Rule-based safety assessment   |
                                      |  - Marine parameter thresholding  |
                                      |  - Geofence restriction checks    |
                                      +-----------------+-----------------+
                                                        |
                                         Risk Assessment + Evidence Matrix
                                                        |
                                                        v
                                      +-----------------------------------+
                                      |      Evidence Aggregator &        |
                                      |     LLM Response Synthesizer      |
                                      |  (Generates natural-language response|
                                      |   strictly bound to retrieved data)|
                                      +-----------------+-----------------+
                                                        |
                                                        v
                                      +-----------------------------------+
                                      |       Structured Output JSON      |
                                      | - Answer (Localized)              |
                                      | - Risk Card (Level, Factors)      |
                                      | - Evidence List (Provenance)      |
                                      | - GeoJSON Layers (Map Rendering)  |
                                      +-----------------------------------+
```

---

### 4. Component Deep Dive

#### 4.1. Orchestrator / Planner
- **Input**: Natural language text, conversation history (for multi-turn context), client metadata (selected location, language preference).
- **Execution**:
  1. Detects language (ISO 639-1 code: `en`, `mr`, `hi`).
  2. Extracts entities: Target location name, coordinates (resolved via local gazetteer), target date (e.g., "tomorrow"), target time (e.g., "06:00").
  3. Classifies Intent:
     - `MARINE_SAFETY`: Requires Weather + Ocean + Marine Advisory + Geospatial check.
     - `PFZ_DISCOVERY`: Requires Marine/PFZ Agent + Geospatial Engine (nearest neighbor).
     - `OCEAN_CONDITIONS`: Requires Ocean Agent + Weather Agent.
     - `GENERAL_MARINE_QUERY`: Dispatches to relevant agents.
  4. Dispatches agents concurrently via `asyncio.gather`.

#### 4.2. Specialized Agents
Each agent is an isolated Python class inheriting from `BaseAgent`, enforcing strict Pydantic I/O contracts:
- **WeatherAgent**: Fetches wind speed ($km/h$ or $knots$), gusts, wind direction (degrees and cardinal), precipitation probability, and IMD cyclone/squall advisories.
- **OceanAgent**: Fetches significant wave height ($m$), swell height, wave period ($s$), sea surface temperature ($^\circ C$), and INCOIS Ocean State Forecast alerts.
- **PFZAgent**: Retrieves INCOIS Potential Fishing Zone polygons and advisories, including depth contour, bearing, distance from landing centres, and oceanographic indicators (Chlorophyll-a, SST gradient).
- **GeospatialEngine**: Executes deterministic GIS operations:
  - Nearest PFZ calculation from port/vessel coordinate.
  - Point-in-polygon containment against Marine Protected Areas (e.g., Malvan Marine Sanctuary) and naval restricted zones.
  - Safe distance calculation from coastline.

#### 4.3. Deterministic Risk & Decision Engine
A standalone, testable module that enforces maritime advisory standards (e.g., IMD / INCOIS fishing safety guidelines):
- **Safety Categories**: `SAFE` (Green), `CAUTION` (Yellow), `UNSAFE` (Red), `UNKNOWN` (Insufficient Data).
- **Evaluation Criteria**:
  - *Wave Height*: $< 1.8m$ (Safe), $1.8m - 2.5m$ (Caution), $> 2.5m$ (Unsafe).
  - *Wind Speed*: $< 30 km/h$ (Safe), $30 - 45 km/h$ (Caution), $> 45 km/h$ (Unsafe).
  - *Advisories*: Active squally weather or gale warnings immediately elevate risk to `UNSAFE`.
  - *Geofencing*: Presence inside restricted areas generates explicit boundary violations.
- **Output**: Deterministic risk level, list of contributing factors, safety recommendations, and references to supporting evidence IDs.

#### 4.4. LLM Response Synthesizer
- Receives: User query, structured agent observations, risk assessment, and evidence records.
- System prompt strictly instructs the LLM:
  > *"You are the ORCA Marine Assistant. You must formulate your response using ONLY the provided structured marine observations and risk assessment. Never cite any metric or value not present in the evidence list. Address the user in their preferred language."*

---

### 5. Multi-Turn Conversational Memory
The system maintains session context:
- If a user asks *"Is fishing safe near Ratnagiri tomorrow?"*, the context stores `{location: "Ratnagiri", date: "tomorrow", activity: "fishing"}`.
- If the user follows up with *"What about 9 AM instead?"*, the orchestrator merges the context: `{location: "Ratnagiri", date: "tomorrow", time: "09:00", activity: "fishing"}` and re-evaluates the temporal window without re-asking basic parameters.

---

### 6. Geospatial Visualization Layer (MapLibre GL)
The frontend map dynamically displays:
- Base maritime tile layer (OpenStreetMap / Carto Positron / Bathymetry).
- Target location marker with interactive popup showing real-time oceanic metrics.
- Active INCOIS PFZ polygons styled with fish density gradients.
- Red polygon overlays for restricted marine corridors and protected marine zones.
- Vector bearing line from selected landing centre (e.g., Mirya Bandar) to the nearest PFZ centroid with nautical distance annotations.
