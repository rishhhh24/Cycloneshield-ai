"""
CycloneShield AI - Configuration Module
"""
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'cycloneshield-dev-secret-key-2026')
    DATABASE_PATH = os.getenv('DATABASE_PATH', os.path.join(BASE_DIR, 'database', 'cycloneshield.db'))
    
    # Geospatial & Risk Settings
    DEFAULT_BUFFER_KM = float(os.getenv('DEFAULT_BUFFER_DISTANCE_KM', 50.0))
    MAX_SIMULATION_WIND_INCREASE_KNOTS = float(os.getenv('MAX_SIMULATION_WIND_INCREASE_KNOTS', 50))
    
    # Demo Data Configuration
    IS_DEMO_ENVIRONMENT = True
    DEMO_SOURCE_NOTE = "Demo track representation based on NOAA IBTrACS historical track data for Bay of Bengal cyclones."

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'test_cycloneshield.db')

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
