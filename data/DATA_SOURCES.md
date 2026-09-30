# CycloneShield AI - Data Sources & Geospatial Pipeline Documentation

## 1. Primary Data Sources & Provenance

| Dataset | Provider / Source | Geographic Coverage | License / Usage | Currency / Date |
|---|---|---|---|---|
| **Cyclone Historical Tracks** | NOAA IBTrACS v04r00 (International Best Track Archive for Climate Stewardship) | Bay of Bengal / North Indian Ocean (NI Basin) | Public Domain (US Government) | Updated 2024 / Historical Tracks 2019–2023 |
| **Critical Infrastructure** | OpenStreetMap (OSM) via Overpass API / Planet Dump | Coastal Odisha & West Bengal (19.0°N–23.0°N, 85.0°E–89.5°E) | Open Database License (ODbL) | Live 2026 Query / Cached MVP Extracts |
| **Topography / Elevation** | NASA SRTM 30m Digital Elevation Model (DEM) | Coastal South 24 Parganas, East Midnapore, Puri, Kendrapara | Public Domain (NASA/USGS) | SRTM v3 |
| **Meteorological Telemetry** | IMD (India Meteorological Department) & NOAA GFS | Bay of Bengal Landfall Corridors | Open Government Data (OGD) India / NOAA | Amphan (May 2020) & Fani (May 2019) Event Data |

---

## 2. Infrastructure Categorization & OSM Tag Mapping

The geospatial ingestion pipeline maps OpenStreetMap key-value tags to standardized CycloneShield AI categories:

```json
{
  "hospital": [
    "amenity=hospital",
    "amenity=clinic",
    "healthcare=hospital"
  ],
  "shelter": [
    "amenity=shelter",
    "building=shelter",
    "shelter_type=cyclone",
    "emergency=assembly_point"
  ],
  "power": [
    "power=substation",
    "power=plant",
    "power=station"
  ],
  "road": [
    "highway=primary",
    "highway=trunk",
    "highway=secondary"
  ],
  "railway": [
    "railway=rail",
    "railway=station"
  ]
}
```

---

## 3. Preprocessing & Normalization Pipeline

1. **Bounding Box Filter**:
   Geospatial queries are constrained to the target MVP coastal sector:
   $$\text{BBOX} = [19.0^\circ\text{N}, 85.0^\circ\text{E}, 23.0^\circ\text{N}, 89.5^\circ\text{E}]$$
2. **Coordinate Reference System (CRS)**:
   All spatial features are standardized to `WGS84` (`EPSG:4326`) format: `[longitude, latitude]`.
3. **Distance Calculation**:
   Geodesic distances are computed using the Haversine formula on Earth ellipsoid ($R = 6371.0\text{ km}$).
4. **Data Fallback & Labeling**:
   - Every record carries an `is_demo` boolean flag ($0 = \text{Real Telemetry/OSM}$, $1 = \text{Curated Demo Fallback}$).
   - Synthetic/demo datasets are explicitly badged in the UI as **`DEMO DATA`**.
