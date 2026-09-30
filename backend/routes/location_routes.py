"""
CycloneShield AI - Location Analysis API Routes
"""
from flask import Blueprint, request
from services.location_service import LocationService
from utils.response import success_response, error_response

location_bp = Blueprint('location', __name__)

@location_bp.route('/location/analyze', methods=['GET'])
@location_bp.route('/v1/location/analyze', methods=['GET'])
def analyze_location():
    try:
        lat_str = request.args.get('lat')
        lon_str = request.args.get('lon')

        if not lat_str or not lon_str:
            return error_response(
                code="MISSING_COORDINATES",
                message="Query parameters 'lat' and 'lon' are required.",
                status_code=400
            )

        lat = float(lat_str)
        lon = float(lon_str)

        analysis_res = LocationService.analyze_location(lat, lon)
        return success_response(
            data=analysis_res,
            message=f"Location analysis generated for coordinates ({lat}, {lon})."
        )
    except ValueError:
        return error_response(
            code="INVALID_COORDINATES",
            message="Latitude and longitude must be valid floating point numbers.",
            status_code=400
        )
    except Exception as e:
        return error_response(
            code="LOCATION_ANALYSIS_ERROR",
            message=f"Failed to analyze location: {str(e)}",
            status_code=500
        )
