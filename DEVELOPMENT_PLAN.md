# CycloneShield AI - Phased Development Plan

This document outlines the step-by-step development sequence for coding agents and developers building CycloneShield AI.

---

## Phase 1: Environment Setup & Data Foundation
**Goal**: Establish base directory structure, dependencies, database schema, and historical track datasets.

- [x] **Task 1.1**: Create folder structure and skeleton configuration files (`.env.example`, `requirements.txt`, `config.py`).
- [ ] **Task 1.2**: Implement SQLite database initialization script (`backend/database/db.py` & `backend/database/schema.sql`).
- [ ] **Task 1.3**: Populate historical demo datasets (`data/demo/amphan_2020_demo.json` and `data/demo/fani_2019_demo.json`).
- [ ] **Task 1.4**: Ingest coastal infrastructure datasets for West Bengal and Odisha (hospitals, shelters, power stations, roads) into SQLite.

---

## Phase 2: GIS Processing & Infrastructure Exposure Engine
**Goal**: Build spatial buffering and point-in-polygon exposure calculations.

- [ ] **Task 2.1**: Implement `backend/services/gis_service.py` using GeoPandas and Shapely:
  - Generate spatial buffer polygons along cyclone trajectories ($25\text{ km}$, $50\text{ km}$, $100\text{ km}$).
  - Calculate distance from any coordinate to storm center/path.
- [ ] **Task 2.2**: Implement `backend/services/exposure_service.py`:
  - Query infrastructure elements falling within active spatial buffers.
  - Summarize exposed hospital beds, power substations, shelter capacities, and flooded road distances.

---

## Phase 3: Multi-Criteria Vulnerability Risk Engine & What-If Simulator
**Goal**: Calculate deterministic Infrastructure Vulnerability Risk Scores ($0-100$).

- [ ] **Task 3.1**: Implement `backend/services/risk_engine.py`:
  - Develop multi-criteria weighted risk index model ($W_{\text{wind}}, F_{\text{rain}}, S_{\text{surge}}, I_{\text{exposure}}, E_{\text{elevation}}$).
  - Classify output into `LOW`, `MODERATE`, `HIGH`, and `EXTREME` risk bands.
- [ ] **Task 3.2**: Implement `backend/services/simulation_service.py`:
  - Enable parameter modification ($\Delta\text{ wind}$, $\Delta\text{ rainfall}$, lateral track offset).
  - Calculate dynamic score deltas for what-if scenario testing.

---

## Phase 4: Flask REST API Controllers
**Goal**: Expose backend logic via documented REST endpoints.

- [ ] **Task 4.1**: Create Flask blueprints in `backend/api/`:
  - `routes_cyclone.py`: Endpoints for listing cyclones and retrieving GeoJSON track data.
  - `routes_risk.py`: Endpoints for calculating risk scores and hazard breakdowns.
  - `routes_infrastructure.py`: Endpoints for exposure analytics and spatial layers.
  - `routes_simulation.py`: Endpoint for what-if scenario execution.
- [ ] **Task 4.2**: Register blueprints in `backend/app.py` and test endpoints with curl / Postman.

---

## Phase 5: Command Center Frontend Dashboard
**Goal**: Build an interactive, dark-mode geospatial dashboard.

- [ ] **Task 5.1**: Build `frontend/index.html` structure:
  - Navigation header with `DEMO DATA` badge and Cyclone Selector dropdown.
  - Metric summary cards (Risk Score gauge, Peak Wind, Exposed Assets count).
  - Main Leaflet.js map viewport with layer toggles.
  - What-If simulation slider panel.
  - AI reasoning & advisory drawer.
- [ ] **Task 5.2**: Implement `frontend/js/map.js`:
  - Render interactive Leaflet map with storm tracks, intensity popups, and spatial buffer circles.
  - Render GeoJSON infrastructure markers (custom icons for hospitals, shelters, power grid).
- [ ] **Task 5.3**: Implement `frontend/js/dashboard.js`:
  - Wire up dynamic API fetches using `fetch()` to populate UI components, charts, and metric counters.

---

## Phase 6: Gemini AI Integration & Emergency Advisory Generator
**Goal**: Integrate Google Gemini API for risk reasoning, conversational assistance, and advisory generation.

- [ ] **Task 6.1**: Implement `backend/services/gemini_service.py` using `google-genai` SDK:
  - Configure Gemini client with `GEMINI_API_KEY` from `.env`.
  - Build prompt templates injecting structured numerical risk JSON.
- [ ] **Task 6.2**: Implement AI REST Endpoints in `backend/api/routes_ai.py`:
  - `/api/v1/ai/explain`: Risk factor narrative generation.
  - `/api/v1/ai/advisory`: Pre-landfall civil defense advisory generator.
  - `/api/v1/ai/chat`: Grounded chat assistant endpoint.
- [ ] **Task 6.3**: Implement Markdown & PDF export functionality (`fpdf2`) for downloadable advisories.

---

## Phase 7: Testing, Polishing & Verification
**Goal**: Ensure system reliability, run automated unit tests, and verify performance.

- [ ] **Task 7.1**: Write unit tests in `tests/`:
  - `test_risk_engine.py`: Test score boundaries ($0-100$) and category mapping.
  - `test_gis.py`: Verify buffer intersections.
  - `test_api.py`: Verify HTTP status codes and JSON response contracts.
- [ ] **Task 7.2**: Conduct end-to-end workflow check (Cyclone selection -> Map render -> Exposure calculation -> What-if simulation -> Gemini Advisory generation -> PDF export).
