# Google Earth Engine Integration - CycloneShield AI

This directory contains the Google Earth Engine (GEE) integration pipelines, Region of Interest (ROI) definitions, satellite flood extent analyzers, elevation extractors, and processed geospatial layer exports for CycloneShield AI.

---

## 1. Earth Engine Setup & Authentication

### Step 1: Install Dependencies
The Python Google Earth Engine API (`earthengine-api`) is required:
```bash
pip install earthengine-api
```

### Step 2: Google Cloud Project Setup
1. Create or register a Google Cloud project with Google Earth Engine API enabled via the [Google Cloud Console](https://console.cloud.google.com/).
2. Set the `GEE_PROJECT_ID` in your backend `.env` file:
   ```env
   GEE_PROJECT_ID=your-gcp-project-id
   ```

### Step 3: Authenticate User Account (Interactive Environment)
Run the Earth Engine authentication command in your command terminal:
```bash
earthengine authenticate
```
Follow the browser web flow to log in with your authorized Google Account. A token will be saved locally to `~/.config/earthengine/credentials`.

### Step 4: Headless Server Service Account Setup (Non-Interactive / Production)
For headless server deployments or CI/CD environments:
1. Create a Service Account in GCP Console with the **Earth Engine Resource Viewer / Admin** role.
2. Generate and download a Service Account JSON Key file (e.g. `gee-credentials.json`).
3. Point your `.env` environment variable to the key path:
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/gee-credentials.json
   ```

---

## 2. Earth Engine Datasets Used

| Earth Engine Dataset ID | Category | Description & Usage |
|---|---|---|
| `USGS/SRTMGL1_003` | Elevation / DEM | NASA Shuttle Radar Topography Mission 30m DEM for coastal topography. |
| `COPERNICUS/S1_GRD` | Satellite SAR | Sentinel-1 C-Band Synthetic Aperture Radar for post-cyclone flood extent mapping. |
| `COPERNICUS/S2_SR_HARMONIZED` | Satellite Optical | Sentinel-2 Multi-Spectral Surface Reflectance for high-res optical thumbnails. |
| `ESA/WorldCover/v100` | Land Cover | 10m global land use/land cover map (mangroves, wetlands, settlements, cropland). |
| `UCSB-CHG/CHIRPS/DAILY` | Precipitation | CHIRPS Daily precipitation grid for storm rainfall totals. |

---

## 3. Directory Layout & Reusable Scripts

```
gee/
├── README.md                          # Documentation & Authentication Guide
├── config/
│   ├── __init__.py
│   └── gee_config.py                  # GEE Project ID, Dataset IDs, and Event Windows
├── scripts/
│   ├── __init__.py
│   ├── define_roi.py                  # Region of Interest (ROI) geometry manager
│   ├── elevation_exporter.py          # NASA SRTM 30m DEM & slope extractor
│   ├── satellite_flood_analyzer.py    # Sentinel-1 SAR pre/post cyclone flood extent analyzer
│   ├── environmental_features.py      # CHIRPS precipitation & ESA WorldCover land use extractor
│   └── export_processed_layers.py     # Aggregates & exports layers to JSON summaries
└── exports/
    └── coastal_india_gee_layers.json  # Exported GEE layer payload for Flask API integration
```

---

## 4. Running the Processing Pipeline

To execute the GEE layer extraction and export pre-processed summaries for the Flask backend:

```bash
python gee/scripts/export_processed_layers.py
```

This updates both `gee/exports/coastal_india_gee_layers.json` and `data/processed/gee_summary.json`.

---

## 5. Flask API Integration Endpoints

The Flask backend exposes GEE processed layers via the following endpoints:

- `GET /api/gee/layers` - Returns complete GEE geospatial summary payload.
- `GET /api/gee/elevation` - Returns NASA SRTM DEM elevation statistics.
- `GET /api/gee/satellite` - Returns Sentinel-1 SAR flood inundation metadata.
