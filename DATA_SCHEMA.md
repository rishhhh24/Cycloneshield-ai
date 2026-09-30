# CycloneShield AI - Data Schema Specification

## 1. Database Schema (SQLite / SpatiaLite Compatible)

The SQLite database structure is designed to support easy migration to PostgreSQL/PostGIS by using standard SQL data types and normalized relational entities.

```sql
-- 1. Cyclones Master Table
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
);

-- 2. Cyclone Track Points Table
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
);

-- Index for spatial & temporal range lookup
CREATE INDEX IF NOT EXISTS idx_track_points_spatial ON track_points(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_track_points_cyclone ON track_points(cyclone_id);

-- 3. Critical Infrastructure Table
CREATE TABLE IF NOT EXISTS infrastructure (
    infra_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL, -- hospital, power, road, railway, shelter
    subcategory VARCHAR(50),
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    state VARCHAR(50) NOT NULL DEFAULT 'Odisha',
    district VARCHAR(100) NOT NULL,
    capacity_val INTEGER,
    elevation_meters REAL,
    geojson_geometry TEXT NOT NULL, -- GeoJSON Point or LineString representation
    is_demo BOOLEAN DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_infra_category ON infrastructure(category);
CREATE INDEX IF NOT EXISTS idx_infra_spatial ON infrastructure(latitude, longitude);

-- 4. Calculated Regional Vulnerability Scores Cache
CREATE TABLE IF NOT EXISTS vulnerability_evaluations (
    eval_id VARCHAR(50) PRIMARY KEY,
    cyclone_id VARCHAR(50) NOT NULL,
    district_name VARCHAR(100) NOT NULL,
    overall_score REAL NOT NULL, -- 0.0 to 100.0
    risk_category VARCHAR(20) NOT NULL, -- LOW, MODERATE, HIGH, EXTREME
    wind_score REAL NOT NULL,
    rainfall_score REAL NOT NULL,
    surge_score REAL NOT NULL,
    infra_exposure_score REAL NOT NULL,
    exposed_hospital_count INTEGER NOT NULL,
    exposed_shelter_count INTEGER NOT NULL,
    evaluated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cyclone_id) REFERENCES cyclones(cyclone_id)
);

-- 5. What-If Simulation Logs Table
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
);
```

---

## 2. GeoJSON Feature Standard Specifications

### 2.1 Cyclone Track Point Feature
```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [88.3, 21.7]
  },
  "properties": {
    "point_id": 104,
    "cyclone_id": "amphan_2020",
    "timestamp_utc": "2020-05-20T12:00:00Z",
    "wind_speed_knots": 85,
    "central_pressure_hpa": 960,
    "storm_category": "VSCS",
    "is_landfall_point": true
  }
}
```

### 2.2 Infrastructure GeoJSON Feature (Hospital / Shelter)
```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [88.12, 21.85]
  },
  "properties": {
    "infra_id": "HOSP-WB-049",
    "name": "Kakdwip Super Specialty Hospital",
    "category": "hospital",
    "district": "South 24 Parganas",
    "bed_capacity": 250,
    "has_power_backup": true,
    "elevation_m": 4.5
  }
}
```

---

## 3. Risk Engine Output Data Payload Standard

```json
{
  "evaluation_metadata": {
    "cyclone_id": "amphan_2020",
    "evaluation_timestamp": "2026-09-26T12:00:00Z",
    "buffer_radius_km": 50.0,
    "is_demo_data": true
  },
  "metrics": {
    "vulnerability_score": 84.5,
    "risk_category": "EXTREME",
    "component_weights": {
      "wind": 0.35,
      "rainfall": 0.25,
      "surge": 0.20,
      "infrastructure": 0.20
    }
  },
  "exposure_counts": {
    "hospitals": 14,
    "shelters": 42,
    "power_substations": 9,
    "flooded_road_km": 125.4
  }
}
```

---

## 4. PostgreSQL / PostGIS Migration Rules

When migrating from SQLite to PostgreSQL/PostGIS:
1. Replace `latitude REAL, longitude REAL` with standard Geometry types: `geometry(Point, 4326)`.
2. Replace spatial indexing with GIST index: `CREATE INDEX idx_infra_geom ON infrastructure USING GIST(geom);`.
3. Spatial buffer query `ST_DWithin` will replace client/Python side distance approximations:
   ```sql
   SELECT name, category FROM infrastructure 
   WHERE ST_DWithin(geom::geography, ST_MakePoint(88.3, 21.7)::geography, 50000);
   ```
