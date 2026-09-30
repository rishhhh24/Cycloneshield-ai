# CycloneShield AI - Infrastructure Vulnerability Risk Engine (ML)

This module implements the deterministic and machine-learning risk scoring pipeline for CycloneShield AI. It calculates the **Infrastructure Vulnerability Risk Score (0–100)**, maps scores to operational risk categories (`LOW`, `MODERATE`, `HIGH`, `EXTREME`), and extracts structured, explainable contributing factors for downstream Google Gemini AI reasoning.

---

## 1. System Design & Model Architecture

```mermaid
flowchart TD
    RAW[Meteorological & GIS Telemetry] --> PREP[Feature Preprocessor\n(StandardScaler & Feature Scaling)]
    PREP --> XGB[XGBoost Regressor Model\n(Trained on IBTrACS & Coastal Grids)]
    PREP --> BASE[Multi-Criteria Physics Baseline\n(Decision Support Prototype)]
    
    XGB --> PRED[Vulnerability Predictor]
    BASE --> PRED
    
    PRED --> OUT[Risk Score: 0-100\nRisk Level: LOW / MOD / HIGH / EXTREME\nExplainable Contributing Factors]
    OUT --> GEMINI[Google Gemini AI Reasoning Layer]
```

### Models Implemented
1. **Multi-Criteria Physics Baseline Model (`baseline_model.py`)**:
   - Transparent decision-support model combining wind load ($W_h$), rainfall inundation ($F_h$), storm surge ($S_h$), infrastructure asset density ($I_c$), and topographic elevation mitigation ($E_v$).
   - Used to generate deterministic component breakdowns and explainable factor drivers.
2. **XGBoost Regressor (`train.py`)**:
   - Gradient boosted decision tree regressor trained on historical cyclone parameter grids (NOAA IBTrACS + OpenStreetMap + DEM).
   - Artifacts persisted to `ml/model/vulnerability_xgb.joblib`.

---

## 2. Risk Classification Thresholds

| Risk Score | Risk Level | Hex Color Code | Operational Impact |
|---|---|---|---|
| **0.0 – 25.0** | **LOW** | `#10B981` (Green) | Minimal physical asset damage; routine monitoring. |
| **25.1 – 50.0** | **MODERATE** | `#F59E0B` (Yellow) | Minor tree downing, localized coastal road flooding. |
| **50.1 – 75.0** | **HIGH** | `#EF4444` (Orange) | Structural wall damage, hospital power backup activation required. |
| **75.1 – 100.0** | **EXTREME** | `#991B1B` (Dark Red) | Widespread power grid failure, mandatory civil defense evacuation. |

---

## 3. Explainable Contributing Factors Contract

The predictor outputs an array of structured `contributing_factors` designed for Gemini AI to synthesize narrative explanations:

```json
{
  "risk_score": 84.5,
  "risk_level": "EXTREME",
  "model_type": "XGBoost Regressor (Trained on IBTrACS & Coastal Geometry)",
  "contributing_factors": [
    {
      "factor": "wind_speed",
      "value": 115.0,
      "unit": "knots",
      "impact": "HIGH",
      "description": "Peak sustained wind speed of 115.0 knots (213 km/h) creates high structural hazard."
    },
    {
      "factor": "rainfall",
      "value": 280.0,
      "unit": "mm",
      "impact": "HIGH",
      "description": "Projected 280.0 mm 24h precipitation poses high flood inundation risk."
    },
    {
      "factor": "infrastructure_exposure",
      "value": 14,
      "unit": "critical_facilities",
      "impact": "HIGH",
      "description": "5 hospitals, 7 shelters, and 2 power stations are exposed within the storm buffer."
    },
    {
      "factor": "elevation",
      "value": 4.2,
      "unit": "meters",
      "impact": "MODERATE",
      "description": "Terrain elevation of 4.2m ASL provides moderate vulnerability to storm surge."
    }
  ]
}
```

---

## 4. Model Training & Evaluation

To train the models and persist joblib artifacts to `ml/model/`:

```bash
python ml/train.py
```

To run model evaluation metrics (RMSE, MAE, R² score, and Feature Importances):

```bash
python ml/evaluate.py
```
