from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from backend.models.schemas import SourceTypeEnum

class BaseDataAdapter(ABC):
    def __init__(self, name: str):
        self.name = name
        self.last_fetched_at: Optional[datetime] = None
        self.is_healthy: bool = True
        self.last_error: Optional[str] = None

    @abstractmethod
    async def fetch(self, latitude: float, longitude: float, target_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Fetch marine or meteorological observations / forecasts."""
        pass

    @abstractmethod
    def get_provenance_metadata(self, is_cached: bool = False) -> Dict[str, Any]:
        """Return standardized provenance metadata for the retrieved dataset."""
        pass
