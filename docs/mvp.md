# ORCA MVP Scope & Specification (SIH 2026)

## 1. Project Identity & Objective
**ORCA** is an agentic marine intelligence and decision-support platform designed to empower coastal fishing communities, maritime administrators, and port authorities with explainable, multi-source marine reasoning.

The objective of this MVP is to deliver a **technically credible, demonstrable, fully working prototype** for Smart India Hackathon 2026 that proves:
1. Multi-agent collaborative orchestration.
2. Multi-source marine data integration (ocean state, weather, satellite PFZ, GIS boundaries).
3. Deterministic spatial reasoning (nearest PFZ, geofencing, distance, bearing).
4. Deterministic temporal reasoning (hourly forecasting, multi-turn time updates).
5. Evidence-backed, explainable risk assessments.
6. Interactive geospatial visualization using MapLibre GL.
7. Multi-turn conversational memory.
8. Multilingual natural language interaction (English, Marathi, Hindi).

---

## 2. Geographic Focus: Coastal Maharashtra & Ratnagiri
To ensure maximum precision and authentic domain data, the prototype concentrates on **Coastal Maharashtra**, with high-resolution modeling of the **Ratnagiri maritime district**:

- **Target Latitude / Longitude**: $16.99^\circ N, 73.30^\circ E$
- **Key Landing Centres / Ports**:
  - Mirkarwada Major Fishing Harbour (Ratnagiri)
  - Mirya Bandar / Bhagwati Port (Ratnagiri)
  - Bhatye Beach & Estuary
  - Jaigad Commercial Port (40 km North)
  - Malvan / Devgad Fishing Centres (Sindhudurg, South)
- **Marine Protected Area (Geofenced)**: Malvan Marine Sanctuary ($16.05^\circ N, 73.46^\circ E$ to $16.12^\circ N, 73.53^\circ E$)
- **Navigation Channel**: Jaigad deep-water channel approach

---

## 3. Five Mandatory Demonstration Scenarios

### Scenario 1: Marine Safety Query
- **Query**: *"Is it safe to go fishing tomorrow at 6 AM near Ratnagiri?"*
- **Execution Flow**:
  1. Orchestrator extracts intent `MARINE_SAFETY`, location `Ratnagiri`, date `tomorrow`, time `06:00`.
  2. Weather Agent fetches 06:00 forecast (wind speed, precipitation, squall warnings).
  3. Ocean Agent fetches 06:00 ocean conditions (wave height, wave period, swell).
  4. Marine Agent checks active IMD/INCOIS advisory bulletins.
  5. Geospatial Service checks if coordinate intersects restricted zones.
  6. Deterministic Risk Engine evaluates values against safety rules.
  7. Final localized response generated with safety card, contributing factors, evidence citations, and map layers.

### Scenario 2: Potential Fishing Zone (PFZ) Discovery
- **Query**: *"Where is the nearest Potential Fishing Zone?"*
- **Execution Flow**:
  1. Orchestrator identifies intent `PFZ_DISCOVERY` and user's default/selected port (Mirya Bandar, Ratnagiri).
  2. Marine/PFZ Agent retrieves valid PFZ polygons derived from satellite SST and chlorophyll gradients.
  3. Geospatial Engine calculates geodesic distance, navigation bearing, and estimated travel time from port.
  4. Map renders the bearing vector and PFZ polygons with depth bathymetry.
  5. Response explains distance ($22.5\ km$), bearing ($240^\circ\ WSW$), depth ($35-50\ m$), and SST ($28.4^\circ C$).

### Scenario 3: Marine Weather & Sea Conditions
- **Query**: *"What are the sea conditions near Ratnagiri tomorrow morning?"*
- **Execution Flow**:
  1. Orchestrator identifies intent `OCEAN_CONDITIONS`, location `Ratnagiri`, time window `morning (06:00 - 10:00)`.
  2. Ocean and Weather agents retrieve time-series metrics.
  3. Structured response displays wind speed, wave height, wave period, and water temperature.
  4. Map highlights sea surface conditions.

### Scenario 4: Conversational Follow-Up & Context Retention
- **Prior Query**: *"Is it safe to go fishing tomorrow at 6 AM near Ratnagiri?"*
- **Follow-Up Query**: *"What about 9 AM instead?"*
- **Execution Flow**:
  1. Orchestrator recalls conversation context: `location = Ratnagiri`, `activity = fishing`, `date = tomorrow`.
  2. Updates `time = 09:00`.
  3. Re-runs temporal filtering and risk engine for the new timestamp without requiring the user to repeat the location or activity.
  4. Returns updated comparison explaining any changes in wave height or wind between 6 AM and 9 AM.

### Scenario 5: Native Multilingual Query (Marathi)
- **Query**: *"उद्या सकाळी रत्नागिरीजवळ मासेमारीसाठी समुद्रात जाणे सुरक्षित आहे का?"*
- **Execution Flow**:
  1. Orchestrator detects language as Marathi (`mr`).
  2. Normalizes query to internal intent `MARINE_SAFETY`, location `Ratnagiri`, target `tomorrow 06:00`.
  3. Standard agents retrieve identical deterministic data.
  4. Risk engine computes identical deterministic risk score.
  5. LLM generator formats the final response in fluent Marathi while preserving exact English metrics and data tables.

---

## 4. In-Scope vs. Out-of-Scope

| Capability | In Scope (MVP) | Out of Scope (Future Work) |
| :--- | :--- | :--- |
| **Geographic Scope** | Coastal Maharashtra (Ratnagiri focused) | Entire Indian EEZ & International Waters |
| **Language Support** | English, Marathi, Hindi | All 14 coastal Indian languages |
| **Data Ingestion** | Live Open-Meteo REST API + INCOIS/IMD verified cached bulletins | Automated real-time scraping of all state fisheries PDFs |
| **Vessel Profiling** | Standard artisanal / mechanized motorized fishing craft (< 15m) | Specialized commercial cargo ships & deep-sea trawlers |
| **Geospatial Engine** | Point-in-polygon, nearest-neighbor, bearing, distance, bounding boxes | Hydrodynamic storm surge simulation modelling |
| **Deployment** | Local production-style app (Docker / uvicorn / Vite dev server) | Multi-region Kubernetes cluster deployment |

---

## 5. Success Criteria
1. **Response Time**: Total query execution time $< 2.5\ seconds$.
2. **Accuracy**: 0% hallucinated marine metrics; 100% adherence to retrieved data values.
3. **Deterministic Safety**: Identical input parameters always produce the exact same risk level (`SAFE`, `CAUTION`, or `UNSAFE`).
4. **UI Quality**: Fluid MapLibre GL map with interactive vector markers, step-by-step agent execution indicators, and clear evidence inspection tabs.
5. **Offline/Demo Resilience**: 100% operational in Demo Mode even if external Internet connectivity is cut.
