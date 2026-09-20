import json
from fastapi import APIRouter, HTTPException
from backend.config import settings

router = APIRouter(prefix="/api/map", tags=["Map Layers"])

@router.get("/layers")
async def get_map_layers():
    """Return all GeoJSON layers for MapLibre visualization."""
    try:
        layers = {
            "landing_centres": {"type": "FeatureCollection", "features": []},
            "pfz_polygons": {"type": "FeatureCollection", "features": []},
            "restricted_zones": {"type": "FeatureCollection", "features": []}
        }
        
        lc_file = settings.GEOJSON_DIR / "landing_centres.geojson"
        if lc_file.exists():
            with open(lc_file, "r", encoding="utf-8") as f:
                layers["landing_centres"] = json.load(f)

        pfz_file = settings.GEOJSON_DIR / "pfz_polygons.geojson"
        if pfz_file.exists():
            with open(pfz_file, "r", encoding="utf-8") as f:
                layers["pfz_polygons"] = json.load(f)

        rz_file = settings.GEOJSON_DIR / "restricted_zones.geojson"
        if rz_file.exists():
            with open(rz_file, "r", encoding="utf-8") as f:
                layers["restricted_zones"] = json.load(f)

        return layers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load map layers: {str(e)}")
