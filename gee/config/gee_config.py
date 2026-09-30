"""
CycloneShield AI - Google Earth Engine Configuration Module
"""
import os
from dotenv import load_dotenv

load_dotenv()

class GEEConfig:
    # Earth Engine Project Configuration
    GEE_PROJECT_ID = os.getenv('GEE_PROJECT_ID', 'cycloneshield-ai-2026')
    GEE_SERVICE_ACCOUNT = os.getenv('GEE_SERVICE_ACCOUNT', '')
    
    # Target Coastal India Region of Interest (Odisha & West Bengal)
    # Bounding Box: [min_lon, min_lat, max_lon, max_lat]
    BBOX_COASTAL_INDIA = [85.0, 19.0, 89.5, 23.0]
    
    # Earth Engine Catalog Dataset IDs
    DATASETS = {
        'elevation_srtm': 'USGS/SRTMGL1_003',             # NASA SRTM Digital Elevation 30m
        'elevation_copernicus': 'COPERNICUS/DEM/GLO30',    # Copernicus DEM 30m
        'landcover_esa': 'ESA/WorldCover/v100',           # ESA WorldCover 10m
        'sentinel1_sar': 'COPERNICUS/S1_GRD',             # Sentinel-1 Synthetic Aperture Radar
        'sentinel2_optical': 'COPERNICUS/S2_SR_HARMONIZED',# Sentinel-2 MSI Surface Reflectance
        'chirps_rainfall': 'UCSB-CHG/CHIRPS/DAILY',        # CHIRPS Daily Precipitation
        'era5_reanalysis': 'ECMWF/ERA5_LAND/DAILY_AGGR'    # ERA5 Land Daily Aggregated
    }

    # Target Historical Cyclones Event Windows
    EVENT_WINDOWS = {
        'amphan_2020': {
            'pre_event': ['2020-05-01', '2020-05-15'],
            'post_event': ['2020-05-21', '2020-06-05']
        },
        'fani_2019': {
            'pre_event': ['2019-04-15', '2019-04-30'],
            'post_event': ['2019-05-04', '2019-05-20']
        }
    }
