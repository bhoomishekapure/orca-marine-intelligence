import time
from typing import Dict, Any, List
from backend.adapters.open_meteo_adapter import OpenMeteoMarineAdapter, OpenMeteoWeatherAdapter
from backend.adapters.incois_adapter import INCOISPFZAdapter
from backend.adapters.imd_adapter import IMDCoastalAdapter

class DataProviderRegistry:
    def __init__(self):
        self.marine_adapter = OpenMeteoMarineAdapter()
        self.weather_adapter = OpenMeteoWeatherAdapter()
        self.pfz_adapter = INCOISPFZAdapter()
        self.imd_adapter = IMDCoastalAdapter()

    def get_providers_status(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "Open-Meteo Marine (Live Wave Models)",
                "type": "LIVE_API",
                "healthy": self.marine_adapter.is_healthy,
                "coverage": "Ratnagiri Coastal & Offshore Waters (0.1° resolution)",
                "last_error": self.marine_adapter.last_error
            },
            {
                "name": "Open-Meteo Weather (Atmospheric & Wind)",
                "type": "LIVE_API",
                "healthy": self.weather_adapter.is_healthy,
                "coverage": "Ratnagiri & Coastal Maharashtra",
                "last_error": self.weather_adapter.last_error
            },
            {
                "name": "INCOIS Potential Fishing Zone (PFZ) Advisories",
                "type": "VERIFIED_CACHE",
                "healthy": True,
                "coverage": "Maharashtra Sector (Mirya Bandar / Ratnagiri)",
                "last_error": None
            },
            {
                "name": "IMD Coastal Warnings (ACWC Mumbai)",
                "type": "VERIFIED_CACHE",
                "healthy": True,
                "coverage": "Maharashtra & Goa Coastal Waters",
                "last_error": None
            }
        ]

registry = DataProviderRegistry()
