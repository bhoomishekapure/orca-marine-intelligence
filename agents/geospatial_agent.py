import math
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional
from shapely.geometry import Point, Polygon, shape
from agents.base_agent import BaseAgent
from backend.config import settings
from backend.models.schemas import LocationQuery, GeospatialResponse, SourceTypeEnum

logger = logging.getLogger(__name__)

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points on the Earth (in km)."""
    R = 6371.0  # Earth's mean radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> Tuple[float, str]:
    """Calculate forward azimuth / initial bearing from point 1 to point 2."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    
    y = math.sin(dlambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)
    bearing_rad = math.atan2(y, x)
    bearing_deg = (math.degrees(bearing_rad) + 360.0) % 360.0
    
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    ix = int((bearing_deg + 11.25) / 22.5) % 16
    return round(bearing_deg, 1), dirs[ix]

class GeospatialService(BaseAgent):
    def __init__(self):
        super().__init__(
            name="geospatial",
            description="Performs deterministic GIS calculations: distance, bearing, point-in-polygon, and geofence restriction checks."
        )
        self._load_layers()

    def _load_layers(self):
        self.restricted_zones = []
        self.pfz_polygons = []
        
        rz_file = settings.GEOJSON_DIR / "restricted_zones.geojson"
        if rz_file.exists():
            with open(rz_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for feat in data.get("features", []):
                    poly = shape(feat["geometry"])
                    self.restricted_zones.append({
                        "id": feat["properties"]["id"],
                        "name": feat["properties"]["name"],
                        "category": feat["properties"]["category"],
                        "restriction_level": feat["properties"]["restriction_level"],
                        "description": feat["properties"].get("description", ""),
                        "polygon": poly,
                        "raw_feature": feat
                    })
                    
        pfz_file = settings.GEOJSON_DIR / "pfz_polygons.geojson"
        if pfz_file.exists():
            with open(pfz_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for feat in data.get("features", []):
                    poly = shape(feat["geometry"])
                    self.pfz_polygons.append({
                        "id": feat["properties"]["id"],
                        "name": feat["properties"]["name"],
                        "reference_centre": feat["properties"]["reference_centre"],
                        "bearing_deg": feat["properties"]["bearing_deg"],
                        "direction": feat["properties"]["direction"],
                        "distance_km": feat["properties"]["distance_km"],
                        "depth_range_m": feat["properties"]["depth_range_m"],
                        "sst_celsius": feat["properties"]["sst_celsius"],
                        "chlorophyll_mg_m3": feat["properties"]["chlorophyll_mg_m3"],
                        "target_species": feat["properties"].get("target_species", ""),
                        "polygon": poly,
                        "centroid": (poly.centroid.y, poly.centroid.x),  # lat, lon
                        "raw_feature": feat
                    })

    async def run(
        self,
        location: LocationQuery,
        target_time: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> GeospatialResponse:
        now = datetime.now(timezone.utc)
        curr_point = Point(location.longitude, location.latitude)
        
        # 1. Check Restricted Zones (Point-in-polygon)
        is_inside_restricted = False
        active_violation = None
        closest_restricted = None
        min_dist_restricted = float("inf")
        
        for rz in self.restricted_zones:
            if rz["polygon"].contains(curr_point):
                is_inside_restricted = True
                active_violation = {
                    "zone_id": rz["id"],
                    "name": rz["name"],
                    "category": rz["category"],
                    "restriction_level": rz["restriction_level"],
                    "description": rz["description"]
                }
                break
            else:
                # Estimate distance to centroid
                c_lat, c_lon = rz["polygon"].centroid.y, rz["polygon"].centroid.x
                d = haversine_distance(location.latitude, location.longitude, c_lat, c_lon)
                if d < min_dist_restricted:
                    min_dist_restricted = d
                    closest_restricted = {
                        "name": rz["name"],
                        "distance_km": round(d, 1),
                        "status": "CLEAR"
                    }

        # 2. Calculate Nearest Potential Fishing Zone (PFZ)
        nearest_pfz = None
        min_pfz_dist = float("inf")
        bearing_deg = 0.0
        bearing_dir = "N"
        
        for pfz in self.pfz_polygons:
            c_lat, c_lon = pfz["centroid"]
            dist = haversine_distance(location.latitude, location.longitude, c_lat, c_lon)
            if dist < min_pfz_dist:
                min_pfz_dist = dist
                b_deg, b_dir = calculate_bearing(location.latitude, location.longitude, c_lat, c_lon)
                bearing_deg = b_deg
                bearing_dir = b_dir
                nearest_pfz = {
                    "id": pfz["id"],
                    "name": pfz["name"],
                    "reference_centre": pfz["reference_centre"],
                    "distance_km": round(dist, 1),
                    "distance_nm": round(dist / 1.852, 2),
                    "bearing_deg": bearing_deg,
                    "direction": bearing_dir,
                    "depth_range_m": pfz["depth_range_m"],
                    "sst_celsius": pfz["sst_celsius"],
                    "chlorophyll_mg_m3": pfz["chlorophyll_mg_m3"],
                    "target_species": pfz["target_species"],
                    "target_coords": [c_lon, c_lat]
                }

        # 3. Generate Navigation Vector Feature (Line from location to nearest PFZ)
        nav_features = []
        if nearest_pfz:
            c_lon, c_lat = nearest_pfz["target_coords"]
            nav_features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [location.longitude, location.latitude],
                        [c_lon, c_lat]
                    ]
                },
                "properties": {
                    "feature_type": "navigation_vector",
                    "origin": location.name,
                    "destination": nearest_pfz["name"],
                    "distance_km": nearest_pfz["distance_km"],
                    "bearing": f"{nearest_pfz['bearing_deg']}° {nearest_pfz['direction']}"
                }
            })

        geo_data = {
            "origin": {
                "name": location.name,
                "latitude": location.latitude,
                "longitude": location.longitude
            },
            "is_inside_restricted_zone": is_inside_restricted,
            "active_violation": active_violation,
            "nearest_restricted_zone": closest_restricted,
            "nearest_pfz": nearest_pfz,
            "navigation_vector": {
                "distance_km": nearest_pfz["distance_km"] if nearest_pfz else 0.0,
                "bearing_deg": bearing_deg,
                "bearing_cardinal": bearing_dir
            },
            "geojson_features": {
                "type": "FeatureCollection",
                "features": nav_features
            }
        }

        return GeospatialResponse(
            agent="geospatial",
            status="success",
            timestamp=now,
            source="Shapely / Haversine Deterministic Spatial Engine",
            source_type=SourceTypeEnum.DETERMINISTIC_GIS,
            data=geo_data,
            errors=[]
        )
