"""
Unit and Integration Tests for CycloneShield AI API Endpoints
"""
import sys
import os
import pytest
import json

# Ensure backend directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app import create_app
from utils.db import init_db
from utils.seed_data import seed_demo_data

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            init_db()
            seed_demo_data()
        yield client

def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['status'] == 'healthy'

def test_frontend_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'CYCLONESHIELD AI' in response.data


def test_get_cyclones(client):
    response = client.get('/api/cyclones')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['data']) >= 2
    cyclone_ids = [c['cyclone_id'] for c in data['data']]
    assert 'amphan_2020' in cyclone_ids

def test_get_cyclone_by_id(client):
    response = client.get('/api/cyclones/amphan_2020')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['cyclone_id'] == 'amphan_2020'
    assert 'geojson_track' in data['data']
    features = data['data']['geojson_track']['features']
    assert len(features) > 0

def test_get_cyclone_not_found(client):
    response = client.get('/api/cyclones/non_existent_cyclone')
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False
    assert data['error']['code'] == 'CYCLONE_NOT_FOUND'

def test_get_infrastructure(client):
    response = client.get('/api/infrastructure')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    features = data['data']['features']
    assert len(features) > 0

def test_get_infrastructure_filter_category(client):
    response = client.get('/api/infrastructure?category=hospital')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    features = data['data']['features']
    for f in features:
        assert f['properties']['category'] == 'hospital'

def test_post_forecast_risk(client):
    payload = {
        "cyclone_id": "amphan_2020",
        "buffer_km": 50.0,
        "wind_knots": 105.0,
        "rainfall_mm": 280.0
    }
    response = client.post('/api/forecast', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    result = data['data']
    assert result['cyclone_id'] == 'amphan_2020'
    assert 'vulnerability_score' in result
    assert 0 <= result['vulnerability_score'] <= 100
    assert result['risk_category'] in ['LOW', 'MODERATE', 'HIGH', 'EXTREME']
    assert 'contributing_factors' in result
    assert len(result['contributing_factors']) > 0


def test_post_forecast_missing_param(client):
    response = client.post('/api/forecast', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert data['error']['code'] == 'MISSING_PARAMETER'

def test_post_simulation(client):
    payload = {
        "cyclone_id": "amphan_2020",
        "delta_wind_knots": 20,
        "delta_rainfall_percent": 30,
        "shift_direction": "WEST",
        "shift_distance_km": 15
    }
    response = client.post('/api/simulation', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    sim = data['data']
    assert 'baseline' in sim
    assert 'simulated' in sim
    assert 'delta' in sim
    assert sim['delta']['is_increased_risk'] is True
    assert 'disclaimer' in sim
    assert "NOT AN OFFICIAL WEATHER FORECAST" in sim['disclaimer']
    assert 'infrastructure_summary' in sim['baseline']
    assert 'infrastructure_summary' in sim['simulated']
    assert 'gemini_explanation' in sim

def test_post_simulation_absolute_values(client):
    payload = {
        "cyclone_id": "amphan_2020",
        "wind_knots": 135.0,
        "rainfall_mm": 350.0,
        "shift_direction": "WEST",
        "shift_distance_km": 20
    }
    response = client.post('/api/simulation', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    sim = data['data']
    assert sim['simulated']['peak_wind_knots'] == 135.0
    assert sim['simulated']['projected_rainfall_mm'] == 350.0

def test_get_gee_layers(client):
    response = client.get('/api/gee/layers')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'elevation_dem' in data['data']
    assert 'sentinel1_sar_flood' in data['data']

def test_get_gee_elevation(client):
    response = client.get('/api/gee/elevation')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'elevation_mean_meters' in data['data']

def test_get_gee_satellite(client):
    response = client.get('/api/gee/satellite')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'flood_inundation_detected_sqkm' in data['data']

def test_live_status_endpoint(client):
    response = client.get('/api/live/status')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'data_freshness' in data['data']
    assert data['data']['mode'] in ['LIVE', 'DEMO']

def test_live_cyclone_endpoint(client):
    response = client.get('/api/live/cyclone')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'active_cyclone' in data['data'] or 'status' in data['data']

def test_live_weather_endpoint(client):
    response = client.get('/api/live/weather?lat=21.7&lon=88.3')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'weather' in data['data']

def test_live_risk_endpoint(client):
    response = client.get('/api/live/risk')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_live_infrastructure_endpoint(client):
    response = client.get('/api/live/infrastructure')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_live_mode_toggle(client):
    response = client.post('/api/live/mode', json={'mode': 'DEMO'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['mode'] == 'DEMO'

    response = client.post('/api/live/mode', json={'mode': 'LIVE'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['mode'] == 'LIVE'


