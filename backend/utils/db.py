"""
CycloneShield AI - SQLite Database Utility Module
"""
import sqlite3
import os
from flask import current_app, g

def get_db_path():
    if current_app and 'DATABASE_PATH' in current_app.config:
        return current_app.config['DATABASE_PATH']
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'cycloneshield.db')

def get_db():
    if 'db' not in g:
        db_path = get_db_path()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        g.db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(db_path=None):
    if db_path is None:
        db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Cyclones Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cyclones (
            cyclone_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            year INTEGER NOT NULL,
            basin VARCHAR(50) NOT NULL DEFAULT 'Bay of Bengal',
            max_intensity_category VARCHAR(50),
            landfall_location VARCHAR(150),
            landfall_time_utc DATETIME,
            is_demo BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Track Points Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS track_points (
            point_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cyclone_id VARCHAR(50) NOT NULL,
            timestamp_utc DATETIME NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            wind_speed_knots REAL NOT NULL,
            central_pressure_hpa REAL,
            storm_category VARCHAR(20),
            distance_to_landfall_km REAL,
            is_landfall_point BOOLEAN DEFAULT 0,
            FOREIGN KEY (cyclone_id) REFERENCES cyclones(cyclone_id) ON DELETE CASCADE
        )
    ''')

    # Infrastructure Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS infrastructure (
            infra_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(150) NOT NULL,
            category VARCHAR(50) NOT NULL,
            subcategory VARCHAR(50),
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            state VARCHAR(50) NOT NULL DEFAULT 'Odisha',
            district VARCHAR(100) NOT NULL,
            capacity_val INTEGER,
            elevation_meters REAL,
            geojson_geometry TEXT NOT NULL,
            is_demo BOOLEAN DEFAULT 1
        )
    ''')

    # Vulnerability Evaluations Cache Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vulnerability_evaluations (
            eval_id VARCHAR(50) PRIMARY KEY,
            cyclone_id VARCHAR(50) NOT NULL,
            district_name VARCHAR(100) NOT NULL,
            overall_score REAL NOT NULL,
            risk_category VARCHAR(20) NOT NULL,
            wind_score REAL NOT NULL,
            rainfall_score REAL NOT NULL,
            surge_score REAL NOT NULL,
            infra_exposure_score REAL NOT NULL,
            exposed_hospital_count INTEGER NOT NULL,
            exposed_shelter_count INTEGER NOT NULL,
            evaluated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Simulation Logs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS simulation_logs (
            sim_id VARCHAR(50) PRIMARY KEY,
            base_cyclone_id VARCHAR(50) NOT NULL,
            delta_wind_knots REAL DEFAULT 0,
            delta_rainfall_percent REAL DEFAULT 0,
            shift_direction VARCHAR(10),
            shift_distance_km REAL DEFAULT 0,
            baseline_score REAL NOT NULL,
            simulated_score REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
