"""
Forecast and Risk Calculation Routes
"""
from flask import Blueprint, request
from services.risk_engine import RiskEngine
from utils.response import success_response, error_response

forecast_bp = Blueprint('forecast', __name__)

@forecast_bp.route('/forecast', methods=['POST'])
@forecast_bp.route('/v1/forecast', methods=['POST'])
@forecast_bp.route('/v1/risk/calculate', methods=['POST'])
def calculate_forecast_risk():
    try:
        payload = request.get_json() or {}
        cyclone_id = payload.get('cyclone_id')
        
        if not cyclone_id:
            return error_response(
                code="MISSING_PARAMETER",
                message="Field 'cyclone_id' is required in request payload.",
                status_code=400
            )

        buffer_km = float(payload.get('buffer_km', 50.0))
        wind_knots = payload.get('wind_knots')
        rainfall_mm = float(payload.get('rainfall_mm', 250.0))

        risk_evaluation = RiskEngine.calculate_vulnerability_score(
            cyclone_id=cyclone_id,
            buffer_km=buffer_km,
            wind_knots=wind_knots,
            rainfall_mm=rainfall_mm
        )

        if not risk_evaluation:
            return error_response(
                code="CYCLONE_NOT_FOUND",
                message=f"No cyclone found with ID '{cyclone_id}'.",
                status_code=404
            )

        return success_response(
            data=risk_evaluation,
            message=f"Calculated Infrastructure Vulnerability Risk Score for cyclone '{cyclone_id}'."
        )
    except Exception as e:
        return error_response(
            code="CALCULATION_ERROR",
            message=f"Failed to calculate forecast risk: {str(e)}",
            status_code=500
        )
