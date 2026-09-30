"""
Google Earth Engine - Region of Interest (ROI) Definition Utility
"""
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from gee.config.gee_config import GEEConfig

try:
    import ee
    EE_AVAILABLE = True
except ImportError:
    EE_AVAILABLE = False

class ROIManager:
    @staticmethod
    def get_coastal_india_roi():
        if not EE_AVAILABLE:
            return None
        bbox = GEEConfig.BBOX_COASTAL_INDIA
        return ee.Geometry.Rectangle(bbox)

    @staticmethod
    def get_district_roi(district_name):
        districts = {
            'south_24_parganas': [88.0, 21.5, 89.2, 22.6],
            'east_midnapore': [87.4, 21.5, 88.1, 22.3],
            'puri': [85.5, 19.7, 86.4, 20.3],
            'kendrapara': [86.3, 20.3, 87.0, 20.8]
        }
        bounds = districts.get(district_name.lower().replace(' ', '_'), GEEConfig.BBOX_COASTAL_INDIA)
        if EE_AVAILABLE:
            return ee.Geometry.Rectangle(bounds)
        return bounds
