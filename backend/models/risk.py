"""
Risk Evaluation Model
"""
from utils.db import get_db

class RiskEvaluationModel:
    @staticmethod
    def save_evaluation(eval_data):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO vulnerability_evaluations
            (eval_id, cyclone_id, district_name, overall_score, risk_category, wind_score, rainfall_score, surge_score, infra_exposure_score, exposed_hospital_count, exposed_shelter_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            eval_data['eval_id'],
            eval_data['cyclone_id'],
            eval_data['district_name'],
            eval_data['overall_score'],
            eval_data['risk_category'],
            eval_data['wind_score'],
            eval_data['rainfall_score'],
            eval_data['surge_score'],
            eval_data['infra_exposure_score'],
            eval_data['exposed_hospital_count'],
            eval_data['exposed_shelter_count']
        ))
        db.commit()

    @staticmethod
    def log_simulation(sim_data):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO simulation_logs
            (sim_id, base_cyclone_id, delta_wind_knots, delta_rainfall_percent, shift_direction, shift_distance_km, baseline_score, simulated_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sim_data['sim_id'],
            sim_data['base_cyclone_id'],
            sim_data['delta_wind_knots'],
            sim_data['delta_rainfall_percent'],
            sim_data['shift_direction'],
            sim_data['shift_distance_km'],
            sim_data['baseline_score'],
            sim_data['simulated_score']
        ))
        db.commit()
