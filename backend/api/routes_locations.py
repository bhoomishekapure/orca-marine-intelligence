from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from typing import List
from backend.database.db import get_db, AsyncSession
from backend.models.database_models import LocationModel
from backend.models.schemas import LandingCentre

router = APIRouter(prefix="/api", tags=["Locations"])

@router.get("/locations", response_model=List[LandingCentre])
async def list_locations(db: AsyncSession = Depends(get_db)):
    """List all registered coastal landing centres and fishing harbours."""
    result = await db.execute(select(LocationModel))
    locations = result.scalars().all()
    
    return [
        LandingCentre(
            id=loc.id,
            name=loc.name,
            location_name=loc.location_name,
            district=loc.district,
            state=loc.state,
            category=loc.category,
            latitude=loc.latitude,
            longitude=loc.longitude,
            active_vessels=loc.active_vessels,
            contact=loc.contact
        )
        for loc in locations
    ]
