import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.future import select

from backend.config import settings
from backend.database.db import init_db, AsyncSessionLocal
from backend.database.seed_data import seed_all
from backend.models.database_models import LocationModel
from backend.api.routes_query import router as query_router
from backend.api.routes_map import router as map_router
from backend.api.routes_locations import router as locations_router
from backend.api.routes_health import router as health_router
from backend.api.routes_conditions import router as conditions_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing ORCA Marine Intelligence platform...")
    await init_db()
    # Check if seed data exists; if not, seed automatically
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(LocationModel))
        if not res.scalars().first():
            logger.info("Seeding initial Maharashtra coastal GIS datasets...")
            await seed_all()
    logger.info("ORCA Platform initialized and ready.")
    yield
    logger.info("Shutting down ORCA Marine Intelligence platform.")

app = FastAPI(
    title="ORCA — Marine Ecosystem Reasoning with Collaborative Agents",
    description="Agentic marine intelligence and decision-support platform for coastal Maharashtra (SIH 2026)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers (Mounted before static files)
app.include_router(query_router)
app.include_router(map_router)
app.include_router(locations_router)
app.include_router(health_router)
app.include_router(conditions_router)

@app.get("/health", tags=["Health & Status"])
async def root_health():
    """Root health check endpoint."""
    from backend.adapters.registry import registry
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "demo_mode": settings.DEMO_MODE,
        "llm_provider": settings.LLM_PROVIDER,
        "providers": registry.get_providers_status()
    }

# Mount Built React Frontend if dist exists
dist_dir = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="frontend")
else:
    @app.get("/")
    async def root():
        return {
            "project": "ORCA — Marine Ecosystem Reasoning with Collaborative Agents",
            "competition": "Smart India Hackathon 2026",
            "status": "online",
            "docs": "/docs",
            "health": "/api/health"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
