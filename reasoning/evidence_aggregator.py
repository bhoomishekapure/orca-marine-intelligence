from typing import List, Dict, Any
from datetime import datetime, timezone
from backend.models.schemas import EvidenceRecord

class EvidenceAggregator:
    @staticmethod
    def compile_evidence(
        weather_res: Dict[str, Any],
        ocean_res: Dict[str, Any],
        pfz_res: Dict[str, Any],
        geo_res: Dict[str, Any]
    ) -> List[EvidenceRecord]:
        now_str = datetime.now(timezone.utc).isoformat()
        records: List[EvidenceRecord] = []
        counter = 1

        # 1. Ocean Evidence
        o_data = ocean_res.get("data", {})
        loc_str = f"{ocean_res.get('location', {}).get('name', 'Ratnagiri')} ({ocean_res.get('location', {}).get('latitude')}, {ocean_res.get('location', {}).get('longitude')})"
        
        records.append(EvidenceRecord(
            evidence_id=f"EVID-{counter:03d}",
            agent="ocean",
            parameter="Significant Wave Height",
            value=o_data.get("significant_wave_height_m"),
            unit="meters",
            source=ocean_res.get("source", "Open-Meteo Marine / INCOIS OSF"),
            source_type=str(ocean_res.get("source_type", "LIVE_API")),
            source_timestamp=str(ocean_res.get("source_timestamp")),
            retrieved_at=now_str,
            location=loc_str
        ))
        counter += 1

        records.append(EvidenceRecord(
            evidence_id=f"EVID-{counter:03d}",
            agent="ocean",
            parameter="Wave Period",
            value=o_data.get("wave_period_s"),
            unit="seconds",
            source=ocean_res.get("source", "Open-Meteo Marine / INCOIS OSF"),
            source_type=str(ocean_res.get("source_type", "LIVE_API")),
            source_timestamp=str(ocean_res.get("source_timestamp")),
            retrieved_at=now_str,
            location=loc_str
        ))
        counter += 1

        records.append(EvidenceRecord(
            evidence_id=f"EVID-{counter:03d}",
            agent="ocean",
            parameter="Sea Surface Temperature",
            value=o_data.get("sea_surface_temperature_c"),
            unit="°C",
            source=ocean_res.get("source", "Open-Meteo Marine / INCOIS OSF"),
            source_type=str(ocean_res.get("source_type", "LIVE_API")),
            source_timestamp=str(ocean_res.get("source_timestamp")),
            retrieved_at=now_str,
            location=loc_str
        ))
        counter += 1

        # 2. Weather Evidence
        w_data = weather_res.get("data", {})
        records.append(EvidenceRecord(
            evidence_id=f"EVID-{counter:03d}",
            agent="weather",
            parameter="Wind Speed & Direction",
            value=f"{w_data.get('wind_speed_kmh')} km/h ({w_data.get('wind_direction_cardinal')})",
            unit="km/h",
            source=weather_res.get("source", "Open-Meteo Weather / IMD"),
            source_type=str(weather_res.get("source_type", "LIVE_API")),
            source_timestamp=str(weather_res.get("source_timestamp")),
            retrieved_at=now_str,
            location=loc_str
        ))
        counter += 1

        # 3. PFZ Evidence
        p_data = pfz_res.get("data", {}).get("primary_zone", {})
        if p_data:
            records.append(EvidenceRecord(
                evidence_id=f"EVID-{counter:03d}",
                agent="marine_pfz",
                parameter="Potential Fishing Zone Bearing & Distance",
                value=f"{p_data.get('distance_km')} km at {p_data.get('bearing_deg')}° {p_data.get('direction')}",
                unit="km / degrees",
                source=pfz_res.get("source", "INCOIS PFZ Multi-lingual Advisory"),
                source_type=str(pfz_res.get("source_type", "VERIFIED_CACHE")),
                source_timestamp=str(pfz_res.get("source_timestamp")),
                retrieved_at=now_str,
                location=p_data.get("landing_centre", loc_str)
            ))
            counter += 1

        # 4. Geospatial Geofence Evidence
        g_data = geo_res.get("data", {})
        rz = g_data.get("nearest_restricted_zone")
        if rz:
            records.append(EvidenceRecord(
                evidence_id=f"EVID-{counter:03d}",
                agent="geospatial",
                parameter="Sanctuary Distance & Geofence Status",
                value=f"{rz.get('distance_km')} km from {rz.get('name')}",
                unit="km",
                source=geo_res.get("source", "PostGIS / Shapely Spatial Engine"),
                source_type=str(geo_res.get("source_type", "DETERMINISTIC_GIS")),
                source_timestamp=now_str,
                retrieved_at=now_str,
                location=loc_str
            ))

        return records
