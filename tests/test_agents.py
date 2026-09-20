import pytest
from datetime import datetime
from backend.models.schemas import LocationQuery
from agents.weather_agent import WeatherAgent
from agents.ocean_agent import OceanAgent
from agents.marine_pfz_agent import MarinePFZAgent

@pytest.mark.asyncio
async def test_weather_agent():
    agent = WeatherAgent()
    loc = LocationQuery(name="Ratnagiri", latitude=16.99, longitude=73.30)
    res = await agent.run(location=loc, target_time=datetime(2026, 9, 21, 6, 0))
    
    assert res.agent == "weather"
    assert res.status == "success"
    assert res.data.wind_speed_kmh >= 0
    assert res.data.wind_direction_cardinal in [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ]
    assert res.confidence >= 0.8

@pytest.mark.asyncio
async def test_ocean_agent():
    agent = OceanAgent()
    loc = LocationQuery(name="Ratnagiri", latitude=16.99, longitude=73.30)
    res = await agent.run(location=loc, target_time=datetime(2026, 9, 21, 6, 0))
    
    assert res.agent == "ocean"
    assert res.status == "success"
    assert res.data.significant_wave_height_m > 0
    assert res.data.wave_period_s > 0
    assert res.data.sea_surface_temperature_c > 20.0

@pytest.mark.asyncio
async def test_pfz_agent():
    agent = MarinePFZAgent()
    loc = LocationQuery(name="Mirya Bandar, Ratnagiri", latitude=17.025, longitude=73.275)
    res = await agent.run(location=loc)
    
    assert res.agent == "marine_pfz"
    assert res.status == "success"
    assert res.data["active_zones_count"] >= 1
    assert "primary_zone" in res.data
    assert res.data["primary_zone"]["distance_km"] > 0
