"""
What-If Scenario Simulation Service
Recalculates vulnerability risk and infrastructure exposure under modified physical storm parameters.
"""
import uuid
from services.risk_engine import RiskEngine
from services.exposure_service import ExposureService
from models.cyclone import CycloneModel
from models.risk import RiskEvaluationModel

class SimulationService:
    @staticmethod
    def run_simulation(cyclone_id, delta_wind_knots=0, delta_rainfall_percent=0, shift_direction="NONE", shift_distance_km=0, wind_knots=None, rainfall_mm=None):
        # 1. Calculate baseline risk score & baseline infrastructure exposure
        baseline = RiskEngine.calculate_vulnerability_score(cyclone_id)
        if not baseline:
            cyclone_id = "amphan_2020"
            baseline = RiskEngine.calculate_vulnerability_score(cyclone_id)
            
        if not baseline:
            return None

        base_wind = float(baseline["hazard_breakdown"]["peak_wind_knots"])
        base_rain = float(baseline["hazard_breakdown"]["projected_rainfall_mm"])
        base_buffer = float(baseline.get("buffer_radius_km", 50.0))

        # 2. Extract or calculate simulated parameters
        if wind_knots is not None:
            simulated_wind = max(10.0, float(wind_knots))
            delta_wind_knots = simulated_wind - base_wind
        else:
            simulated_wind = max(10.0, base_wind + float(delta_wind_knots))

        if rainfall_mm is not None:
            simulated_rain = max(0.0, float(rainfall_mm))
            delta_rainfall_percent = ((simulated_rain - base_rain) / base_rain * 100.0) if base_rain > 0 else 0.0
        else:
            simulated_rain = max(0.0, base_rain * (1.0 + float(delta_rainfall_percent) / 100.0))

        # 3. Buffer radius modification based on lateral track shift
        shift_dist = float(shift_distance_km)
        sim_buffer = base_buffer
        if shift_direction in ["WEST", "SOUTH"] and shift_dist > 0:
            sim_buffer = max(15.0, base_buffer - (shift_dist * 0.4))
        elif shift_direction in ["EAST", "NORTH"] and shift_dist > 0:
            sim_buffer = base_buffer + (shift_dist * 0.4)

        # 4. Recalculate simulated risk score & infrastructure exposure
        simulated = RiskEngine.calculate_vulnerability_score(
            cyclone_id,
            buffer_km=sim_buffer,
            wind_knots=simulated_wind,
            rainfall_mm=simulated_rain
        )

        baseline_exposure = ExposureService.calculate_exposure(cyclone_id, base_buffer)
        simulated_exposure = ExposureService.calculate_exposure(cyclone_id, sim_buffer)

        sim_id = f"sim_{uuid.uuid4().hex[:8]}"
        score_delta = round(simulated["vulnerability_score"] - baseline["vulnerability_score"], 1)

        result = {
            "simulation_id": sim_id,
            "base_cyclone_id": cyclone_id,
            "disclaimer": "SIMULATED WHAT-IF SCENARIO ONLY — FOR INFORMATIONAL DECISION SUPPORT (NOT AN OFFICIAL WEATHER FORECAST)",
            "simulation_parameters": {
                "delta_wind_knots": float(round(delta_wind_knots, 1)),
                "delta_rainfall_percent": float(round(delta_rainfall_percent, 1)),
                "shift_direction": shift_direction,
                "shift_distance_km": shift_dist,
                "simulated_wind_knots": float(round(simulated_wind, 1)),
                "simulated_rainfall_mm": float(round(simulated_rain, 1))
            },
            "baseline": {
                "vulnerability_score": baseline["vulnerability_score"],
                "risk_category": baseline["risk_category"],
                "peak_wind_knots": base_wind,
                "projected_rainfall_mm": base_rain,
                "buffer_radius_km": base_buffer,
                "infrastructure_summary": baseline_exposure["summary_counts"],
                "hazard_breakdown": baseline["hazard_breakdown"]
            },
            "simulated": {
                "vulnerability_score": simulated["vulnerability_score"],
                "risk_category": simulated["risk_category"],
                "peak_wind_knots": float(round(simulated_wind, 1)),
                "projected_rainfall_mm": float(round(simulated_rain, 1)),
                "buffer_radius_km": sim_buffer,
                "infrastructure_summary": simulated_exposure["summary_counts"],
                "hazard_breakdown": simulated["hazard_breakdown"],
                "exposed_infrastructure": simulated_exposure["exposed_infrastructure"]
            },
            "delta": {
                "score_delta": score_delta,
                "wind_delta_knots": float(round(simulated_wind - base_wind, 1)),
                "rainfall_delta_mm": float(round(simulated_rain - base_rain, 1)),
                "is_increased_risk": score_delta > 0,
                "category_changed": baseline["risk_category"] != simulated["risk_category"]
            },
            "is_demo_data": True
        }

        # 5. Invoke Gemini AI Scenario Analysis Reasoning
        try:
            from services.gemini_service import GeminiService
            gemini_res = GeminiService.analyze_scenario(result)
            result["gemini_explanation"] = gemini_res.get("scenario_analysis", "")
        except Exception as e:
            print(f"Gemini scenario explanation note: {e}")
            result["gemini_explanation"] = (
                f"**What-If Simulation Analysis**:\n"
                f"- **Baseline Score**: {baseline['vulnerability_score']} ({base_wind} kts, {base_rain} mm)\n"
                f"- **Simulated Score**: {simulated['vulnerability_score']} ({round(simulated_wind, 1)} kts, {round(simulated_rain, 1)} mm)\n"
                f"- **Threat Delta**: {score_delta > 0 and '+' or ''}{score_delta} points.\n"
                f"Increasing physical parameters elevates infrastructure stress along low-lying coastal sectors."
            )

        # Log simulation run in database
        try:
            RiskEvaluationModel.log_simulation({
                'sim_id': sim_id,
                'base_cyclone_id': cyclone_id,
                'delta_wind_knots': float(delta_wind_knots),
                'delta_rainfall_percent': float(delta_rainfall_percent),
                'shift_direction': shift_direction,
                'shift_distance_km': shift_dist,
                'baseline_score': baseline["vulnerability_score"],
                'simulated_score': simulated["vulnerability_score"]
            })
        except Exception as e:
            print(f"Warning: Failed to log simulation to DB: {e}")

        return result
