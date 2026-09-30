"""
Unit Tests for Machine Learning Risk Engine
"""
import os
import sys
import pytest
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.preprocessing import FeaturePreprocessor
from ml.baseline_model import BaselineVulnerabilityModel
from ml.predict import VulnerabilityPredictor
from ml.evaluate import evaluate_models

def test_feature_preprocessor():
    prep = FeaturePreprocessor()
    sample_dict = {
        'wind_speed_knots': 110.0,
        'rainfall_mm': 260.0,
        'distance_to_track_km': 15.0,
        'elevation_meters': 3.5,
        'hospital_count': 6,
        'shelter_count': 12,
        'power_substation_count': 4,
        'road_km': 50.0
    }
    df = prep.extract_features_dict(sample_dict)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (1, 8)
    
    scaled = prep.fit_transform(df)
    assert scaled.shape == (1, 8)

def test_baseline_vulnerability_model():
    model = BaselineVulnerabilityModel()
    sample_data = {
        'wind_speed_knots': 115.0,
        'rainfall_mm': 280.0,
        'distance_to_track_km': 20.0,
        'elevation_meters': 4.0,
        'hospital_count': 5,
        'shelter_count': 10,
        'power_substation_count': 3,
        'road_km': 45.0
    }
    result = model.predict(sample_data)
    assert 'risk_score' in result
    assert 0.0 <= result['risk_score'] <= 100.0
    assert result['risk_level'] in ['LOW', 'MODERATE', 'HIGH', 'EXTREME']
    assert 'contributing_factors' in result
    assert len(result['contributing_factors']) >= 4
    for factor in result['contributing_factors']:
        assert 'factor' in factor
        assert 'impact' in factor
        assert 'description' in factor

def test_vulnerability_predictor():
    predictor = VulnerabilityPredictor(use_xgboost=True)
    sample_data = {
        'wind_speed_knots': 95.0,
        'rainfall_mm': 220.0,
        'distance_to_track_km': 30.0,
        'elevation_meters': 6.0,
        'hospital_count': 4,
        'shelter_count': 8,
        'power_substation_count': 2,
        'road_km': 35.0
    }
    pred = predictor.predict(sample_data)
    assert 'risk_score' in pred
    assert 0.0 <= pred['risk_score'] <= 100.0
    assert pred['risk_level'] in ['LOW', 'MODERATE', 'HIGH', 'EXTREME']
    assert 'contributing_factors' in pred

def test_model_evaluation():
    metrics = evaluate_models()
    assert 'xgboost' in metrics
    assert 'baseline' in metrics
    assert metrics['xgboost']['r2'] >= 0.90
