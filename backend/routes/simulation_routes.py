"""
Simulation Routes for What-If Scenario Analysis
"""
from flask import Blueprint, request
from services.simulation_service import SimulationService
from utils.response import success_response, error_response

simulation_bp = Blueprint('simulation', __name__)

@simulation_bp.route('/simulation', methods=['POST'])
@simulation_bp.route('/v1/simulation', methods=['POST'])
@simulation_bp.route('/v1/simulation/what-if', methods=['POST'])
def run_simulation():
    try:
        payload = request.get_json() or {}
        cyclone_id = payload.get('cyclone_id')
        
        if not cyclone_id:
            return error_response(
                code="MISSING_PARAMETER",
                message="Field 'cyclone_id' is required in request payload.",
                status_code=400
            )

        delta_wind = payload.get('delta_wind_knots', 0)
        delta_rain = payload.get('delta_rainfall_percent', 0)
        shift_dir = payload.get('shift_direction', 'NONE')
        shift_dist = payload.get('shift_distance_km', 0)
        wind_knots = payload.get('wind_knots')
        rainfall_mm = payload.get('rainfall_mm')

        sim_result = SimulationService.run_simulation(
            cyclone_id=cyclone_id,
            delta_wind_knots=delta_wind,
            delta_rainfall_percent=delta_rain,
            shift_direction=shift_dir,
            shift_distance_km=shift_dist,
            wind_knots=wind_knots,
            rainfall_mm=rainfall_mm
        )

        if not sim_result:
            return error_response(
                code="CYCLONE_NOT_FOUND",
                message=f"No cyclone found with ID '{cyclone_id}'.",
                status_code=404
            )

        return success_response(
            data=sim_result,
            message="What-If simulation executed successfully."
        )
    except Exception as e:
        return error_response(
            code="SIMULATION_ERROR",
            message=f"Failed to execute scenario simulation: {str(e)}",
            status_code=500
        )
