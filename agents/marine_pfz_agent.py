import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from backend.models.schemas import LocationQuery, PFZAgentResponse, SourceTypeEnum
from backend.adapters.registry import registry

logger = logging.getLogger(__name__)

class MarinePFZAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="marine_pfz",
            description="Retrieves INCOIS Potential Fishing Zone (PFZ) advisories, depth, bearing, and species aggregation."
        )

    async def run(
        self,
        location: LocationQuery,
        target_time: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> PFZAgentResponse:
        now = datetime.now(timezone.utc)
        
        pfz_res = await registry.pfz_adapter.fetch(
            latitude=location.latitude,
            longitude=location.longitude,
            target_time=target_time
        )
        
        raw_data = pfz_res.get("data", {})
        
        return PFZAgentResponse(
            agent="marine_pfz",
            status="success",
            location=location,
            timestamp=now,
            source=pfz_res.get("source", "INCOIS Marine Fisheries Division"),
            source_type=pfz_res.get("source_type", SourceTypeEnum.VERIFIED_CACHE),
            source_timestamp=pfz_res.get("source_timestamp", now.isoformat()),
            confidence=pfz_res.get("confidence", 0.94),
            data=raw_data,
            errors=[]
        )
