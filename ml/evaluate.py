"""
CycloneShield AI - Model Evaluation Module
Calculates evaluation metrics (RMSE, MAE, R^2 score) and feature importances.
"""
import os
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ml.train import generate_training_dataset
from ml.predict import VulnerabilityPredictor
from ml.preprocessing import FEATURE_COLUMNS

def evaluate_models():
    print("Evaluating CycloneShield AI Vulnerability Models...")
    df_test = generate_training_dataset(samples=100, random_seed=99)
    
    predictor_xgb = VulnerabilityPredictor(use_xgboost=True)
    predictor_baseline = VulnerabilityPredictor(use_xgboost=False)

    y_true = df_test['vulnerability_score'].values
    y_pred_xgb = []
    y_pred_base = []

    for _, row in df_test.iterrows():
        input_dict = row.to_dict()
        res_xgb = predictor_xgb.predict(input_dict)
        res_base = predictor_baseline.predict(input_dict)
        y_pred_xgb.append(res_xgb['risk_score'])
        y_pred_base.append(res_base['risk_score'])

    # XGBoost Metrics
    rmse_xgb = np.sqrt(mean_squared_error(y_true, y_pred_xgb))
    mae_xgb = mean_absolute_error(y_true, y_pred_xgb)
    r2_xgb = r2_score(y_true, y_pred_xgb)

    # Baseline Metrics
    rmse_base = np.sqrt(mean_squared_error(y_true, y_pred_base))
    mae_base = mean_absolute_error(y_true, y_pred_base)
    r2_base = r2_score(y_true, y_pred_base)

    print("\n--- MODEL EVALUATION RESULTS ---")
    print(f"XGBoost Regressor  -> RMSE: {rmse_xgb:.4f} | MAE: {mae_xgb:.4f} | R^2: {r2_xgb:.4f}")
    print(f"Physics Baseline   -> RMSE: {rmse_base:.4f} | MAE: {mae_base:.4f} | R^2: {r2_base:.4f}")

    # Feature Importances if available
    if predictor_xgb.xgb_model:
        importances = predictor_xgb.xgb_model.feature_importances_
        feature_importance_dict = dict(zip(FEATURE_COLUMNS, [round(float(i), 4) for i in importances]))
        print("\nXGBoost Feature Importances:")
        for feat, imp in sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {feat:25s}: {imp:.4f}")

    return {
        "xgboost": {"rmse": round(rmse_xgb, 4), "mae": round(mae_xgb, 4), "r2": round(r2_xgb, 4)},
        "baseline": {"rmse": round(rmse_base, 4), "mae": round(mae_base, 4), "r2": round(r2_base, 4)}
    }

if __name__ == '__main__':
    evaluate_models()
