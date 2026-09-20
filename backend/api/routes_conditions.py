from fastapi import APIRouter, Query
from datetime import datetime, timezone
from backend.models.schemas import LocationQuery
from agents.weather_agent import WeatherAgent
from agents.ocean_agent import OceanAgent

router = APIRouter(prefix="/api", tags=["Conditions Telemetry"])

weather_agent = WeatherAgent()
ocean_agent = OceanAgent()

@router.get("/marine-conditions")
async def get_conditions(
    name: str = Query("Ratnagiri", description="Location name"),
    lat: float = Query(16.99, description="Latitude"),
    lon: float = Query(73.30, description="Longitude")
):
    """Direct condition telemetry feed for dashboard instruments."""
    loc = LocationQuery(name=name, latitude=lat, longitude=lon)
    now = datetime.now(timezone.utc)
    
    w_res = await weather_agent.run(location=loc, target_time=now)
    o_res = await ocean_agent.run(location=loc, target_time=now)
    
    return {
        "location": loc.model_dump(),
        "timestamp": now.isoformat(),
        "weather": w_res.data.model_dump(),
        "ocean": o_res.data.model_dump(),
        "source_marine": o_res.source,
        "source_weather": w_res.source,
        "source_type": o_res.source_type.value
    }
