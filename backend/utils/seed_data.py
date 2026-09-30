"""
CycloneShield AI - Seed Realistic Demo Data Utility
"""
import sqlite3
import json
import os
from utils.db import get_db_path

def seed_demo_data(db_path=None):
    if db_path is None:
        db_path = get_db_path()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Seed Cyclones
    cyclones = [
        (
            'amphan_2020', 'Amphan', 2020, 'Bay of Bengal',
            'Super Cyclonic Storm (SuCS)', 'Sunderbans / West Bengal',
            '2020-05-20 12:00:00', 1
        ),
        (
            'fani_2019', 'Fani', 2019, 'Bay of Bengal',
            'Extremely Severe Cyclonic Storm (ESCS)', 'Puri, Odisha',
            '2020-05-03 08:00:00', 1
        )
    ]
    cursor.executemany('''
        INSERT OR REPLACE INTO cyclones 
        (cyclone_id, name, year, basin, max_intensity_category, landfall_location, landfall_time_utc, is_demo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', cyclones)

    # 2. Seed Track Points for Amphan 2020
    amphan_tracks = [
        ('amphan_2020', '2020-05-16 12:00:00', 13.2, 86.3, 45, 998, 'CS', 820.5, 0),
        ('amphan_2020', '2020-05-17 12:00:00', 15.4, 86.7, 85, 965, 'VSCS', 560.2, 0),
        ('amphan_2020', '2020-05-18 18:00:00', 18.8, 87.9, 130, 920, 'SuCS', 240.0, 0),
        ('amphan_2020', '2020-05-19 18:00:00', 20.2, 88.1, 105, 945, 'VSCS', 110.0, 0),
        ('amphan_2020', '2020-05-20 12:00:00', 21.7, 88.3, 85, 960, 'VSCS', 0.0, 1),
        ('amphan_2020', '2020-05-21 00:00:00', 23.5, 88.9, 40, 990, 'CS', -180.0, 0)
    ]
    
    # Track Points for Fani 2019
    fani_tracks = [
        ('fani_2019', '2019-04-27 12:00:00', 5.2, 88.5, 40, 1000, 'CS', 1600.0, 0),
        ('fani_2019', '2019-04-30 12:00:00', 12.5, 85.8, 90, 960, 'VSCS', 850.0, 0),
        ('fani_2019', '2019-05-02 12:00:00', 17.8, 84.9, 115, 932, 'ESCS', 230.0, 0),
        ('fani_2019', '2019-05-03 08:00:00', 19.8, 85.8, 100, 950, 'ESCS', 0.0, 1),
        ('fani_2019', '2019-05-04 00:00:00', 22.1, 87.5, 45, 992, 'CS', -210.0, 0)
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO track_points 
        (cyclone_id, timestamp_utc, latitude, longitude, wind_speed_knots, central_pressure_hpa, storm_category, distance_to_landfall_km, is_landfall_point)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', amphan_tracks + fani_tracks)

    # 3. Seed Coastal Infrastructure (Hospitals, Power, Shelters, Roads, Railways)
    infrastructure = [
        # Hospitals - West Bengal & Odisha
        (
            'HOSP-WB-01', 'Kakdwip Super Specialty Hospital', 'hospital', 'medical_center',
            21.875, 88.188, 'West Bengal', 'South 24 Parganas', 250, 4.2,
            json.dumps({"type": "Point", "coordinates": [88.188, 21.875]}), 1
        ),
        (
            'HOSP-WB-02', 'Digha General Hospital', 'hospital', 'medical_center',
            21.626, 87.507, 'West Bengal', 'East Midnapore', 150, 3.5,
            json.dumps({"type": "Point", "coordinates": [87.507, 21.626]}), 1
        ),
        (
            'HOSP-OD-01', 'Puri District Headquarter Hospital', 'hospital', 'medical_center',
            19.813, 85.831, 'Odisha', 'Puri', 400, 6.0,
            json.dumps({"type": "Point", "coordinates": [85.831, 19.813]}), 1
        ),
        (
            'HOSP-OD-02', 'Kendrapara Government Hospital', 'hospital', 'medical_center',
            20.501, 86.422, 'Odisha', 'Kendrapara', 200, 5.1,
            json.dumps({"type": "Point", "coordinates": [86.422, 20.501]}), 1
        ),
        (
            'HOSP-OD-03', 'Jagatsinghpur District Hospital', 'hospital', 'medical_center',
            20.268, 86.172, 'Odisha', 'Jagatsinghpur', 180, 7.0,
            json.dumps({"type": "Point", "coordinates": [86.172, 20.268]}), 1
        ),
        
        # Cyclone Shelters
        (
            'SHELTER-WB-01', 'Sagar Island Multi-Purpose Cyclone Shelter', 'shelter', 'cyclone_shelter',
            21.643, 88.082, 'West Bengal', 'South 24 Parganas', 1200, 5.5,
            json.dumps({"type": "Point", "coordinates": [88.082, 21.643]}), 1
        ),
        (
            'SHELTER-WB-02', 'Bakkhali Community Shelter', 'shelter', 'cyclone_shelter',
            21.564, 88.261, 'West Bengal', 'South 24 Parganas', 800, 4.0,
            json.dumps({"type": "Point", "coordinates": [88.261, 21.564]}), 1
        ),
        (
            'SHELTER-OD-01', 'Astaranga Coastal Shelter', 'shelter', 'cyclone_shelter',
            19.982, 86.271, 'Odisha', 'Puri', 1500, 6.2,
            json.dumps({"type": "Point", "coordinates": [86.271, 19.982]}), 1
        ),
        (
            'SHELTER-OD-02', 'Paradip Port Cyclone Refuge', 'shelter', 'cyclone_shelter',
            20.316, 86.611, 'Odisha', 'Jagatsinghpur', 2000, 8.0,
            json.dumps({"type": "Point", "coordinates": [86.611, 20.316]}), 1
        ),

        # Power Substations
        (
            'POWER-WB-01', 'Haldia 220kV Grid Substation', 'power', 'substation',
            22.062, 88.071, 'West Bengal', 'East Midnapore', 500, 5.0,
            json.dumps({"type": "Point", "coordinates": [88.071, 22.062]}), 1
        ),
        (
            'POWER-OD-01', 'Paradip Port 132kV Power Grid', 'power', 'substation',
            20.291, 86.602, 'Odisha', 'Jagatsinghpur', 350, 4.5,
            json.dumps({"type": "Point", "coordinates": [86.602, 20.291]}), 1
        ),

        # Tamil Nadu
        ('HOSP-TN-01', 'Rajiv Gandhi Government General Hospital', 'hospital', 'medical_center', 13.081, 80.278, 'Tamil Nadu', 'Chennai', 1500, 7.0, json.dumps({"type": "Point", "coordinates": [80.278, 13.081]}), 1),
        ('SHELTER-TN-01', 'Mahabalipuram Coastal Disaster Shelter', 'shelter', 'cyclone_shelter', 12.620, 80.194, 'Tamil Nadu', 'Chengalpattu', 2000, 8.5, json.dumps({"type": "Point", "coordinates": [80.194, 12.620]}), 1),
        ('POWER-TN-01', 'North Chennai Thermal Power Substation', 'power', 'substation', 13.250, 80.320, 'Tamil Nadu', 'Chennai', 800, 6.0, json.dumps({"type": "Point", "coordinates": [80.320, 13.250]}), 1),
        ('ROAD-TN-01', 'East Coast Road (ECR Chennai-Puducherry)', 'road', 'primary_highway', 12.850, 80.240, 'Tamil Nadu', 'Kanchipuram', 0, 5.0, json.dumps({"type": "LineString", "coordinates": [[80.250, 12.980], [80.240, 12.850], [80.194, 12.620]]}), 1),

        # Andhra Pradesh
        ('HOSP-AP-01', 'King George Hospital Visakhapatnam', 'hospital', 'medical_center', 17.708, 83.303, 'Andhra Pradesh', 'Visakhapatnam', 1200, 12.0, json.dumps({"type": "Point", "coordinates": [83.303, 17.708]}), 1),
        ('SHELTER-AP-01', 'Bheemunipatnam Multi-Purpose Relief Refuge', 'shelter', 'cyclone_shelter', 17.890, 83.450, 'Andhra Pradesh', 'Visakhapatnam', 1800, 10.0, json.dumps({"type": "Point", "coordinates": [83.450, 17.890]}), 1),
        ('POWER-AP-01', 'Simhadri Super Thermal Power Substation', 'power', 'substation', 17.600, 83.150, 'Andhra Pradesh', 'Visakhapatnam', 1000, 14.0, json.dumps({"type": "Point", "coordinates": [83.150, 17.600]}), 1),

        # Maharashtra
        ('HOSP-MH-01', 'Seth GS Medical College & KEM Hospital', 'hospital', 'medical_center', 19.002, 72.842, 'Maharashtra', 'Mumbai', 1800, 11.0, json.dumps({"type": "Point", "coordinates": [72.842, 19.002]}), 1),
        ('SHELTER-MH-01', 'Alibag Coastal Relief Center', 'shelter', 'cyclone_shelter', 18.641, 72.872, 'Maharashtra', 'Raigad', 1500, 9.0, json.dumps({"type": "Point", "coordinates": [72.872, 18.641]}), 1),
        ('POWER-MH-01', 'Trombay Thermal Power Station', 'power', 'substation', 19.005, 72.900, 'Maharashtra', 'Mumbai', 1200, 8.0, json.dumps({"type": "Point", "coordinates": [72.900, 19.005]}), 1),

        # Gujarat
        ('HOSP-GJ-01', 'Surat Civil Hospital & Medical College', 'hospital', 'medical_center', 21.170, 72.831, 'Gujarat', 'Surat', 1400, 13.0, json.dumps({"type": "Point", "coordinates": [72.831, 21.170]}), 1),
        ('SHELTER-GJ-01', 'Hazira Coastal Cyclone Shelter', 'shelter', 'cyclone_shelter', 21.100, 72.630, 'Gujarat', 'Surat', 2200, 7.0, json.dumps({"type": "Point", "coordinates": [72.630, 21.100]}), 1),
        ('POWER-GJ-01', 'Mundra Ultra Mega Power Grid', 'power', 'substation', 22.840, 69.720, 'Gujarat', 'Kutch', 1500, 15.0, json.dumps({"type": "Point", "coordinates": [69.720, 22.840]}), 1),

        # Kerala & Karnataka
        ('HOSP-KL-01', 'Ernakulam General Hospital', 'hospital', 'medical_center', 9.970, 76.280, 'Kerala', 'Ernakulam', 800, 5.0, json.dumps({"type": "Point", "coordinates": [76.280, 9.970]}), 1),
        ('HOSP-KA-01', 'Government Wenlock Hospital Mangaluru', 'hospital', 'medical_center', 12.870, 74.840, 'Karnataka', 'Dakshina Kannada', 900, 18.0, json.dumps({"type": "Point", "coordinates": [74.840, 12.870]}), 1),

        # North & Central India (Delhi, UP, Rajasthan, Assam)
        ('HOSP-DL-01', 'All India Institute of Medical Sciences (AIIMS)', 'hospital', 'medical_center', 28.567, 77.210, 'Delhi', 'New Delhi', 2500, 210.0, json.dumps({"type": "Point", "coordinates": [77.210, 28.567]}), 1),
        ('POWER-DL-01', 'Dadri National Capital Power Station', 'power', 'substation', 28.600, 77.550, 'Uttar Pradesh', 'Gautam Buddha Nagar', 2000, 205.0, json.dumps({"type": "Point", "coordinates": [77.550, 28.600]}), 1),
        ('HOSP-RJ-01', 'SMS Hospital Jaipur', 'hospital', 'medical_center', 26.895, 75.815, 'Rajasthan', 'Jaipur', 1600, 430.0, json.dumps({"type": "Point", "coordinates": [75.815, 26.895]}), 1),
        ('HOSP-AS-01', 'Guwahati Medical College & Hospital', 'hospital', 'medical_center', 26.155, 91.780, 'Assam', 'Kamrup Metropolitan', 1100, 55.0, json.dumps({"type": "Point", "coordinates": [91.780, 26.155]}), 1)
    ]

    cursor.executemany('''
        INSERT OR REPLACE INTO infrastructure
        (infra_id, name, category, subcategory, latitude, longitude, state, district, capacity_val, elevation_meters, geojson_geometry, is_demo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', infrastructure)

    conn.commit()
    conn.close()
    print("Demo data seeded successfully into SQLite database.")

if __name__ == '__main__':
    seed_demo_data()
