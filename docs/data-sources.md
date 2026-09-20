# ORCA Data Sources & Feasibility Specification

## 1. Overview & Strict Engineering Guidelines
A core principle of the ORCA architecture is **Zero Data Fabrication**. Every marine parameter presented to the user must originate from an authentic observational or forecast source, or from an explicitly flagged, verified cached dataset. 

This document details the exact access mechanisms, endpoints, data schemas, update cadences, and fallback strategies for all data providers.

---

## 2. Primary Authoritative Data Sources

### 2.1. INCOIS (Indian National Centre for Ocean Information Services)
*Ministry of Earth Sciences, Govt. of India*

| Property | Details |
| :--- | :--- |
| **Products** | Ocean State Forecast (OSF), Potential Fishing Zone (PFZ) Advisories, High Wave Alerts |
| **Coverage** | Arabian Sea, Bay of Bengal, Coastal Maharashtra (Ratnagiri, Sindhudurg, Raigad, Mumbai) |
| **Official Portal** | [https://incois.gov.in](https://incois.gov.in) |
| **ERDDAP Server** | `https://erddap.incois.gov.in/erddap/` |
| **WebGIS Services** | OGC WMS/WFS for PFZ polygons and sea surface temperature contours |
| **Update Cadence** | OSF updated daily (6-hourly forecast steps); PFZ advisories updated 3 times/week (Tuesdays, Thursdays, Saturdays, excluding monsoon fishing ban period June 1 - July 31) |
| **Access Feasibility** | ERDDAP and WebGIS endpoints are publicly browsable. However, institutional REST APIs for automated programmatic downloads often experience intermittent institutional firewall throttling or session timeouts during high-traffic alerts. |
| **ORCA Adapter Strategy** | 1. Direct adapter queries INCOIS ERDDAP REST endpoint when reachable.<br>2. Verified sample adapter contains official INCOIS PFZ bulletins and OSF time series for Ratnagiri (Mirya Bandar / Mirkarwada Port) collected under standard non-monsoon fishing conditions. |

#### Real INCOIS PFZ Advisory Format (Maharashtra Sector)
INCOIS PFZ advisories provide actionable fishing vectors relative to recognized fish landing centres:
```json
{
  "landing_centre": "Mirya Bandar, Ratnagiri",
  "latitude": 17.01,
  "longitude": 73.28,
  "bearing_degrees": 240,
  "direction": "WSW",
  "distance_km": 22.5,
  "distance_nm": 12.15,
  "depth_range_m": [35, 50],
  "sst_celsius": 28.4,
  "chlorophyll_mg_m3": 0.85,
  "valid_from": "2026-09-20T06:00:00Z",
  "valid_to": "2026-09-22T18:00:00Z"
}
```

---

### 2.2. IMD (India Meteorological Department)
*Ministry of Earth Sciences, Govt. of India*

| Property | Details |
| :--- | :--- |
| **Products** | Coastal Weather Forecasts, Fishermen Warnings, Cyclone Alerts, Squall Bulletins |
| **Coverage** | Maharashtra-Goa Coastal Region, Sub-division: Konkan & Goa |
| **Official Portal** | [https://mausam.imd.gov.in](https://mausam.imd.gov.in) |
| **API Management** | `https://api.imd.gov.in` (Requires registered institutional developer API key) |
| **Dissemination Format**| Daily marine coastal bulletins published in PDF and text formats at 09:00 and 17:30 IST |
| **Access Feasibility** | Automated real-time programmatic ingestion directly from `api.imd.gov.in` requires formal API clearance. Web scraping HTML bulletins is fragile. |
| **ORCA Adapter Strategy** | 1. Official IMD bulletin adapter parses structured coastal warning levels (Green / Yellow / Orange / Red) and squally weather advisories.<br>2. Verified baseline cache populated with active/historical IMD Konkan coastal bulletins. |

---

### 2.3. Live Open-Meteo Marine & Atmosphere API (Authoritative Numerical Models)
*Open-Meteo GmbH / Copernicus Marine Service / ECMWF / DWD / NOAA GFS*

| Property | Details |
| :--- | :--- |
| **Products** | Significant wave height ($m$), wave direction ($^\circ$), wave period ($s$), swell wave height, wind speed ($km/h$), wind gusts, precipitation ($mm$), temperature ($^\circ C$) |
| **Coverage** | Global oceanic grid at 0.1° resolution (~11 km), fully covering Ratnagiri coastal waters ($16.99^\circ N, 73.30^\circ E$) |
| **Marine Endpoint** | `https://marine-api.open-meteo.com/v1/marine?latitude=16.99&longitude=73.30&hourly=wave_height,wave_direction,wave_period,swell_wave_height` |
| **Weather Endpoint**| `https://api.open-meteo.com/v1/forecast?latitude=16.99&longitude=73.30&hourly=temperature_2m,precipitation,wind_speed_10m,wind_direction_10m,weather_code` |
| **Authentication** | Free for non-commercial open data access; no API key required; 10,000 daily requests |
| **Latency & SLA** | Low latency (< 250 ms), 99.9% uptime, reliable JSON REST responses |
| **ORCA Adapter Strategy** | Utilized as the **primary live numerical weather and wave engine** for real-time temporal forecasts, cross-referenced with INCOIS and IMD safety thresholds. |

---

### 2.4. MOSDAC / ISRO (Meteorological and Oceanographic Satellite Data Archival Centre)
*Space Applications Centre (SAC), ISRO*

| Property | Details |
| :--- | :--- |
| **Products** | Oceansat-3 Ocean Colour Monitor (OCM-3), INSAT-3D/3DR Sea Surface Temperature (SST) |
| **Official Portal** | [https://mosdac.gov.in](https://mosdac.gov.in) |
| **Access Feasibility** | Large HDF5 / NetCDF raster files requiring OpenDAP or sftp client access; unsuited for sub-second REST queries during conversational chat. |
| **ORCA Adapter Strategy** | Sample metadata adapter representing satellite overpass records, thermal SST anomalies, and optical chlorophyll gradients mapped to Ratnagiri coordinates. |

---

### 2.5. Geospatial & Administrative Datasets (GIS)
*Survey of India / OpenStreetMap / Wildlife Institute of India / Maharashtra Maritime Board*

| Dataset | Format | Coverage / Purpose |
| :--- | :--- | :--- |
| **Maharashtra Coastline & Landing Centres** | GeoJSON / PostGIS `POINT`, `POLYGON` | Ratnagiri (Mirkarwada, Bhagwati, Bhatye), Jaigad, Devgad, Malvan, Alibaug |
| **Marine Protected Areas (MPAs)** | GeoJSON / PostGIS `POLYGON` | Malvan Marine Sanctuary (Sindhudurg) — strictly restricted from mechanized fishing |
| **Navigational Hazards & Fairways** | GeoJSON / PostGIS `LINESTRING`, `POLYGON`| Jaigad Port navigation channel, offshore shipping corridor (12 nautical mile boundary) |

---

## 3. Data Integrity & Provenance Schema
Every single marine record returned to the reasoning engine or client includes the following metadata:

```json
{
  "source_name": "Open-Meteo Marine / Copernicus Marine",
  "source_type": "LIVE_API", 
  "source_timestamp": "2026-09-20T06:00:00Z",
  "retrieved_at": "2026-09-20T06:36:41Z",
  "is_cached": false,
  "confidence_score": 0.95,
  "quality_flag": "PASSED_RANGE_VALIDATION",
  "location": {
    "name": "Ratnagiri Offshore (12 km WSW)",
    "latitude": 16.985,
    "longitude": 73.204
  }
}
```

If an external network error occurs:
1. `source_type` becomes `"VERIFIED_CACHE"`.
2. `is_cached` becomes `true`.
3. The UI prominently displays a warning badge: **"Demo / Cached Data"** with the exact timestamp of the cached observation.
4. No synthetic or invented measurements are ever presented.
