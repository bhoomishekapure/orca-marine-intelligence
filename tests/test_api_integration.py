import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app

@pytest.mark.asyncio
async def test_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/")
    assert res.status_code == 200
    # Verifies root endpoint serves ORCA frontend or API metadata
    assert "ORCA" in res.text

@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert len(data["providers"]) >= 4

@pytest.mark.asyncio
async def test_locations():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/locations")
    assert res.status_code == 200
    locations = res.json()
    assert len(locations) >= 4
    names = [l["location_name"] for l in locations]
    assert "Ratnagiri" in names

@pytest.mark.asyncio
async def test_map_layers():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/map/layers")
    assert res.status_code == 200
    layers = res.json()
    assert "landing_centres" in layers
    assert "pfz_polygons" in layers
    assert "restricted_zones" in layers
    assert len(layers["landing_centres"]["features"]) > 0

@pytest.mark.asyncio
async def test_marine_conditions_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/marine-conditions?name=Ratnagiri&lat=16.99&lon=73.30")
    assert res.status_code == 200
    data = res.json()
    assert "weather" in data
    assert "ocean" in data
    assert data["ocean"]["significant_wave_height_m"] > 0

@pytest.mark.asyncio
async def test_api_query_post():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "session_id": "test-session-api",
            "query": "Is it safe to go fishing tomorrow at 6 AM near Ratnagiri?"
        }
        res = await ac.post("/api/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "MARINE_SAFETY"
    assert data["risk_assessment"]["risk_level"] in ["SAFE", "CAUTION", "UNSAFE"]
    assert len(data["evidence"]) > 0
    assert len(data["agent_timeline"]) >= 4
