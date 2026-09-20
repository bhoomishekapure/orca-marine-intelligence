# ORCA — Marine Ecosystem Reasoning with Collaborative Agents
### Smart India Hackathon (SIH) 2026 — Working Prototype & System Documentation

[![CI Tests](https://img.shields.io/badge/pytest-20%20passed-emerald.svg)](https://pytest.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev)
[![MapLibre GL](https://img.shields.io/badge/MapLibre%20GL-WebGL-38bdf8.svg)](https://maplibre.org)
[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://python.org)

---

## 1. Project Overview & Problem Statement
Coastal fishermen, maritime operators, and harbour authorities in India face fragmented and high-latency marine data:
- **Ocean state forecasts** (wave heights, currents, swell) are published in isolated bulletins.
- **Atmospheric forecasts** (wind speed, direction, squall warnings) reside in separate portals.
- **Potential Fishing Zones (PFZ)** require interpreting technical bearing vectors and depth contours.
- **Marine Protected Areas (MPAs)** (e.g., Malvan Marine Sanctuary) lack real-time geofence alerting.

**ORCA** solves this by providing a unified, conversational, multi-agent intelligence platform. Users can query the system in natural language (English, Marathi, or Hindi), and ORCA autonomously:
1. Deconstructs the query into structured intents and spatio-temporal entities.
2. Coordinates specialized agents (**Weather**, **Ocean**, **Marine/PFZ**, and **Geospatial**).
3. Executes deterministic GIS calculations (geodesic distance, bearing, point-in-polygon).
4. Evaluates marine safety thresholds through a deterministic Risk Engine.
5. Returns an explainable, evidence-backed decision card alongside an interactive WebGL marine map.

---

## 2. Core Architecture & Division of Responsibilities

```
                                    +-----------------------------------+
                                    |         End User / Web UI         |
                                    |   React 18 + Vite + MapLibre GL   |
                                    +-----------------+-----------------+
                                                      |
                                     Natural Language Query (EN/MR/HI)
                                                      |
                                                      v
                                    +-----------------------------------+
                                    |       FastAPI API Gateway         |
                                    |      POST /api/query (Async)      |
                                    +-----------------+-----------------+
                                                      |
                                                      v
                                    +-----------------------------------+
                                    |    ORCA Planner / Orchestrator    |
                                    |  - Language & Intent Extraction   |
                                    |  - Temporal & Entity Resolution   |
                                    |  - Concurrent Execution DAG       |
                                    +-----------------+-----------------+
                                                      |
                   +------------------+---------------+-------------------+
                   |                  |               |                   |
                   v                  v               v                   v
           +---------------+  +---------------+  +----------+  +--------------------+
           | Weather Agent |  |  Ocean Agent  |  |PFZ Agent |  | Geospatial Service |
           +-------+-------+  +-------+-------+  +----+-----+  +----------+---------+
                   |                  |               |                   |
            (Wind, Rain, GFS)  (Waves, SST, OSF)  (PFZ, Chl)     (PostGIS / Shapely)
                   |                  |               |                   |
                   +------------------+---------------+-------------------+
                                                      |
                                      Normalized Agent Data Payloads
                                                      |
                                                      v
                                    +-----------------------------------+
                                    |    Deterministic Risk Engine      |
                                    |  - Wave & Wind safety rules       |
                                    |  - Sanctuary geofence alert       |
                                    |  - Marine warning triggers        |
                                    +-----------------+-----------------+
                                                      |
                                       Evaluated Risk + Evidence Trail
                                                      |
                                                      v
                                    +-----------------------------------+
                                    |     LLM Response Synthesizer      |
                                    |  - Strict evidence binding        |
                                    |  - Zero hallucination guarantee   |
                                    |  - Multilingual generation        |
                                    +-----------------+-----------------+
                                                      |
                                                      v
                                    +-----------------------------------+
                                    |    Output JSON to Frontend        |
                                    | - Natural-language Answer         |
                                    | - Decision Risk Card              |
                                    | - Real Agent Timeline (ms)        |
                                    | - Complete Evidence Provenance    |
                                    | - Dynamic GeoJSON Vector Layers   |
                                    +-----------------------------------+
```

### Strict Engineering Principles
- **No Hallucinated Marine Measurements**: The LLM is strictly prohibited from inventing numerical parameters. All numbers originate from verified live APIs, authentic official bulletins, or deterministic GIS algorithms.
- **Deterministic Math & GIS**: Great-circle distances, compass bearings, point-in-polygon containment, and safety risk scoring are handled exclusively by compiled Python/GIS logic.

---

## 3. Five Primary SIH Demonstration Flows

| Flow | Query | Key Orchestration & Reasoning |
| :--- | :--- | :--- |
| **1. Marine Safety** | *"Is it safe to go fishing tomorrow at 6 AM near Ratnagiri?"* | Resolves 06:00 forecast; queries Ocean & Weather agents; evaluates wave height ($1.4\text{ m} < 1.8\text{ m}$) & wind ($24.5\text{ km/h} < 30\text{ km/h}$); returns **SAFE** risk card. |
| **2. Nearest PFZ** | *"Where is the nearest Potential Fishing Zone?"* | Identifies primary landing centre (Mirya Bandar); calculates geodesic distance ($22.5\text{ km}$) and compass bearing ($240^\circ\text{ WSW}$); draws navigation vector on MapLibre map. |
| **3. Sea Conditions** | *"What are the sea conditions near Ratnagiri tomorrow morning?"* | Fetches wave height, period ($8.0\text{ s}$), swell ($1.1\text{ m}$), and SST ($28.5^\circ\text{C}$); renders tabular condition gauges. |
| **4. Follow-Up** | *"What about 9 AM instead?"* | Multi-turn memory retains `location = Ratnagiri` and `activity = fishing`; updates time to `09:00`; re-evaluates risk without re-prompting user. |
| **5. Multilingual (मराठी)** | *"उद्या सकाळी रत्नागिरीजवळ मासेमारीसाठी समुद्रात जाणे सुरक्षित आहे का?"* | Detects Marathi; executes identical deterministic pipeline; synthesizes fluent Marathi response with English numeric metrics. |

---

## 4. Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, MapLibre GL JS.
- **Backend**: Python 3.14, FastAPI, Pydantic v2, Uvicorn.
- **Spatial Engine**: Shapely 2.1, Haversine/Spherical Geodesics, PostGIS / SQLite dual schema.
- **Data Adapters**: Open-Meteo Marine & Atmospheric API (Live), INCOIS PFZ Advisories (Official Bulletin Adapter), IMD ACWC Mumbai Coastal Bulletins.
- **AI & NLP**: Provider abstraction supporting Google Gemini, OpenAI, and a built-in deterministic local NLP provider for guaranteed offline demonstration.

---

## 5. Quick Start Instructions

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Node.js 18+ (Tested on Node.js v24.19)

### 1. Backend Setup
```powershell
# In orca-marine-intelligence root directory:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Seed the Maharashtra coastal GIS database:
python -m backend.database.seed_data

# Run the backend API server on port 8000:
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Setup (Development Mode)
```powershell
# In a separate terminal:
cd frontend
$env:PATH = "C:\Program Files\nodejs;" + $env:PATH
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser.

> [!TIP]
> **Unified Single-Port Mode**: The backend automatically serves the built frontend production bundle directly from `http://127.0.0.1:8000`.

### 3. Run Automated Tests
```powershell
.\venv\Scripts\python.exe -m pytest tests/ -v
```
All 20 tests verify data adapters, agents, geospatial calculations, risk engine thresholds, conversational context, and HTTP endpoints.

---

## 6. SIH 6-Slide Presentation Guide

- **Slide 1: ORCA Identity**: Problem statement, vision, and team overview.
- **Slide 2: The Maritime Challenge**: Fragmented ocean bulletins vs. unified conversational agent solution.
- **Slide 3: Collaborative Agent Architecture**: Orchestrator DAG, specialized agents, and separation of LLM from deterministic GIS.
- **Slide 4: Feasibility & Resilience**: Live API integration paired with verified cache failover; zero-hallucination compliance.
- **Slide 5: Interactive Decision Interface**: Screenshot of MapLibre GL map, Risk Assessment card, and Evidence Provenance table.
- **Slide 6: Impact, Multilingual Reach & Future Scope**: Artisanal fishing safety, Marathi/Hindi localization, and nationwide expansion roadmap.