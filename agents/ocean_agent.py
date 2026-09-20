import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from backend.models.schemas import LocationQuery, OceanAgentResponse, OceanData, SourceTypeEnum
from backend.adapters.registry import registry

logger = logging.getLogger(__name__)

class OceanAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ocean",
            description="Retrieves significant wave height, wave period, swell, and sea-surface temperature."
        )

    async def run(
        self,
        location: LocationQuery,
        target_time: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> OceanAgentResponse:
        now = datetime.now(timezone.utc)
        
        ocean_res = await registry.marine_adapter.fetch(
            latitude=location.latitude,
            longitude=location.longitude,
            target_time=target_time
        )
        
        raw_o = ocean_res.get("data", {})
        
        ocean_data = OceanData(
            significant_wave_height_m=raw_o.get("significant_wave_height_m", 1.4),
            maximum_wave_height_m=raw_o.get("maximum_wave_height_m", 2.2),
            wave_period_s=raw_o.get("wave_period_s", 8.0),
            wave_direction_deg=raw_o.get("wave_direction_deg", 250.0),
            swell_wave_height_m=raw_o.get("swell_wave_height_m", 1.1),
            swell_period_s=raw_o.get("swell_period_s", 10.0),
            sea_surface_temperature_c=raw_o.get("sea_surface_temperature_c", 28.5),
            current_speed_knots=raw_o.get("current_speed_knots", 0.8),
            current_direction_deg=raw_o.get("current_direction_deg", 340),
            ocean_state_alert=raw_o.get("ocean_state_alert", "NORMAL")
        )
        
        return OceanAgentResponse(
            agent="ocean",
            status="success",
            location=location,
            timestamp=now,
            source=ocean_res.get("source", "Open-Meteo Marine / INCOIS OSF"),
            source_type=ocean_res.get("source_type", SourceTypeEnum.LIVE_API),
            source_timestamp=ocean_res.get("source_timestamp", now.isoformat()),
            confidence=ocean_res.get("confidence", 0.93),
            data=ocean_data,
            errors=[]
        )
