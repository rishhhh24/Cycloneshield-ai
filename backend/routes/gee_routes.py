"""
Google Earth Engine API Route Blueprint
"""
from flask import Blueprint, request
from services.gee_service import GEEService
from utils.response import success_response, error_response

gee_bp = Blueprint('gee', __name__)

@gee_bp.route('/gee/layers', methods=['GET'])
@gee_bp.route('/v1/gee/layers', methods=['GET'])
def get_gee_layers():
    try:
        data = GEEService.get_layer_summary()
        return success_response(
            data=data,
            message="Retrieved Google Earth Engine geospatial layer summary."
        )
    except Exception as e:
        return error_response(
            code="GEE_SERVICE_ERROR",
            message=f"Failed to retrieve GEE layers: {str(e)}",
            status_code=500
        )

@gee_bp.route('/gee/elevation', methods=['GET'])
@gee_bp.route('/v1/gee/elevation', methods=['GET'])
def get_gee_elevation():
    try:
        data = GEEService.get_elevation_data()
        return success_response(
            data=data,
            message="Retrieved NASA SRTM DEM elevation data."
        )
    except Exception as e:
        return error_response(
            code="GEE_ELEVATION_ERROR",
            message=f"Failed to retrieve elevation data: {str(e)}",
            status_code=500
        )

@gee_bp.route('/gee/satellite', methods=['GET'])
@gee_bp.route('/v1/gee/satellite', methods=['GET'])
def get_gee_satellite():
    try:
        event_key = request.args.get('event', 'amphan_2020')
        data = GEEService.get_satellite_data(event_key)
        return success_response(
            data=data,
            message="Retrieved Sentinel-1 SAR satellite imagery metadata."
        )
    except Exception as e:
        return error_response(
            code="GEE_SATELLITE_ERROR",
            message=f"Failed to retrieve satellite data: {str(e)}",
            status_code=500
        )
