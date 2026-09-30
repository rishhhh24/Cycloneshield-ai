"""
CycloneShield AI - Model Inference & Predictor Module
Provides standardized risk predictions, risk categorization, and explainable contributing factors.
"""
import os
import sys
import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ml.baseline_model import BaselineVulnerabilityModel
from ml.preprocessing import FeaturePreprocessor, FEATURE_COLUMNS

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'model'))

class VulnerabilityPredictor:
    def __init__(self, use_xgboost=True):
        self.use_xgboost = use_xgboost
        self.baseline_model = BaselineVulnerabilityModel()
        self.xgb_model = None
        self.preprocessor = None
        self._load_artifacts()

    def _load_artifacts(self):
        xgb_path = os.path.join(MODEL_DIR, 'vulnerability_xgb.joblib')
        prep_path = os.path.join(MODEL_DIR, 'preprocessor.joblib')

        if os.path.exists(xgb_path) and os.path.exists(prep_path):
            try:
                self.xgb_model = joblib.load(xgb_path)
                self.preprocessor = joblib.load(prep_path)
            except Exception as e:
                print(f"Note loading XGBoost model artifact: {e}")

    def predict(self, input_features):
        """
        Executes model prediction and extracts explainable contributing factors for Gemini AI.
        """
        # Baseline physics model prediction for component breakdown & explainability
        baseline_result = self.baseline_model.predict(input_features)

        if self.use_xgboost and self.xgb_model and self.preprocessor:
            try:
                X_scaled = self.preprocessor.transform(input_features)
                raw_xgb_pred = self.xgb_model.predict(X_scaled)[0]
                risk_score = round(float(max(0.0, min(100.0, raw_xgb_pred))), 1)
                risk_level = BaselineVulnerabilityModel.classify_risk_level(risk_score)
                
                return {
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "model_type": "XGBoost Regressor (Trained on IBTrACS & Coastal Geometry)",
                    "hazard_components": baseline_result["hazard_components"],
                    "contributing_factors": baseline_result["contributing_factors"]
                }
            except Exception as e:
                print(f"XGBoost inference fallback to baseline physics model: {e}")

        return baseline_result
