"""
Cyclone Data Models & DB Access Layer
"""
import json
from utils.db import get_db

class CycloneModel:
    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM cyclones ORDER BY year DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_by_id(cyclone_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM cyclones WHERE cyclone_id = ?", (cyclone_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        cyclone_dict = dict(row)
        
        # Fetch track points
        cursor.execute("""
            SELECT * FROM track_points 
            WHERE cyclone_id = ? 
            ORDER BY timestamp_utc ASC
        """, (cyclone_id,))
        points = [dict(p) for p in cursor.fetchall()]
        
        # Format GeoJSON FeatureCollection
        features = []
        for p in points:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [p["longitude"], p["latitude"]]
                },
                "properties": {
                    "point_id": p["point_id"],
                    "timestamp_utc": p["timestamp_utc"],
                    "wind_speed_knots": p["wind_speed_knots"],
                    "central_pressure_hpa": p["central_pressure_hpa"],
                    "storm_category": p["storm_category"],
                    "distance_to_landfall_km": p["distance_to_landfall_km"],
                    "is_landfall_point": bool(p["is_landfall_point"])
                }
            })

        cyclone_dict["geojson_track"] = {
            "type": "FeatureCollection",
            "metadata": {
                "cyclone_id": cyclone_id,
                "name": cyclone_dict["name"],
                "is_demo_data": bool(cyclone_dict.get("is_demo", True))
            },
            "features": features
        }

        return cyclone_dict
