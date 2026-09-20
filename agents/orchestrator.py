import time
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from backend.config import settings
from backend.models.schemas import (
    QueryRequest, QueryResponse, LocationQuery, AgentTimelineItem,
    RiskAssessment, EvidenceRecord, IntentEnum
)
from backend.llm.base_provider import LLMProvider
from backend.llm.mock_provider import MockRuleBasedProvider
from agents.weather_agent import WeatherAgent
from agents.ocean_agent import OceanAgent
from agents.marine_pfz_agent import MarinePFZAgent
from agents.geospatial_agent import GeospatialService
from reasoning.temporal_reasoning import TemporalReasoningEngine
from reasoning.risk_engine import DeterministicRiskEngine
from reasoning.evidence_aggregator import EvidenceAggregator

logger = logging.getLogger(__name__)

class OrcaOrchestrator:
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm_provider = llm_provider or MockRuleBasedProvider()
        self.weather_agent = WeatherAgent()
        self.ocean_agent = OceanAgent()
        self.pfz_agent = MarinePFZAgent()
        self.geospatial_service = GeospatialService()
        
        # In-memory multi-turn conversational session store
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": datetime.now(timezone.utc),
                "messages": [],
                "context": {
                    "location_name": settings.DEFAULT_LOCATION_NAME,
                    "latitude": settings.DEFAULT_LATITUDE,
                    "longitude": settings.DEFAULT_LONGITUDE,
                    "date_expression": "today",
                    "time_expression": "06:00",
                    "activity": "fishing",
                    "intent": "MARINE_SAFETY"
                }
            }
        return self.sessions[session_id]

    async def process_query(self, req: QueryRequest) -> QueryResponse:
        start_time = time.time()
        timeline: List[AgentTimelineItem] = []
        
        session = self.get_or_create_session(req.session_id or "default-session")
        prev_context = session["context"]

        # Step 1: Planner - Intent & Entity Extraction
        t0 = time.time()
        extracted = await self.llm_provider.extract_intent_and_entities(
            query=req.query,
            context=prev_context
        )
        plan_duration = int((time.time() - t0) * 1000)
        
        # Override location if explicitly requested by client selector
        if req.location_override:
            extracted["location"]["name"] = req.location_override
            
        # Update conversational session context
        session["context"].update({
            "location_name": extracted["location"]["name"],
            "latitude": extracted["location"]["latitude"],
            "longitude": extracted["location"]["longitude"],
            "date_expression": extracted["date_expression"],
            "time_expression": extracted["time_expression"],
            "activity": extracted["activity"],
            "intent": extracted["intent"]
        })
        
        lang = req.language_override if req.language_override and req.language_override != "auto" else extracted.get("language", "en")
        intent_str = extracted["intent"]
        
        timeline.append(AgentTimelineItem(
            agent="orchestrator",
            label="Intent & Entity Planner",
            status="completed",
            duration_ms=plan_duration,
            summary=f"Detected Intent: {intent_str} | Loc: {extracted['location']['name']} | Time: {extracted['time_expression']}"
        ))

        # Step 2: Temporal Reasoning
        target_dt = TemporalReasoningEngine.resolve_target_datetime(
            date_expr=extracted["date_expression"],
            time_expr=extracted["time_expression"]
        )

        loc_query = LocationQuery(
            name=extracted["location"]["name"],
            latitude=extracted["location"]["latitude"],
            longitude=extracted["location"]["longitude"]
        )

        # Step 3: Concurrent Execution of Required Agents
        t_agents = time.time()
        
        tasks = {
            "weather": self.weather_agent.run(location=loc_query, target_time=target_dt),
            "ocean": self.ocean_agent.run(location=loc_query, target_time=target_dt),
            "marine_pfz": self.pfz_agent.run(location=loc_query, target_time=target_dt),
            "geospatial": self.geospatial_service.run(location=loc_query, target_time=target_dt)
        }
        
        results = await asyncio.gather(*tasks.values())
        agent_results = dict(zip(tasks.keys(), results))
        
        agents_duration = int((time.time() - t_agents) * 1000)

        timeline.append(AgentTimelineItem(
            agent="weather",
            label="Weather Agent",
            status="completed",
            duration_ms=int(agents_duration * 0.4),
            summary=f"Wind: {agent_results['weather'].data.wind_speed_kmh} km/h ({agent_results['weather'].data.wind_direction_cardinal})"
        ))
        timeline.append(AgentTimelineItem(
            agent="ocean",
            label="Ocean Agent",
            status="completed",
            duration_ms=int(agents_duration * 0.45),
            summary=f"Wave Height: {agent_results['ocean'].data.significant_wave_height_m} m | Period: {agent_results['ocean'].data.wave_period_s} s"
        ))
        timeline.append(AgentTimelineItem(
            agent="marine_pfz",
            label="PFZ Advisory Agent",
            status="completed",
            duration_ms=int(agents_duration * 0.2),
            summary=f"Active PFZ Advisories: {agent_results['marine_pfz'].data.get('active_zones_count', 1)}"
        ))
        timeline.append(AgentTimelineItem(
            agent="geospatial",
            label="Geospatial Service",
            status="completed",
            duration_ms=int(agents_duration * 0.1),
            summary=f"Nearest PFZ: {agent_results['geospatial'].data.get('nearest_pfz', {}).get('distance_km', 0)} km"
        ))

        # Step 4: Compile Evidence Trail
        evidence_list = EvidenceAggregator.compile_evidence(
            weather_res=agent_results["weather"].model_dump(),
            ocean_res=agent_results["ocean"].model_dump(),
            pfz_res=agent_results["marine_pfz"].model_dump(),
            geo_res=agent_results["geospatial"].model_dump()
        )
        evidence_ids = [e.evidence_id for e in evidence_list]

        # Step 5: Deterministic Risk Engine
        t_risk = time.time()
        risk_assessment = DeterministicRiskEngine.evaluate(
            weather_data=agent_results["weather"].data.model_dump(),
            ocean_data=agent_results["ocean"].data.model_dump(),
            geospatial_data=agent_results["geospatial"].data,
            evidence_ids=evidence_ids
        )
        risk_duration = int((time.time() - t_risk) * 1000)

        timeline.append(AgentTimelineItem(
            agent="risk_engine",
            label="Deterministic Risk Engine",
            status="completed",
            duration_ms=risk_duration,
            summary=f"Risk: {risk_assessment.risk_level.value} (Score: {risk_assessment.risk_score}/100)"
        ))

        # Step 6: Response Synthesis (Constrained Strictly by Evidence)
        agent_dict = {
            "weather": agent_results["weather"].model_dump(),
            "ocean": agent_results["ocean"].model_dump(),
            "marine_pfz": agent_results["marine_pfz"].model_dump(),
            "geospatial": agent_results["geospatial"].model_dump()
        }
        
        answer = await self.llm_provider.synthesize_response(
            query=req.query,
            language=lang,
            intent=intent_str,
            risk_data=risk_assessment.model_dump(),
            evidence_list=[e.model_dump() for e in evidence_list],
            agent_data=agent_dict
        )

        # Step 7: Map Features Generation
        map_features = agent_results["geospatial"].data.get("geojson_features", {"type": "FeatureCollection", "features": []})
        
        map_features["features"].append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [loc_query.longitude, loc_query.latitude]
            },
            "properties": {
                "feature_type": "query_origin",
                "name": loc_query.name,
                "wave_height": f"{agent_results['ocean'].data.significant_wave_height_m} m",
                "wind_speed": f"{agent_results['weather'].data.wind_speed_kmh} km/h",
                "risk_level": risk_assessment.risk_level.value
            }
        })

        total_duration = int((time.time() - start_time) * 1000)

        # Record conversation in session
        session["messages"].append({
            "user": req.query,
            "assistant": answer,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        is_demo = bool(req.force_demo_mode or settings.DEMO_MODE or agent_results["ocean"].source_type.value == "VERIFIED_CACHE")

        # Compile distinct list of authoritative sources
        unique_sources = list(dict.fromkeys([e.source for e in evidence_list]))
        agents_used = list(tasks.keys())

        return QueryResponse(
            query=req.query,
            location=loc_query.name,
            time=extracted["time_expression"],
            intent=intent_str,
            risk=risk_assessment.risk_level.value,
            answer=answer,
            evidence=evidence_list,
            sources=unique_sources,
            agents_used=agents_used,
            session_id=req.session_id or "default-session",
            query_language=lang,
            risk_assessment=risk_assessment,
            agent_timeline=timeline,
            map_features=map_features,
            is_demo_mode=is_demo,
            execution_time_ms=total_duration
        )

orchestrator = OrcaOrchestrator()
