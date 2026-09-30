"""
Infrastructure Routes Engine
"""
from flask import Blueprint, request
from models.infrastructure import InfrastructureModel
from services.exposure_service import ExposureService
from utils.response import success_response, error_response

infrastructure_bp = Blueprint('infrastructure', __name__)

@infrastructure_bp.route('/infrastructure', methods=['GET'])
@infrastructure_bp.route('/v1/infrastructure', methods=['GET'])
def get_infrastructure():
    try:
        category = request.args.get('category')
        state = request.args.get('state')
        
        infra_data = InfrastructureModel.get_all(category=category, state=state)
        return success_response(
            data=infra_data,
            message="Retrieved infrastructure GeoJSON dataset."
        )
    except Exception as e:
        return error_response(
            code="FETCH_INFRA_ERROR",
            message=f"Failed to retrieve infrastructure data: {str(e)}",
            status_code=500
        )

@infrastructure_bp.route('/infrastructure/exposed', methods=['GET'])
@infrastructure_bp.route('/v1/infrastructure/exposed', methods=['GET'])
def get_exposed_infrastructure():
    try:
        cyclone_id = request.args.get('cyclone_id', 'amphan_2020')
        buffer_km = float(request.args.get('buffer_km', 50.0))
        category = request.args.get('category') or request.args.get('type')
        risk_level = request.args.get('risk_level')

        exposure_data = ExposureService.calculate_exposure(
            cyclone_id=cyclone_id,
            buffer_km=buffer_km,
            category_filter=category,
            risk_level_filter=risk_level
        )

        if not exposure_data:
            return error_response(
                code="CYCLONE_NOT_FOUND",
                message=f"No cyclone found with ID '{cyclone_id}'.",
                status_code=404
            )

        return success_response(
            data=exposure_data,
            message=f"Calculated exposed infrastructure for cyclone '{cyclone_id}' within {buffer_km}km buffer."
        )
    except Exception as e:
        return error_response(
            code="EXPOSURE_CALCULATION_ERROR",
            message=f"Failed to calculate exposed infrastructure: {str(e)}",
            status_code=500
        )
