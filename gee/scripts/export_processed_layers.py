"""
Google Earth Engine - Export Processed Layers Script
Generates compiled GEE geospatial layer JSON summaries for Flask backend integration.
"""
import sys
import os
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from gee.scripts.elevation_exporter import ElevationProcessor
from gee.scripts.satellite_flood_analyzer import SatelliteFloodAnalyzer
from gee.scripts.environmental_features import EnvironmentalExtractor

def run_export():
    print("Executing Google Earth Engine layer processing and export pipeline...")
    
    elevation_data = ElevationProcessor.get_elevation_and_slope()
    sar_data = SatelliteFloodAnalyzer.get_sentinel_sar_flood_metadata('amphan_2020')
    rainfall_data = EnvironmentalExtractor.get_chirps_rainfall('amphan_2020')
    landcover_data = EnvironmentalExtractor.get_landcover_distribution()

    export_payload = {
        "gee_pipeline_metadata": {
            "region": "Coastal Odisha & West Bengal (Bay of Bengal)",
            "bounding_box": [85.0, 19.0, 89.5, 23.0],
            "exported_at": "2026-09-26T15:00:00Z",
            "crs": "EPSG:4326 (WGS84)"
        },
        "elevation_dem": elevation_data,
        "sentinel1_sar_flood": sar_data,
        "chirps_precipitation": rainfall_data,
        "esa_worldcover": landcover_data
    }

    # Destination 1: gee/exports/coastal_india_gee_layers.json
    export_dir1 = os.path.abspath(os.path.join(PROJECT_ROOT, 'gee', 'exports'))
    os.makedirs(export_dir1, exist_ok=True)
    target_file1 = os.path.join(export_dir1, 'coastal_india_gee_layers.json')

    with open(target_file1, 'w', encoding='utf-8') as f:
        json.dump(export_payload, f, indent=2)

    # Destination 2: data/processed/gee_summary.json
    export_dir2 = os.path.abspath(os.path.join(PROJECT_ROOT, 'data', 'processed'))
    os.makedirs(export_dir2, exist_ok=True)
    target_file2 = os.path.join(export_dir2, 'gee_summary.json')

    with open(target_file2, 'w', encoding='utf-8') as f:
        json.dump(export_payload, f, indent=2)

    print(f"GEE layers successfully exported to:\n  - {target_file1}\n  - {target_file2}")

if __name__ == '__main__':
    run_export()
