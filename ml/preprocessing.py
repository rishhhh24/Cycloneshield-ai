"""
CycloneShield AI - ML Feature Preprocessing Module
Extracts, scales, and formats raw meteorological, geospatial, and infrastructure features for model inference.
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Feature vector definitions
FEATURE_COLUMNS = [
    'wind_speed_knots',
    'rainfall_mm',
    'distance_to_track_km',
    'elevation_meters',
    'hospital_count',
    'shelter_count',
    'power_substation_count',
    'road_km'
]

class FeaturePreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False

    def extract_features_dict(self, input_data):
        """
        Converts raw dict or model payload into structured pandas DataFrame.
        """
        if isinstance(input_data, dict):
            row = {
                'wind_speed_knots': float(input_data.get('wind_speed_knots', 80.0)),
                'rainfall_mm': float(input_data.get('rainfall_mm', 200.0)),
                'distance_to_track_km': float(input_data.get('distance_to_track_km', 25.0)),
                'elevation_meters': float(input_data.get('elevation_meters', 5.0)),
                'hospital_count': float(input_data.get('hospital_count', 5.0)),
                'shelter_count': float(input_data.get('shelter_count', 10.0)),
                'power_substation_count': float(input_data.get('power_substation_count', 3.0)),
                'road_km': float(input_data.get('road_km', 45.0))
            }
            return pd.DataFrame([row])
        elif isinstance(input_data, pd.DataFrame):
            return input_data[FEATURE_COLUMNS].copy()
        else:
            raise ValueError("Input data must be a dictionary or pandas DataFrame.")

    def fit(self, df):
        X = self.extract_features_dict(df)
        self.scaler.fit(X)
        self.is_fitted = True
        return self

    def transform(self, input_data):
        X = self.extract_features_dict(input_data)
        if not self.is_fitted:
            # Default fit on standardized reference bounds if not pre-fitted
            ref_df = pd.DataFrame([{
                'wind_speed_knots': 75.0, 'rainfall_mm': 150.0,
                'distance_to_track_km': 50.0, 'elevation_meters': 10.0,
                'hospital_count': 5.0, 'shelter_count': 10.0,
                'power_substation_count': 3.0, 'road_km': 30.0
            }])
            self.fit(ref_df)
        return self.scaler.transform(X)

    def fit_transform(self, df):
        return self.fit(df).transform(df)
