import pytest
from backend.models.schemas import QueryRequest
from agents.orchestrator import OrcaOrchestrator

@pytest.mark.asyncio
async def test_flow_1_marine_safety():
    orch = OrcaOrchestrator()
    req = QueryRequest(
        session_id="test-session-1",
        query="Is it safe to go fishing tomorrow at 6 AM near Ratnagiri?"
    )
    res = await orch.process_query(req)
    
    assert res.intent == "MARINE_SAFETY"
    assert "Ratnagiri" in res.answer or "safe" in res.answer.lower()
    assert res.risk_assessment is not None
    assert len(res.agent_timeline) >= 4
    assert len(res.evidence) >= 4
    assert res.map_features["type"] == "FeatureCollection"
    assert len(res.map_features["features"]) >= 1

@pytest.mark.asyncio
async def test_flow_2_nearest_pfz():
    orch = OrcaOrchestrator()
    req = QueryRequest(
        session_id="test-session-2",
        query="Where is the nearest Potential Fishing Zone?"
    )
    res = await orch.process_query(req)
    
    assert res.intent == "PFZ_DISCOVERY"
    assert "PFZ" in res.answer or "km" in res.answer
    assert "bearing" in res.answer.lower() or "°" in res.answer
    # Check navigation vector feature is in map
    has_nav_vector = any(
        f.get("properties", {}).get("feature_type") == "navigation_vector"
        for f in res.map_features["features"]
    )
    assert has_nav_vector is True

@pytest.mark.asyncio
async def test_flow_4_conversational_follow_up():
    orch = OrcaOrchestrator()
    session_id = "test-session-multi-turn"
    
    # Turn 1: Establish context
    req1 = QueryRequest(
        session_id=session_id,
        query="Is it safe to go fishing tomorrow at 6 AM near Ratnagiri?"
    )
    res1 = await orch.process_query(req1)
    assert res1.intent == "MARINE_SAFETY"
    
    # Turn 2: Follow-up with only time change
    req2 = QueryRequest(
        session_id=session_id,
        query="What about 9 AM instead?"
    )
    res2 = await orch.process_query(req2)
    
    # Verify context retained
    session_context = orch.sessions[session_id]["context"]
    assert session_context["location_name"] == "Ratnagiri"
    assert session_context["time_expression"] == "09:00"
    assert res2.intent == "MARINE_SAFETY"
    assert res2.risk_assessment is not None

@pytest.mark.asyncio
async def test_flow_5_marathi_query():
    orch = OrcaOrchestrator()
    req = QueryRequest(
        session_id="test-session-marathi",
        query="उद्या सकाळी रत्नागिरीजवळ मासेमारीसाठी समुद्रात जाणे सुरक्षित आहे का?"
    )
    res = await orch.process_query(req)
    
    assert res.query_language == "mr"
    assert res.intent == "MARINE_SAFETY"
    assert "रत्नागिरी" in res.answer or "सुरक्षित" in res.answer
