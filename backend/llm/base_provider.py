from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text response from LLM."""
        pass

    @abstractmethod
    async def extract_intent_and_entities(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract language, intent, location, date, and time entities."""
        pass

    @abstractmethod
    async def synthesize_response(
        self,
        query: str,
        language: str,
        intent: str,
        risk_data: Dict[str, Any],
        evidence_list: list,
        agent_data: Dict[str, Any]
    ) -> str:
        """Synthesize explainable answer strictly bound to evidence."""
        pass
