"""
CycloneShield AI - Multi-Criteria Baseline Vulnerability Risk Model
Decision-support prototype engine providing deterministic risk scoring and feature explainability.
"""
try:
    import numpy as np
    import pandas as pd
except ImportError:
    np = None
    pd = None

class BaselineVulnerabilityModel:
    """
    Transparent Multi-Criteria Vulnerability Model for Decision Support.
    Combines wind hazard, rainfall inundation, storm surge, infrastructure density, and topographic elevation.
    """
    def __init__(self):
        self.weights = {
            'wind': 0.35,
            'rainfall': 0.25,
            'surge': 0.20,
            'infrastructure': 0.20
        }

    @staticmethod
    def classify_risk_level(score):
        if score <= 25.0:
            return "LOW"
        elif score <= 50.0:
            return "MODERATE"
        elif score <= 75.0:
            return "HIGH"
        else:
            return "EXTREME"

    def predict(self, feature_data):
        """
        Computes vulnerability risk score (0-100), risk level, and explainable contributing factors.
        """
        if isinstance(feature_data, dict):
            row = feature_data
        elif isinstance(feature_data, pd.DataFrame):
            row = feature_data.iloc[0].to_dict()
        else:
            row = feature_data

        wind_knots = float(row.get('wind_speed_knots', 80.0))
        rain_mm = float(row.get('rainfall_mm', 200.0))
        dist_track = float(row.get('distance_to_track_km', 25.0))
        elevation_m = float(row.get('elevation_meters', 5.0))

        hospitals = int(row.get('hospital_count', 0))
        shelters = int(row.get('shelter_count', 0))
        power_stations = int(row.get('power_substation_count', 0))
        road_km = float(row.get('road_km', 0.0))
        total_assets = hospitals + shelters + power_stations

        # 1. Component Hazard Scores (0 to 100)
        wind_score = min(100.0, (wind_knots / 130.0) * 100.0)
        rain_score = min(100.0, (rain_mm / 350.0) * 100.0)
        surge_score = min(100.0, wind_score * 0.9)
        infra_score = min(100.0, (total_assets / 15.0) * 100.0)

        # 2. Elevation Mitigation (Higher elevation reduces vulnerability)
        elevation_mitigation = min(20.0, max(0.0, elevation_m * 1.5))

        # 3. Distance to Track Penalty / Decay
        track_factor = max(0.5, 1.0 - (dist_track / 150.0))

        # 4. Raw Multi-Criteria Score Calculation
        raw_score = (
            self.weights['wind'] * wind_score +
            self.weights['rainfall'] * rain_score +
            self.weights['surge'] * surge_score +
            self.weights['infrastructure'] * infra_score -
            elevation_mitigation
        ) * track_factor

        risk_score = round(max(0.0, min(100.0, raw_score)), 1)
        risk_level = self.classify_risk_level(risk_score)

        # 5. Extract Explainable Contributing Factors for Gemini AI
        contributing_factors = []

        # Wind Factor
        wind_impact = "HIGH" if wind_knots >= 90 else ("MODERATE" if wind_knots >= 60 else "LOW")
        contributing_factors.append({
            "factor": "wind_speed",
            "value": wind_knots,
            "unit": "knots",
            "impact": wind_impact,
            "description": f"Peak sustained wind speed of {wind_knots} knots ({round(wind_knots * 1.852)} km/h) creates {wind_impact.lower()} structural hazard."
        })

        # Rainfall Factor
        rain_impact = "HIGH" if rain_mm >= 250 else ("MODERATE" if rain_mm >= 150 else "LOW")
        contributing_factors.append({
            "factor": "rainfall",
            "value": rain_mm,
            "unit": "mm",
            "impact": rain_impact,
            "description": f"Projected {rain_mm} mm 24h precipitation poses {rain_impact.lower()} flood inundation risk."
        })

        # Infrastructure Exposure Factor
        infra_impact = "HIGH" if hospitals >= 5 or total_assets >= 10 else ("MODERATE" if total_assets >= 5 else "LOW")
        contributing_factors.append({
            "factor": "infrastructure_exposure",
            "value": total_assets,
            "unit": "critical_facilities",
            "impact": infra_impact,
            "description": f"{hospitals} hospitals, {shelters} shelters, and {power_stations} power stations are exposed within the storm buffer."
        })

        # Elevation Resilience Factor
        elev_impact = "HIGH" if elevation_m < 5.0 else ("MODERATE" if elevation_m < 10.0 else "LOW")
        contributing_factors.append({
            "factor": "elevation",
            "value": elevation_m,
            "unit": "meters",
            "impact": elev_impact,
            "description": f"Terrain elevation of {elevation_m}m ASL provides {elev_impact.lower()} vulnerability to storm surge."
        })

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "model_type": "Multi-Criteria Physics Baseline Prototype",
            "hazard_components": {
                "wind_score": round(wind_score, 1),
                "rainfall_score": round(rain_score, 1),
                "surge_score": round(surge_score, 1),
                "infra_score": round(infra_score, 1),
                "elevation_mitigation": round(elevation_mitigation, 1)
            },
            "contributing_factors": contributing_factors
        }
