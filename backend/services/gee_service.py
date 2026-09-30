"""
CycloneShield AI - Google Earth Engine Integration Service
Connects Flask backend with GEE geospatial processing & pre-processed raster summaries.
"""
import os
import json
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from gee.scripts.elevation_exporter import ElevationProcessor
from gee.scripts.satellite_flood_analyzer import SatelliteFloodAnalyzer
from gee.scripts.environmental_features import EnvironmentalExtractor

class GEEService:
    @staticmethod
    def get_layer_summary():
        export_path = os.path.join(PROJECT_ROOT, 'gee', 'exports', 'coastal_india_gee_layers.json')
        if os.path.exists(export_path):
            try:
                with open(export_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Note loading GEE export: {e}")

        return {
            "gee_pipeline_metadata": {
                "region": "Coastal Odisha & West Bengal (Bay of Bengal)",
                "bounding_box": [85.0, 19.0, 89.5, 23.0],
                "crs": "EPSG:4326 (WGS84)"
            },
            "elevation_dem": ElevationProcessor.get_elevation_and_slope(),
            "sentinel1_sar_flood": SatelliteFloodAnalyzer.get_sentinel_sar_flood_metadata('amphan_2020'),
            "chirps_precipitation": EnvironmentalExtractor.get_chirps_rainfall('amphan_2020'),
            "esa_worldcover": EnvironmentalExtractor.get_landcover_distribution()
        }

    @staticmethod
    def get_elevation_data():
        return ElevationProcessor.get_elevation_and_slope()

    @staticmethod
    def get_satellite_data(event_key='amphan_2020'):
        return SatelliteFloodAnalyzer.get_sentinel_sar_flood_metadata(event_key)
