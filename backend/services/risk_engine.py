"""
Vulnerability Risk Engine - Multi-Criteria Numerical Risk Scoring Model & ML Inference Service
"""
import os
import sys
import uuid
from services.exposure_service import ExposureService
from models.cyclone import CycloneModel
from models.risk import RiskEvaluationModel

# Ensure ML package is accessible
ML_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ML_DIR not in sys.path:
    sys.path.insert(0, ML_DIR)

from ml.predict import VulnerabilityPredictor

# Initialize predictor singleton
predictor_instance = VulnerabilityPredictor(use_xgboost=True)

class RiskEngine:
    @staticmethod
    def classify_risk_category(score):
        if score <= 25.0:
            return "LOW"
        elif score <= 50.0:
            return "MODERATE"
        elif score <= 75.0:
            return "HIGH"
        else:
            return "EXTREME"

    @staticmethod
    def calculate_vulnerability_score(cyclone_id, buffer_km=50.0, wind_knots=None, rainfall_mm=250.0):
        cyclone = CycloneModel.get_by_id(cyclone_id)
        if not cyclone:
            return None

        # Fetch exposure data
        exposure_data = ExposureService.calculate_exposure(cyclone_id, buffer_km)
        counts = exposure_data["summary_counts"]

        # Peak wind speed determination
        if wind_knots is None:
            features = cyclone["geojson_track"]["features"]
            wind_speeds = [f["properties"]["wind_speed_knots"] for f in features]
            peak_wind = max(wind_speeds) if wind_speeds else 80.0
        else:
            peak_wind = float(wind_knots)

        power_count = counts.get("power_facilities", counts.get("power_substations", 0))
        road_len = counts.get("exposed_road_distance_km", counts.get("roads", 0) * 15.0)

        input_features = {
            'wind_speed_knots': peak_wind,
            'rainfall_mm': float(rainfall_mm),
            'distance_to_track_km': float(buffer_km * 0.5),
            'elevation_meters': 4.5,
            'hospital_count': counts.get("hospitals", 0),
            'shelter_count': counts.get("shelters", 0),
            'power_substation_count': power_count,
            'road_km': float(road_len)
        }

        # Predict using ML & Baseline Engine
        pred = predictor_instance.predict(input_features)

        overall_score = float(pred["risk_score"])
        risk_cat = str(pred["risk_level"])
        eval_id = f"eval_{uuid.uuid4().hex[:8]}"

        result = {
            "eval_id": eval_id,
            "cyclone_id": cyclone_id,
            "cyclone_name": cyclone["name"],
            "landfall_location": cyclone["landfall_location"],
            "vulnerability_score": overall_score,
            "risk_category": risk_cat,
            "buffer_radius_km": buffer_km,
            "model_type": pred.get("model_type", "ML Vulnerability Engine"),
            "hazard_breakdown": {
                "wind_hazard_score": float(pred["hazard_components"]["wind_score"]),
                "rainfall_hazard_score": float(pred["hazard_components"]["rainfall_score"]),
                "surge_hazard_score": float(pred["hazard_components"]["surge_score"]),
                "infrastructure_exposure_score": float(pred["hazard_components"]["infra_score"]),
                "peak_wind_knots": float(peak_wind),
                "projected_rainfall_mm": float(rainfall_mm)
            },
            "infrastructure_summary": counts,
            "contributing_factors": pred["contributing_factors"],
            "is_demo_data": True
        }

        # Cache evaluation in database
        try:
            RiskEvaluationModel.save_evaluation({
                'eval_id': eval_id,
                'cyclone_id': cyclone_id,
                'district_name': cyclone['landfall_location'],
                'overall_score': overall_score,
                'risk_category': risk_cat,
                'wind_score': float(pred["hazard_components"]["wind_score"]),
                'rainfall_score': float(pred["hazard_components"]["rainfall_score"]),
                'surge_score': float(pred["hazard_components"]["surge_score"]),
                'infra_exposure_score': float(pred["hazard_components"]["infra_score"]),
                'exposed_hospital_count': counts.get("hospitals", 0),
                'exposed_shelter_count': counts.get("shelters", 0)
            })
        except Exception as e:
            print(f"Warning: Failed to log evaluation to DB: {e}")

        return result
