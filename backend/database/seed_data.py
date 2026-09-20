import json
import asyncio
from pathlib import Path
from sqlalchemy.future import select

from backend.config import settings
from backend.database.db import init_db, AsyncSessionLocal
from backend.models.database_models import LocationModel, PFZZoneModel, RestrictedZoneModel

async def seed_all():
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        result = await session.execute(select(LocationModel))
        existing = result.scalars().first()
        if existing:
            print("Database already contains seed data. Refreshing...")
            await session.execute(LocationModel.__table__.delete())
            await session.execute(PFZZoneModel.__table__.delete())
            await session.execute(RestrictedZoneModel.__table__.delete())
            await session.commit()

        # 1. Seed Landing Centres
        landing_centres_file = settings.GEOJSON_DIR / "landing_centres.geojson"
        if landing_centres_file.exists():
            with open(landing_centres_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for feat in data.get("features", []):
                    props = feat["properties"]
                    coords = feat["geometry"]["coordinates"]
                    loc = LocationModel(
                        id=props["id"],
                        name=props["name"],
                        location_name=props["location_name"],
                        district=props["district"],
                        state=props["state"],
                        category=props["category"],
                        longitude=coords[0],
                        latitude=coords[1],
                        active_vessels=props.get("active_vessels"),
                        contact=props.get("contact")
                    )
                    session.add(loc)
            print(f"Loaded landing centres from {landing_centres_file.name}")

        # 2. Seed PFZ Zones
        pfz_file = settings.GEOJSON_DIR / "pfz_polygons.geojson"
        if pfz_file.exists():
            with open(pfz_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for feat in data.get("features", []):
                    props = feat["properties"]
                    geom = feat["geometry"]
                    pfz = PFZZoneModel(
                        id=props["id"],
                        name=props["name"],
                        reference_centre=props["reference_centre"],
                        bearing_deg=props["bearing_deg"],
                        direction=props["direction"],
                        distance_km=props["distance_km"],
                        depth_range_m=props["depth_range_m"],
                        sst_celsius=props["sst_celsius"],
                        chlorophyll_mg_m3=props["chlorophyll_mg_m3"],
                        target_species=props.get("target_species", ""),
                        coordinates_json=json.dumps(geom["coordinates"]),
                        valid_from=props["valid_from"],
                        valid_to=props["valid_to"]
                    )
                    session.add(pfz)
            print(f"Loaded PFZ polygons from {pfz_file.name}")

        # 3. Seed Restricted Zones
        restricted_file = settings.GEOJSON_DIR / "restricted_zones.geojson"
        if restricted_file.exists():
            with open(restricted_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for feat in data.get("features", []):
                    props = feat["properties"]
                    geom = feat["geometry"]
                    rz = RestrictedZoneModel(
                        id=props["id"],
                        name=props["name"],
                        category=props["category"],
                        restriction_level=props["restriction_level"],
                        legal_basis=props.get("legal_basis"),
                        description=props["description"],
                        authority=props["authority"],
                        polygon_json=json.dumps(geom["coordinates"])
                    )
                    session.add(rz)
            print(f"Loaded restricted zones from {restricted_file.name}")

        await session.commit()
        print("Database seed complete successfully!")

if __name__ == "__main__":
    asyncio.run(seed_all())
