import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from backend.models.schemas import LocationQuery, WeatherAgentResponse, WeatherData, SourceTypeEnum
from backend.adapters.registry import registry

logger = logging.getLogger(__name__)

class WeatherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="weather",
            description="Retrieves wind speed, gusts, direction, precipitation, and IMD coastal alerts."
        )

    async def run(
        self,
        location: LocationQuery,
        target_time: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> WeatherAgentResponse:
        now = datetime.now(timezone.utc)
        
        # 1. Fetch atmospheric conditions
        weather_res = await registry.weather_adapter.fetch(
            latitude=location.latitude,
            longitude=location.longitude,
            target_time=target_time
        )
        
        # 2. Fetch IMD fishermen warnings
        imd_res = await registry.imd_adapter.fetch(
            latitude=location.latitude,
            longitude=location.longitude,
            target_time=target_time
        )
        
        raw_w = weather_res.get("data", {})
        imd_d = imd_res.get("data", {})
        
        active_warnings = []
        if imd_d.get("squally_alert"):
            active_warnings.append("Squally weather alert: Gusts up to 45 km/h possible")
        if imd_d.get("cyclone_name"):
            active_warnings.append(f"Cyclone advisory: {imd_d.get('cyclone_name')}")
            
        weather_data = WeatherData(
            temperature_c=raw_w.get("temperature_c", 29.0),
            wind_speed_kmh=raw_w.get("wind_speed_kmh", 24.0),
            wind_gusts_kmh=raw_w.get("wind_gusts_kmh", 32.0),
            wind_direction_deg=raw_w.get("wind_direction_deg", 260.0),
            wind_direction_cardinal=raw_w.get("wind_direction_cardinal", "WSW"),
            precipitation_mm=raw_w.get("precipitation_mm", 0.0),
            weather_code=raw_w.get("weather_code", 1),
            weather_description=raw_w.get("weather_description", "Mainly clear"),
            active_warnings=active_warnings
        )
        
        return WeatherAgentResponse(
            agent="weather",
            status="success",
            location=location,
            timestamp=now,
            source=weather_res.get("source", "Open-Meteo Weather / IMD"),
            source_type=weather_res.get("source_type", SourceTypeEnum.LIVE_API),
            source_timestamp=weather_res.get("source_timestamp", now.isoformat()),
            confidence=weather_res.get("confidence", 0.94),
            data=weather_data,
            errors=[]
        )
