from fastapi import APIRouter
from backend.config import settings
from backend.adapters.registry import registry

router = APIRouter(prefix="/api", tags=["Health & Status"])

@router.get("/health")
async def health_check():
    """Return health and freshness status of ORCA agents and marine adapters."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "demo_mode": settings.DEMO_MODE,
        "llm_provider": settings.LLM_PROVIDER,
        "focus_geography": {
            "region": "Coastal Maharashtra (Ratnagiri Sector)",
            "default_lat": settings.DEFAULT_LATITUDE,
            "default_lon": settings.DEFAULT_LONGITUDE
        },
        "providers": registry.get_providers_status()
    }
