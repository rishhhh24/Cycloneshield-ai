"""
Infrastructure Data Models & DB Access Layer
"""
import json
from utils.db import get_db

class InfrastructureModel:
    @staticmethod
    def get_all(category=None, state=None):
        db = get_db()
        cursor = db.cursor()
        
        query = "SELECT * FROM infrastructure WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        if state:
            query += " AND state = ?"
            params.append(state)
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        features = []
        for r in rows:
            r_dict = dict(r)
            geometry = json.loads(r_dict["geojson_geometry"])
            features.append({
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "infra_id": r_dict["infra_id"],
                    "name": r_dict["name"],
                    "category": r_dict["category"],
                    "subcategory": r_dict["subcategory"],
                    "state": r_dict["state"],
                    "district": r_dict["district"],
                    "capacity_val": r_dict["capacity_val"],
                    "elevation_meters": r_dict["elevation_meters"],
                    "is_demo": bool(r_dict["is_demo"])
                }
            })

        return {
            "type": "FeatureCollection",
            "metadata": {
                "total_count": len(features),
                "category_filter": category,
                "is_demo_data": True
            },
            "features": features
        }
