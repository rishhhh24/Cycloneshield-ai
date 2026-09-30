"""
Cyclone Data Routes
"""
from flask import Blueprint, jsonify
from models.cyclone import CycloneModel
from utils.response import success_response, error_response

cyclone_bp = Blueprint('cyclone', __name__)

@cyclone_bp.route('/cyclones', methods=['GET'])
@cyclone_bp.route('/v1/cyclones', methods=['GET'])
def get_cyclones():
    try:
        cyclones = CycloneModel.get_all()
        return success_response(
            data=cyclones,
            message=f"Retrieved {len(cyclones)} historical cyclones."
        )
    except Exception as e:
        return error_response(
            code="FETCH_CYCLONES_ERROR",
            message=f"Failed to retrieve cyclones: {str(e)}",
            status_code=500
        )

@cyclone_bp.route('/cyclones/<cyclone_id>', methods=['GET'])
@cyclone_bp.route('/v1/cyclones/<cyclone_id>', methods=['GET'])
def get_cyclone_by_id(cyclone_id):
    try:
        cyclone = CycloneModel.get_by_id(cyclone_id)
        if not cyclone:
            return error_response(
                code="CYCLONE_NOT_FOUND",
                message=f"No cyclone found with ID '{cyclone_id}'.",
                status_code=404
            )
        return success_response(
            data=cyclone,
            message=f"Retrieved details for cyclone '{cyclone['name']}'."
        )
    except Exception as e:
        return error_response(
            code="FETCH_CYCLONE_DETAIL_ERROR",
            message=f"Failed to retrieve cyclone details: {str(e)}",
            status_code=500
        )
