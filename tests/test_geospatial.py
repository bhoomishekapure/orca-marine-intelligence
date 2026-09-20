import pytest
from backend.models.schemas import LocationQuery
from agents.geospatial_agent import GeospatialService, haversine_distance, calculate_bearing

def test_haversine_and_bearing():
    # Ratnagiri harbour (17.0019, 73.2842) to offshore point (16.895, 73.072)
    dist = haversine_distance(17.0019, 73.2842, 16.895, 73.072)
    assert 20.0 < dist < 30.0  # Approx 25 km
    
    bearing, cardinal = calculate_bearing(17.0019, 73.2842, 16.895, 73.072)
    assert 230 <= bearing <= 255
    assert cardinal in ["SW", "WSW"]

@pytest.mark.asyncio
async def test_geospatial_service_ratnagiri():
    geo_svc = GeospatialService()
    loc = LocationQuery(name="Mirya Bandar, Ratnagiri", latitude=17.0251, longitude=73.2755)
    
    res = await geo_svc.run(location=loc)
    assert res.status == "success"
    assert res.agent == "geospatial"
    
    # Check nearest PFZ found
    nearest = res.data.get("nearest_pfz")
    assert nearest is not None
    assert nearest["id"] == "PFZ-MH-RTG-01"
    assert nearest["distance_km"] > 0
    assert nearest["direction"] == "WSW" or "SW" in nearest["direction"]
    
    # Check not inside restricted zone
    assert res.data["is_inside_restricted_zone"] is False
    assert res.data["nearest_restricted_zone"] is not None

@pytest.mark.asyncio
async def test_geospatial_service_inside_restricted():
    geo_svc = GeospatialService()
    # Malvan Marine Sanctuary point (inside polygon: 73.44 - 73.53 lon, 16.03 - 16.12 lat)
    loc = LocationQuery(name="Inside Malvan Sanctuary", latitude=16.06, longitude=73.48)
    
    res = await geo_svc.run(location=loc)
    assert res.data["is_inside_restricted_zone"] is True
    assert res.data["active_violation"]["zone_id"] == "MPA-MH-MALVAN-01"
