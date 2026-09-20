from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from backend.models.schemas import LocationQuery

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def run(
        self,
        location: LocationQuery,
        target_time: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the agent task and return structured output matching contract."""
        pass
