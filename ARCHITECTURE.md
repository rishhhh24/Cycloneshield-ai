# CycloneShield AI - System Architecture

## 1. System Architecture Overview

CycloneShield AI follows a clean, decoupled, tiered architecture. The system separates spatial telemetry processing, deterministic risk modeling, and generative AI reasoning into distinct execution layers.

```mermaid
flowchart TD
    subgraph Data Layer ["1. Data Layer"]
        DB[(SQLite / SpatiaLite)]
        RAW[NOAA IBTrACS Tracks]
        OSM[OSM Infrastructure GeoJSON]
        ENV[Rainfall / Elevation Data]
    end

    subgraph Backend ["2. Flask Backend Core"]
        API[Flask REST API Controllers]
        
        subgraph GIS ["Geospatial & Risk Pipeline"]
            GIS_SVC[GIS Processing Service\n(GeoPandas / Shapely)]
            EXP_SVC[Infrastructure Exposure Service]
            RISK_ENG[Vulnerability Risk Engine\n(Multi-Criteria / XGBoost)]
            SIM_ENG[What-If Simulation Engine]
        end
        
        subgraph AI_Layer ["Gemini AI Layer"]
            GEM_SVC[Gemini Reasoning Service\n(Google GenAI SDK)]
            ADV_GEN[Advisory Generator]
        end
    end

    subgraph Frontend ["3. Client Layer"]
        UI[Command Center Dashboard\n(HTML5 + Tailwind CSS + Vanilla JS)]
        MAP[Interactive Track & Risk Map\n(Leaflet.js + GeoJSON Overlays)]
        CHAT[AI Advisory & Assistant Panel]
    end

    RAW --> DB
    OSM --> DB
    ENV --> DB

    DB --> API
    API --> GIS_SVC
    GIS_SVC --> EXP_SVC
    EXP_SVC --> RISK_ENG
    SIM_ENG --> RISK_ENG

    RISK_ENG -->|Structured JSON Risk Payload| GEM_SVC
    GEM_SVC --> ADV_GEN

    API <-->|REST APIs / JSON| UI
    API <-->|GeoJSON Payloads| MAP
    ADV_GEN --> CHAT
```

---

## 2. Decoupled Pipeline & Component Responsibilities

### Step 1: Data Ingestion & Storage
- Historical cyclone tracks (NOAA IBTrACS format converted to standardized GeoJSON).
- Spatial infrastructure layers (Hospitals, Roads, Power, Railways, Shelters) indexed in SQLite using Spatial indexing / bounding box coordinates.
- Environmental grids (Rainfall mm/day, elevation contours, bathymetry).

### Step 2: Geospatial Buffer & Exposure Service (`gis_service.py` & `exposure_service.py`)
- Takes a cyclone track segment or projected landfall point.
- Constructs spatial buffer polygons using Shapely & GeoPandas (e.g., $25\text{ km}$ eye core, $50\text{ km}$ gale radius, $100\text{ km}$ outer band).
- Performs spatial point-in-polygon and linestring intersection queries against infrastructure features.
- Computes counts, densities, and proximity metrics for all critical assets.

### Step 3: Vulnerability Risk Engine (`risk_engine.py`)
- Calculates the **Infrastructure Vulnerability Risk Score (0–100)** deterministically:
  $$S_{\text{risk}} = w_w \cdot H_{\text{wind}} + w_r \cdot H_{\text{rain}} + w_s \cdot H_{\text{surge}} + w_i \cdot I_{\text{exposure}} - w_e \cdot E_{\text{elevation}}$$
- Maps scores to standard risk categories:
  - **LOW**: $0 - 25$
  - **MODERATE**: $26 - 50$
  - **HIGH**: $51 - 75$
  - **EXTREME**: $76 - 100$

### Step 4: What-If Simulation Engine (`simulation_service.py`)
- Modifies physical inputs (e.g. $+20\text{ knots}$ wind, $+30\%$ rainfall, $\pm 25\text{ km}$ track shift).
- Re-runs the GIS exposure and Risk Engine pipeline on modified parameters in real-time.

### Step 5: Gemini AI Reasoning Layer (`gemini_service.py`)
- Connected via the official `google-genai` Python SDK (`from google import genai`).
- Accepts the **structured numerical JSON payload** from the Risk Engine.
- System prompt enforces the **Strict Non-Fabrication Rule**: Gemini acts strictly as an analyst interpreting provided data, drafting official disaster management advisories, and explaining risk drivers.

### Step 6: Command Center Frontend
- Lightweight Vanilla JavaScript SPA architecture avoiding complex build toolchains.
- Tailwind CSS via CDN / standard stylesheet for modern dark-mode emergency dashboard aesthetic.
- Leaflet.js for high-performance vector layer rendering (Cyclone track, animated storm eye, risk zones, infrastructure markers).

---

## 3. Strict AI Boundary Enforcement Strategy

To guarantee that Gemini AI never fabricates risk scores or invents unverified numbers:

1. **Structured Context Injection**:
   Every prompt sent to Gemini is formatted with explicit JSON context containing exact pre-calculated values:
   ```json
   {
     "cyclone_name": "AMPHAN",
     "region": "South 24 Parganas, WB",
     "computed_risk_score": 84.5,
     "risk_category": "EXTREME",
     "exposed_hospitals": 14,
     "exposed_shelters": 42,
     "peak_wind_knots": 115,
     "projected_rainfall_mm": 280
   }
   ```
2. **System Prompt Guardrails**:
   > *"You are CycloneShield AI Decision Support Assistant. You MUST ONLY use the numerical scores, hospital counts, wind speeds, and rainfall figures provided in the context payload above. You are explicitly forbidden from generating new numbers or modifying existing scores."*

3. **Output Validation Filter**:
   Backend response middleware inspects generated responses to verify consistency against source metrics before serving to client UI.

---

## 4. SQLite to PostgreSQL / PostGIS Migration Blueprint

To ensure hackathon code is enterprise-ready for production scaling:
- MVP utilizes SQLite with GeoJSON text blobs / spatial bounding boxes for zero-config simplicity.
- DB layer abstracts query logic using lightweight repository methods (`db.py`).
- Schema definitions use standard ANSI SQL with spatial column layout ready for direct migration to PostgreSQL + PostGIS extension (`ST_DWithin`, `ST_Buffer`, `ST_Contains`).
