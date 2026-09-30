# CycloneShield AI - API Contract Specification

**Version**: `1.0.0-mvp`  
**Base URL**: `http://localhost:5000/api/v1`  
**Content-Type**: `application/json`

---

## 1. Common Response Formats

### Standard Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully.",
  "timestamp": "2026-09-26T12:00:00Z"
}
```

### Standard Error Response
```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Rainfall value must be a non-negative number.",
    "details": null
  },
  "timestamp": "2026-09-26T12:00:00Z"
}
```

### HTTP Status Codes
- `200 OK`: Request succeeded.
- `400 Bad Request`: Validation failure or missing parameters.
- `404 Not Found`: Resource or cyclone ID does not exist.
- `500 Internal Server Error`: Engine or processing error.
- `503 Service Unavailable`: External AI API issue or missing key.

---

## 2. API Endpoints

### 2.1 System Health
`GET /health`

**Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "CycloneShield AI Backend Engine",
    "version": "1.0.0-mvp",
    "gemini_api_configured": true
  }
}
```

---

### 2.2 List Cyclones
`GET /cyclones`

Returns list of historical cyclones available in the platform database.

**Response `200 OK`**:
```json
{
  "success": true,
  "data": [
    {
      "cyclone_id": "amphan_2020",
      "name": "Amphan",
      "year": 2020,
      "basin": "Bay of Bengal",
      "max_intensity": "Super Cyclonic Storm (SuCS)",
      "landfall_region": "Sunderbans / West Bengal",
      "is_demo": true
    },
    {
      "cyclone_id": "fani_2019",
      "name": "Fani",
      "year": 2019,
      "basin": "Bay of Bengal",
      "max_intensity": "Extremely Severe Cyclonic Storm (ESCS)",
      "landfall_region": "Puri, Odisha",
      "is_demo": true
    }
  ]
}
```

---

### 2.3 Get Cyclone Track (GeoJSON)
`GET /cyclones/<cyclone_id>/track`

Returns complete trajectory as GeoJSON FeatureCollection.

**Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "type": "FeatureCollection",
    "metadata": {
      "cyclone_id": "amphan_2020",
      "name": "Amphan"
    },
    "features": [
      {
        "type": "Feature",
        "geometry": { "type": "Point", "coordinates": [88.3, 21.7] },
        "properties": {
          "timestamp_utc": "2020-05-20T12:00:00Z",
          "wind_speed_knots": 85,
          "central_pressure_hpa": 960,
          "storm_category": "VSCS",
          "is_landfall_point": true
        }
      }
    ]
  }
}
```

---

### 2.4 Calculate Vulnerability Risk Score
`POST /risk/calculate`

Computes overall vulnerability score ($0-100$) and risk category for a target coordinate / region.

**Request Body**:
```json
{
  "cyclone_id": "amphan_2020",
  "region_bounds": {
    "lat_min": 21.0,
    "lat_max": 22.5,
    "lon_min": 87.5,
    "lon_max": 89.0
  },
  "buffer_km": 50.0
}
```

**Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "region_id": "wb_south_24_parganas",
    "vulnerability_score": 84.5,
    "risk_category": "EXTREME",
    "risk_breakdown": {
      "wind_hazard_score": 90.0,
      "rainfall_hazard_score": 82.0,
      "surge_hazard_score": 88.0,
      "infrastructure_exposure_score": 85.0,
      "topographic_resilience_score": 20.0
    },
    "buffer_radius_km": 50.0,
    "is_demo": true
  }
}
```

---

### 2.5 Infrastructure Exposure Analysis
`POST /infrastructure/exposure`

Returns exposed critical infrastructure assets filtered by category and distance to cyclone trajectory.

**Request Body**:
```json
{
  "cyclone_id": "amphan_2020",
  "buffer_km": 50.0,
  "categories": ["hospitals", "power", "roads", "shelters"]
}
```

**Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_exposed": 87,
      "hospitals": 14,
      "power_substations": 9,
      "road_km_flooded": 125.4,
      "shelters": 42,
      "railway_km_exposed": 45.2
    },
    "geojson": {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": { "type": "Point", "coordinates": [88.12, 21.85] },
          "properties": {
            "id": "hosp_0102",
            "category": "hospital",
            "name": "Kakarwip District Hospital",
            "bed_capacity": 150,
            "dist_to_eye_km": 14.2,
            "risk_level": "EXTREME"
          }
        }
      ]
    }
  }
}
```

---

### 2.6 What-If Scenario Simulation
`POST /simulation/what-if`

Simulates parameter changes and returns modified risk score & delta.

**Request Body**:
```json
{
  "cyclone_id": "amphan_2020",
  "delta_wind_knots": 15,
  "delta_rainfall_percent": 25,
  "shift_track_km": {
    "direction": "WEST",
    "distance_km": 20
  }
}
```

**Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "original_risk_score": 84.5,
    "simulated_risk_score": 92.1,
    "score_delta": 7.6,
    "original_category": "EXTREME",
    "simulated_category": "EXTREME",
    "newly_exposed_infrastructure": {
      "additional_hospitals": 3,
      "additional_shelters": 8
    }
  }
}
```

---

### 2.7 AI Risk Explanation
`POST /ai/explain`

Requests Gemini AI to synthesize numerical risk data into narrative explanations.

**Request Body**:
```json
{
  "cyclone_id": "amphan_2020",
  "risk_payload": {
    "vulnerability_score": 84.5,
    "risk_category": "EXTREME",
    "exposed_hospitals": 14,
    "peak_wind_knots": 115,
    "rainfall_mm": 280
  }
}
```

**Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "explanation_markdown": "### Vulnerability Analysis: EXTREME (Score: 84.5/100)\n\n**Primary Drivers:**\n1. **Severe Wind Load**: Peak winds of 115 knots exceed structural tolerances for coastal non-reinforced buildings.\n2. **High Medical Asset Exposure**: 14 hospitals fall directly within the 50km eye-wall destruction buffer.\n3. **Low Elevation**: Low-lying coastal topography exacerbates 280mm predicted rainfall inundation.",
    "model_used": "gemini-2.5-flash"
  }
}
```

---

### 2.8 AI Emergency Advisory Generation
`POST /ai/advisory`

Generates pre-landfall emergency advisories for civil defense authorities.

**Request Body**:
```json
{
  "cyclone_id": "amphan_2020",
  "target_audience": "Disaster Response Commanders",
  "risk_summary": {
    "score": 84.5,
    "category": "EXTREME",
    "shelters_available": 42,
    "high_risk_districts": ["South 24 Parganas", "East Midnapore"]
  }
}
```

**Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "advisory_id": "ADV-2020-AMP-001",
    "advisory_markdown": "# PRE-LANDFALL EMERGENCY ADVISORY\n**Issued by**: CycloneShield AI Decision Support System\n...",
    "download_url": "/api/v1/advisory/export?id=ADV-2020-AMP-001"
  }
}
```
