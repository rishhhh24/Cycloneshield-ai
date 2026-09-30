# CycloneShield AI - Project Specification

## 1. Executive Summary
**CycloneShield AI** is an AI-powered cyclone impact and infrastructure vulnerability decision-support platform designed specifically for coastal India. The platform integrates meteorological cyclone track data, geospatial infrastructure datasets (OpenStreetMap/satellite GIS), and environmental parameters with a deterministic/ML risk engine to generate an **Infrastructure Vulnerability Risk Score (0–100)**. Google Gemini AI acts as the reasoning and decision-support layer, interpreting complex vulnerability calculations into actionable emergency advisories, scenario analysis, and conversational intelligence for disaster response commanders.

---

## 2. Product Principles & Architecture Boundary

### Core Principle
> **CycloneShield AI is NOT a generic chatbot.**

The system strictly decouples numerical risk calculation from generative AI reasoning:

$$\text{Data} \longrightarrow \text{Geospatial Processing} \longrightarrow \text{Risk Engine} \longrightarrow \text{Infrastructure Exposure} \longrightarrow \text{Gemini AI Reasoning} \longrightarrow \text{Decision Support UI}$$

1. **Numerical Authority**: The ML/GIS pipeline computes all physical exposure, spatial buffer intersections, and numerical risk scores ($0-100$).
2. **Generative Boundary**: Google Gemini AI receives the structured output from the Risk & GIS engines. Gemini interprets, explains, contextualizes, answers what-if scenarios, and drafts advisories.
3. **Strict Non-Fabrication Rule**: **Gemini AI must NEVER fabricate or invent numerical risk values.** All figures cited by Gemini must originate directly from the upstream engine payloads.

---

## 3. MVP Scope & Baseline Scenario

For the hackathon MVP, the system focuses on a high-impact, realistic scenario:
- **Historical Cyclone**: Cyclone Amphan (May 2020) / Cyclone Fani (May 2019) in the Bay of Bengal.
- **Target Coastal Region**: Coastal Odisha (Puri, Kendrapara, Jagatsinghpur) and West Bengal (South 24 Parganas, East Midnapore).
- **Primary Objective**: Demonstrate end-to-end ingestion, GIS spatial buffering, multi-criteria risk scoring, what-if scenario testing, and automated AI advisory generation.

---

## 4. Detailed Feature Specifications

### F-01: Command Center Dashboard
- Sleek, dark-mode geospatial dashboard providing single-pane monitoring of coastal threats.
- Key metric cards: Cyclone Status, Peak Wind Speed, Estimated Exposed Population, High-Risk Infrastructure Count, Overall Regional Vulnerability Score.

### F-02: Cyclone Selector
- Dropdown interface to toggle between preset historical track data (e.g., Cyclone Amphan 2020, Cyclone Fani 2019) and user-uploaded custom track GeoJSON files.

### F-03: Interactive Cyclone Track Map
- Render track points and historical trajectory using Leaflet.js.
- Color-coded track segments based on storm intensity (Saffir-Simpson / IMD scale: CS, VSCS, SuCS).
- Clickable track points displaying timestamp, central pressure (hPa), wind speed (knots/km/h), and distance to landfall.

### F-04: Environmental Data Layer
- Overlay environmental variables: predicted rainfall (mm/24h), storm surge height (meters), elevation/DEM contour zones, and coastal bathymetry indicators.

### F-05: Risk & Vulnerability Map
- Spatial heatmap / chloropleth polygon overlay showing regional risk zones.
- Dynamic color coding:
  - **LOW** (Score 0 – 25): Green `#10B981`
  - **MODERATE** (Score 26 – 50): Yellow `#F59E0B`
  - **HIGH** (Score 51 – 75): Orange `#EF4444`
  - **EXTREME** (Score 76 – 100): Dark Red `#991B1B`

### F-06: Multi-Layer Infrastructure Map
- Layer controls to toggle specific critical infrastructure nodes & vectors:
  - 🏥 **Hospitals & Medical Centers**: Capacity, trauma facility status.
  - 🛣️ **Primary & Secondary Roads**: Evacuation route status, flood hazard zones.
  - ⚡ **Power Infrastructure**: Substations, high-tension lines.
  - 🚆 **Railway Infrastructure**: Major coastal tracks and stations.
  - 🛡️ **Cyclone Shelters**: Capacity and elevation safety.

### F-07: Infrastructure Exposure Analysis Engine
- Automated spatial buffer calculation (e.g., 25km, 50km, 100km radii from cyclone eye/path).
- Precise counting and categorizing of exposed infrastructure within buffer zones.

### F-08: Infrastructure Vulnerability Risk Score (0–100)
- Multi-criteria weighted scoring algorithm incorporating:
  - Wind Hazard Index ($W_h$)
  - Rainfall & Surge Flood Index ($F_h$)
  - Infrastructure Density & Criticality Index ($I_c$)
  - Topographic Vulnerability / Elevation Index ($E_v$)

### F-09: What-If Simulation Engine
- Interactive sliders allowing decision-makers to adjust parameters:
  - Rainfall increase/decrease ($\pm 50\%$)
  - Wind speed adjustment ($\pm 30\text{ knots}$)
  - Cyclone track shift (Lateral displacement North/South/East/West by $10-50\text{ km}$)
- Dynamic re-calculation of vulnerability scores and affected infrastructure.

### F-10: Gemini AI Reasoning & Conversational Assistant
- **Risk Explanation**: Converts raw spatial indices into clear narrative explanations of *why* a region is marked HIGH/EXTREME.
- **Conversational Assistant**: Grounded Chat interface answering disaster manager questions using spatial context.
- **Scenario Analysis**: Evaluates what-if slider changes and highlights emerging bottlenecks.
- **Emergency Advisories**: Automated drafting of pre-landfall evacuation recommendations, resource staging priorities, and emergency warnings.

### F-11: Multimodal Satellite Image Analysis (Optional / Modular)
- Image upload capability allowing users to attach post-event or pre-event SAR/optical satellite thumbnails.
- Gemini Vision analysis to inspect flooded areas or structural damage patterns.

### F-12: Downloadable Advisory Report
- One-click export of AI-generated advisories and risk summaries to Markdown and PDF formats.

### F-13: Model Confidence & Data Limitations Display
- Transparent UI banner and breakdown outlining model uncertainty, data currency (e.g. OpenStreetMap completeness), and operational disclaimers.

---

## 5. Non-Functional Requirements
- **Performance**: GIS buffer calculation and risk score generation in under 1.5 seconds for MVP datasets.
- **Security**: Zero hardcoded API keys; all sensitive parameters stored in `.env`.
- **Usability**: Clean responsive layout, clear visual hierarchy, accessible color palette meeting WCAG guidelines.
