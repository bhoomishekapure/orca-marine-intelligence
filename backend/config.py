import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    APP_NAME: str = "ORCA Marine Intelligence"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "127.0.0.1"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    # Mode
    DEMO_MODE: bool = False
    
    # Database URL (Default sqlite for zero-dependency local execution)
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'orca_marine.db'}"
    
    # LLM Settings
    LLM_PROVIDER: str = "mock"  # "mock", "gemini", "openai"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # External APIs
    OPEN_METEO_MARINE_URL: str = "https://marine-api.open-meteo.com/v1/marine"
    OPEN_METEO_WEATHER_URL: str = "https://api.open-meteo.com/v1/forecast"
    INCOIS_ERDDAP_URL: str = "https://erddap.incois.gov.in/erddap"
    
    # Geographic Focus Default: Ratnagiri, Maharashtra
    DEFAULT_LOCATION_NAME: str = "Ratnagiri"
    DEFAULT_LATITUDE: float = 16.99
    DEFAULT_LONGITUDE: float = 73.30
    
    # Safety Threshold Rules (Configurable maritime prototype rules)
    WAVE_HEIGHT_SAFE_M: float = 1.8
    WAVE_HEIGHT_CAUTION_M: float = 2.5
    WIND_SPEED_SAFE_KMH: float = 30.0
    WIND_SPEED_CAUTION_KMH: float = 45.0
    
    # Data Paths
    DATA_DIR: Path = BASE_DIR / "data"
    GEOJSON_DIR: Path = BASE_DIR / "data" / "geojson"
    VERIFIED_CACHE_DIR: Path = BASE_DIR / "data" / "verified_cache"

settings = Settings()
