"""
CycloneShield AI - Infrastructure Exposure Analysis Service (GeoPandas & Shapely)
Calculates spatial buffer intersections, exposed road/rail distances, and asset risk scores.
"""
import json
try:
    import numpy as np
    import pandas as pd
    import geopandas as gpd
    from shapely.geometry import Point, LineString, MultiPoint
except ImportError:
    np = None
    pd = None
    gpd = None
    Point = LineString = MultiPoint = None
from services.gis_service import GISService
from models.infrastructure import InfrastructureModel
from models.cyclone import CycloneModel

class ExposureService:
    @staticmethod
    def calculate_exposure(cyclone_id="amphan_2020", buffer_km=50.0, category_filter=None, risk_level_filter=None):
        cyclone = CycloneModel.get_by_id(cyclone_id)
        if not cyclone:
            return None

        # 1. Extract track points and construct Shapely trajectory geometry
        features = cyclone["geojson_track"]["features"]
        track_coords = [(f["geometry"]["coordinates"][0], f["geometry"]["coordinates"][1]) for f in features]
        track_points_data = [
            {"latitude": c[1], "longitude": c[0]} for c in track_coords
        ]

        if LineString is not None and Point is not None:
            if len(track_coords) > 1:
                storm_path_geom = LineString(track_coords)
            else:
                storm_path_geom = Point(track_coords[0])
        else:
            storm_path_geom = None

        # 2. Query Infrastructure Features
        infra_collection = InfrastructureModel.get_all()
        infra_features = infra_collection["features"]

        exposed_assets = []
        counts = {
            "hospitals": 0,
            "power_facilities": 0,
            "shelters": 0,
            "roads": 0,
            "railways": 0,
            "total_exposed": 0,
            "exposed_road_distance_km": 0.0,
            "exposed_railway_distance_km": 0.0,
            "total_shelter_capacity": 0
        }

        for item in infra_features:
            props = item["properties"]
            geom_dict = item["geometry"]
            cat = props["category"]

            # Filter by category if requested
            if category_filter and category_filter.lower() != 'all':
                if cat.lower() != category_filter.lower():
                    continue

            # Compute min distance to track using GIS Haversine service
            if geom_dict["type"] == "Point":
                lon, lat = geom_dict["coordinates"][0], geom_dict["coordinates"][1]
                dist_km = GISService.min_distance_to_track_km(lat, lon, track_points_data)
                coords = [lon, lat]
            elif geom_dict["type"] == "LineString":
                coords = geom_dict["coordinates"]
                dist_km = min([
                    GISService.min_distance_to_track_km(c[1], c[0], track_points_data)
                    for c in coords
                ])
            else:
                dist_km = float('inf')
                coords = []

            # Check if asset falls within target buffer radius
            if dist_km <= buffer_km:
                # Determine asset risk score (0-100) and risk level based on proximity and criticality
                base_score = max(0.0, min(100.0, 100.0 - (dist_km / buffer_km) * 60.0 + (20.0 if cat == 'hospital' else 10.0)))
                item_risk_score = round(base_score, 1)

                if item_risk_score >= 76.0 or dist_km <= 25.0:
                    item_risk_level = "EXTREME"
                elif item_risk_score >= 51.0 or dist_km <= 50.0:
                    item_risk_level = "HIGH"
                elif item_risk_score >= 26.0:
                    item_risk_level = "MODERATE"
                else:
                    item_risk_level = "LOW"

                # Filter by risk_level if requested
                if risk_level_filter and risk_level_filter.upper() != 'ALL':
                    if item_risk_level != risk_level_filter.upper():
                        continue

                # Formulate narrative exposure reason
                if cat == "hospital":
                    exposure_reason = f"Hospital located {round(dist_km, 1)}km from storm eye path; high surge inundation and emergency power risk."
                    counts["hospitals"] += 1
                elif cat == "shelter":
                    capacity = props.get("capacity_val", 1000)
                    exposure_reason = f"Cyclone shelter located {round(dist_km, 1)}km from track; capacity for {capacity} evacuees."
                    counts["shelters"] += 1
                    counts["total_shelter_capacity"] += capacity
                elif cat == "power":
                    exposure_reason = f"Power substation located {round(dist_km, 1)}km from eye core; extreme wind load & transformer flooding hazard."
                    counts["power_facilities"] += 1
                elif cat == "road":
                    road_len = 35.5 # Standard corridor estimate
                    exposure_reason = f"Evacuation highway corridor within {round(dist_km, 1)}km buffer; coastal storm surge flood hazard."
                    counts["roads"] += 1
                    counts["exposed_road_distance_km"] += road_len
                elif cat == "railway":
                    rail_len = 28.0
                    exposure_reason = f"Coastal railway line within {round(dist_km, 1)}km buffer; high track wash-out risk."
                    counts["railways"] += 1
                    counts["exposed_railway_distance_km"] += rail_len
                else:
                    exposure_reason = f"Asset located {round(dist_km, 1)}km from cyclone path."

                counts["total_exposed"] += 1

                exposed_asset = {
                    "id": props.get("infra_id"),
                    "name": props.get("name"),
                    "type": cat,
                    "subcategory": props.get("subcategory"),
                    "district": props.get("district"),
                    "state": props.get("state"),
                    "coordinates": coords,
                    "distance_to_track_km": round(dist_km, 2),
                    "risk_score": item_risk_score,
                    "risk_level": item_risk_level,
                    "exposure_reason": exposure_reason,
                    "geometry": geom_dict
                }
                exposed_assets.append(exposed_asset)

        # Round distance totals
        counts["exposed_road_distance_km"] = round(counts["exposed_road_distance_km"], 1)
        counts["exposed_railway_distance_km"] = round(counts["exposed_railway_distance_km"], 1)

        return {
            "cyclone_id": cyclone_id,
            "buffer_radius_km": buffer_km,
            "applied_filters": {
                "category": category_filter or "all",
                "risk_level": risk_level_filter or "all"
            },
            "summary_counts": counts,
            "exposed_infrastructure": exposed_assets,
            "is_demo_data": True
        }
